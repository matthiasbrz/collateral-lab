# Modélisation dimensionnelle

*Conception du 09/10/2026, avant implémentation (S9-J3 et J4).*

## Les quatre étapes
1. Le processus : la vente immobilière, une mutation de nature "Vente" publiée par la DGFiP.
2. Le grain : une mutation retenue après les règles 1 à 6. `id_mutation` est déjà testé unique dans `int_mutations_filtrees`. C'est l'étape pivot : chaque mesure doit être vraie à ce grain.
3. Les dimensions : commune, temps, type de bien. `id_mutation` reste dans la table de faits comme dimension dégénérée.
4. Les faits : 
    - `valeur_fonciere` et `surface_bati`, additives.
    - `prix_m2`, non additive. La mesure est une médiane de prix unitaires, et une médiane a besoin du ratio de chaque vente. Les deux composantes restent dans la table de faits, donc on peut toujours calculer l'autre lecture.

## Inventaire des colonnes
`id_mutation` : Dimension dégénérée
`date_mutation`, `code_commune`, `type_local` : Clés vers `dim_temps`, `dim_commune`, `dim_type_bien` 
`valeur_fonciere`, `surface_bati`, `prix_m2` : Mesures
`mois`, `annee`, `trimestre` : Attributs de `dim_temps`. Aucun modèle ne lit `annee` ni `trimestre` aujourd'hui.
`code_departement` : Attribut déjà présent dans `dim_commune`
`nature_mutation`, `nb_communes`, `nb_natures`, `nb_types_principaux` : Constantes après filtrage (règles 1, 1 bis, 2, 4) : hors de l'étoile
`nb_dates`, `nb_lignes_source` : Traçabilité de l'entonnoir : hors de l'étoile

## Ecart
 - Le Héron (76358) : 5 mutations portent un code absent du COG 2026. La clé orpheline est tolérée (WARN).
 - Kimball garantirait l'intégrité référentielle, par une ligne "inconnu" ou par l'historique de la dimension.
 - Le traitement prévu est le snapshot, au J5 ou en S10.

# Arbitrages

### Grain de la dimension temps : le jour
 - Ce que lit le SQL : `agg_prix_m2_glissant.sql`, ligne 36 : la fenêtre est `f.mois BETWEEN s.mois - INTERVAL 11 MONTH AND s.mois`. Elle travaille au mois.
 Même fichier, ligne 10 : le calendrier est `SELECT DISTINCT mois FROM int_mutations_filtrees`, un calendrier mensuel tiré des données.
 `agg_prix_m2_evolution.sql`, ligne 10 : `lag(prix_m2_median_12m, 12)` remonte de 12 lignes. Cela ne fait 12 mois que si le calendrier n’a aucun trou.
 Le mensuel, le mart et les tests lisent le mois.
 Le jour n’est lu qu’à un seul endroit : `int_mutations_filtrees.sql`, lignes 9 à 11, pour en dériver mois, année et trimestre.
 - Décision : le jour.
 - Raison : Une dimension au jour peut servir un mart au mois, mais pas l'inverse.
 - Plage : de la plus petite à la plus grande `date_mutation` des faits.
 Ni `current_date`, ni une plage plus large écrite en dur : `current_date` est une fonction instable de par son fonctionnement, et une plage plus large écrite en dur verraient des mois de 2026 entrer dans le squelette du glissant, avec des fenêtres encore pleines de ventes de 2025. Le mart gagnerait des cellules, et la signature bougerait.

### Type de bien : Dimension
 - Ce que dit le SQL : deux valeurs ; cle de regroupement partout ; liste `['Maison', 'Appartement]` répétée dans trois tests.
 - Décision : dimension
 - Raison : la liste autorisée devient une donnée, rangée à un seul endroit. Un test `relationships` vers la dimension remplace les trois listes répétées. Le libellé et l'ordre d'affichage y vivent aussi.

### Les trois mesures qu'aucun mart ne lit
 - `nb_locaux_principaux`, `nb_pieces`, `nb_dependances` : dans la table de faits, raison : métriques associées à une observation de la table de faits.