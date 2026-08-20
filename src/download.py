"""Telechargement des sources externes.

- DVF geolocalisees (Etalib / DGFiP) : un fichier par departement et millesime
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
    cible = DESTINATION / FICHIER_COG
    if cible.exists():
        print(f"deja present, ignore : {cible.name}")
        return cible
    DESTINATION.mkdir(parents=True, exist_ok=True)
    print(f"telechargement : {URL_COG}")
    requete = urllib.request.Request(URL_COG, headers={"User-Agent": "collateral-lab"})
    with urllib.request.urlopen(requete) as reponse:
        archive = zipfile.ZipFile(io.BytesIO(reponse.read()))
    csv = [n for n in archive.namelist() if n.endswith(".csv")]
    if len(csv) != 1:
        raise RuntimeError(f"archive COG inattendue : {csv}")
    cible.write_bytes(archive.read(csv[0]))
    print(f"ecrit : {cible.name}")
    return cible


if __name__ == "__main__":
    for annee in (2023, 2024, 2025):
        download_dvf("76", annee)
    download_cog