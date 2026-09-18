-- Grain : une seule ligne. Bornes d'ecretage du prix au m2.
-- Calculees sur le perimetre deja filtre, jamais sur la table brute.
--
-- date_calcul retiree le 18/09 : current_date enregistrait la date du dernier
-- build, pas celle d'un figement. Une table de reference ne porte pas une
-- valeur qui change sans que son contenu change.
-- Le figement reel des bornes par millesime est l'affaire de la semaine 10.

SELECT
    'p1/p99 sur perimetre filtre' AS methode,
    quantile_cont(prix_m2, 0.01) AS seuil_bas,
    quantile_cont(prix_m2, 0.99) AS seuil_haut,
    count(*) AS mutations_perimetre
FROM {{ ref('int_mutations_perimetre') }}
    