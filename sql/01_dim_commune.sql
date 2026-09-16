-- sql/dim_commune.sql
-- Table : dim_commune
-- Source : Code officiel geographique Insee, millesime 2026
-- Grain : une ligne = une commune existante au 01/01/2026
-- Perimetre : communes de plein exercice uniquement (TYPECOM = 'COM')

CREATE OR REPLACE TABLE dim_commune AS
SELECT
    COM AS code_commune,
    LIBELLE AS nom_commune,
    DEP AS code_departement,
    REG AS code_region,
    COMPARENT AS code_commune_parent,
    2026 AS millesime_cog
FROM raw_communes
WHERE TYPECOM = 'COM';  