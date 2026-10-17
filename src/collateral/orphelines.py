"""Relations de l'entrepot que dbt ne declare pas.

Une table que plus rien ne reconstruit se lit sans erreur, avec des chiffres
perimes. Le controle compare tout ce qui existe dans la base, tous schemas
confondus, a ce que le manifeste declare : modeles, snapshots et sources.
"""

import json
import sys

import duckdb

from collateral.config import MANIFESTE_DBT

TYPES_RELATIONS = ("model", "snapshot", "seed")


def declarees(manifeste: dict) -> set[str]:
    """Rend 'schema.table' de chaque relation que dbt construit ou lit."""
    noeuds = {
        f"{n['schema']}.{n['alias']}"
        for n in manifeste["nodes"].values()
        if n["resource_type"] in TYPES_RELATIONS and n["config"].get("materialized") != "ephemeral"
    }
    sources = {f"{s['schema']}.{s['identifier']}" for s in manifeste["sources"].values()}
    return noeuds | sources


def existantes(con: duckdb.DuckDBPyConnection) -> set[str]:
    """Rend 'schema.table' de chaque table ou vue de la base, tous schemas confondus."""
    lignes = con.execute(
        """
        SELECT table_schema || '.' || table_name
        FROM information_schema.tables
        WHERE table_catalog = current_database()
        """
    ).fetchall()
    return {ligne[0] for ligne in lignes}


def orphelines(con: duckdb.DuckDBPyConnection, manifeste: dict) -> list[str]:
    """Rend, triees, les relations presentes que le manifeste ne declare pas."""
    return sorted(existantes(con) - declarees(manifeste))


if __name__ == "__main__":
    from collateral.db import connexion

    manifeste = json.loads(MANIFESTE_DBT.read_text(encoding="utf-8"))
    with connexion(lecture_seule=True) as con:
        trouvees = orphelines(con, manifeste)
    for relation in trouvees:
        print(relation)
    sys.exit(1 if trouvees else 0)
