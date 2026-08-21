-- tests/02_non_nullite.sql
SELECT * FROM (
    SELECT 'code_commune' AS colonne, count(*) AS lignes_nulles FROM mart_prix_m2_reference WHERE code_commune IS NULL
    UNION ALL SELECT 'nom_commune', count(*) FROM mart_prix_m2_reference WHERE nom_commune IS NULL
    UNION ALL SELECT 'type_local', count(*) FROM mart_prix_m2_reference WHERE type_local IS NULL
    UNION ALL SELECT 'mois', count(*) FROM mart_prix_m2_reference WHERE mois IS NULL
    UNION ALL SELECT 'prix_m2_median_12m', count(*) FROM mart_prix_m2_reference WHERE prix_m2_median_12m IS NULL
    UNION ALL SELECT 'nb_mutations_12m', count(*) FROM mart_prix_m2_reference WHERE nb_mutations_12m IS NULL
) WHERE lignes_nulles > 0;