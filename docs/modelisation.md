# Modélisation dimensionnelle

*Conception du 09/10/2026, avant implémentation (S9-J3 et J4).*

## Les quatres étapes
1. Le processus : la vente immobilière, une mutation de nature "Vente" publiée par la DGFiP.
2. Le grain : une mutation retenue après les règles 1 à 6. `id_mutation` est déjà testé unique dans `int_mutations_filtrees`. C'est l'étape pivot : chaque mesure doit être vraie à ce grain.
3. Les dimensions : commune, temps, type de bien. `id_mutation` reste dans la table de faits comme dimension dégénérée.
4. Les faits : 
    - `valeur_fonciere` et `surface_bati`, additives.
    - `prix_m2`, non additive.

## Inventaire des colonnes
`id_mutation` : Dimension dégénérée
`date_mutation`, `code_commune`, `type_local` : Clés vers `dim_temps`, `dim_commune`, `dim_type_bien` (selon l'arbitrage)
`valeur_fonciere`, `surface_bati`, `prix_m2` : Mesures
`mois`, `annee`, `trimestre` : Attributs de `dim_temps`. Aucun modèle ne lit `annee` ni `trimestre` aujourd'hui.
`code_departement` : Attribut déjà présent dans `dim_commune`
`nature_mutation`, `nb_communes`, `nb_natures`, `nb_types_principaux` : Constantes après filtrage (règles 1, 1 bis, 2, 4) : hors de l'étoile
`nb_dates`, `nb_lignes_sources` : Traçabilité de l'entonnoir : hors de l'étoile
`nb_locaux_principaux`, `nb_pieces`, `nb_dependances` : mesures possibles, qu'aucun mart ne lit

## Ecart
 - Le Héron (76358) : 5 mutations portent un code absent du COG 2026. La clé orpheline est tolérée (WARN).
 - Kimball garantirait l'intégrité référentielle, par une ligne "inconnu" ou par l'historique de la dimension.
 - Le traitement prévu est le snapshot, au J5 ou en S10.