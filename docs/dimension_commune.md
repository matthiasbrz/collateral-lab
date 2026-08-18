# Dimension commune - Règles

## 1. Source et millésime
Code officiel geographique Insee, millesime 2026

## 2. Règles
TYPECOM = 'COM'
communes de plein exercice uniquement, les communes déléguéees, associées et les arrondissements municipaux sont ici hors question directrice.
34875 communes

## 3. Taux sur les deux tables
stg_mutations_filtrees : 46655 mutations, 46650 appariées, taux: 99.99%
stg_mutations : 66151 mutations, 66145 appariées, taux: 99.99%
1 code non apparié sur 708, 6 mutations sur 66 151, cause identifiée et sourcée.
Oissel, Quiberville et Trouville sont non appariés dû à un renommage de commune (le code reste identique).
Morville-sur-Andelle correspond à une fusion avec l'ancienne commune 'Le Héron'.

# 4. Liste des non appariés
 code_commune  │       nom_dvf        │         nom_cog         │ mutations │
│   varchar    │       varchar        │         varchar         │   int64   │
├──────────────┼──────────────────────┼─────────────────────────┼───────────┤
│ 76484        │ Oissel               │ Oissel-sur-Seine        │       291 │
│ 76515        │ Quiberville          │ Quiberville-sur-Mer     │        34 │
│ 76715        │ Trouville            │ Trouville-Alliquerville │        23 │
│ 76455        │ Morville-sur-Andelle │ Morville-le-Héron       │        13 │

  code_commune │ nom_dvf  │  premiere  │  derniere  │ mutations │
│   varchar    │ varchar  │    date    │    date    │   int64   │
├──────────────┼──────────┼────────────┼────────────┼───────────┤
│ 76358        │ Le Héron │ 2023-06-14 │ 2025-09-02 │         6	