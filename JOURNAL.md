# Journal

## 2026-08-13 - J1 : poser le cadre
- Fait : dépôt public créé, outillage installé, .gitignore et README v0 écrits, 2 commits poussés, configuration de ces éléments sur 2 PCs.
- Coincé : Rédaction de la partie 'Gouvernance' dans le README.
- Demain : Git pour de vrai - 3 branches, 1 PR fusionnée, 1 conflit provoqué et résolu.

## 2026-08-14 — J2 : Git pour de vrai
- Fait : 1 PR ouverte, relue et fusionnée ; 1 conflit provoqué et résolu à la main ; graphe lu.
- Un conflit de fusion, avec mes mots : Un conflit de fusion est un problème survenant lors de la modification distincte d'un même fichier deux la part de deux ou plus branches au même instant T, sans merging en amont des chemins. Cela survient lorsque la Pull Request d'une branche a été fusionné, mais pas celle de la seconde branche.
- Coincé : Lecture du graph, la scission de la branche OK, mais à quel moment les deux branches se rejoignent précisement. Cela m'a demandé un peu plus de temps.
- Demain : charger et profiler — un seul département.

## 2026-08-17 - J4 : Table de faits
- Fait : 1 PR ouverte (feat/staging), deux tables SQL créées (stg_mutations et stg_mutations_filtrees), fixation de la granularité, règles de filtrage explicites, documentation règles filtrage rédigée (nombre de lignes écartées par filtre), calcul prix m2 entre seuil justifié p1/p99
- Coincé : plus de temps prévu passé sur la génération des tables SQL et le receuil des métriques (temps total de la journée = environ 120 minutes)
- Demain : début génération tables dimensions

## 2026-08-18 - J5 : La dimension qui bouge
- Fait : 1 PR ouverte (feat/dim-commune), une table SQL créée (dim_commune), contrôle de la jointure / du grain, analyse des codes non-appariés
- Coincé : RAS
- Demain : La première fenêtre
- Note SCD2 : Entre le 2 janvier 2024 et le 1er janvier 2025, 110 communes ont fusionné pour former 46 communes nouvelles, 8 ont changé de nom, une communne créée en 2016 à été rétablie en 5 communes distinctes. Entre le 2 janvier 2025 et le 1er janvier 2026 : aucune commune nouvelle, la loi interdisant de modifier le périmètre des circonscriptions dans l'année précédant un scrutin - les municipales tombaient en mars 2026. Mais 19 changements de nom et 40 suppressions de communes déléguées. La volatilité de cette dimension obéit au calendrier éléctoral. Une année à zéro fusion ne signifie pas une dimension stable, elle signifie une dimension sous contrainte légale temporaire - et 2027 rattrapera le retard.

## 2026-08-19 - J6 : La première fenêtre
- Fait : 1 PR ouverte (feat/agregats), 4 tables SQL créées (agg_prix_m2_mensuel, glissant, evolution, mart_prix_m2_reference)
- Coincé : Point de contrôle S1 (erreur attendue à "dim_commune", obtenue dès table "raw_mutations")
- Demain : Début S2 (SQL analytique, toutes les fonctions de fenêtrage sortent de ce projet)

## 2026-08-20 - S2-J1 : Solder la dette
- Fait : 1 PR ouverte (chore/dette-s1), 1 table SQL créée (00_raw_mutations.sql, remplace src/load.py), 7 tables SQL renommées (01_dim_commune.sql, 02_stg_mutations.sql, 03_mutations_filtrees.sql, 04_agg_prix_m2_mensuel.sql, 05_agg_prix_m2_glissant.sql, 06_agg_prix_m2_evolution.sq, 07_mart_prix_m2_reference.sql), automatisation du téléchargement des sources. Refactoring réussi : la structure change, le résultat non
- Coincé : Passé pas mal de temps à corriger les anomalies de la nouvelle version de src/download.py et src/build.py
- Demain : S2-J2 (Les tests, à la main)

## 2026-08-21 - S2-J2 : Les tests, à la main
- Fait : 1 PR ouverte (feat/tests), 5 tests SQL mis en place (unicité, non-nullité, plage de valeurs, cohérence de l'entonnoir, intégrité référentielle), exécution des tests puis casse volontaire pour découvrir l'effet produit. Notes : Aujourd'hui rien ne relis un test à un modèle. Une nouvelle table peut bien être ajoutée sans qu'aucun mécanisme de réclame de test. La mise en place des tests est répétitive (exemple 02_non_nullite avec IS NULL), un bloc par colonne. La convention "zero ligne" se reconstruit à la main à chaque fois (le WHERE ... > 0 externe, le IS NULL explicite, le coalesce), une règle qu'on réimplémente est une règle qu'on finira par oublier. Enfin aucun ordre de dépendance, le harnais exécute par ordre alphabétique et non selon le graphe des modèles.
- Coincé : RAS
- Demain : S2-J3 (Le SQL qu'on n'apprend pas en formation)

## 2026-08-22 - S2-J3 : Le SQL qu'on n'apprend pas en formation
- Fait : 1 PR ouverte (feat/analyses), 6 tests SQL mis en place, définis par une question métier et non une description technique (exemple : "Quelles communes sont les plus actives ?", et non "Requête de classement avec QUALIFY"). Un bug de cadre de produit pas une erreur, il produit un autre indicateur.
- Coincé : RAS
- Demain : S2-J4 (Repos)

## 2026-08-24 - S2-J4 : Lire un plan d'exécution
- Fait : 1 PR ouverte (feat/performance), tests de performance SQL mis en place, lecture de plans d'executions (EXPLAIN / EXPLAIN ANALYZE), analyse du cout par etape, cout estime vs. cout reel. Modification de requetes et calcul avant/apres
- Coincé : Lecture du plan via terminal (ne pas utiliser con.sql(".."), mais print(con.execute("EXPLAIN ANALYZE <requete>").fetchone()[1]))
- Demain : S2-J5 (Le transfert en mission)

## 2026-08-25 - S2-J5 : Lire un plan d'exécution
- Fait : Lecture uniquement. Note : Plan passé de "TABLE ACCESS FULL" à "INDEX RANGE SCAN", gain non mesuré faute d'accès aux statistiques d'exécution.
- Coincé : Impossible d'utiliser la quasi-totalité des commandes attendues dans l'environnement client
- Demain : S2-J6 (Fiabilité, limites, contrôle)

## 2026-08-26 - S2-J6 : Fiabilité, limites, contrôle
- Fait : 1 PR ouverte (feat/fiabilite), génération d'indicateurs de fiabilite (écart interquartile), clone de zero du projet
- Coincé : RAS
- Demain : S3(Python d'ingéniere)-J1

## 2026-08-28 - S3-J1 : L'outillage qui attrape les fautes
- Fait : Point zéro Ruff : 4 erreurs sur 12 fichiers, dont 0 de la famille F. Les règles F n'auraient attrapé aucune de mes trois fautes de la semaine dernière. Le lint garantit la forme, pas la correction. Trois colonnes ou tables orphelines découvertes en deux jours : ecart_interquartile calculée et jamais publiée, ref_seuils_dispersion que rien ne consomme, evolution_pct sans spécification de nullabilité. Un alias SQL mal orthographié survit à tous les outils Python. Cause commune : rien ne relie un modèle à ses colonnes ni à ses tests.
- Coincé : Détecter la faute de frappe dans la génération des tables, mettre en place les modules corrigées après check ruff
- Demain : S3-J2 (Découper le script en modules)