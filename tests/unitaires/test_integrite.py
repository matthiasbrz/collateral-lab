"""Tests unitaires des controles d'integrite."""

import gzip
import os 

import pytest

from collateral.integrite import SourceInvalide, verifier

def _gz_incompressible(chemin, octets=200_000):
    """Ecrit une archive gzip depassant le seuil de taille minimale."""
    with gzip.open(chemin, "wb") as flux:
        flux.write(os.urandom(octets))
    return chemin

def test_verifier_accepte_une_archive_complete(tmp_path):
    verifier(_gz_incompressible(tmp_path / "complet.csv.gz"))

def test_verifier_refuse_un_fichier_absent(tmp_path):
    with pytest.raises(SourceInvalide, match="download"):
        verifier(tmp_path / "fantome.csv.gz")

def test_verifier_refuse_un_fichier_trop_petit(tmp_path):
    petit = tmp_path / "petit.csv.gz"
    petit.write_bytes(b"x" * 10)
    with pytest.raises(SourceInvalide, match="octets"):
        verifier(petit)

def test_verifier_refuse_une_archive_tronquee(tmp_path):
    complet = _gz_incompressible(tmp_path / "complet.csv.gz")
    tronque = tmp_path / "tronque.csv.gz"
    tronque.write_bytes(complet.read_bytes()[:-100])
    with pytest.raises(SourceInvalide, match="tronque"):
        verifier(tronque)

def test_verifier_refuse_un_entete_inattendu(tmp_path):
    csv = tmp_path / "cog.csv"
    csv.write_text("A,B,C\n" + "1,2,3\n" * 20_000, encoding="utf-8")
    with pytest.raises(SourceInvalide, match="TYPECOM"):
        verifier(csv, entete_attendu="TYPECOM")