"""Tests unitaires de la comparaison de relations. Base en memoire."""

import duckdb
import pytest

from collateral.controle import comparer


@pytest.fixture
def con():
    c = duckdb.connect(":memory:")
    c.execute("CREATE SCHEMA gauche")
    c.execute("CREATE SCHEMA droite")
    yield c
    c.close()


def test_relations_identiques(con):
    for schema in ("gauche", "droite"):
        con.execute(f"CREATE TABLE {schema}.t AS SELECT 1 AS a, 'x' AS b UNION ALL SELECT 2, 'y'")
    assert comparer(con, "t", "gauche", "droite").identique


def test_ecart_de_contenu(con):
    con.execute("CREATE TABLE gauche.t AS SELECT 1 AS a, 'x' AS b UNION ALL SELECT 2, 'y'")
    con.execute("CREATE TABLE droite.t AS SELECT 1 AS a, 'x' AS b UNION ALL SELECT 2, 'z'")
    assert comparer(con, "t", "gauche", "droite").verdict == "contenu"


def test_ordre_des_colonnes_est_un_ecart_de_structure(con):
    """Memes donnees, ordre different : la structure doit etre vue AVANT le contenu."""
    con.execute("CREATE TABLE gauche.t AS SELECT 1 AS a, 2 AS b")
    con.execute("CREATE TABLE droite.t AS SELECT 2 AS b, 1 AS a")
    assert comparer(con, "t", "gauche", "droite").verdict == "structure"


def test_colonne_manquante(con):
    """Cas vecu le 04/09 : mois, annee et trimestre absentes du modele dbt."""
    con.execute("CREATE TABLE gauche.t AS SELECT 1 AS a, 2 AS b")
    con.execute("CREATE TABLE droite.t AS SELECT 1 AS a")
    resultat = comparer(con, "t", "gauche", "droite")
    assert resultat.verdict == "structure"
    assert any("b" in d for d in resultat.details)


def test_ecart_de_volumetrie(con):
    con.execute("CREATE TABLE gauche.t AS SELECT 1 AS a UNION ALL SELECT 2")
    con.execute("CREATE TABLE droite.t AS SELECT 1 AS a")
    assert comparer(con, "t", "gauche", "droite").verdict == "volumetrie"


def test_multiplicite_differente(con):
    """EXCEPT dedoublonne : sans la signature, ce cas passerait pour identique."""
    con.execute("CREATE TABLE gauche.t AS SELECT 1 AS a UNION ALL SELECT 1 UNION ALL SELECT 2")
    con.execute("CREATE TABLE droite.t AS SELECT 1 AS a UNION ALL SELECT 2 UNION ALL SELECT 2")
    assert comparer(con, "t", "gauche", "droite").verdict == "multiplicite"


def test_table_absente_d_un_schema(con):
    con.execute("CREATE TABLE gauche.t AS SELECT 1 AS a")
    assert comparer(con, "t", "gauche", "droite").verdict == "absente"
