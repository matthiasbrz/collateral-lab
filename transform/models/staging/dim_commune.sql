-- Grain : une commune de plein exercice au milllesime declare.
--
-- Le fichier COG contient aussi les communes deleguees, associees et les
-- arrondissements municipaux. Sans le filtre TYPECOM, la jointure duplique :
-- constate le 04/09, 303 lignes de mart en trop.

SELECT
    COM                         AS code_commune,
    LIBELLE                     AS nom_commune,
    DEP                         AS code_departement,
    REG                         AS code_region,
    COMPARENT                   AS code_commune_parent,
    {{ var('millesime_cog') }}  AS millesime_cog
FROM {{ source('brut', 'raw_communes') }}
WHERE TYPECOM = 'COM'