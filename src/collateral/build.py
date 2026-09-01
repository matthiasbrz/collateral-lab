"""Point d'entree : construction de l'entrepot.

Prerequis : sources presentes dans data/raw (lancer collateral.download au prealable).
Usage : python -m collateral.build
"""

import logging
import sys

from collateral import journal
from collateral.config import DOSSIER_DATA, DOSSIER_SQL, FICHIER_COG, MOTIF_DVF
from collateral.controle import signature
from collateral.db import connexion
from collateral.download import sources_manquantes
from collateral.integrite import verifier
from collateral.sql import executer, lister

logger = logging.getLogger(__name__)

CODE_OK = 0
CODE_ERREUR = 1


def verifier_sources() -> None:
    """Verifie que les sources sont presentes ET completes avant toute lecture."""
    manquants = sources_manquantes()
    if manquants:
        raise RuntimeError(
            "sources manquantes : "
            + ", ".join(manquants)
            + "\n  que faire : python -m collateral.download"
        )
    for chemin in sorted(DOSSIER_DATA.glob(MOTIF_DVF)):
        verifier(chemin)
    verifier(DOSSIER_DATA / FICHIER_COG, entete_attendu="TYPECOM")


def main() -> int:
    verifier_sources()

    scripts = lister(DOSSIER_SQL)
    if not scripts:
        logger.error("aucun script SQL dans %s", DOSSIER_SQL)
        return CODE_ERREUR

    with connexion() as con:
        for chemin in scripts:
            executer(con, chemin)
        lignes, empreinte = signature(con, "mart_prix_m2_reference")

    logger.info("mart_prix_m2_reference : %s lignes, signature %s", lignes, empreinte)
    return CODE_OK


if __name__ == "__main__":
    journal.configurer()
    try:
        sys.exit(main())
    except RuntimeError as erreur:
        logger.error("%s", erreur)
        sys.exit(CODE_ERREUR)
