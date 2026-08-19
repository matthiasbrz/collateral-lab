-- sql/agg_prix_m2_mensuel.sql
CREATE OR REPLACE TABLE agg_prix_m2_mensuel AS
SELECT
    f.code_commune,
    d.nom_commune,
    f.type_local,
    f.mois,
    count(*) AS nb_mutations,
    round(quantile_cont(f.prix_m2, 0.50), 0) AS prix_m2_median,
    round(quantile_cont(f.prix_m2, 0.25), 0) AS prix_m2_q1,
    round(quantile_cont(f.prix_m2, 0.75), 0) AS prix_m2_q3
FROM stg_mutations_filtrees f
LEFT JOIN dim_commune d USING (code_commune)
GROUP BY 1,2,3,4;