CREATE OR REPLACE TABLE ref_seuils_dispersion AS
SELECT type_local,
       round(quantile_cont(dispersion_relative, 0.33), 3) AS borne_basse,
       round(quantile_cont(dispersion_relative, 0.67), 3) AS borne_haute,
       round(quantile_cont(dispersion_relative, 0.50), 3) AS mediane,
       current_date AS date_calcul
FROM mart_prix_m2_reference
GROUP BY type_local
