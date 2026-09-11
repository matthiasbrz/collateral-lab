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

## Bascule

Condition : les neuf modeles portes, chaque signature identique a son
equivalent Python. Prevu en semaien 5.
A la bascule : suppression de tests_donnees.py, de la numerotation des
scripts, et passage de dbt-duckdb en dependance de production.

## Dette de nommage

"stg_mutations_filtrees" dépend désormais d'un modèle "int_", ce qui inverse la convention dbt - staging, puis intermédiaire, puis marts.
Le nom ne peut pas changer aujourd'hui (11/09/2026) : il doit correspondre à "main.stg_mutations_filtrees" pour que "comparer()" fonctionne.
Il changera à la bascule, quand les noms Python disparaîtront.