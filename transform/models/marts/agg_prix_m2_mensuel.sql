-- Grain : une ligne = commune x type de bien x mois.
--
-- Agregat d'observation, pas une etape de la chaine : aucun modele ne le
-- consomme. Il sert a mesurer la dispersion du volume, qui justifie le
-- passage a une fenetre glissante - 15,1 % des cellules seulement
-- atteignent cinq transactions.

SELECT
    f.code_commune,
    d.nom_commune,
    f.type_local,
    f.mois,
    count(*) AS nb_mutations,
    round(quantile_cont(f.prix_m2, 0.50), 0) AS prix_m2_median,
    round(quantile_cont(f.prix_m2, 0.25), 0) AS prix_m2_q1,
    round(quantile_cont(f.prix_m2, 0.75), 0) AS prix_m2_q3
FROM {{ ref('stg_mutations_filtrees') }} f
LEFT JOIN {{ ref('dim_commune') }} d USING (code_commune)
GROUP BY 1, 2, 3, 4