"""La chaine de scripts/lancer.txt, lancee par Dagster sans changer une etape (07/11).

Chaque etape lance la commande que lancer.txt lance deja, dans le meme ordre et
depuis le meme dossier. Comme lancer.txt, elle suppose une base neuve : le passage
2024 du snapshot ne se rejoue pas sur un historique complet (constat du 13/10).
La derniere etape compare la signature du mart a l'etalon (regle 9).

Environnement actif, depuis la racine du depot :
    dagster job execute -m collateral.orchestration -j chaine
"""

import subprocess
import sys

from dagster import Definitions, In, Nothing, job, op

from collateral.config import BASE_DUCKDB, RACINE

TRANSFORM = RACINE / "transform"
SIGNATURE_ATTENDUE = RACINE / "docs" / "signature_attendue.txt"
APRES = {"apres": In(Nothing)}


@op
def base_neuve() -> None:
    if BASE_DUCKDB.exists() or BASE_DUCKDB.with_suffix(".duckdb.wal").exists():
        raise RuntimeError("base existante : lancer.txt suppose une base neuve (README, Lancer)")


@op(ins=APRES)
def telecharger() -> None:
    subprocess.run([sys.executable, "-m", "collateral.download"], cwd=RACINE, check=True)


@op(ins=APRES)
def charger() -> None:
    subprocess.run([sys.executable, "-m", "collateral.load"], cwd=RACINE, check=True)


@op(ins=APRES)
def capturer() -> None:
    commande = ["dbt", "snapshot", "--vars", "{millesime_snapshot: 2024}", "--profiles-dir", "."]
    subprocess.run(commande, cwd=TRANSFORM, check=True)


@op(ins=APRES)
def construire() -> None:
    subprocess.run(["dbt", "build", "--profiles-dir", "."], cwd=TRANSFORM, check=True)


@op(ins=APRES)
def controler(context) -> None:
    commande = [sys.executable, "-m", "collateral.controle", "--signature"]
    sortie = subprocess.run(commande, cwd=RACINE, capture_output=True, text=True)
    if sortie.returncode != 0:
        raise RuntimeError(f"signature illisible : {sortie.stderr.strip()}")
    obtenue = sortie.stdout.strip()
    attendue = SIGNATURE_ATTENDUE.read_text(encoding="utf-8").strip()
    if obtenue != attendue:
        raise RuntimeError(f"signature modifiee : attendue {attendue}, obtenue {obtenue}")
    context.log.info(f"signature inchangee : {obtenue}")


@job
def chaine() -> None:
    charge = charger(apres=telecharger(apres=base_neuve()))
    controler(apres=construire(apres=capturer(apres=charge)))


defs = Definitions(jobs=[chaine])
