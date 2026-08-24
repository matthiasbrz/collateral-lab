## Plan de reference - mediane glissante 12 mois

Operateur dominant : HASH_GROUP_BY portant les trois quantile_cont,
0,27 s cumules sur 0,0810 s de temps total.
Un quantile est un agregat holistique : il trie chaque groupe.
Les temps par operateur sont cumules sur les threads, pas sur l'horloge :
0,27 + 0,10 = 0,37 s cumules pour 0,081 s reels, soit un parallelisme d'environ 4,6.

Ecart estime / reel le plus important : sortie du HASH_JOIN,
468 775 lignes reelles contre 2 176 689 025 estimees, facteur 4 643.
2 176 689 025 = 46 655 exactement au carre : l'optimiseur s'est rabattu
sur le produit cartesien, aucune selectivite appliquee ni aux egalites
ni a l'intervalle de dates.

Volumetrie intermediaire : 468 775 = 46 655 x 10,05.
Chaque transaction est visitee par 10 mois de reference en moyenne.

| # | Variante | Mediane | Rapport | Note |
|---|---|---|---|---|
| A | Jointure sur squelette dense | 0,1134 | 1,00 | reference |
| B | Fenetre RANGE 11 mois | 0,0462 | 0,41 | NON COMPARABLE : 12 669 lignes contre 31 176 |
| C | A, optimiseur desactive | | | a refaire, 5 passages |
| D | A, sans la jointure morte dim_commune | | | |
| E | A, cast ::DATE dans la condition |0,11 | | supprime 468 775 CAST vers TIMESTAMP |

## Cout par etape de la chaine
| Script | Mediane | Part |
|---|---|---|
| 02_stg_mutations | 0,3694 | 55 % |
| 03_stg_mutations_filtrees | 0,0711 | 11 % |
| 05_agg_prix_m2_glissant | 0,1134 | 17 % |
| 06_agg_prix_m2_evolution | 0,0580 | 9 % |
| 04_agg_prix_m2_mensuel | 0,0408 | 6 % |
| 07_mart_prix_m2_reference | 0,0191 | 3 % |
| **Total** | **0,672** | |
L'etape dominante de la chaine est la resolution du grain, pas l'agregation.