# collateral-lab

[![qualité du code](https://github.com/matthiasbrz/collateral-lab/actions/workflows/qualite.yml/badge.svg?branch=main)](https://github.com/matthiasbrz/collateral-lab/actions/workflows/qualite.yml)
[![construction et publication](https://github.com/matthiasbrz/collateral-lab/actions/workflows/publication.yml/badge.svg?branch=main)](https://github.com/matthiasbrz/collateral-lab/actions/workflows/publication.yml)

Pour une commune et un type de bien, quelle est la valeur de référence au m², comment a-t-elle evolué sur 12 mois, et avec quelle fiabilité ?

**Exemple de résultat — Rouen, appartements : 2 664 €/m²**, médiane sur les 12 mois
à fin décembre 2025, calculée sur 1 921 ventes — la cellule la plus fiable du
dernier mois. Évolution sur un an : +0,6 %. *Données DVF, millésime d'avril 2026.*

## Ce qui est vérifié

Le calcul fait exactement ce qui est spécifié, et le refait à l'identique.

- **Reproductible** — un clone neuf rejoue toute la chaine et vérifie le resultat
  en une commande : [`scripts/reproduction_clone_neuf.ps1`](scripts/reproduction_clone_neuf.ps1).
- **Non-regressif** — la signature du mart est fixée depuis le 28/08/2026 et a
  traversé un changement complet d'outil : [`docs/signature_attendue.txt`](docs/signature_attendue.txt).
- **Teste** — 60 tests de données au 23/10/2026, dont un qui rend exécutable la règle de
  publication : [`transform/`](transform/).
- **Documente** — catalogue et graphe de lignee publiés :
  [matthiasbrz.github.io/collateral-lab](https://matthiasbrz.github.io/collateral-lab/).

## Ce qui ne l'est pas

La valeur n'a pas de vérité de référence. Elle dépend des règles de filtrage
retenues et des limites des données DVF : délai de publication, biais de
composition, aucune qualification du bien. Ces choix sont chiffrés dans les
[règles de filtrage](docs/regles_filtrage.md) et les [limites connues](docs/limites.md).

Confrontée le 24/10/2026 aux prix publiés par les notaires de l'Eure et de la Seine-Maritime : <k> cellules sur 3 dans la tolérance de ±10 % déclarée avant comparaison ; <écart hors tolérance éventuel, tel quel> ([docs/validation.md](docs/validation.md)).

Confrontée le 24/10/2026 aux prix médians publiés par les notaires de l'Eure et de la
Seine-Maritime (base Perval, ventes du 01/07/2024 au 30/06/2025) : 2 sur 2 cellules
comparables dans la tolérance de ±10 % déclarée avant comparaison (Rouen, appartements -0,0 % ; Le Havre, appartements +1,8 %) ; la troisième
cellule du protocole, Le Havre maisons, n'est pas publiée par la source
([validation externe](docs/validation.md)).

## Lancer

Prérequis : Python 3.12 et un environnement virtuel actif.

- Windows (PowerShell) : `py -m venv .venv ; .\.venv\Scripts\Activate.ps1`
- macOS / Linux : `python3 -m venv .venv ; source .venv/bin/activate`

Puis, depuis la racine du dépôt :

<!-- lancer:debut -->
```
python -m pip install -e ".[dev]" -c constraints.txt
python -m collateral.download
python -m collateral.load
cd transform
dbt snapshot --vars "{millesime_snapshot: 2024}" --profiles-dir .
dbt build --profiles-dir .
```
<!-- lancer:fin -->

Ces commandes sont exécutées telles quelles par `scripts/reproduction_clone_neuf.ps1`,
et sous Linux par la CI à chaque fusion dans `main`, et chaque lundi pour détecter une nouvelle livraison DVF.

### Mettre à jour un environnement existant

`git pull` met à jour le code, pas la base : `collateral.duckdb` garde l'état de la dernière construction sur ce poste. Après un `git pull`, depuis la racine :

```
python -m pip install -e ".[dev]" -c constraints.txt
python -m collateral.download
python -m collateral.load
cd transform ; dbt build --profiles-dir . ; cd ..
.\scripts\etat_depot.ps1
```

Si `dbt build` échoue sur `stg_mutations`, le seul modèle incrémental :

- `Binder Error: Referenced column "empreinte_source" not found in FROM clause!` : la table existante date d'avant l'incrémental (19/10) ;
- `The source and target schemas on this incremental model are out of sync!` : le schéma du modèle a changé, et `on_schema_change: fail` refuse de l'ignorer ;

alors : `dbt build --full-refresh --select stg_mutations+`, puis le rituel, qui contrôle aussi les relations orphelines.

Poste resté longtemps sans construire, ou au moindre doute : base neuve. Elle ne contient que du dérivé (brut rechargé depuis des fichiers aux empreintes déclarées, modèles depuis le code, snapshot rejoué par le passage 2024). Supprimer la base et son WAL ensemble, jamais le WAL seul :

- Windows : `Remove-Item .\collateral.duckdb, .\collateral.duckdb.wal -ErrorAction SilentlyContinue`
- macOS / Linux : `rm -f collateral.duckdb collateral.duckdb.wal`

puis les commandes de « Lancer ». Appliqué le 22/10/2026 sur un poste dont la base datait du 17/10 : `Binder Error`, aucune relation orpheline, base neuve, signature retrouvée.

## En savoir plus

**Conception**
- [Architecture et frontière Python / dbt](docs/architecture.md)
- [Règles de filtrage et volumes écartés](docs/regles_filtrage.md)
- [Référentiel des communes](docs/dimension_commune.md)
- [Validation externe : les prix des notaires](docs/validation.md)

**Fiabilité**
- [Gouvernance des données](docs/gouvernance.md)
- [Limites connues](docs/limites.md)
- [Robustesse du téléchargement](docs/robustesse.md)

**Mesures**
- [Profilage des sources](docs/profilage.md)
- [Performance de la chaîne](docs/performance.md)