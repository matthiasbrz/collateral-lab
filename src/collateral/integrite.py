"""Controles d'integrite des fichiers sources.

Un fichier tronque qui se charge sans erreur est le pire des cas : la chaine produit un resultat faux sans rien signaler.
"""

import gzip
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

TAILLE_MINIMALE = 100_000 # octets : toute source complete pese davantage

class SourceInvalide(RuntimeError):
    """Un fichier source est absent, tronque ou illisible."""

def verifier(chemin : Path, entete_attendu: str | None = None) -> None:
    """Verifie qu'un fichier source est complet et lisible.

    Raises:
        SourceInvalide: message indiquant quoi faire, pas seulement ce qui s'est passe.
    """
    if not chemin.exists():
        raise SourceInvalide(
            f"{chemin.name} absent de {chemin.parent}\n"
            f"  que faire : python -m collateral.download"
        )

    taille = chemin.stat().st_size
    if taille < TAILLE_MINIMALE:
        raise SourceInvalide(
            f"{chemin.name} ne pese que {taille} octets, une source complete en pese davantage\n"
            f"  cause probable : telechargement interrompu\n"
            "   que faire : supprimez {chemin} puis relancez python -m collateral.download"
        )

    if chemin.suffixes[-1] == ".gz":
        _verifier_gzip(chemin)
    elif entete_attendu is not None:
        _verifier_entete(chemin, entete_attendu)

    logger.debug("integrite verifiee : %s (%.1f Mo)", chemin.name, taille / 1e6)

def _verifier_gzip(chemin: Path) -> None:
    """Decompresse integralement l'archive : valide la somme de controle gzip."""
    try:
        with gzip.open(chemin, "rb") as flux:
            while flux.read(1 << 20):
                pass
    except (OSError, EOFError) as erreur:
        raise SourceInvalide(
            f"{chemin.name} est tronque ou illisible\n"
            f"  cause : {erreur}\n"
            f"  que faire : supprimez {chemin} puis relancez python -m collateral.download"
        ) from erreur

def _verifier_entete(chemin: Path, attendu: str) -> None:
    """Verifie qu'une colonne attendue figure dans la premiere ligne."""
    with chemin.open("r", encoding="utf-8", errors="replace") as flux:
        premiere = flux.readline()
    if attendu not in premiere:
        raise SourceInvalide(
            f"{chemin.name} ne contient pas la colonne attendue '{attendu}'\n"
            f"  premiere ligne : {premiere[:120]!r}\n"
            f"  que faire : supprimez {chemin} puis relancez python -m collateral.download"
        )