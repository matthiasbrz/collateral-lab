-- Grain : une seule ligne. Bornes d'ecretage du prix au m2.
-- Calculees sur le perimetre deja filtre, jamais sur la table brute.

SELECT
    current_date AS date_calcul,
    'p1/p99 sur perimetre filtre' AS methode,
    quantile_cont(prix_m2, 0.01) AS seuil_bas,
    quantile_cont(prix_m2, 0.99) AS seuil_haut,
    count(*) AS mutations_perimetre
FROM {{ ref('int_mutations_perimetre') }}
    