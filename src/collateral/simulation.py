"""Livraison DVF simulee : l'incremental doit rendre exactement le full refresh.

Une seule commande, rejouable a chaque changement (regle 12) :
    python -m collateral.simulation

1. copie la base principale et les sources dans un dossier hors depot ;
2. y fabrique une livraison N+1 deterministe : des ventes retirees et des
   ventes ajoutees dans le premier millesime, des valeurs modifiees dans le
   deuxieme, le dernier intact ;
3. la charge par les memes scripts sql/00_*.sql qu'une vraie livraison ;
4. construit l'incremental (schema dbt) puis un full refresh (schema plein) ;
5. compare les deux, relation par relation. Code retour 0 si tout est identique.

Seul ce script est versionne : la livraison simulee vit hors depot, dans
DOSSIER_SIMULATION, jusqu'a l'execution suivante, qui la recree.
"""

import csv
import gzip
import io
import os
import shutil
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path

import duckdb

from collateral.config import (
    BASE_DUCKDB,
    DEPARTEMENT,
    DOSSIER_DATA,
    DOSSIER_SIMULATION,
    DOSSIER_SQL,
    MILLESIMES,
    RACINE,
)
from collateral.controle import comparer, relations_communes
from collateral.download import nom_fichier_dvf
from collateral.sql import executer, lister

NB_MUTATIONS = 3  # par geste : retrait, ajout, modification
BASE_SIMULATION = DOSSIER_SIMULATION / BASE_DUCKDB.name
DONNEES_SIMULATION = DOSSIER_SIMULATION / "data" / "raw"


def lire(chemin: Path) -> tuple[list[str], list[dict]]:
    with gzip.open(chemin, "rt", encoding="utf-8-sig", newline="") as flux:
        lecteur = csv.DictReader(flux)
        return list(lecteur.fieldnames), list(lecteur)


def ecrire(chemin: Path, entete: list[str], lignes: list[dict]) -> None:
    """mtime=0 : le meme contenu donne toujours le meme fichier, donc la meme empreinte."""
    tampon = io.StringIO()
    ecrivain = csv.DictWriter(tampon, fieldnames=entete, lineterminator="\n")
    ecrivain.writeheader()
    ecrivain.writerows(lignes)
    chemin.write_bytes(gzip.compress(tampon.getvalue().encode("utf-8"), mtime=0))


def candidates(lignes: list[dict]) -> list[str]:
    """Ventes de maison ou d'appartement, triees : un choix sans hasard."""
    return sorted({
        ligne["id_mutation"]
        for ligne in lignes
        if ligne["nature_mutation"] == "Vente"
        and ligne["type_local"] in ("Maison", "Appartement")
        and ligne["valeur_fonciere"]
    })


def majorer(valeur: str) -> str:
    """+10 %, dans le format du fichier : un format change ferait changer le type infere."""
    nombre = float(valeur) * 1.1
    if "." in valeur:
        return f"{nombre:.{len(valeur.split('.')[1])}f}"
    return str(round(nombre))


@contextmanager
def dans(dossier: Path):
    """Les scripts sql/ lisent 'data/raw/...' : un chemin relatif au dossier courant."""
    origine = Path.cwd()
    os.chdir(dossier)
    try:
        yield
    finally:
        os.chdir(origine)


def preparer() -> None:
    """Dossier neuf : copie des sources, puis de la base principale, lue sans y ecrire."""
    if DOSSIER_SIMULATION.exists():
        shutil.rmtree(DOSSIER_SIMULATION)
    DONNEES_SIMULATION.mkdir(parents=True)
    for fichier in DOSSIER_DATA.iterdir():
        if fichier.is_file():
            shutil.copy2(fichier, DONNEES_SIMULATION / fichier.name)
    con = duckdb.connect(str(BASE_SIMULATION))
    try:
        con.execute(f"ATTACH '{BASE_DUCKDB}' AS source (READ_ONLY)")
        con.execute(f"COPY FROM DATABASE source TO {BASE_SIMULATION.stem}")
        con.execute("DETACH source")
    finally:
        con.close()


def livrer() -> None:
    """La livraison N+1, deterministe : retraits et ajouts, puis modifications."""
    premier, deuxieme = MILLESIMES[0], MILLESIMES[1]

    chemin = DONNEES_SIMULATION / nom_fichier_dvf(DEPARTEMENT, premier)
    entete, lignes = lire(chemin)
    choix = candidates(lignes)
    retirees = set(choix[:NB_MUTATIONS])
    copiees = set(choix[NB_MUTATIONS : 2 * NB_MUTATIONS])
    ajouts = [
        {**ligne, "id_mutation": ligne["id_mutation"] + "-sim"}
        for ligne in lignes
        if ligne["id_mutation"] in copiees
    ]
    ecrire(
        chemin, entete, [ligne for ligne in lignes if ligne["id_mutation"] not in retirees] + ajouts
    )
    print(f"{premier} : {NB_MUTATIONS} ventes retirees, {NB_MUTATIONS} ajoutees")

    chemin = DONNEES_SIMULATION / nom_fichier_dvf(DEPARTEMENT, deuxieme)
    entete, lignes = lire(chemin)
    modifiees = set(candidates(lignes)[:NB_MUTATIONS])
    for ligne in lignes:
        if ligne["id_mutation"] in modifiees:
            ligne["valeur_fonciere"] = majorer(ligne["valeur_fonciere"])
    ecrire(chemin, entete, lignes)
    print(f"{deuxieme} : {NB_MUTATIONS} valeurs foncieres majorees de 10 %")


def charger() -> None:
    """Le meme chemin qu'une vraie livraison : les scripts sql/00_*.sql, sans raccourci."""
    con = duckdb.connect(str(BASE_SIMULATION))
    try:
        with dans(DOSSIER_SIMULATION):
            for chemin in lister(DOSSIER_SQL):
                executer(con, chemin)
    finally:
        con.close()


def construire(cible: str, *options: str) -> None:
    """dbt sur la base de simulation, avec son propre dossier d'artefacts.

    Le snapshot est exclu : son historique n'est pas la question, et un schema
    neuf le recreerait sans le passage 2024.
    """
    commande = [
        "dbt",
        "--no-use-colors",
        "build",
        "--profiles-dir",
        ".",
        "--target",
        cible,
        *options,
        "--exclude",
        "snap_cog_communes+",
        "--target-path",
        str(DOSSIER_SIMULATION / f"target-{cible}"),
        "--log-path",
        str(DOSSIER_SIMULATION / "logs"),
    ]
    env = {
        **os.environ,
        "COLLATERAL_SIMULATION": str(BASE_SIMULATION),
        "PYTHONIOENCODING": "utf-8",
    }
    resultat = subprocess.run(
        commande,
        cwd=RACINE / "transform",
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    bilan = [ligne for ligne in resultat.stdout.splitlines() if "Done." in ligne]
    print(f"dbt {cible} : {bilan[-1].strip() if bilan else 'aucun bilan'}")
    if resultat.returncode != 0:
        print(resultat.stdout[-3000:])
        sys.exit(2)


def comparer_tout() -> int:
    """Incremental (dbt) contre full refresh (plein), sur la meme entree."""
    con = duckdb.connect(str(BASE_SIMULATION), read_only=True)
    try:
        resultats = [
            comparer(con, t, "plein", "dbt") for t in relations_communes(con, "plein", "dbt")
        ]
    finally:
        con.close()
    for resultat in resultats:
        print(resultat)
    ecarts = sum(1 for r in resultats if not r.identique)
    print(f"\n{len(resultats) - ecarts}/{len(resultats)} relations identiques")
    return 1 if ecarts else 0


if __name__ == "__main__":
    preparer()
    livrer()
    charger()
    construire("simulation")
    construire("simulation_plein", "--full-refresh")
    sys.exit(comparer_tout())
