# Profilage - DVF géolocalisés, Seine-Maritime (76), 2023-2025
Chargé le 15/08/2026 depuis files.data.gouv.fr/geo-dvf/latest - Licence Ouverte 2.0.

## 1. Volumétrie et période
165634 lignes, 66151 mutations distinctes, 708 communes, du 2023-01-02 au 2025-12-31

## 2. Granularité réelle
Une ligne n'est pas une vente : 37,81% des mutations portent plusieurs lignes, jusqu'à 715 lignes pour une seule mutation. valeur_fonciere est répétée à l'identique.
Conséquence : toute agrégation naïve surestime le marché.

## 3. Complétude 
surface_reelle_bati manquante sur 54.29 % des lignes, type_local sur 23.74 %.
Impact directe sur le calcul du prix au m².

## 4. Distribution et extrêmes
p1 = 1.0, médiane = 169000.0, p99 = 12600000.0, max = 62098000.0
Les valeurs hautes correspondent à des ensembles immobiliers, pas à des erreurs de saisie.

## 5. Conséquence pour la table de faits (J4)
Un nettoyage des données s'impose avant toute création de la table de faits.
Des valeurs manquantes sur des champs comme surface_reelle_bati et type_local, ayant un impact sur le calcul du prix au m², nécessitent un nettoyage et/ou une correction.

## Note de gouvernance
La table brute contient adresse, id_parcelle, latitude et longitude.
C'est le support concret du risque de réidentification indirecte : ni data ni collateral.duckdb ne sont versionnés.