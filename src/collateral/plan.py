"""Affiche et enregistre le plan d'execution d'une requete.

Usage :
    python src/plan.py sql/perf/05_agg_prix_m2_glissant.sql [--analyze]
"""

import logging
import sys
from pathlib import Path

import duckdb

from config import BASE_DUCKDB, DOSSIER_PLANS, configurer_journal

logger = logging.getLogger(__name__)


def plan(chemin: Path, analyze: bool = False) -> str:
    """Rend le texte du plan d'execution d'une requete stockee dans un fichier."""
    requete = chemin.read_text(encoding="utf-8").strip().rstrip(";")
    prefixe = "EXPLAIN ANALYZE" if analyze else "EXPLAIN"
    con = duckdb.connect(str(BASE_DUCKDB), read_only=True)
    texte = con.execute(f"{prefixe} {requete}").fetchone()[1]
    con.close()
    return texte


if __name__ == "__main__":
    configurer_journal()
    chemin = Path(sys.argv[1])
    analyze = "--analyze" in sys.argv

    texte = plan(chemin, analyze)
    DOSSIER_PLANS.mkdir(parents=True, exist_ok=True)
    cible = DOSSIER_PLANS / f"{chemin.stem}_{'analyze' if analyze else 'explain'}.txt"
    cible.write_text(texte, encoding="utf-8")

    print(texte)  # le plan est le produit demande
    logger.info("plan ecrit dans %s", cible)  # le chemin est un diagnostic
