"""Version declaree des sources : chaque fichier a une empreinte attendue."""

import hashlib
from pathlib import Path

from collateral.config import RACINE

FICHIER_EMPREINTES = RACINE / "docs" / "empreintes_attendues.txt"

CONSIGNE = (
    "Nouvelle livraison DVF probable. Verifier les donnees, puis mettre a jour "
    "docs/empreintes_attendues.txt dans le meme commit que docs/signature_attendue.txt."
)


class EmpreinteInattendue(RuntimeError):
    """Le fichier present n'est pas la version declaree dans le depot."""


def calculer(chemin: Path) -> str:
    """Empreinte SHA-256 d'un fichier, en hexadecimal minuscule."""
    with chemin.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def lire_attendues(fichier: Path = FICHIER_EMPREINTES) -> dict[str, str]:
    """Lit un fichier au format sha256sum : '<empreinte> <nom>' par ligne."""
    attendues = {}
    for ligne in fichier.read_text(encoding="ascii").splitlines():
        if ligne.strip():
            empreinte, nom = ligne.split(maxsplit=1)
            attendues[nom.strip().lstrip("*")] = empreinte.lower()
    return attendues


def verifier(chemin: Path, attendues: dict[str, str]) -> None:
    """Echoue si le fichier n'a pas d'empreinte declaree, ou pas celle-la."""
    attendue = attendues.get(chemin.name)
    if attendue is None:
        raise EmpreinteInattendue(
            f"{chemin.name} : aucune empreinte declaree dans docs/empreintes_attendues.txt."
        )
    calculee = calculer(chemin)
    if calculee != attendue:
        raise EmpreinteInattendue(
            f"{chemin.name} : empreinte {calculee[:12]}, attendue {attendue[:12]}. {CONSIGNE}"
        )
