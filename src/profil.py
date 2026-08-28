# src/profil.py
"""Metriques par operateur, triees par temps decroissant."""

import json
import sys
from pathlib import Path

import duckdb


def aplatir(noeud, lignes):
    info = noeud.get("extra_info")
    info = info if isinstance(info, dict) else {}
    lignes.append({
        "operateur": noeud.get("operator_type", "QUERY"),
        "temps": noeud.get("operator.timing", 0.0),
        "reel": noeud.get("operator_cardinality", 0),
        "estime": info.get("Estimated Cardinality"),
    })
    for enfant in noeud.get("children", []):
        aplatir(enfant, lignes)
    return lignes


if __name__ == "__main__":
    chemin = Path(sys.argv[1])
    requete = chemin.read_text(encoding="utf-8").strip().rstrip(";")
    sortie = Path("docs/plans/profil.json").resolve()
    sortie.parent.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect("collateral.duckdb", read_only=True)
    con.execute("PRAGMA enable_profiling = 'json'")
    con.execute(f"PRAGMA profiling_output = '{sortie.as_posix()}'")
    con.execute(requete).fetchall()
    con.execute("PRAGMA disable_profiling")
    con.close()

    lignes = sorted(
        aplatir(json.loads(sortie.read_text(encoding="utf-8")), []),
        key=lambda: li["temps"],
        reverse=True,
    )

    print(f"{'operateur':<24}{'temps (s)':>12}{'reel':>12}{'estime':>12}")
    for li in lignes[:12]:
        print(
            f"{li['operateur']:<24}{li['temps']:>12.4f}{li['reel']:>12}"
            f"{li['estime'] if li['estime'] is not None else '-'!s:>12}"
        )
