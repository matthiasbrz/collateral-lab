-- sql/stg_mutations.sql
-- Table : stg_mutations
-- Source : raw_mutations (geo-dvf, dept 76, millesimes 2023-2025)
-- Grain : une ligne = une mutation (id_mutation)
-- Verifie le 16/08/2026 : 0 mutation porte plusieurs valeurs foncieres distinctes.
-- Aucun filtre metier ici : les exclusions sont dans stg_mutations_filtrees.sql

CREATE OR REPLACE TABLE stg_mutations AS

WITH entete AS (
    SELECT
        id_mutation,
        min(date_mutation)              AS date_mutation,
        min(nature_mutation)            AS nature_mutation,
        min(valeur_fonciere)            AS valeur_fonciere,
        min(code_commune)               AS code_commune,
        min(nom_commune)                AS nom_commune,
        min(code_departement)           AS code_departement,
        count(DISTINCT code_commune)    AS nb_communes,
        count(DISTINCT nature_mutation) AS nb_natures,
        count(DISTINCT date_mutation)   AS nb_dates,
        count(*)                        AS nb_lignes_source
    FROM raw_mutations
    GROUP BY id_mutation
),

-- Dedoublonnage des locaux : une ligne source par (local x subdivision fiscale).
-- Sans ce DISTINCT, sum(surface_reelle_bati) surestime les surfaces
-- exactement comme sum(valeur_fonciere) surestimait les prix.
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

-- Convention : la dependance reste dans le prix (numerateur) mais pas dans
-- la surface (denominateur), surface_reelle_bati n'etant pas exploitable
-- sur les dependances. Consequence assumee : le prix au m2 d'une maison
-- avec garage est legerement majore.
biens AS (
    SELECT
        id_mutation,
        count(*)                       FILTER (WHERE type_local <> 'Dépendance') AS nb_locaux_principaux,
        count(DISTINCT type_local)     FILTER (WHERE type_local <> 'Dépendance') AS nb_types_principaux,
        min(type_local)                FILTER (WHERE type_local <> 'Dépendance') AS type_local,
        sum(surface_reelle_bati)       FILTER (WHERE type_local <> 'Dépendance') AS surface_bati,
        sum(nombre_pieces_principales) FILTER (WHERE type_local <> 'Dépendance') AS nb_pieces,
        count(*)                       FILTER (WHERE type_local =  'Dépendance') AS nb_dependances
    FROM locaux
    GROUP BY id_mutation
)

SELECT
    e.*,
    b.nb_locaux_principaux,
    b.nb_types_principaux,
    b.type_local,
    b.surface_bati,
    b.nb_pieces,
    b.nb_dependances
FROM entete e
LEFT JOIN biens b USING (id_mutation);