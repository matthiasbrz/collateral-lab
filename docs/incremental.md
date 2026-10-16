Conception du 16/10/2026 ; rien n'est encore construit.

## Ce qu'une livraison change
Les fichiers mis a disposition font l’objet d’une mise a jour semestrielle, en avril et en octobre.
Chaque mise a jour supprime puis remplace la totalite des fichiers precedemment publies.
Point d’attention : les fichiers sont alimentes par les donnees saisies dans les services de la publicite fonciere de la DGFiP et a chaque mise a jour de nouvelles transactions sont susceptibles d’être ajoutees dans tous les millesimes en fonction de la date de mutation.

## L'unite de remplacement : la mutation ou le millesime
`stg_mutations` a une ligne par `id_mutation`, et il y a un fichier geolocalise par annee (`dvf_76_2023.csv.gz`, etc.).
Seul le millesime voit une vente disparue, possibilite de comparer entre version N et N-1.

## La détection
Aujourd'hui, l'information n'arrive pas jusqu'a l'entrepot.
`00_raw_mutations.sql` recharge tous les fichiers en `SELECT *, now() AS charge_le`. `charge_le` change a chaque chargement, il ne peut donc rien detecter.
`raw_mutations` ne sait pas de quel fichier vient une ligne. DuckDB fournit une colonne virtuelle `filename` depuis sa version 1.3, mais `SELECT *` ne la ramene pas (verifie sur la 1.5.5)
Les empreintes restent cote Python (`docs/empreintes_attendues.txt`, controlees par `download`), et tout fichier modifie est aujourd'hui refuse avec "Nouvelle livraison DVF probable".
Hypothese a mesurer sur la vraie livraison : l'empreinte d'un `.gz` change aussi quand seule la date de compression inscrite dans l'en-tete gzip change.

## Le placement
La chaine : 
 - `stg_mutations`, le regroupement des lignes brutes, qui fait l'essentiel du calcul ;
 - `int_mutations_perimetre`, les regles 1 a 5, un simple filtre de lignes ; 
 - `ref_seuils_prix_m2`, les seuils p1/p99 calcules sur tout le perimetre, en une seule ligne ;
 - `int_mutations_filtrees`, qui croise chaque mutation avec ces seuils (`CROSS_JOIN`).
Tout ce qui est en aval des seuils depend de tous les millesimes.

## La preuve
Sur une meme entree, l'incremental egale le full refresh, par signature, suppressions comprises. Et la strategie naive doit echouer sur cette meme entree.

## Les seuils
La limite de `docs/limites.md` est ouverte depuis le 26/08, et `ref_seuils_prix_m2.sql` l'annonce : "Le figement reel des bornes par millesime est l'affaire de la semaine 10".
Le choix est de figer les seuils par millesime : la definition change, la signature aussi.

## Ce qu'on n'attend pas de l'incremental
Aucun gain de temps a cette volumetrie, seulement l'exactitude.