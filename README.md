# collateral-lab

Observatoire du collatéral immobilier : mini-entrepôt analytique sur les transactions immobilières françaises, construit comme le ferait une banque pour valoriser et surveiller son collatéral.


## Question directrice

Pour une commune et un type de bien donnés, quelle est la valeur de référence au m², comment a-t-elle évolué sur 12 mois, et avec quel niveau de fiabilité (volume de transactions) ?

## Données

Demandes de valeurs foncières (DVF), DGFiP, publiée sur data.gouv.fr.
Licence Ouverte 2.0. Mise à jour semestrielle (avril et octobre).

Indicateur	            Mensuel	            Glissant 12 mois, seuil 5
Cellules exploitables	15,1 %	            52,6 %
Communes couvertes	    —	                79,2 % (559 / 706)
52 % des cellules mensuelles contiennent exactement une vente. Une médiane sur une transaction, c'est la transaction.

type_local    │ communes │ publiables │
├─────────────┼──────────┼────────────┤
│ Maison      │      706 │        423 │
│ Appartement │      160 │         54


## Schéma cible

Fait : mutation. Dimensions : date, géographie, type de bien, nature de mutation.
Le projet a détecté une fusion de communes par croisement de référentiels, huit mois avant que la source ne l'ait intégréé.

## Gouvernance : pourquoi aucune donnée n'est versionnée

Il ne doit pas être possible d'identifier un individu à partir des transactions seulement.
Les données doivent être traitées conformément au RGPD, un non-respect de ces lois entrainant des sanctions lourdes.
La collecte, le traitement et la protections de ces données doivent être démontrable.
Ces données ayant un caractère sensible, il est nécessaire de savoir qui utilise ces données et à quelle fin.

## Stack

Python, DuckDB, SQL, Git. dbt introduit en semaine 10.
duckdb==1.5.5
Python 3.12.10

## Comparatif p99 lignes vs. mutations
p99 à 12 600 000 € au grain ligne, 955 500 € au grain mutation.
Le fait d'avoir un prix reproduit sur chaque ligne d'une même mutation faisait exploser le quantile 99%.
Après nettoyage et définition du grain (une ligne = une mutation), une valeur cohérente est obtenue.