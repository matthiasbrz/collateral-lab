"""Verdict binaire sur la qualite des donnees.

Convention : chaque fichier tests/NN_*.sql renvoie les lignes EN FAUTE.
Zero ligne = test reussi.

Sortie volontairement en print et non en logging : le verdict est le produit
attendu du programme, pas un diagnostic sur son deroulement.
"""

import sys

import duckdb

from collateral.config import DOSSIER_TESTS
from collateral.db import connexion

CODE_OK = 0
CODE_ECHEC = 1
CODE_ERREUR = 2
MAX_LIGNES_AFFICHEES = 5


def main() -> int:
    tests = sorted(DOSSIER_TESTS.glob("[0-9][0-9]_*.sql"))
    if not tests:
        print("Aucun test trouve dans tests/", file=sys.stderr)
        return CODE_ERREUR

    echecs = 0
    with connexion(lecture_seule=True) as con:
        for chemin in tests:
            try:
                lignes = con.execute(chemin.read_text(encoding="utf-8")).fetchall()
            except duckdb.Error as erreur:
                echecs += 1
                print(f"[ERREUR] {chemin.stem} : {erreur}")
                continue

            if lignes:
                echecs += 1
                print(f"[ECHEC ] {chemin.stem} : {len(lignes)} ligne(s) en faute")
                for ligne in lignes[:MAX_LIGNES_AFFICHEES]:
                    print(f"          {ligne}")
                if len(lignes) > MAX_LIGNES_AFFICHEES:
                    print(f"          ... et {len(lignes) - MAX_LIGNES_AFFICHEES} autre(s)")
            else:
                print(f"[OK    ] {chemin.stem}")

    print(f"\n{len(tests) - echecs}/{len(tests)} tests reussis")
    return CODE_ECHEC if echecs else CODE_OK


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as erreur:
        print(f"[HARNAIS] erreur inattendue : {erreur}", file=sys.stderr)
        sys.exit(CODE_ERREUR)
