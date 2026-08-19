CREATE OR REPLACE TABLE mart_prix_m2_reference AS
SELECT code_commune, type_local, mois,
        prix_m2_median_12m, prix_m2_q1_12m, prix_m2_q3_12m,
        nb_mutations_12m, evolution_pct
FROM agg_prix_m2_evolution
LEFT JOIN dim_commune USING (code_commune)
WHERE fenetre_complete
    AND nb_mutations_12m >=5; -- seuil justifie dans docs/gouvernance.md