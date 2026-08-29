"""Telechargement des sources externes.

- DVF geolocalisees (Etalab / DGFiP) : un fichier par departement et par millesime
- Code officiel geographique (Insee), millesime courant

Licence Ouverte 2.0. Aucune donnee n'est versionnee : voir .gitignore.
"""

import io
import logging
import urllib.request
import zipfile
from pathlib import Path

from collateral import journal
from collateral.config import (
    DEPARTEMENT,
    DOSSIER_DATA,
    FICHIER_COG,
    MILLESIMES,
    MOTIF_DVF,
    URL_COG,
    URL_DVF,
)

logger = logging.getLogger(__name__)


def _telecharger(url: str, cible: Path) -> Path:
    """Telecharge une URL vers un fichier. Idempotent : ne refait rien si present."""
    cible.parent.mkdir(parents=True, exist_ok=True)
    if cible.exists():
        logger.info("deja present, ignore : %s", cible.name)
        return cible

    logger.info("telechargement : %s", url)
    urllib.request.urlretrieve(url, cible)
    logger.info("ecrit : %s (%.1f Mo)", cible.name, cible.stat().st_size / 1e6)
    return cible


def download_dvf(code_departement: str, annee: int) -> Path:
    """Telecharge le fichier DVF geolocalise d'un departement pour une annee."""
    url = f"{URL_DVF}/{annee}/departements/{code_departement}.csv.gz"
    return _telecharger(url, DOSSIER_DATA / f"dvf_{code_departement}_{annee}.csv.gz")


def download_cog() -> Path:
    """Telecharge le referentiel COG. L'Insee sert un CSV brut ou une archive zip."""
    cible = DOSSIER_DATA / FICHIER_COG
    if cible.exists():
        logger.info("deja present, ignore : %s", cible.name)
        return cible

    DOSSIER_DATA.mkdir(parents=True, exist_ok=True)
    logger.info("telechargement : %s", URL_COG)
    requete = urllib.request.Request(URL_COG, headers={"User-Agent": "collateral-lab"})
    with urllib.request.urlopen(requete) as reponse:
        contenu = reponse.read()

    if contenu[:4] == b"PK\x03\x04":
        archive = zipfile.ZipFile(io.BytesIO(contenu))
        csv = [nom for nom in archive.namelist() if nom.endswith(".csv")]
        if len(csv) != 1:
            raise RuntimeError(f"archive COG inattendue : {csv}")
        logger.info("archive zip detectee, extraction de %s", csv[0])
        contenu = archive.read(csv[0])

    entete = contenu[:200].decode("utf-8", errors="replace")
    if "TYPECOM" not in entete:
        raise RuntimeError(f"ce n'est pas le fichier COG attendu. Debut recu : {entete[:120]!r}")

    cible.write_bytes(contenu)
    logger.info("ecrit : %s (%.1f Mo)", cible.name, cible.stat().st_size / 1e6)
    return cible


SIGNATURE_ZIP = b"PK\x03\x04"


def url_dvf(code_departement: str, annee: int) -> str:
    """Rend l'URL du fichier DVF geolocalise d'un departement pour une annee."""
    return f"{URL_DVF}/{annee}/departements/{code_departement}.csv.gz"


def nom_fichier_dvf(code_departement: str, annee: int) -> str:
    """Rend le nom local du fichier DVF."""
    return f"dvf_{code_departement}_{annee}.csv.gz"


def contenu_cog(donnees: bytes) -> bytes:
    """Rend le CSV du referentiel a partir de ce que l'Insee a renvoye.

    Accepte un CSV brut ou une archive zip contenant un unique CSV.
    Leve RuntimeError si le contenu ne ressemble pas au fichier attendu.
    """
    if donnees[:4] == SIGNATURE_ZIP:
        archive = zipfile.ZipFile(io.BytesIO(donnees))
        csv = [nom for nom in archive.namelist() if nom.endswith(".csv")]
        if len(csv) != 1:
            raise RuntimeError(f"archive COG inattendue : {csv}")
        donnees = archive.read(csv[0])

    entete = donnees[:200].decode("utf-8", errors="replace")
    if "TYPECOM" not in entete:
        raise RuntimeError(f"ce n'est pas le fichier COG attendu. Debut recu : {entete[:120]!r}")
    return donnees


def sources_manquantes(dossier: Path = DOSSIER_DATA) -> list[str]:
    """Rend la liste des sources absentes du dossier, vide si tout est present."""
    manquants = []
    if not list(dossier.glob(MOTIF_DVF)):
        manquants.append(f"fichiers DVF ({MOTIF_DVF})")
    if not (dossier / FICHIER_COG).exists():
        manquants.append(f"referentiel COG ({FICHIER_COG})")
    return manquants


if __name__ == "__main__":
    journal.configurer()
    for annee in MILLESIMES:
        download_dvf(DEPARTEMENT, annee)
    download_cog()
