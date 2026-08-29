"""Tests unitaires de la configuration."""

from collateral import config


def test_racine_contient_pyproject():
    """Bug du 28/08 : RACINE calculee par comptage de niveaux, cassee par un deplacement."""
    assert (config.RACINE / "pyproject.toml").exists()


def test_dossiers_du_projet_sont_sous_la_racine():
    for dossier in (config.DOSSIER_SQL, config.DOSSIER_TESTS, config.DOSSIER_DATA):
        assert config.RACINE in dossier.parents


def test_fichier_cog_porte_le_millesime():
    assert str(config.MILLESIME_COG) in config.FICHIER_COG
