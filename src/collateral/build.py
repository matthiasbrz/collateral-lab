"""Point d'entree : construction de l'entrepot.

Prerequis : sources presentes dans data/raw (lancer collateral.download au prealable).
Usage : python -m collateral.build
"""

import logging
import sys

from collateral import journal
from collateral.config import DOSSIER_SQL
from collateral.controle import signature
from collateral.db import connexion
from collateral.download import sources_manquantes
from collateral.sql import executer, lister

logger = logging.getLogger(__name__)

CODE_OK = 0
CODE_ERREUR = 1


def main() -> int:
    manquants = sources_manquantes()
    if manquants:
        logger.error("sources manquantes : %s", ", ".join(manquants))
        logger.error("lancez d'abord : python -m collateral.download")
        return CODE_ERREUR

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
    sys.exit(main())
