-- sql/analyses/01_top_communes.sql
-- Question : quelles sont les communes ou le marche est le plus actif ?
SELECT
    code_commune,
    count(*) AS nb_mutations
FROM stg_mutations_filtrees
GROUP BY code_commune
QUALIFY row_number() OVER (ORDER BY count(*) DESC <= 10
ORDER BY nb_mutations DESC

SELECT
    type_local,
    code_commune,
    count(*) AS nb_mutations,
    round(quantile_cont(prix_m2, 0.5), 0) AS prix_m2_median
FROM stg_mutations_filtrees
GROUP BY type_local, code_commune
QUALIFY row_number() OVER (PARTITION BY type_local ORDER BY count(*) DESC) <= 5
ORDER BY type_local, nb_mutations DESC

SELECT * FROM (
    SELECT type_local, code_commune, count(*) AS nb_mutations,
        ROW_NUMBER() OVER (PARTITION BY type_local ORDER BY count(*) DESC) AS rn
    FROM stg_mutations_filtrees
    GROUP BY type_local, code_commune
) WHERE rn <= 5