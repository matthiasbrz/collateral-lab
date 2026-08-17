# Règles de filtrage - table de faits

Périmètre : mutations DVF, Seine-Maritime (76), 2023-2025.
Grain retenu : une ligne = une mutation (id_mutation).
Justification : valeur_fonciere est constante à l'intérieur d'un id_mutation
(vérifié : 0 mutations en écart sur 66 151);

| # | Règle | Justification métier | Ecartées | Restantes |
|---|---|---|---|---|
| 0 | - | mutations après passage au grain | - | 66 151 |
| 1 | nature mutation = 'Vente' | échanges, exproriations et adjudications ne forment pas un prix de marché  | 3777 | 62374 |
| 2 | nb_communes = 1 | un prix unique sur deux communes n'est rattachable à aucune | 474 | 61900 |
| 3 | valeur_fonciere > 0 | les ventes symboliques à 1€ (cessions familiales, soultes) sont hors question directrice | 320 | 61580 |
| 4 | nb_types_local = 1 et type IN (Maison, Appartement) | un prix unique sur un lot mixte n'est pas un prix au m2 | 37805 | 23775 |
| 5 | surface_bati > 0 | un terrain nu n'est pas pris en compte | 4 | 23771 |
| 6 | prix_m2 entre p1 et p99 |  |  |  |

## Ce qui est exclu du périmètre, et pourquoi ce n'est pas une perte de qualité
Terrains nus, dépendances seules, locaux industriels et commerciaux : hors question directrice, pas hors qualité.

## Taux de couverture finale
23771 mutations retenus sur 66 151 soit 35,93%.