-- sql/analyses/06_piege_last_value.sql
-- Question : quelle est l'evolution totale du prix median sur la peride observee ?
SELECT
    mois,
    prix_m2_median_12m,
    first_value(prix_m2_median_12m) OVER (PARTITION BY code_commune, type_local ORDER BY mois)
        AS premier_defaut,
    last_value(prix_m2_median_12m) OVER (PARTITION BY code_commune, type_local ORDER BY mois)
        AS dernier_defaut,
    first_value(prix_m2_median_12m) OVER (PARTITION BY code_commune, type_local ORDER BY mois
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS premier_explicite,
    last_value(prix_m2_median_12m) OVER (PARTITION BY code_commune, type_local ORDER BY mois
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS dernier_explicite
FROM mart_prix_m2_reference
WHERE code_commune = '76540' AND type_local = 'Appartement'
ORDER BY mois
    

SELECT
    mois,
    round(100.0 * (last_value(prix_m2_median_12m) OVER (PARTITION BY code_commune, type_local ORDER BY mois)
                 / first_value(prix_m2_median_12m) OVER (PARTITION BY code_commune, type_local ORDER BY mois) - 1), 1)
        AS evolution_fausse,
    round(100.0 * (last_value(prix_m2_median_12m) OVER (PARTITION BY code_commune, type_local ORDER BY mois
                        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
                 / first_value(prix_m2_median_12m) OVER (PARTITION BY code_commune, type_local ORDER BY mois
                        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) - 1), 1)
        AS evolution_juste
FROM mart_prix_m2_reference
WHERE code_commune = '76540' AND type_local = 'Appartement'
ORDER BY mois