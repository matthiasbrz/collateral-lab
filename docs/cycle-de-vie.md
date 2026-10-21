# collateral-lab dans le cycle de vie du data engineering

Première version du 21/10/2026, d'après le chapitre 2 de *Fundamentals of Data Engineering* (Reis & Housley, 2022).

## Les cinq étapes

| Étape | Où dans collateral-lab | État | Raison |
|---|---|---|---|
| Génération | Hors du projet : DVF géolocalisé (Etalab, à partir des actes de la DGFiP) et COG de l'INSEE. Livraison semestrielle qui remplace tous les fichiers et peut modifier tous les millésimes (`docs/incremental.md`) ; version déclarée par empreintes (`docs/empreintes_attendues.txt`) | couvert | Origine de la donnée utilisée dans le cycle de vie de l'ingénierie de données. |
| Stockage | Une base DuckDB locale, `collateral.duckdb` : `main` pour le brut, `dbt` pour les modèles et le snapshot. Sources dans `data/raw/`, jamais versionnées (règle 4) | couvert | Lieu où stocker la donnée, présente dans tout le cycle de vie de l'ingénerie de données. |
| Ingestion | Par lot, tirée : `collateral.download` (téléchargement, intégrité, empreintes), puis `collateral.load` (`sql/00_*.sql`, provenance et empreinte de chaque fichier) ; détection hebdomadaire d'une livraison en CI | couvert | Récupérer la donnée depuis les sources externes : peut être sujet à des échecs (ici la non livraison de nouvelles données). |
| Transformation | dbt, 13 modèles et 60 tests : staging incrémental par millésime, périmètre et écrêtage p1/p99, étoile (un fait, trois dimensions), agrégats et mart ; snapshot du COG | couvert | Changement de la forme originalle de la donnée en quelque chose d'exploitable par la suite. |
| Service | `mart_prix_m2_reference`, 11 383 cellules publiables ; catalogue dbt republié à chaque fusion ; le chiffre du premier écran du README. Ni outil BI, ni ML, ni reverse ETL | couvert | Utiliser la donnée transformée en un but pratique, ne pas laisser cette donnée transformée inerte. |

## Les six courants sous-jacents

| Courant | Où dans collateral-lab | État | Raison |
|---|---|---|---|
| Sécurité | Aucun secret dans le dépôt ; données non versionnées, raison RGPD écrite (`docs/gouvernance.md`) ; workflows en `contents: read` ; `main` protégée par PR et vérification exigée | couvert | Règle de moindre privilège : n'accéder qu'à la donnée strictement nécessaire, uniquement au moment nécessaire. |
| Gestion des données | Qualité : 60 tests, dont l'entonnoir et le seuil de publication ; modélisation : `docs/modelisation.md` ; règles chiffrées : `docs/regles_filtrage.md` ; lignage : le DAG du catalogue ; historique : le snapshot du COG | à compléter en S11 | à compléter en S11 |
| DataOps | CI qualité (ruff, pytest, `dbt parse`) et construction sous Linux ; rituel `verif_depot` (graphe, orphelines, signature) ; `verif_clone` ; simulation de livraison ; constats datés au journal | à compléter en S11 | à compléter en S11 |
| Architecture des données | Base locale sur un seul poste ; frontière Python / dbt du 08/09 ; `docs/architecture.md`, en partie périmé (constat du 16/10) | à compléter en S11 | à compléter en S11 |
| Orchestration | Une séquence linéaire (`scripts/lancer.txt`), un déclencheur hebdomadaire en CI, le DAG de dbt dans la transformation ; aucun orchestrateur | à compléter en S11 | à compléter en S11 |
| Génie logiciel | Paquet Python (`src/`), 38 tests unitaires, ruff, versions épinglées (`constraints.txt`), PR et CI | à compléter en S11 | à compléter en S11 |

## Ce que ce tableau ne dit pas encore
- … 