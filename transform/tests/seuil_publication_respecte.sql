-- Attendu : 0 ligne.
-- Aucune cellule publiee ne repose sur moins de cinq transactions.
-- C'est la regle de gouvernance du README, rendue executable.

SELECT code_commune, type_local, mois, nb_mutations_12m
FROM {{ ref('mart_prix_m2_reference') }}
WHERE nb_mutations_12m < 5
    OR nb_mutations_12m IS NULL