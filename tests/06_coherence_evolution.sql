-- tests/06_coherence_evolution.sql
-- Attendu : 0 ligne.
-- evolution_pct ne peut etre nulle que si l'une de ses entrees l'est,
-- ou si la valeur N-1 est nulle (division impossible).
SELECT code_commune, type_local, mois,
       prix_m2_median_12m, prix_m2_median_12m_n1, evolution_pct
FROM agg_prix_m2_evolution
WHERE evolution_pct IS NULL
  AND prix_m2_median_12m    IS NOT NULL
  AND prix_m2_median_12m_n1 IS NOT NULL
  AND prix_m2_median_12m_n1 <> 0;