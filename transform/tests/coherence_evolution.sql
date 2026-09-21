-- Attendu : 0 ligne. evolution_pct n'est nulle que si une entree l'est.
-- Porte depuis tests/donnees/06_coherence_evolution.sql le 21/09.
SELECT code_commune, type_local, mois, prix_m2_median_12m,
        prix_m2_median_12m_n1, evolution_pct
FROM {{ ref('agg_prix_m2_evolution') }}
WHERE evolution_pct IS NULL
    AND prix_m2_median_12m IS NOT NULL
    AND prix_m2_median_12m_n1 IS NOT NULL
    AND prix_m2_median_12m_n1 <> 0