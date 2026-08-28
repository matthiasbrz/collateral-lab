"""Point d'entree unique des transformations.

Execute tous les scripts sql/NN_*.sql dans l'ordre de leur prefixe numerique.
Prerequis : sources presentes dans data/raw (lancer src/download.py au prealable).
"""

import logging
import sys

import duckdb

from config import (
    BASE_DUCKDB,
    DOSSIER_DATA,
    DOSSIER_SQL,
    FICHIER_COG,
    MOTIF_DVF,
    configurer_journal,
)

logger = logging.getLogger(__name__)

CODE_OK = 0
CODE_ERREUR = 1


def verifier_sources() -> None:
    """Echoue tot et clairement, plutot que sur une erreur SQL incomprehensible."""
    manquants = []
    if not list(DOSSIER_DATA.glob(MOTIF_DVF)):
        manquants.append(f"fichiers DVF ({MOTIF_DVF})")
    if not (DOSSIER_DATA / FICHIER_COG).exists():
        manquants.append(f"referentiel COG ({FICHIER_COG})")
    if manquants:
        logger.error("sources manquantes dans %s : %s", DOSSIER_DATA, ", ".join(manquants))
        logger.error("lancez d'abord : python src/download.py")
        sys.exit(CODE_ERREUR)


def main() -> int:
    verifier_sources()
    scripts = sorted(DOSSIER_SQL.glob("[0-9][0-9]_*.sql"))
    if not scripts:
        logger.error("aucun script SQL trouve dans %s", DOSSIER_SQL)
        return CODE_ERREUR

    con = duckdb.connect(str(BASE_DUCKDB))
    for chemin in scripts:
        logger.info("execution : %s", chemin.name)
        con.execute(chemin.read_text(encoding="utf-8"))

    lignes, signature = con.execute(
        "SELECT count(*), sum(hash(t)) FROM mart_prix_m2_reference t"
    ).fetchone()
    con.close()

    logger.info("mart_prix_m2_reference : %s lignes, signature %s", lignes, signature)
    return CODE_OK


if __name__ == "__main__":
    configurer_journal()
    sys.exit(main())
