-- Attendu : 0 ligne. Le grain de fct_mutations est conserve, pas seulement
-- declare : exactement les lignes d'int_mutations_filtrees.

WITH comptes AS (
    SELECT
        (SELECT count(*) FROM {{ ref('int_mutations_filtrees') }}) AS intermediaire,
        (SELECT count(*) FROM {{ ref('fct_mutations') }}) AS faits
)
SELECT * FROM comptes WHERE faits <> intermediaire