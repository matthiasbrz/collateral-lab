CREATE OR REPLACE TABLE agg_prix_m2_evolution AS
SELECT
    *,
    lag(prix_m2_median_12m, 12) OVER w AS prix_m2_median_12m_n1,
    round(100.0 * (prix_m2_median_12m
                    / nullif(lag(prix_m2_median_12m, 12) OVER w, 0) - 1), 1) AS evolution_pct
FROM agg_prix_m2_glissant
WINDOW w AS (PARTITION BY code_commune, type_local ORDER BY mois);