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
    con = duckdb.connect(str(BASE_DUCKDB), read_only=lecture_seule)
    logger.debug("connexion ouverte sur %s (lecture_seule=%s)", BASE_DUCKDB, lecture_seule)
    try:
        yield con
    finally:
        con.close()
        logger.debug("connexion fermee")
