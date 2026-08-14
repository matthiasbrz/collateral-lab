"""Téléchargement des fichiers DVF géolocalisés.

Un fichier par département et par millésime, déposé dans data/raw.
Aucune donnée n'est versionnée : voir .gitignore.
"""

def download_department(code_departement: str, annee: int, destination: str = "data/raw") -> str:
    """Télécharge le fichier DVF d'un département pour une année donnée.

    Args:
        code_departement: code INSEE du département, par exemple "76".
        annee: millesime, par exemple 2025.
        destination: dossier de dépôt, non versionné.

    Returns:
        Le chemin du fichier écrit sur disque.
    """
    raise NotImplementedError("Implémenté au J3, samedi 15 août.")