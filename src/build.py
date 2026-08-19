"""Exécute les scripts SQL de transformation dans l'ordre."""

from pathlib import Path
import duckdb

SCRIPTS = [
    "sql/stg_mutations.sql",
    "sql/stg_mutations_filtrees.sql",
    "sql/dim_commune.sql",
    "sql/agg_prix_m2_mensuel.sql",
    "sql/agg_prix_m2_glissant.sql",
    "sql/agg_prix_m2_evolution.sql",
    "sql/mart_prix_m2_reference.sql"
]


def main() -> None:
    con = duckdb.connect("collateral.duckdb")
    for chemin in SCRIPTS:
        print(f"exécution : {chemin}")
        con.execute(Path(chemin).read_text(encoding="utf-8"))
    print(con.sql("SELECT count(*) AS mutations FROM stg_mutations"))
    print(con.sql("SELECT count(*) AS mutations_filtrees FROM stg_mutations_filtrees"))
    print(con.sql("SELECT count(*) AS communes FROM dim_commune"))
    print(con.sql("SELECT count(*) AS agg_prix_m2_mensuel from agg_prix_m2_mensuel"))
    print(con.sql("SELECT count(*) AS agg_prix_m2_glissant from agg_prix_m2_glissant"))
    print(con.sql("SELECT count(*) AS agg_prix_m2_evolution from agg_prix_m2_evolution"))
    print(con.sql("SELECT count(*) AS mart_prix_m2_reference from mart_prix_m2_reference"))
    con.close()


if __name__ == "__main__":
    main()