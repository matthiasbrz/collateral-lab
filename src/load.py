"""Chargement des fichiers DVF bruts dans l'entrepôt local DuckDB."""

import duckdb

BASE = "collateral.duckdb"


def main() -> None:
    con = duckdb.connect(BASE)
    con.execute("""
        CREATE OR REPLACE TABLE raw_mutations AS
        SELECT *
        FROM read_csv(
            'data/raw/*.csv.gz',
            union_by_name = true,
            types = {
                'code_commune': 'VARCHAR',
                'code_postal': 'VARCHAR',
                'code_departement': 'VARCHAR',
                'id_parcelle': 'VARCHAR'
                }
            );
    """)
    print(con.sql("SELECT count(*) AS lignes FROM raw_mutations"))
    con.close()


if __name__ == "__main__":
    main()