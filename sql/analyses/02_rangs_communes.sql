-- sql/analyses/02_rangs_communes.sql
-- Question : comment classer les communes par volume, et que faire des ex aequo ?
SELECT
    code_commune,
    min(nom_commune) AS nom_commune,
    count(*) AS nb_mutations,
    row_number() OVER (ORDER BY count(*) DESC) AS num_ligne,
    rank() OVER (ORDER BY count(*) DESC) AS rang,
    dense_rank() OVER (ORDER BY count(*) DESC) AS rang_dense
FROM stg_mutations_filtrees
GROUP BY code_commune
ORDER BY nb_mutations DESC, code_commune
LIMIT 40