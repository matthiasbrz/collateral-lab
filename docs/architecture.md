# Architecture

## Frontiere

Python amene la donnee jusqu'a l'entrepot et garantit qu'elle est complete.
dbt transforme ce qui est deja dans l'entrepot et prouve que le resultat tient.

La ligne de partage est l'entrepot : rien n'y entre par dbt, rien ne s'y
transforme par Python.

## Etat au 08/09/2026 - transition
    reseau                  disque                      entrepot DuckDB
    ------                  ------                      ---------------
    files.data.gouv.fr  --> data/raw/*.csv.gz   -->     main.raw_mutations
    insee.fr            --> data/raw/*.csv      -->     main.dim_commune
                                                             |
                            [ PYTHON ] ................... [ FRONTIERE ] .........
                                                             |
                                                        dbt.stg_mutations
                                                        dbt.stg_mutations_filtrees
                                                             |
                                                        (7 modeles restants,
                                                         encore dans main/)
                
Deux chaines coexistent volontairement pendant la transition, dans deux
schemas distincts. Chaque modele porte est prouve identique a son equivalent
Python par comparaison de signature, pas par relecture.

## Ce qui reste cote Python apres bascule

- telechargement des sources (reseau)
- controle d'integrite avant lecture (disque)
- chargement brut dans l'entrepot (sql/00_raw_mutations.sql, sql/01_raw_communes.sql)
- tests unitaires du code Python (pytest)

## Ce qui passe sous dbt

- grain, filtres, agregats, publication
- tests de donnees, generiques et singuliers
- documentation et lignes

## Decoupages imposes par la frontiere

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

## Bascule

Condition : les neuf modeles portes, chaque signature identique a son
equivalent Python. Prevu en semaien 5.
A la bascule : suppression de tests_donnees.py, de la numerotation des
scripts, et passage de dbt-duckdb en dependance de production.

## Dette de nommage

"stg_mutations_filtrees" depend desormais d'un modele "int_", ce qui inverse la convention dbt - staging, puis intermediaire, puis marts.
Le nom ne peut pas changer aujourd'hui (11/09/2026) : il doit correspondre a "main.stg_mutations_filtrees" pour que "comparer()" fonctionne.
Il changera a la bascule, quand les noms Python disparaitront.

## Controle freshness

Age du chargement : mesure. 'charge_le' dit quand l'entrepot a ete reconstruit.
Age du fichier : non mesure. Un fichier telecharge le 15 aout peut avoir ete charge ce matin.
Age du millesime : non mesure, et c'est celui vraiment interessant. Savoir si on tourne sur la derniere livraison 
publiee exige de consulter data.gouv.fr, ce qu'aucun controle de fraicheur ne sait faire.
Consequence pratique : 'build.py' recharge les table brutes a chaque execution, donc le controle sera vert en permanence.
Il ne se declenchera que dans un seul cas - quelqu'un qui reprend le depot six mois plus tard sans savoir a quoi s'attendre.

## Ecarte d'ici le 10 octobre, a reprendre ensuite

- Portage sur entrepot cloud et orchestration (paliers 2 et 3 du sujet initial).
  Motif : ne rentre pas avant l'echeance. A reeexaminer au point de controle 2.
- Snapshots dbt et SCD2 sur dim_commune, malgre le cas Morville-le-Heron.
  La dette est declaree par un seuil de test, elle tient jusque-la.
- dbt-utils. Un paquet externe le mois de l'entretien est une variable de trop.
- Extension a d'autres departements. Le volume ne prouverait rien de plus.