-- Grain : une mutation retenue (regles 1 a 6). Conception : docs/modelisation.md
-- Colonnes explicites : un SELECT * ferait entrer dans l'etoile les colonnes
-- que l'inventaire du 09/10 en a sorties.

SELECT
    -- dimension degeneree
    id_mutation,
    -- cles vers les dimensions
    date_mutation,      -- dim_temps.date_jour
    code_commune,       -- dim_commune.code_commune
    type_local,         -- dim_type_bien.type_local
    -- mesures
    valeur_fonciere,
    surface_bati,
    prix_m2,
    nb_locaux_principaux,
    nb_pieces,
    nb_dependances
FROM {{ ref('int_mutations_filtrees') }}