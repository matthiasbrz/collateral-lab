"""Plan d'execution d'une requete stockee dans un fichier.

Usage : python -m collateral.plan sql/perf/05_agg_prix_m2_glissant.sql [--analyze]
"""

import logging
import sys
from pathlib import Path

from collateral import journal
from collateral.config import DOSSIER_PLANS
from collateral.db import connexion

logger = logging.getLogger(__name__)


def plan(chemin: Path, analyze: bool = False) -> str:
    """Rend le texte du plan d'execution d'une requete."""
    requete = chemin.read_text(encoding="utf-8").strip().rstrip(";")
    prefixe = "EXPLAIN ANALYZE" if analyze else "EXPLAIN"
    with connexion(lecture_seule=True) as con:
        return con.execute(f"{prefixe} {requete}").fetchone()[1]


if __name__ == "__main__":
    journal.configurer()
    chemin = Path(sys.argv[1])
    analyze = "--analyze" in sys.argv

    texte = plan(chemin, analyze)
    DOSSIER_PLANS.mkdir(parents=True, exist_ok=True)
    cible = DOSSIER_PLANS / f"{chemin.stem}_{'analyze' if analyze else 'explain'}.txt"
    cible.write_text(texte, encoding="utf-8")

    print(texte)
    logger.info("plan ecrit dans %s", cible)
