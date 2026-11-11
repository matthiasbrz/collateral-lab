-- Grain : une ligne = une mutation (id_mutation)
-- Verifie le 16/08/2026 : 0 mutation porte plusieurs valeurs foncieres distinctes.
-- Aucun filtre metier ici : les exclusions sont dans int_mutations_filtrees.sql
--
-- Incremental depuis le 19/10, conception : docs/incremental.md.
-- Un millesime se reconstruit en entier quand l'empreinte de son fichier change.
-- Tout changement de ce SQL impose un --full-refresh : la detection voit les
-- fichiers, pas le code. Un commentaire n'en demande pas.

{{ config(
    materialized='incremental',
    incremental_strategy='delete+insert',
    unique_key='millesime',
    on_schema_change='fail'
) }}

WITH a_traiter AS (
    -- Fichiers dont l'empreinte differe de celle dont leur millesime a ete
    -- construit, ou dont le millesime manque. Premiere construction : tous.
    SELECT f.fichier, f.millesime, f.empreinte
    FROM {{ source('brut', 'raw_fichiers') }} f
    {% if is_incremental() %}
    LEFT JOIN (SELECT DISTINCT millesime, empreinte_source FROM {{ this }}) t
        ON t.millesime = f.millesime
    WHERE t.empreinte_source IS DISTINCT FROM f.empreinte
    {% endif %}
),

lignes AS (
    SELECT r.*, a.millesime, a.empreinte AS empreinte_source
    FROM {{ source('brut', 'raw_mutations') }} r
    JOIN a_traiter a USING (fichier)
),

entete AS (
    SELECT
        id_mutation,
        min(date_mutation)              AS date_mutation,
        min(nature_mutation)            AS nature_mutation,
        min(valeur_fonciere)            AS valeur_fonciere,
        min(code_commune)               AS code_commune,
        min(code_departement)           AS code_departement,
        count(DISTINCT code_commune)    AS nb_communes,
        count(DISTINCT nature_mutation) AS nb_natures,
        count(DISTINCT date_mutation)   AS nb_dates,
        count(*)                        AS nb_lignes_source,
        min(millesime)                  AS millesime,
        min(empreinte_source)           AS empreinte_source
    FROM lignes
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
    FROM lignes
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
LEFT JOIN biens b USING (id_mutation)