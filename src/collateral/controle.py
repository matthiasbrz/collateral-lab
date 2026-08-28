"""Signature d'une table : preuve mecanique de non-regression."""

import duckdb


def signature(con: duckdb.DuckDBPyConnection, table: str) -> tuple[int, int]:
    """Rend (nombre de lignes, signature). La somme de hachages ignore l'ordre."""
    return con.execute(f"SELECT count(*), sum(hash(t)) FROM {table} t").fetchone()
