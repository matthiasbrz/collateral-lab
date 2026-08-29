"""Constantes de la chaine collateral-lab.

Aucune valeur litterale ne doit subsister ailleurs dans le code Python.
Les litteraux des fichiers SQL ne sont pas couverts : voir l'issue ouverte.
"""

from pathlib import Path


def _racine() -> Path:
    """Remonte jusqu'au repertoire contenant pyproject.toml."""
    for dossier in Path(__file__).resolve().parents:
        if (dossier / "pyproject.toml").exists():
            return dossier
    raise RuntimeError("racine du projet introuvable : pyproject.toml absent")


# --- Arborescence -----------------------------------------------------------
RACINE = _racine()
DOSSIER_DATA = RACINE / "data" / "raw"
DOSSIER_SQL = RACINE / "sql"
DOSSIER_TESTS = RACINE / "tests" / "donnees"
DOSSIER_PLANS = RACINE / "docs" / "plans"
BASE_DUCKDB = RACINE / "collateral.duckdb"

# --- Perimetre --------------------------------------------------------------
DEPARTEMENT = "76"
MILLESIMES = (2023, 2024, 2025)
MILLESIME_COG = 2026

# --- Sources ----------------------------------------------------------------
URL_DVF = "https://files.data.gouv.fr/geo-dvf/latest/csv"
URL_COG = "https://www.insee.fr/fr/statistiques/fichier/8740222/v_commune_2026.csv"
FICHIER_COG = f"v_commune_{MILLESIME_COG}.csv"
MOTIF_DVF = "dvf_*.csv.gz"

# --- Gouvernance ------------------------------------------------------------
SEUIL_PUBLICATION = 5
