# Règles de filtrage - table de faits

Périmètre : mutations DVF, Seine-Maritime (76), 2023-2025.
Grain retenu : une ligne = une mutation (id_mutation).
Justification : valeur_fonciere est constante à l'intérieur d'un id_mutation
(vérifié : 0 mutations en écart sur 66 151);

| # | Règle | Justification métier | Ecartées | Restantes |
|---|---|---|---|---|
| 0 | - | mutations après passage au grain | - | 66 151 |
| 1 | nature mutation = 'Vente' | échanges, expropriations et adjudications ne forment pas un prix de marché  | 3777 | 62374 |
| 2 | nb_communes = 1 | un prix unique sur deux communes n'est rattachable à aucune | 474 | 61900 |
| 3 | valeur_fonciere > 0 | valeur foncière absente ou nulle : la mutation existe mais son prix n'est pas exploitable | 320 | 61580 |
| 4 | nb_types_local = 1 et type IN (Maison, Appartement) | un prix unique sur un lot mixte n'est pas un prix au m2 | 37805 | 47 613 |
| 5 | surface_bati > 0 | surface manquante ou à zéro, non exploitable | 4 | 47 609 |
| 6 | prix_m2 entre p1(444,58 ) et p99(5 289,66) |  | 954 | 46 655 |

## Ce qui est exclu du périmètre, et pourquoi ce n'est pas une perte de qualité
Terrains nus, dépendances seules, locaux industriels et commerciaux : hors question directrice, pas hors qualité.

## Taux de couverture final
46 655 mutations retenues sur 66 151 soit 70,5%.