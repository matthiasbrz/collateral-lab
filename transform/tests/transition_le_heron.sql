-- Attendu : 0 ligne. Le snapshot capture la fusion de Le Heron (01/01/2025) : 
-- une version COM de 76358 a existe et elle est close ; 76455 a une version
-- COM courante. La deuxieme branche refuse un historique qui n'aurait jamais
-- vu 76358 : sans elle, un snapshot parti de 2026 passerait a vide.

SELECT 'version COM de 76358 encore ouverte' AS ecart
FROM {{ ref('snap_cog_communes') }}
WHERE TYPECOM = 'COM' AND COM = '76358' AND dbt_valid_to IS NULL
UNION ALL
SELECT 'aucune version COM de 76358 close'
WHERE NOT EXISTS (
    SELECT 1 FROM {{ ref('snap_cog_communes') }}
    WHERE TYPECOM = 'COM' AND COM = '76358' AND dbt_valid_to IS NOT NULL
)
UNION ALL
SELECT 'aucune version COM courante pour 76455'
WHERE NOT EXISTS (
    SELECT 1 FROM {{ ref('snap_cog_communes') }}
    WHERE TYPECOM = 'COM' AND COM = '76455' AND dbt_valid_to IS NULL
)
UNION ALL
-- Une version qui finit avant de commencer : le passage 2024 a ete rejoue
-- sur un historique deja complet.
SELECT 'version a rebours : ' || TYPECOM || ' ' || COM
FROM {{ ref('snap_cog_communes') }}
WHERE dbt_valid_to < dbt_valid_from