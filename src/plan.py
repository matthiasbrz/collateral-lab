"""Affiche et enregistre le plan d'execution d'une requete.

Usage : 
    python src/plan.py sql/perf/05_agg_prix_m2_glissant.sql
    python src/plan.py sql/perf/05_agg_prix_m2_glissant.sql --analyze
"""

import sys
from pathlib import Path

import duckdb

SORTIE = Path("docs/plans")

if __name__ == "__main__":
    chemin = Path(sys.argv[1])
    analyze = "--analyze" in sys.argv

    requete = chemin.read_text(encoding="utf-8").strip().rstrip(";")
    prefixe = "EXPLAIN ANALYZE" if analyze else "EXPLAIN"

    con = duckdb.connect("collateral.duckdb", read_only=True)
    texte = con.execute(f"{prefixe} {requete}").fetchone()[1]
    con.close()

    SORTIE.mkdir(parents=True, exist_ok=True)
    cible = SORTIE / f"{chemin.stem}_{'analyze' if analyze else 'explain'}.txt"
    cible.write_text(texte, encoding="utf-8")

    print(texte)
    print(f"\nPlan complet ecrit dans {cible}")