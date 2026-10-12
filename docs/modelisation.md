# Modélisation dimensionnelle

*Conception du 09/10/2026, implémentée les 10 et 12/10/2026.*

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
`valeur_fonciere`, `surface_bati`, `prix_m2`, `nb_locaux_principaux`, `nb_pieces`, `nb_dependances` : Mesures
`mois`, `annee`, `trimestre` : Attributs de `dim_temps`. Ils restent calculés dans `int_mutations_filtrees`, aucun modèle ne les lit depuis le 12/10.
`code_departement` : Attribut déjà présent dans `dim_commune`
`nature_mutation`, `nb_communes`, `nb_natures`, `nb_types_principaux` : Constantes après filtrage (règles 1, 1 bis, 2, 4) : hors de l'étoile
`nb_dates`, `nb_lignes_source` : Traçabilité de l'entonnoir : hors de l'étoile

## Ecart
 - Le Héron (76358) : 5 mutations portent un code absent du COG 2026. La clé orpheline est tolérée (WARN).
 - Kimball garantirait l'intégrité référentielle, par une ligne "inconnu" ou par l'historique de la dimension.
 - Le traitement prévu est le snapshot, au J5 ou en S10.

## Arbitrages

### Grain de la dimension temps : le jour
 - Ce que lisait le SQL au 09/10 : `agg_prix_m2_glissant.sql`, ligne 36 : la fenêtre est `f.mois BETWEEN s.mois - INTERVAL 11 MONTH AND s.mois`. Elle travaille au mois.
 Même fichier, ligne 10 : le calendrier est `SELECT DISTINCT mois FROM int_mutations_filtrees`, un calendrier mensuel tiré des données.
 `agg_prix_m2_evolution.sql`, ligne 10 : `lag(prix_m2_median_12m, 12)` remonte de 12 lignes. Cela ne fait 12 mois que si le calendrier n’a aucun trou.
 Le mensuel, le mart et les tests lisent le mois.
 Le jour n’est lu qu’à un seul endroit : `int_mutations_filtrees.sql`, lignes 9 à 11, pour en dériver mois, année et trimestre.
 - Décision : le jour.
 - Raison : Une dimension au jour peut servir un mart au mois, mais pas l'inverse.
 - Plage : de la plus petite à la plus grande `date_mutation` des faits.
 Ni `current_date`, ni une plage plus large écrite en dur : `current_date` est une fonction instable de par son fonctionnement, et une plage plus large écrite en dur verrait des mois de 2026 entrer dans le squelette du glissant, avec des fenêtres encore pleines de ventes de 2025. Le mart gagnerait des cellules, et la signature bougerait.

### Type de bien : Dimension
 - Ce que dit le SQL : deux valeurs ; clé de regroupement partout ; liste `['Maison', 'Appartement']` répétée dans trois tests.
 - Décision : dimension
 - Raison : La liste autorisée devient une donnée, avec son ordre d’affichage. Les trois tests sont devenus des `relationships` le 12/10. La liste reste écrite dans la règle 4 et dans le test d'entonnoir. Les `relationships` garantissent que les faits ne sortent pas de la dimension.

### Les trois mesures qu'aucun mart ne lit
 - `nb_locaux_principaux`, `nb_pieces`, `nb_dependances` : dans la table de faits, raison : métriques associées à une observation de la table de faits.

### Clés
 - Les clés naturelles (code INSEE, date, libellé DVF) sont stables et uniques aujourd'hui.
 - Leur limite : quand `dim_commune` gardera son historique (SCD2), le code INSEE ne suffira plus à désigner une version, il faudra une clé de substitution (PDF Kimball, page 7).

### Graphe au 12/10
 - `int_mutations_filtrees` n'alimente plus que `fct_mutations`.
 - `dim_temps` lit les bornes dans les faits.
 - le mensuel et le glissant lisent les faits et les dimensions.
 - le mart lit `nom_commune` dans `dim_commune`.

## Références
 - Kimball Dimensional Modeling Techniques (https://www.kimballgroup.com/wp-content/uploads/2013/08/2013.09-Kimball-Dimensional-Modeling-Techniques11.pdf)
 - The Data Warehouse Toolkit: The Definitive Guide to Dimensional Modeling, Kimball et Ross, 3ᵉ édition, Wiley, 2013.