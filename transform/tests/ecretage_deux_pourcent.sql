-- Attendu : 0 ligne.
-- Un ecretage aux centiles 1 et 99 retire 2% du perimetre, par construction.
-- Un ecart signifie que les bornes n'ont pas ete calculees sur le bon ensemble.

WITH comptes AS (
    SELECT
        (SELECT count(*) FROM {{ ref('int_mutations_perimetre') }}) AS perimetre,
        (SELECT count(*) FROM {{ ref('stg_mutations_filtrees') }}) AS retenues
)
SELECT *, round(100.0 * (perimetre - retenues) / perimetre, 3) AS taux_ecretage
FROM comptes
WHERE abs(100.0 * (perimetre - retenues) / perimetre - 2.0) > 0.2