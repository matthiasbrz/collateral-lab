# Incrémental : conception

Conception du 16/10/2026, construite le 17/10 : voir
"Ce qui est prouvé"

## Ce qu'une livraison change
Les fichiers mis a disposition font l’objet d’une mise a jour semestrielle, en avril et en octobre.
Chaque mise a jour supprime puis remplace la totalite des fichiers precedemment publies.
Point d’attention : les fichiers sont alimentes par les donnees saisies dans les services de la publicite fonciere de la DGFiP et a chaque mise a jour de nouvelles transactions sont susceptibles d’être ajoutees dans tous les millesimes en fonction de la date de mutation.

Source : page DGFiP « Demandes de valeurs foncières ». La chaîne télécharge le jeu géolocalisé d'Etalab, qui suit chaque livraison de la DGFiP avec un décalage.
Pour la chaîne, une livraison peut donc, dans n'importe quel millésime, ajouter une vente, en modifier une, en retirer une. La conception doit rester exacte dans les trois cas : le troisième est celui qu'un incrémental naïf rate.

## L'unité de remplacement : le millésime
Une ligne de `stg_mutations` par `id_mutation`, un fichier par millésime (`dvf_76_2023.csv.gz`, etc.) : une mutation n'appartient qu'à un fichier.
Remplacer mutation par mutation ne touche que les mutations présentes dans le nouveau fichier. Une vente retirée par la DGFiP n'y figure plus : sa ligne n'est jamais touchée, elle reste dans l'entrepôt.
Remplacer le millésime entier supprime toutes ses lignes avant d'insérer le nouveau fichier : la vente retirée disparaît.
Décision : on remplace le millésime entier.

## La détection
Un millésime est à reconstruire quand l'empreinte de son fichier diffère de celle à partir de laquelle il a été construit.
- Le chargement écrit l'empreinte de chaque fichier DVF dans une nouvelle table brute, `raw_fichiers` (fichier, millésime, empreinte, `charge_le` comme les autres tables brutes) : `sha256(content)` sur `read_blob('data/raw/dvf_*.csv.gz')`. C'est le même SHA-256 que `docs/empreintes_attendues.txt` (vérifié contre `hashlib` sur DuckDB 1.5.5). Elle entre par le chargement, pas par dbt : la frontière du 08/09 tient.
- `raw_mutations` garde le fichier d'origine de chaque ligne (colonne virtuelle `filename`), donc son millésime.
- Le modèle incrémental porte, sur chaque ligne, l'empreinte du fichier dont elle vient (`empreinte_source`). À chaque exécution, il ne relit que les millésimes dont l'empreinte a changé, ou qu'il ne contient pas encore.
- `charge_le` n'y sert pas : il change à chaque chargement et ferait tout retraiter.

Cohabitation avec le refus du 05/10 : le contrôle d'empreintes de `download` est une porte, la détection vient après. Un fichier modifié est d'abord refusé. Une fois vérifié et déclaré (empreintes et signature dans le même commit), il est chargé, et l'incrémental reconstruit les millésimes dont l'empreinte a changé, et eux seuls.

Hypothèse à mesurer sur la vraie livraison : une recompression sans changement de contenu change aussi l'empreinte (en-tête gzip). Ce serait du retraitement inutile, jamais une erreur.

## Le placement et la stratégie
Modèle incrémental : `stg_mutations`. C'est le premier modèle qui lit la source et celui qui fait l'essentiel du calcul ; tout son calcul est local à une mutation, donc à un millésime.
En aval, `ref_seuils_prix_m2` calcule p1/p99 sur tout le périmètre : rien n'y est local à un millésime. Un modèle incrémental placé là deviendrait faux dès qu'un seuil bouge. Les modèles en aval restent des tables, reconstruites à chaque exécution à partir d'un `stg_mutations` exact.

Configuration : `materialized='incremental'`, `incremental_strategy='delete+insert'`, `unique_key='millesime'`, `on_schema_change='fail'`.
- `delete+insert` sur le millésime : dbt supprime toutes les lignes des millésimes présents dans le lot, puis insère le lot. La clé n'est pas unique, et c'est voulu : la documentation dbt prévoit ce cas pour cette stratégie (vérifié sur dbt-duckdb 1.11).
- La stratégie naïve est `merge` sur `id_mutation` : elle met à jour et elle ajoute, mais elle ne retire rien.
- `on_schema_change='fail'` : par défaut (`ignore`), une colonne ajoutée n'apparaîtrait jamais dans la table, sans erreur.

Conséquences :
- `stg_mutations` gagne deux colonnes, `millesime` et `empreinte_source`. Elles passent dans les deux modèles `int_` (`SELECT *`), pas dans `fct_mutations` (colonnes explicites) : la structure des `int_` change, la signature du mart non.
- Sur une base existante, passer de `table` à `incremental` exige un `--full-refresh` : sans lui, dbt prend la table existante pour une construction incrémentale antérieure (vérifié : erreur sur `empreinte_source`). En CI et sur un clone neuf, la première construction est une vraie construction complète.

## La preuve
1. Au J3, sur les données actuelles : la construction complète laisse la signature du mart inchangée ; une seconde exécution sans changement passe par la branche incrémentale, vérifiée dans le SQL exécuté, et ne change rien.
2. Au J4, sur une livraison simulée par le même chemin qu'une vraie (une vente retirée, une valeur modifiée, une vente ajoutée dans un millésime passé) : l'incrémental est identique au full refresh, par `comparer()` puis par la signature du mart.
3. Calibrage : sur la même entrée, `merge` sur `id_mutation` doit rendre « non identique », à cause de la vente retirée.

La CI part toujours d'une base neuve : elle ne parcourt jamais la branche incrémentale, et son badge vert ne prouve rien sur elle.

## Les seuils
Décision : bornes p1/p99 par millésime, calculées sur les seules ventes du millésime. Un millésime ne bouge donc que si son propre fichier change. La limite n° 7 deviendra : « une valeur historique ne change que si une livraison modifie son millésime ». Un clone neuf recalcule les mêmes bornes à partir des mêmes fichiers : la reproductibilité tient.

Écarté : figer les bornes dans la base à leur premier calcul. Un clone neuf les recalculerait sur les fichiers du jour, et ne retrouverait plus le résultat publié.

C'est un changement de définition (la règle 6), donc de signature. Il se fera dans sa propre PR, avec un nouvel étalon daté, après la preuve de l'incrémental et la mesure de la vraie livraison. Jamais dans la même PR que l'incrémental, dont la preuve exige une signature inchangée.

Une fois les bornes par millésime en place, la chaîne devient locale jusqu'à `int_mutations_filtrees`, et l'incrémental pourra y descendre. On le décidera à ce moment-là, pas avant.

## Limites de cette conception
- Une modification du SQL de `stg_mutations` ne déclenche rien : la détection porte sur les fichiers, pas sur le code. Les millésimes déjà construits garderaient l'ancienne logique. Tout changement de ce modèle impose un `--full-refresh`, dans la même séance.
- Un millésime retiré de la configuration (`MILLESIMES`) n'est pas supprimé : `delete+insert` ne touche que les clés présentes dans le lot. Il faut alors un `--full-refresh`.

## Ce qu'on n'attend pas de l'incrémental
Aucun gain de temps à cette volumétrie, seulement l'exactitude. Si la vraie livraison change tous les fichiers, tout sera reconstruit : la décision de garder l'incrémental se prendra sur cette mesure.

## Ce qui est prouvé au 17/10
 - Construit : `raw_fichiers`, la provenance de chaque ligne dans `raw_mutations`, `stg_mutations` en `delete+insert` par millésime.
 - Les empreintes de `raw_fichiers` sont celles de `docs/empreintes_attendues.txt`, pour les trois fichiers.
 - Sur la base existante, la première construction a demandé un `--full-refresh` ; la signature du mart reste `11383 104679694271579681982287`.
 - Une seconde exécution sans changement passe par la branche incrémentale (requête de détection dans le SQL compilé, `delete` puis `insert` dans le SQL exécuté) : aucun fichier à retraiter, signature de `stg_mutations` identique avant et après.
 - `on_schema_change='fail'` vu en rouge : une colonne ajoutée fait échouer le modèle au lieu d'être ignorée.

Pas encore prouvé : l'exactitude face à une livraison qui ajoute, modifie et retire des ventes. C'est la simulation du J4 ; la CI, qui part d'une base neuve, ne la prouvera jamais.