"""Constantes et configuration de la chaine collateral-lab.

Aucune valeur litterale ne doit subsister ailleurs dans le code Python.
Les litteraux des fichiers SQL ne sont pas couverts : voir l'issue ouverte.
"""

import logging
from pathlib import Path

# --- Arborescence -----------------------------------------------------------
RACINE = Path(__file__).resolve().parent.parent
DOSSIER_DATA = RACINE / "data" / "raw"
DOSSIER_SQL = RACINE / "sql"
DOSSIER_TESTS = RACINE / "tests"
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

# --- Journalisation ---------------------------------------------------------
FORMAT_JOURNAL = "%(asctime)s  %(levelname)-8s %(name)-16s %(message)s"
FORMAT_HORODATAGE = "%Y-%m-%d %H:%M:%S"


def configurer_journal(niveau: int = logging.INFO) -> None:
    """Configure la journalisation. Un seul appel, depuis un point d'entree.

    A deplacer dans src/journal.py au J2 : ce module ne doit porter que des constantes.
    """
    logging.basicConfig(level=niveau, format=FORMAT_JOURNAL, datefmt=FORMAT_HORODATAGE)
