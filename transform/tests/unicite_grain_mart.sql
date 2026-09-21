-- Attendu : 0 ligne. Le grain du mart est (commune, type de bien, mois).
-- Porte depuis tests/donnees/01_unicite.sql le 21/09.
SELECT code_commune, type_local, mois, count(*) AS occurrences
FROM {{ ref('mart_prix_m2_reference') }}
GROUP BY 1, 2, 3
HAVING count(*) > 1