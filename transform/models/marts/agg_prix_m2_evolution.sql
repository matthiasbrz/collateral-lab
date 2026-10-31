-- Grain : commune x type de bien x mois de reference.
-- Ajoute les indicateurs derives : dispersion et evolution sur douze mois.
--
-- La mediane N-1 n'est retenue que si sa fenetre etait complete et au-dessus
-- du seuil de publication (31/10, constat du 28/10). Sinon, l'evolution
-- publiee a cote de la mediane rendait la mediane N-1 lisible :
-- N-1 = N / (1 + evolution). evolution_pct est nulle des qu'une des deux
-- medianes manque : invariant verifie par coherence_evolution.

WITH avec_n1 AS (
    SELECT
        *,
        CASE
            WHEN lag(fenetre_complete, 12) OVER w
                AND lag(nb_mutations_12m, 12) OVER w >= {{ var('seuil_publication') }}
            THEN lag(prix_m2_median_12m, 12) OVER w
        END AS prix_m2_median_12m_n1
    FROM {{ ref('agg_prix_m2_glissant') }}
    WINDOW w AS (PARTITION BY code_commune, type_local ORDER BY mois)
)

SELECT
    *,
    round(100.0 * (prix_m2_median_12m
                    / nullif(prix_m2_median_12m_n1, 0) - 1), 1)                 AS evolution_pct,
    prix_m2_q3_12m - prix_m2_q1_12m                                             AS ecart_interquartile,
    round((prix_m2_q3_12m - prix_m2_q1_12m) / nullif(prix_m2_median_12m, 0), 3) AS dispersion_relative
FROM avec_n1