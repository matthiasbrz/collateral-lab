"""Telechargement des sources externes.

- DVF geolocalisees (Etalab / DGFiP) : un fichier par departement et millesime
- Code officiel geographique (Insee), millesime 2026

Rien n'est versionne : voir .gitignore.
"""

import io
import urllib.request
import zipfile
from pathlib import Path

DESTINATION = Path("data/raw")
BASE_DVF = "https://files.data.gouv.fr/geo-dvf/latest/csv"
URL_COG = "https://www.insee.fr/fr/statistiques/fichier/8740222/v_commune_2026.csv"
FICHIER_COG = "v_commune_2026.csv"


def _telecharger(url: str, cible: Path) -> Path:
    cible.parent.mkdir(parents=True, exist_ok=True)
    if cible.exists():
        print(f"deja present, ignore : {cible.name}")
        return cible
    print(f"telechargement : {url}")
    urllib.request.urlretrieve(url, cible)
    print(f"ecrit : {cible.name} ({cible.stat().st_size / 1e6:.1f} Mo)")
    return cible


def download_dvf(code_departement: str, annee: int) -> Path:
    url = f"{BASE_DVF}/{annee}/departements/{code_departement}.csv.gz"
    return _telecharger(url, DESTINATION / f"dvf_{code_departement}_{annee}.csv.gz")


def download_cog() -> Path:
    """Telecharge le referentiel COG.

    L'Insee sert selon les millesimes un CSV brut ou une archive zip :
    on inspecte le contenu recu au lieu de le supposer.
    """
    cible = DESTINATION / FICHIER_COG
    if cible.exists():
        print(f"deja present, ignore : {cible.name}")
        return cible

    DESTINATION.mkdir(parents=True, exist_ok=True)
    print(f"telechargement : {URL_COG}")
    requete = urllib.request.Request(URL_COG, headers={"User-Agent": "collateral-lab"})
    with urllib.request.urlopen(requete) as reponse:
        contenu = reponse.read()

    if contenu[:4] == b"PK\x03\x04":  # signature d'une archive zip
        archive = zipfile.ZipFile(io.BytesIO(contenu))
        csv = [n for n in archive.namelist() if n.endswith(".csv")]
        if len(csv) != 1:
            raise RuntimeError(f"archive COG inattendue : {csv}")
        contenu = archive.read(csv[0])

    entete = contenu[:200].decode("utf-8", errors="replace")
    if "TYPECOM" not in entete:
        raise RuntimeError(f"ce n'est pas le fichier COG attendu. Debut recu : {entete[:120]!r}")

    cible.write_bytes(contenu)
    print(f"ecrit : {cible.name} ({cible.stat().st_size / 1e6:.1f} Mo)")
    return cible


if __name__ == "__main__":
    for annee in (2023, 2024, 2025):
        download_dvf("76", annee)
    download_cog()
