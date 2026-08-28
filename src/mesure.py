# src/mesure.py
"""Chronomètre une requete SQL sur plusieurs passages.

Usage: : python src/mesure.py
Le fichier doit contenir un SELECT, pas un CREATE TABLE :
on mesure le calcul, pas l'ecriture disque.
"""

import statistics
import sys
import time
from pathlib import Path

import duckdb

PASSAGES = 5

def mesurer(con, requete : str, passages: int = PASSAGES, prepare: str | None = None) -> list[float]:
    if prepare:
        con.execute(prepare)
    temps = []
    for _ in range(passages):
        debut = time.perf_counter()
        con.execute(requete).fetchall() # fetchall() force la materialisation
        temps.append(time.perf_counter() - debut)
    return temps


if __name__ == "__main__":
    chemin = Path(sys.argv[1])
    con = duckdb.connect("collateral.duckdb", read_only=True)
    temps = mesurer(con, chemin.read_text(encoding="utf-8"))
    con.close()

    print(f"{chemin.name}")
    print(" passages : " + " ".join(f"{t:.4f}" for t in temps))
    print(f" min : {min(temps):.4f} s")
    print(f" mediane : {statistics.median(temps):.4f} s")