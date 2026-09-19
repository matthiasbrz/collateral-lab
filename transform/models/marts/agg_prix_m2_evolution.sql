-- Grain : commune x type de bien x mois de reference.
-- Ajoute les indicateurs derives : dispersion et evolution sur douze mois.
--
-- evolution_pct est nullable par construction : le premier mois a fenetre
-- complete n'a pas de N-1, et une cellule dont la fenetre N-1 etait vide non
-- plus. Invariant verifie par le test dedie (voir 06_coherence_evolution).

SELECT
    *,
    lag(prix_m2_median_12m, 12) OVER w                                          AS prix_m2_median_12m_n1,
    round(100.0 * (prix_m2_median_12m
                    / nullif(lag(prix_m2_median_12m, 12) OVER w, 0) - 1), 1)    AS evolution_pct,
    prix_m2_q3_12m - prix_m2_q1_12m                                             AS ecart_interquartile,
    round((prix_m2_q3_12m - prix_m2_q1_12m) / nullif(prix_m2_median_12m, 0), 3) AS dispersion_relative
FROM {{ ref('agg_prix_m2_glissant') }}
WINDOW w AS (PARTITION BY code_commune, type_local ORDER BY mois)