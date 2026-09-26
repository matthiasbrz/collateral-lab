# collateral-lab

Pour une commune et un type de bien, quelle est la valeur de reference au m², comment a-t-elle evolue sur 12 mois, et avec quelle fiabilite ?

**Rouen, Appartement : 2664 €/m²** - mediane sur les 12 mois a fin decembre, calculee sur 1921 ventes. Evolution sur un an : 0.6 %.
*Donnees DVF, millesime d'avril 2026.*

## Pourquoi c'est juste

- **Reproductible** — un clone neuf rejoue toute la chaine et verifie le resultat
  en une commande : [`scripts/verif_clone.ps1`](scripts/verif_clone.ps1).
- **Non-regressif** — la signature du mart est fixee depuis le 28/08/2026 et a
  traverse un changement complet d'outil : [`docs/signature_attendue.txt`](docs/signature_attendue.txt).
- **Teste** — 44 tests de donnees au 26/09/2026, dont un qui rend executable la regle de
  publication : [`transform/`](transform/).
- **Documente** — catalogue et graphe de lignee publies :
  [matthiasbrz.github.io/collateral-lab](https://matthiasbrz.github.io/collateral-lab/).

## Lancer

    py -m venv .venv ; .\.venv\Scripts\Activate.ps1 ; pip install -e ".[dev]"
    python -m collateral.download ; python -m collateral.build
    cd transform ; dbt build --profiles-dir .

*Commandes PowerShell. Sous macOS ou Linux : `python3 -m venv .venv` et `source .venv/bin/activate`.*

## En savoir plus

- [Architecture et frontiere Python / dbt](docs/architecture.md)
- [Gouvernance des donnees](docs/gouvernance.md)
- [Limites connues](docs/limites.md)
- [Regles de filtrage et volumes ecartes](docs/regles_filtrage.md)