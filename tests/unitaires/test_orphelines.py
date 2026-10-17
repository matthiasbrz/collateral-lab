"""Tests unitaires du controle des relations orphelines. Base en memoire."""

import duckdb
import pytest

from collateral.orphelines import orphelines

MANIFESTE = {
    "nodes": {
        "model.p.a": {
            "resource_type": "model",
            "schema": "dbt",
            "alias": "a",
            "config": {"materialized": "table"},
        },
        "snapshot.p.s": {
            "resource_type": "snapshot",
            "schema": "dbt",
            "alias": "s",
            "config": {"materialized": "snapshot"},
        },
    },
    "sources": {"source.p.brut.r": {"schema": "main", "identifier": "r"}},
}


@pytest.fixture
def con():
    c = duckdb.connect(":memory:")
    c.execute("CREATE SCHEMA dbt")
    for table in ("dbt.a", "dbt.s", "main.r"):
        c.execute(f"CREATE TABLE {table} AS SELECT 1 AS x")
    yield c
    c.close()


def test_rien_d_orphelin_quand_tout_est_declare(con):
    assert orphelines(con, MANIFESTE) == []


def test_reste_dans_le_schema_dbt(con):
    """Cas vecu le 10/10: dbt.stg_mutations_filtrees avait survecu a son renommage."""
    con.execute("CREATE TABLE dbt.stg_mutations_filtrees AS SELECT 1 AS x")
    assert orphelines(con, MANIFESTE) == ["dbt.stg_mutations_filtrees"]


def test_reste_dans_le_schema_main(con):
    """Une table de la chaine Python supprimee le 21/09 se lirait sans erreur."""
    con.execute("CREATE TABLE main.mart_prix_m2_reference AS SELECT 1 AS x")
    assert orphelines(con, MANIFESTE) == ["main.mart_prix_m2_reference"]


def test_schema_d_essai(con):
    """Une comparaison cree des schemas d'essai, comme 'avant' en S9."""
    con.execute("CREATE SCHEMA avant")
    con.execute("CREATE TABLE avant.a AS SELECT 1 AS x")
    assert orphelines(con, MANIFESTE) == ["avant.a"]
