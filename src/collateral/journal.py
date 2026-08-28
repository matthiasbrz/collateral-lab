"""Configuration de la journalisation."""

import logging

FORMAT_JOURNAL = "%(asctime)s %(levelname)-8s %(name)-24s %(message)s"
FORMAT_HORODATAGE = "%Y-%m-%d %H:%M:%S"

def configurer(niveau: int = logging.INFO) -> None:
    """Configure la journalisation. Un seul appel, depuis un point d'entree."""
    logging.basicConfig(level=niveau, format=FORMAT_JOURNAL, datefmt=FORMAT_HORODATAGE)