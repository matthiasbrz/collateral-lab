-- sql/analyses/05_matrice_type_annee.sql
-- Question : comment le volume et le prix median evoluent-ils par type de bien et par annee ?
PIVOT stg_mutations_filtrees
ON annee
USING count(*) AS volume,
      round(quantile_cont(prix_m2, 0.5), 0) AS median
GROUP BY type_local

SELECT
    type_local,
    count(CASE WHEN annee = 2023 THEN 1 END) AS volume_2023,
    count(CASE WHEN annee = 2023 THEN 1 END) AS volume_2024,
    count(CASE WHEN annee = 2023 THEN 1 END) AS volume_2025
FROM stg_mutations_filtrees
GROUP BY type_local