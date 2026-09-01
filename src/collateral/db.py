"""Ouverture d'une connexion a l'entrepot DuckDB."""

import logging
from collections.abc import Iterator
from contextlib import contextmanager

import duckdb

from collateral.config import BASE_DUCKDB

logger = logging.getLogger(__name__)


@contextmanager
def connexion(lecture_seule: bool = False) -> Iterator[duckdb.DuckDBPyConnection]:
    """Ouvre une connexion et garantit sa fermeture, meme en cas d'erreur."""
    try:
        con = duckdb.connect(str(BASE_DUCKDB), read_only=lecture_seule)
    except duckdb.IOException as erreur:
        raise RuntimeError(
            f"impossible d'ouvrir {BASE_DUCKDB}\n"
            f" cause : {erreur}\n"
            f" que faire : fermez les autres sessions DuckDB - console Python, "
            f"extension VS Code, autre terminal - puis relancez."
        ) from erreur

    logger.debug("connexion ouverte (lecture_seule=%s)", lecture_seule)
    try:
        yield con
    finally:
        con.close()
        logger.debug("connexion fermee")
