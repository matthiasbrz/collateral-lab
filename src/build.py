"""Point d'entrée unique des transformations.

Execute tous les scripts sql/NN_*.sql dans l'ordre de leur prefixe.
Prerequis : sources presentes dans data/raw (lancer src/download.py avant).
"""

import sys
from pathlib import Path

import duckdb

BASE = "collateral.duckdb"
DOSSIER_SQL = Path("sql")
DOSSIER_DATA = Path("data/raw")


def verifier_sources() -> None:
    """Echoue tot et clairement plutot que sur une erreur SQL incompréhensible."""
    manquants = []
    if not list(DOSSIER_DATA.glob("dvf_*.csv.gz")):
        manquants.append("fichiers DVF (dvf_*.csv.gz)")
    if not list(DOSSIER_DATA.glob("v_commune_*.csv")):
        manquants.append("referentiel COG (v_commune_*.csv)")
    if manquants:
        print("Sources manquantes dans data/raw : " + ", ".join(manquants))
        print("Lancez d'abord : python /src/download.py")
        sys.exit(1)


def main() -> None:
    verifier_sources()
    scripts = sorted(DOSSIER_SQL.glob("[0-9][0-9]_*.sql"))
    if not scripts:
        print("Aucun script SQL trouve dans sql/")
        sys.exit(1)

    con = duckdb.connect(BASE)
    for chemin in scripts:
        print(f"-> {chemin.name}")
        con.execute(chemin.read_text(encoding="utf-8"))
    print(con.sql("SELECT count(*) AS lignes FROM mart_prix_m2_reference"))
    con.close()


if __name__ == "__main__":
    main()
