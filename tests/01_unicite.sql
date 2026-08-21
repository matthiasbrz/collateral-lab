-- tests/01_unicite.sql
-- Attendu : 0 ligne. Toute ligne renvoyee est une violation de grain.

SELECT 'stg_mutations.id_mutation' AS grain,
        id_mutation AS cle,
        count(*) AS occurences
FROM stg_mutations
GROUP BY 1, 2
HAVING count(*) > 1

UNION ALL

SELECT 'mart(code_commune, type_local, mois)',
        code_commune || '|' || type_local || '|' || mois::VARCHAR,
        count(*)
FROM mart_prix_m2_reference
GROUP BY 1, 2
HAVING count(*) > 1;