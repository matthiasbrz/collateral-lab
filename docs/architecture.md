# Architecture

## Frontiere

Python amene la donnee jusqu'a l'entrepot et garantit qu'elle est complete.
dbt transforme ce qui est deja dans l'entrepot et prouve que le resultat tient.

La ligne de partage est l'entrepot : rien n'y entre par dbt, rien ne s'y
transforme par Python.

## Type d'architecture et principes, état au 26/10/2026

Les neuf principes de Reis & Housley (*Fundamentals of Data Engineering*, ch. 3), chacun
rattaché à une décision datée du projet, ou à la raison pour laquelle il ne s'applique pas.

**Type** : un entrepôt de données local et mono-nœud. Un seul fichier DuckDB sur un poste,
alimenté par lot depuis des CSV (DVF, COG de l'Insee), transformé en SQL déclaratif par dbt,
modélisé en étoile et publié en marts.

**Ce qu'il n'est pas** : ni entrepôt cloud, ni lac de données, ni architecture Lambda ou Kappa,
ni data mesh. Un département, une livraison par semestre, un seul domaine et une seule
personne : à cette échelle, un nœud suffit (la médiane glissante tourne en 0,08 s,
`docs/performance.md`), rien n'arrive en flux, et il n'y a ni domaines ni équipes à fédérer.
C'est un choix à cette échelle, pas une limite (« Renonce, etat au 23/10/2026 »).

| Principe | Décision du projet, ou raison de ne pas s'appliquer | Preuve |
|---|---|---|
| 1. Choisir les composants communs avec soin | Un moteur pour toutes les couches (DuckDB), un outil pour transformer, tester et documenter (dbt Core) ; trois dépendances directes, le téléchargement se contente de la bibliothèque standard | `pyproject.toml` ; dépendances figées le 01/10 ; dbt-utils écarté (« Renonce ») |
| 2. Prévoir la panne | Chaque étape échoue tôt et dit pourquoi ; une livraison ou un schéma qui change arrête la chaîne au lieu de passer | téléchargement atomique (01/09) ; empreintes SHA-256 (05/10) ; `on_schema_change: fail` (17/10) ; passage planifié chaque lundi, contrôle qualité à chaque PR |
| 3. Concevoir pour passer à l'échelle | Ne s'applique pas ici, parce que le périmètre est fixé à un département : l'extension est écartée, le volume ne prouverait rien de plus | « Renonce, etat au 23/10/2026 » ; médiane glissante en 0,08 s |
| 4. L'architecture est du leadership | Ne s'applique pas ici, parce que le projet est mené seul : aucune équipe à guider. Ce qui en tient lieu : chaque décision écrite et datée pour un relecteur | cette page ; les constats datés de `JOURNAL.md` |
| 5. Toujours architecturer | L'architecture se révise quand le projet change, et chaque section dit à quelle date elle est vraie | frontière décidée le 08/09, bascule vers dbt le 21/09 ; péremption du 23/10 (PR n°87) ; `docs/robustesse.md` daté le 26/10 |
| 6. Des systèmes faiblement couplés | Python et dbt ne communiquent que par les tables brutes de l'entrepôt : la frontière ci-dessus | bascule du 21/09 : transformation Python retirée au profit de dbt, ingestion conservée, signature du mart identique avant et après |
| 7. Des décisions réversibles | L'incrémental garde son chemin de retour : un full refresh reconstruit tout | `docs/incremental.md` : incrémental identique au full refresh, 13/13 relations (19/10) ; procédure du README (23/10) |
| 8. La sécurité d'abord | DVF contient des données à caractère personnel : aucune donnée versionnée ni publiée, rien du client | règles 4 et 7, section 5 d'`etat_depot` ; catalogue publié vérifié sans valeur ni chemin (15/09, 03/10) ; CI en `contents: read`, seul le déploiement du catalogue écrit sur Pages |
| 9. Adopter le FinOps | Ne s'applique pas ici, parce que le projet n'a aucun coût variable : base locale, CI d'un dépôt public | entrepôt cloud écarté (« Renonce ») |

## Choix technologiques, état au 29/10/2026

Trois choix du projet relus avec les critères de Reis & Housley (ch. 4) : celui qui les
justifie, et celui qui les fragilise.

| Choix | Critère qui le justifie | Critère qui le fragilise |
|---|---|---|
| DuckDB en local plutôt qu'un entrepôt cloud | *Location* et coût : sur site, sans coût variable, et un nœud suffit à cette échelle (médiane glissante en 0,08 s, `docs/performance.md`) ; *Speed to Market* : l'entrepôt cloud ne tenait pas avant l'échéance (« Renonce ») | *Total Opportunity Cost of Ownership* : le projet ne montre ni entrepôt cloud, ni sa facturation, ni ses droits d'accès ; *Today Versus the Future* : DuckDB est la brique la plus récente du projet |
| dbt Core plutôt qu'un outil propriétaire | *Build Versus Buy* : adopter du libre plutôt que construire, sans prix d'achat ; *Today Versus the Future* : le cœur reste du SQL, technologie durable, ce qui limite le coût de sortie | Logiciel libre porté par un éditeur (COSS) : le risque est la stratégie de l'éditeur, pas le prix |
| Python et dbt plutôt qu'un seul outil | *Monolith Versus Modular* : modulaire dans le code, chaque outil fait une chose ; la transformation Python a été remplacée par dbt en gardant l'ingestion (21/09) | Monolithique dans l'environnement : un seul venv, des contraintes communes, et une dépendance qui manque arrête toute la chaîne |

## Historique — la transition, 08/09 → 21/09
    reseau                  disque                      entrepot DuckDB
    ------                  ------                      ---------------
    files.data.gouv.fr  --> data/raw/*.csv.gz   -->     main.raw_mutations
    insee.fr            --> data/raw/*.csv      -->     main.dim_commune
                                                             |
                            [ PYTHON ] ................... [ FRONTIERE ] .........
                                                             |
                                                        [ dbt ] dix modeles
                                                             |
                                                        dbt.mart_prix_m2_reference
                
Deux chaines coexistent volontairement pendant la transition, dans deux
schemas distincts. Chaque modele porte est prouve identique a son equivalent
Python par comparaison de signature, pas par relecture.

## Ce qui reste cote Python, etat au 23/10/2026

- telechargement des sources (reseau), atomique depuis le 01/09
- controle d'integrite avant lecture (disque), et version declaree par empreintes SHA-256 depuis le 05/10
- chargement brut dans l'entrepot `sql/00_*.sql` (`raw_mutations`, `raw_communes`, `raw_communes_2024`, `raw_fichiers`)
- controles qui ne sont pas des tests de donnees : signature et comparaison (`collateral.controle`), relations orphelines (`collateral.orphelines`), livraison simulée (`collateral.simulation`)
- tests unitaires du code Python (pytest)

## Ce qui passe sous dbt

- grain, filtres, agregats, publication
- tests de donnees, generiques et singuliers
- documentation et lignes

## Decoupages imposes par la frontiere - prevus le 08/09, faits avant la bascule du 21/09.

- sql/01_dim_commune.sql fait trois choses : charger, filtrer, renommer.
  Il se coupe en un chargement brut (Python) et un modele dim_commune (dbt).
- sql/03 cree deux tables. dbt impose un fichier, une relation : 
  sql_mutations_filtrees et ref_seuils_prix_m2 deviennent deux modules,
  ce qui supprime la duplication actuelle du bloc de filtres.

### 01_dim_commune, coupe du 12/09/2026

Avant : un script, trois responsabilites - lire, filtrer, renommer.

Apres :
- sql/00_raw_communes.sql (Python) : chargement brut du COG, types forces.
  Aucune ligne ecartee, aucune colonne renommee.
- transform/models/staging/dim_commune.sql (dbt) : filtre TYPECOM = 'COM',
  renommage, millesime declare en variable dbt.

Ce que la coupe a rendu visible : le filtre TYPECOM n'est pas une option de
lecture, c'est la definition de ce qu'est une commune. Colle a un read_csv,
il passait pour un detail technique.

Le millesime 2026 reste declare a deux endroits : config.MILLESIME_COG pour
le nom du fichier, var('millesime_cog') pour la colonne. La duplication ne
disparait pas, elle se deplace sur la frontiere - une valeur au lieu d'un
bloc SQL.

## Bascule - faite le 21/09/2026

Condition posee : les neuf modeles portes, chaque signature identique a son
equivalent Python. Prevu en semaine 5, faite en semaine 6 (voir "Etat au 21/09/2026").
Fait : `tests_donnees.py` supprime le 21/09 ; `sql/01` a `sql/08` supprimes le 21/09 ;
dbt-duckdb en dependance d'execution le 01/10. La numerotation ne survit que dans le
prefixe `00_` des scripts d'ingestion.

## Dette de nommage - soldee le 29/09/2026

`stg_mutations_filtrees` dependait d'un modele `int_`, ce qui inversait la
convention dbt - staging, puis intermediaire, puis marts.
Le nom ne pouvait pas changer le 11/09/2026 : il devait correspondre a
`main.stg_mutations_filtrees` pour que `comparer()` fonctionne.
Renommé `int_mutations_filtrees` le 29/09, apres la bascule. Le remplacement
global du meme jour avait aussi reecrit ce paragraphe : texte retabli le 23/10.

## Controle freshness

Age du chargement : mesure. 'charge_le' dit quand l'entrepot a ete reconstruit.
Age du fichier : non mesure. Un fichier telecharge le 15 aout peut avoir ete charge ce matin.
Age du millesime : non mesure, et c'est celui vraiment interessant. Savoir si on tourne sur la derniere livraison 
publiee exige de consulter data.gouv.fr, ce qu'aucun controle de fraicheur ne sait faire.
Depuis le 05/10, la version est declaree : les empreintes de docs/empreintes_attendues.txt font echouer le telechargement
sur toute autre version, et la CI le verifie chaque lundi.
Consequence pratique : collateral.load (ex-build.py, renomme le 28/09) recharge les tables brutes a chaque execution, donc
le controle sera vert en permanence.
Il ne se declenchera que dans un seul cas - quelqu'un qui reprend le depot six mois plus tard sans savoir a quoi s'attendre.

## Renonce, etat au 23/10/2026

- Entrepot cloud. Motif d'origine : ne rentre pas avant l'echeance ; la volumetrie tient dans une base locale.
- Orchestration : revient au palier 2 de la roadmap, apres la S12.
- dbt-utils. Un paquet externe le mois de l'entretien est une variable en trop.
- Extension a d'autres departements. Le volume ne prouverait rien de plus.
- Optimisation du glissant (defauts 2 et 3 ci-dessous) et `--warn-error-options`.

Historique : section ouverte sous le titre "Ecarte d'ici le 10 octobre" ; les snapshots
en sont sortis le 13/10 (`snap_cog_communes`). `dim_commune` ne lit pas encore 
cet historique ; voir `docs/modelisation.md`, "Ecart".

## Defauts connus des modeles a porter - releves le 17/09/2026

Portage fidele d'abord : la regle 9 interdit qu'un refactoring change le
resultat. Correction apres la bascule (S7), jamais pendant.

| Modele | Defaut | Repere le | Correction |
|---|---|---|---|
| agg_prix_m2_glissant | jointure vers dim_commune sans effet : la colonne selectionnee existe deja | 24/08 | S7 |
| agg_prix_m2_glissant | 'mois - INTERVAL 11 MONTH' force un CAST vers TIMESTAMP sur 468 775 lignes | 01/09 | S7 |
| agg_prix_m2_glissant | sous-requete scalaire pour 'fenetre_complete' : DuckDB ajoute un garde-fou d'unicite | 24/08 | S7 |
| mart_prix_m2_reference | seuil de publication 5 en dur dans le SQL | 27/08 | S7, via '{{ var()}}' |
| ref_seuils_dispersion | 'current_date' rend la table non deterministe | 11/09 | S7 |
| ref_seuils_dispersion | aucun modele ne la consomme | 26/08 | a trancher au J4 |

Statut au 23/10/2026 : jointure vers `dim_commune` absente du modele actuel (le glissant lit l'etoile depuis le 12/10) ;
`INTERVAL` et sous-requete scalaire toujours presents, renonces avec l'optimisation du glissant ; seuil de publication en
`var('seuil_publication')` depuis le 28/09 ; `current_date` retire en portage (aucune fonction instable : controle par le rituel) ;
`ref_seuils_dispersion` gardee comme feuille assumee, decision du 19/09.

## Scripts sans equivalent modele
sql/00_raw_*.sql reste Python - ingestion, par la frontiere du 8 septembre.
sql/01 a sql/08 portes, supprimes le 21/09.
sql/analyses/ (6 fichiers) gardes - ils produisent des rapports, pas des relations. Un script de profilage n'a rien a faire dans un graphe de transformation.
sql/perf/ (6 fichiers) supprimes - dbt ecrit deja le SQL compile de chaque modele dans 'target/compiled', qui est exactement ce que ces copies contenaient. Ils sont perimes depuis le portage.
src/collateral/plan.py, mesure.py, profil.py gardes - outil de diagnostic, pas des transformations.

## Etat au 21/09/2026
Le 21/09/2026, la chaîne Python de transformation a été supprimée après quatre
semaines de fonctionnement en parallèle. Neuf modèles sur dix ont été prouvés
identiques par signature avant suppression ; le dixième n'avait pas d'équivalent. La
signature du mart, 104679694271579681982287, est la même avant et après.
'collateral.build' ne construit plus rien - il charge les sources brutes. Son nom ment
depuis ce matin.

## Figer les dependances directes et transitives
Versions exactes de toutes les dependances, directes et transitives.
Pourquoi pas uniquement les directes ? Risque qu'une version tierce casse dbt en CI, un jour, sans changement. Ce qui n'est pas declare derive.
Genere le 01/10/2026 par : python -m pip freeze --exclude-editable
Usage : pip install -e ".[dev]" -c constraints.txt
A regenerer dans le meme commit que tout changement dans pyproject.toml.