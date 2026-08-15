"""Téléchargement des fichiers DVF géolocalisés (Etalab / DGFiP).

Un CSV compressé par département et par millésime, déposé dans data/raw/.
Aucune donnée n'est versionnée : voir .gitignore.

Source  : https://files.data.gouv.fr/geo-dvf/latest/csv/
Licence : Licence Ouverte 2.0 — DGFiP, géolocalisation Etalab.
"""

import urllib.request
from pathlib import Path

BASE_URL = "https://files.data.gouv.fr/geo-dvf/latest/csv"
DESTINATION = Path("data/raw")

def download_departement(
        code_departement: str, annee: int, destination: Path = DESTINATION
) -> Path:
    """Télécharge le fichier DVF d'un département pour une année.

    Args:
        code_departement: code INSEE du département, par exemple "76".
        annee: millesime, par exemple 2025.
        destination: dossier de dépôt, non versionné.

    Returns:
        Le chemin du fichier écrit sur disque.
    """
    destination.mkdir(parents=True, exist_ok=True)
    url = f"{BASE_URL}/{annee}/departements/{code_departement}.csv.gz"
    cible = destination / f"dvf_{code_departement}_{annee}.csv.gz"

    if cible.exists():
        print(f"déjà présent, ignoré : {cible}")
        return cible
    
    print(f"téléchargement : {url}")
    urllib.request.urlretrieve(url, cible)
    print(f"écrit : {cible} ({cible.stat().st_size / 1e6:.1f} Mo)")
    return cible

if __name__ == "__main__":
    for annee in (2023,2024,2025):
        download_departement("76", annee)