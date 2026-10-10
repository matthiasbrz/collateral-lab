-- Grain : un jour calendaire. Arbitrage du 09/10 : docs/modelisation.md
-- Plage : premiere a derniere date_mutation des faits, bornes incluses.
-- Lue dans fct_mutations, pas dans int_mutations_filtrees : pas de second
-- enfant pour le modele intermediaire. generate_series inclut la borne de fin.

WITH bornes AS (
    SELECT min(date_mutation) AS debut, max(date_mutation) AS fin
    FROM {{ ref('fct_mutations') }}
),

jours AS (
    SELECT unnest(generate_series(debut, fin, INTERVAL 1 DAY))::DATE AS date_jour
    FROM bornes
)

SELECT
    date_jour,
    date_trunc('month', date_jour)::DATE AS mois,
    year(date_jour) AS annee,
    quarter(date_jour) AS trimestre
FROM jours