"""Chronometrage d'une requete SQL sur plusieurs passages.

Usage : python -m collateral.mesure sql/perf/05_agg_prix_m2_glissant.sql
Le fichier doit contenir un SELECT : on mesure le calcul, pas l'ecriture disque.
"""

import statistics
import sys
import time
from pathlib import Path

import duckdb

from collateral.db import connexion

PASSAGES = 5


def mesurer(
    con: duckdb.DuckDBPyConnection,
    requete: str,
    passages: int = PASSAGES,
    prepare: str | None = None,
) -> list[float]:
    """Rend les durees de plusieurs executions. fetchall force la materialisation."""
    if prepare:
        con.execute(prepare)
    temps = []
    for _ in range(passages):
        debut = time.perf_counter()
        con.execute(requete).fetchall()
        temps.append(time.perf_counter() - debut)
    return temps


if __name__ == "__main__":
    chemin = Path(sys.argv[1])
    with connexion(lecture_seule=True) as con:
        temps = mesurer(con, chemin.read_text(encoding="utf-8"))

    print(chemin.name)
    print("  passages : " + "  ".join(f"{t:.4f}" for t in temps))
    print(f"  min      : {min(temps):.4f} s")
    print(f"  mediane  : {statistics.median(temps):.4f} s")
