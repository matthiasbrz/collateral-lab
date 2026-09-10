"""Preuves de non-regression sur les relations de l'entrepot."""

import logging
import sys
from dataclasses import dataclass, field

import duckdb

logger = logging.getLogger(__name__)


@dataclass
class Comparaison:
    """Verdict de comparaison entre deux relations de meme nom."""

    relation: str
    verdict: str  # identique | absente | structure | volumetrie | multiplicite | contenu
    details: list[str] = field(default_factory=list)

    @property
    def identique(self) -> bool:
        return self.verdict == "identique"

    def __str__(self) -> str:
        marque = "OK    " if self.identique else "ECART "
        lignes = [f"[{marque}] {self.relation} : {self.verdict}"]
        lignes += [f"           {d}" for d in self.details]
        return "\n".join(lignes)


def signature(con: duckdb.DuckDBPyConnection, relation: str) -> tuple[int, int]:
    """Rend (nombre de lignes, signature). La somme de hachages ignore l'ordre."""
    return con.execute(f"SELECT count(*), sum(hash(t)) FROM {relation} t").fetchone()


def _colonnes(con, schema: str, table: str) -> list[tuple]:
    return con.execute(
        """
        SELECT ordinal_position, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = ? AND table_name = ?
        ORDER BY ordinal_position
        """,
        [schema, table],
    ).fetchall()


def _ecarts_colonnes(gauche: list[tuple], droite: list[tuple]) -> list[str]:
    noms_g = {c[1] for c in gauche}
    noms_d = {c[1] for c in droite}
    ecarts = [f"absente a droite : {n}" for n in sorted(noms_g - noms_d)]
    ecarts += [f"absente a gauche : {n}" for n in sorted(noms_d - noms_g)]
    pos_g = {c[1]: (c[0], c[2]) for c in gauche}
    pos_d = {c[1]: (c[0], c[2]) for c in droite}
    ecarts += [
        f"{n} : position/type {pos_g[n]} contre {pos_d[n]}"
        for n in sorted(noms_g & noms_d)
        if pos_g[n] != pos_d[n]
    ]
    return ecarts


def comparer(
    con: duckdb.DuckDBPyConnection,
    table: str,
    gauche: str = "main",
    droite: str = "dbt",
) -> Comparaison:
    """Compare une meme table dans deux schemas et rend un verdict.

    L'ordre des controles n'est pas indifferent : une difference de structure
    rendrait toute comparaison de contenu fausse, voire impossible.
    """
    cols_g = _colonnes(con, gauche, table)
    cols_d = _colonnes(con, droite, table)

    if not cols_g or not cols_d:
        absents = [s for s, c in ((gauche, cols_g), (droite, cols_d)) if not c]
        return Comparaison(table, "absente", [f"introuvable dans : {', '.join(absents)}"])

    if cols_g != cols_d:
        return Comparaison(table, "structure", _ecarts_colonnes(cols_g, cols_d))

    n_g, sig_g = signature(con, f"{gauche}.{table}")
    n_d, sig_d = signature(con, f"{droite}.{table}")

    if n_g != n_d:
        return Comparaison(table, "volumetrie", [f"{gauche} : {n_g}", f"{droite} : {n_d}"])

    if sig_g == sig_d:
        return Comparaison(table, "identique", [f"{n_g} lignes, signature {sig_g}"])

    ecarts = con.execute(f"""
        SELECT count(*) FROM (
            (SELECT * FROM {gauche}.{table} EXCEPT SELECT * FROM {droite}.{table})
            UNION ALL
            (SELECT * FROM {droite}.{table} EXCEPT SELECT * FROM {gauche}.{table})
        )
    """).fetchone()[0]

    if ecarts == 0:
        return Comparaison(
            table,
            "multiplicite",
            [
                "meme ensemble de lignes, multiplicites differentes",
                "EXCEPT dedoublonne : il ne voit pas un doublon en plus d'un cote",
            ],
        )

    return Comparaison(
        table,
        "contenu",
        [f"{ecarts} ligne(s) en ecart sur {n_g}", f"signatures : {sig_g} contre {sig_d}"],
    )


def relations_communes(con, gauche: str = "main", droite: str = "dbt") -> list[str]:
    """Rend les tables presentes dans les deux schemas, triees."""
    return [
        r[0]
        for r in con.execute(
            """
            SELECT table_name FROM information_schema.tables WHERE table_schema = ?
            INTERSECT
            SELECT table_name FROM information_schema.tables WHERE table_schema = ?
            ORDER BY 1
            """,
            [gauche, droite],
        ).fetchall()
    ]


if __name__ == "__main__":
    from collateral.db import connexion

    with connexion(lecture_seule=True) as con:
        tables = sys.argv[1:] or relations_communes(con)
        if not tables:
            print("Aucune relation commune aux deux schemas.", file=sys.stderr)
            sys.exit(2)
        resultats = [comparer(con, t) for t in tables]

    for r in resultats:
        print(r)
    ecarts = sum(1 for r in resultats if not r.identique)
    print(f"\n{len(resultats) - ecarts}/{len(resultats)} relations identiques")
    sys.exit(1 if ecarts else 0)
