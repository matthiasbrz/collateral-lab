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

## Prérequis
Python 3.12.10,
pip install -r requirements.txt
python src/download.py
python src/build.py

## Comparatif p99 lignes vs. mutations
p99 à 12 600 000 € au grain ligne, 955 500 € au grain mutation.
Le fait d'avoir un prix reproduit sur chaque ligne d'une même mutation faisait exploser le quantile 99%.
Après nettoyage et définition du grain (une ligne = une mutation), une valeur cohérente est obtenue.

## Dispersion et instabilité
Le volume mesure la confiance dans l'estimation. La dispersion mesure l'hétérogénéité du marché sous-jacent. Ce sont deux questions différentes, et elles peuvent pointer en sens inverse.
Filtrer sur la dispersion supprimerait les grandes villes.

## Limites connues

1. **Périmètre de la source.** DVF ne couvre ni l'Alsace-Moselle ni Mayotte. Sans effet sur la Seine-Maritime, bloquant pour toute extension nationale.
2. **Décalage de publication.** Deux millésimes par an, en avril et en octobre, avec un délai d'environ six mois entre la signature de l'acte et sa parution.
3. **Biais de composition.** Le prix médian bouge quand la composition des ventes change, pas seulement quand les prix bougent. Mesuré : le volume d'appartements a varié de -10 % puis +11 % entre 2023 et 2025.
4. **Aucune qualification du bien.** Ni état, ni étage, ni extérieur, ni performance énergétique. Deux biens au même prix au m² ne sont pas comparables.
5. **Convention sur les dépendances.** Le garage entre au numérateur, pas au dénominateur. Le prix au m² d'une maison avec dépendance est donc légèrement majoré.
6. **Référentiel géographique en retard.** Mesuré : le code 76358 porte des mutations jusqu'au 02/09/2025 alors que la commune a disparu au 01/01/2025.
7. **Seuils recalculés à chaque exécution.** Les bornes p1/p99 dépendent des données présentes : une valeur historique peut changer après une nouvelle livraison.
8. 5318 cellules sur 11383, soit 47 % de la publication, reposent sur 5 à 9 transactions.

## Reproduire

Prérequis : Python 3.12 et Git.

```powershell
git clone https://github.com/matthiasbrz/collateral-lab.git
cd collateral-lab
py -m venv .venv ; .\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

Puis :

```powershell
python -m collateral.download # sources dvf et référentiel COG, ~8 Mo
python -m collateral.build # consruit l'entrepot, affiche la signature
```

Vérifier :

```powershell
python -m collateral.tests_donnees # 6 tests de données
pytest # 16 tests unitaires
```

Aucune étape manuelle. Aucune donnée versionnée : 'data/' et '*.duckdb' sont exclus, et le '.gitignore' a été écrit avant le premier téléchargement.