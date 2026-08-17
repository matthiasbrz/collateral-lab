-- sql/stg_mutations.sql
-- Grain : une ligne = une mutation.
-- Source : raw_mutations (geo-dvf, dept 76, millesimes 2023-2025).

CREATE OR REPLACE TABLE stg_mutations AS 

WITH entete AS (
    SELECT
        id_mutation,
        min(date_mutation) AS date_mutation,
        any_value(nature_mutation) AS nature_mutation,
        any_value(valeur_fonciere) AS valeur_fonciere,
        count(DISTINCT code_commune) AS nb_communes,
        any_value(code_commune) AS code_commune,
        any_value(nom_commune) AS nom_commune,
        count(*) AS nb_lignes_source
    FROM raw_mutations
    GROUP BY id_mutation
),

--Dédoublonnage des locaux : une ligne source par (local x subdivision fiscale)
locaux AS (
    SELECT DISTINCT
        id_mutation,
        id_parcelle,
        type_local,
        surface_reelle_bati,
        nombre_pieces_principales
    FROM raw_mutations
    WHERE type_local IS NOT NULL
),

biens AS (
    SELECT
        id_mutation,
        count(*) AS nb_locaux,
        count(DISTINCT type_local) AS nb_types_local,
        min(type_local) AS type_local,
        sum(surface_reelle_bati) AS surface_bati,
        sum(nombre_pieces_principales) AS nb_pieces
    FROM locaux
    GROUP BY id_mutation
)

SELECT
    e.*,
    b.nb_locaux,
    b.nb_types_local,
    b.type_local,
    b.surface_bati,
    b.nb_pieces
FROM entete e
LEFT JOIN biens b USING (id_mutation);