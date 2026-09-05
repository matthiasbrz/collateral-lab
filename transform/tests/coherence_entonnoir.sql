-- Attendu : 0 ligne. Le total doit se refermer.
-- Aucun test generique n'exprime cet invariant : il porte sur deux modeles
-- a la fois, pas sur une colonne.

WITH classement AS (
    SELECT
        id_mutation,
        coalesce(
            nature_mutation = 'Vente'
            AND nb_natures = 1
            AND nb_communes = 1
            AND valeur_fonciere > 0
            AND nb_types_principaux = 1
            AND type_local IN ('Maison', 'Appartement')
            AND surface_bati > 0,
        false) AS dans_perimetre
    FROM {{ ref('stg_mutations') }}
),

comptes AS (
    SELECT
        (SELECT count(*) FROM {{ ref('stg_mutations') }}) AS total,
        (SELECT count(*) FROM classement WHERE dans_perimetre) AS retenues,
        (SELECT count(*) FROM classement WHERE NOT dans_perimetre) AS ecartees,
        (SELECT count(*) FROM {{ ref('stg_mutations_filtrees') }}) AS publiees
)

SELECT *
FROM comptes
WHERE retenues + ecartees <> total
    OR publiees > retenues