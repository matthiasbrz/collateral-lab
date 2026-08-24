WITH base AS (
    SELECT
        *,
        round(valeur_fonciere / surface_bati, 2) AS prix_m2
    FROM stg_mutations
    WHERE nature_mutation = 'Vente'          -- 1. echanges, expropriations, adjudications hors marche
      AND nb_communes = 1                    -- 2. un prix unique sur deux communes n'est rattachable a aucune
      AND valeur_fonciere > 0                -- 3. valeur absente ou nulle : prix non exploitable
      AND nb_types_principaux = 1            -- 4. un prix unique sur un lot mixte n'est pas un prix au m2
      AND type_local IN ('Maison', 'Appartement')
      AND surface_bati > 0                   -- 5. surface manquante : prix au m2 incalculable
      AND nb_natures = 1
      -- AND nb_locaux_principaux = 1        -- 5 bis : a activer apres mesure du volume concerne
),

-- 6. Bornes calculees sur le perimetre DEJA filtre, jamais sur la table brute.
bornes AS (
    SELECT
        quantile_cont(prix_m2, 0.01) AS p1,
        quantile_cont(prix_m2, 0.99) AS p99
    FROM base
)

SELECT 
    b.*,
    date_trunc('month', date_mutation)::DATE AS mois,
    year(date_mutation)                      AS annee,
    quarter(date_mutation)                   AS trimestre
    
FROM base b
CROSS JOIN bornes
WHERE b.prix_m2 BETWEEN bornes.p1 AND bornes.p99;

WITH base AS (
    SELECT round(valeur_fonciere / surface_bati, 2) AS prix_m2
    FROM stg_mutations
    WHERE nature_mutation = 'Vente'
      AND nb_communes = 1
      AND valeur_fonciere > 0
      AND nb_types_principaux = 1
      AND type_local IN ('Maison', 'Appartement')
      AND surface_bati > 0
      AND nb_natures = 1
)
SELECT
    current_date                 AS date_calcul,
    'p1/p99 sur perimetre filtre' AS methode,
    quantile_cont(prix_m2, 0.01) AS seuil_bas,
    quantile_cont(prix_m2, 0.99) AS seuil_haut,
    count(*)                     AS mutations_perimetre
FROM base;