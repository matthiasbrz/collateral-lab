-- tests/05_integrite_referentielle.sql
SELECT m.code_commune, count(*) AS lignes_mart
FROM mart_prix_m2_reference m
LEFT JOIN dim_commune d USING (code_commune)
WHERE d.code_commune IS NULL
GROUP BY 1;