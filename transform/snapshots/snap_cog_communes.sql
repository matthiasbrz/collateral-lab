{% snapshot snap_cog_communes %}

{{
    config(
        unique_key=['TYPECOM', 'COM'],
        strategy='check',
        check_cols=['LIBELLE', 'COMPARENT'],
        updated_at='debut_millesime',
        hard_deletes='invalidate',
    )
}}

-- Historique du COG brut, tous types confondus : un meme code peut etre une
-- commune et une commune deleguee, d'ou la cle (TYPECOM, COM).
-- Un passage par millesime, du plus ancien au plus recent : scripts/lancer.txt.
-- Le passage 2024 ne vaut que sur une base neuve. Rejoue sur un historique
-- complet, il le remonte dans le temps : le test transition_le_heron le voit.
-- Une suppression est datee de l'execution, pas du millesime : la table n'est
-- pas deterministe et reste hors de toute signature.
{%- set millesime = var('millesime_snapshot', var('millesime_cog')) %}

WITH cog AS (
    SELECT *, {{ var('millesime_cog_anterieur') }} AS millesime
    FROM {{ source('brut', 'raw_communes_2024') }}
    UNION ALL BY NAME
    SELECT *, {{ var('millesime_cog') }} AS millesime
    FROM {{ source('brut', 'raw_communes') }}
)

SELECT
    TYPECOM, COM, DEP, LIBELLE, COMPARENT,
    make_timestamp(millesime, 1, 1, 0, 0, 0) AS debut_millesime
FROM cog
WHERE millesime = {{ millesime }}

{% endsnapshot %}