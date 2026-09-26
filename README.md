# collateral-lab

Pour une commune et un type de bien, quelle est la valeur de référence au m², comment a-t-elle evolué sur 12 mois, et avec quelle fiabilité ?

**Rouen, appartements : 2 664 €/m²** — médiane sur les 12 mois à fin décembre 2025,
calculée sur 1 921 ventes. Évolution sur un an : +0,6 %.
*Données DVF, millésime d'avril 2026.*

## Pourquoi c'est juste

- **Reproductible** — un clone neuf rejoue toute la chaine et vérifie le resultat
  en une commande : [`scripts/verif_clone.ps1`](scripts/verif_clone.ps1).
- **Non-regressif** — la signature du mart est fixée depuis le 28/08/2026 et a
  traversé un changement complet d'outil : [`docs/signature_attendue.txt`](docs/signature_attendue.txt).
- **Teste** — 44 tests de données au 26/09/2026, dont un qui rend exécutable la règle de
  publication : [`transform/`](transform/).
- **Documente** — catalogue et graphe de lignee publiés :
  [matthiasbrz.github.io/collateral-lab](https://matthiasbrz.github.io/collateral-lab/).

## Lancer

    py -m venv .venv ; .\.venv\Scripts\Activate.ps1 ; pip install -e ".[dev]"
    python -m collateral.download ; python -m collateral.build
    cd transform ; dbt build --profiles-dir .

*Commandes PowerShell. Sous macOS ou Linux : `python3 -m venv .venv` et `source .venv/bin/activate`.*

## En savoir plus

**Conception**
- [Architecture et frontière Python / dbt](docs/architecture.md)
- [Règles de filtrage et volumes écartés](docs/regles_filtrage.md)
- [Référentiel des communes](docs/dimension_commune.md)

**Fiabilité**
- [Gouvernance des données](docs/gouvernance.md)
- [Limites connues](docs/limites.md)
- [Robustesse du téléchargement](docs/robustesse.md)

**Mesures**
- [Profilage des sources](docs/profilage.md)
- [Performance de la chaîne](docs/performance.md)