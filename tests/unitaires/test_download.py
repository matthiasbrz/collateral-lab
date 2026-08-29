"""Tests unitaires du telechargement. Aucun acces reseau, aucun acces a l'entrepot."""

import io
import zipfile

import pytest

from collateral.download import contenu_cog, nom_fichier_dvf, sources_manquantes, url_dvf

COG_MINIMAL = b"TYPECOM,COM,REG,DEP,LIBELLE\nCOM,76540,28,76,Rouen\n"


def test_url_dvf_cas_nominal():
    url = url_dvf("76", 2025)
    assert url.startswith("https://")
    assert url.endswith("/2025/departements/76.csv.gz")


def test_nom_fichier_dvf_cas_nominal():
    assert nom_fichier_dvf("76", 2025) == "dvf_76_2025.csv.gz"


def test_contenu_cog_accepte_un_csv_brut():
    assert contenu_cog(COG_MINIMAL) == COG_MINIMAL


def test_contenu_cog_extrait_une_archive_zip():
    tampon = io.BytesIO()
    with zipfile.ZipFile(tampon, "w") as archive:
        archive.writestr("v_commune_2026.csv", COG_MINIMAL)
    assert contenu_cog(tampon.getvalue()) == COG_MINIMAL


def test_contenu_cog_refuse_une_page_html():
    """Cas vecu : l'Insee renvoie une page d'erreur au lieu du fichier."""
    with pytest.raises(RuntimeError, match="pas le fichier COG"):
        contenu_cog(b"<!DOCTYPE html><html><body>Service indisponible</body></html>")


def test_contenu_cog_refuse_une_archive_a_deux_csv():
    tampon = io.BytesIO()
    with zipfile.ZipFile(tampon, "w") as archive:
        archive.writestr("a.csv", COG_MINIMAL)
        archive.writestr("b.csv", COG_MINIMAL)
    with pytest.raises(RuntimeError, match="archive COG inattendue"):
        contenu_cog(tampon.getvalue())


def test_sources_manquantes_tout_present(tmp_path):
    (tmp_path / "dvf_76_2025.csv.gz").write_bytes(b"")
    (tmp_path / "v_commune_2026.csv").write_bytes(b"")
    assert sources_manquantes(tmp_path) == []


def test_sources_manquantes_dossier_vide(tmp_path):
    assert len(sources_manquantes(tmp_path)) == 2


def test_sources_manquantes_cog_absent(tmp_path):
    (tmp_path / "dvf_76_2025.csv.gz").write_bytes(b"")
    manquants = sources_manquantes(tmp_path)
    assert len(manquants) == 1
    assert "COG" in manquants[0]
