"""Execution des fichiers SQL de transformation."""

import logging
from pathlib import Path

import duckdb

logger = logging.getLogger(__name__)

MOTIF_SCRIPTS = "[0-9][0-9]_*.sql"

def lister(dossier: Path, motif: str = MOTIF_SCRIPTS) -> list[Path]:
    """Rend les scripts d'un dossier, tries par prefixe numerique."""
    return sorted(dossier.glob(motif))

def executer(con: duckdb.DuckDBPyConnection, chemin: Path) -> None:
    """Execute le contenu d'un fichier SQL."""
    logger.info("execution : %s", chemin.name)
    con.execute(chemin.read_text(encoding="utf-8"))