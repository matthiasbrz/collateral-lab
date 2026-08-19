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