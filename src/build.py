"""Exécute les scripts SQL de transformation dans l'ordre."""

from pathlib import Path
import duckdb

SCRIPTS = [
    "sql/stg_mutations.sql",
    "sql/stg_mutations_filtrees.sql",
    "sql/dim_commune.sql"
]


def main() -> None:
    con = duckdb.connect("collateral.duckdb")
    for chemin in SCRIPTS:
        print(f"exécution : {chemin}")
        con.execute(Path(chemin).read_text(encoding="utf-8"))
    print(con.sql("SELECT count(*) AS mutations FROM stg_mutations"))
    print(con.sql("SELECT count(*) AS mutations_filtrees FROM stg_mutations_filtrees"))
    print(con.sql("SELECT count(*) AS communes FROM dim_commune"))
    con.close()


if __name__ == "__main__":
    main()