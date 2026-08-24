WITH calendrier AS (
    SELECT DISTINCT mois FROM stg_mutations_filtrees
)
,

perimetre AS (
    SELECT DISTINCT code_commune, type_local FROM stg_mutations_filtrees
),

squelette AS (
    SELECT p.code_commune, p.type_local, c.mois
    FROM perimetre p
    CROSS JOIN calendrier c
),

glissant AS (
    SELECT
        s.code_commune,
        s.type_local,
        s.mois,
        count(f.id_mutation) AS nb_mutations_12m,
        round(quantile_cont(f.prix_m2, 0.50), 0) AS prix_m2_median_12m,
        round(quantile_cont(f.prix_m2, 0.25), 0) AS prix_m2_q1_12m,
        round(quantile_cont(f.prix_m2, 0.75), 0) AS prix_m2_q3_12m
    FROM squelette s
    LEFT JOIN stg_mutations_filtrees f
       ON f.code_commune = s.code_commune
      AND f.type_local   = s.type_local
      AND f.mois >= (s.mois - INTERVAL 11 MONTH)::DATE
      AND f.mois <= s.mois
    GROUP BY 1, 2, 3
)

SELECT
    g.*,
    g.mois >= (SELECT min(mois) FROM calendrier) + INTERVAL 11 MONTH AS fenetre_complete
FROM glissant g;