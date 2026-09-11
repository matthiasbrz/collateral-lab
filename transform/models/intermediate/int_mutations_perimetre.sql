-- Grain : une mutation du perimetre metier, AVANT ecretage des extremes.
--
-- Ce modele n'existait pas : il etait duplique dans les deux CTE 'base'
-- de sql/03_stg_mutations_filtrees.sql. Le nommer supprime sa duplication
-- et rend le calcul des bornes acyclique.
--
-- Regles 1 a 5. La regle 6 (ecretage p1/p99) est dans stg_mutations_filtrees.

SELECT
    *,
    round(valeur_fonciere / surface_bati, 2) AS prix_m2
FROM {{ ref('stg_mutations') }}
WHERE nature_mutation = 'Vente'         -- 1. hors marche : echanges, expropriations
    AND nb_natures = 1                  -- 1 bis. nature juridique non unique
    AND nb_communes = 1                 -- 2. non rattachable a une commune
    AND valeur_fonciere > 0             -- 3. valeur absente ou nulle
    AND nb_types_principaux = 1         -- 4. lot mixte
    AND type_local IN ('Maison', 'Appartement')
    AND surface_bati > 0                -- 5. prix au m2 incalculable