# src/tests_donnees.py
"""Verdict binaire sur la qualite des donnees.

Convention : chaque fichier tests/NN_*.sql renvoie les lignes EN FAUTE.
Zero ligne = test reussi. Code retour 1 des qu'un test echoue.
"""

import sys
from pathlib import Path

import duckdb

BASE = "collateral.duckdb"
DOSSIER_TESTS = Path("tests")
MAX_LIGNES_AFFICHEES = 5

CODE_OK, CODE_ECHEC, CODE_ERREUR = 0, 1, 2

def main() -> int:
    tests = sorted(DOSSIER_TESTS.glob("[0-9][0-9]_*.sql"))
    if not tests:
        print("Aucun test trouve dans test/")
        return 1

    con = duckdb.connect(BASE, read_only=True)
    echecs = 0

    for chemin in tests:
        try:
            lignes = con.execute(chemin.read_text(encoding="utf-8")).fetchall()
        except duckdb.Error as erreur:
            echecs +=1
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
            print(f"[OK ] {chemin.stem}")

    con.close()
    print(f"\n{len(tests) - echecs}/{len(tests)} tests reussis")
    return CODE_ECHEC if echecs else CODE_OK


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as erreur:          # bug du harnais, pas echec de test
        print(f"[HARNAIS] erreur inattendue : {erreur}", file=sys.stderr)
        sys.exit(CODE_ERREUR)

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as erreur:          # bug du harnais, pas echec de test
        print(f"[HARNAIS] erreur inattendue : {erreur}", file=sys.stderr)
        sys.exit(CODE_ERREUR)
