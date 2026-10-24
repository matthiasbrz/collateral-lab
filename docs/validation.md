# Validation externe : les prix publiés par les notaires

## Protocole, déclaré le 24/10/2026 avant toute lecture des chiffres des notaires

- Cellules, choisies par une seule règle (les deux marchés d'appartements et le marché de maisons au plus fort volume du mart, fenêtre de décembre 2025) :
  - Rouen (76540), appartements, 1921 ventes ;
  - Le Havre (76351), appartements, 1687 ventes ;
  - Le Havre (76351), maisons, 760 ventes.
- Fenêtre : 12 mois glissants à fin décembre 2025. Si la publication porte sur une autre période, la fenêtre glissante qui finit le même mois ; l'écart restant est noté.
- Mesure : la médiane du prix au m² (`prix_m2_median_12m`). Pour les maisons, si le chiffre publié est un prix en euros, la médiane de `valeur_fonciere` du projet sur la même fenêtre, même tolérance. Tout autre chiffre (moyenne, autre type de bien) : « non comparable », avec la raison.
- Tolérance : écart relatif |projet − publié| / publié ≤ 10 %.
- Raison : les deux chiffres ne mesurent pas exactement la même chose. Différences possibles, connues avant de regarder et à vérifier dans leur note de méthode : base exhaustive des actes (DVF) contre base des notaires ; surface réelle bâtie contre surface habitable ; valeur foncière qui inclut les dépendances de la mutation ; logements récents gardés par le projet si les notaires ne publient que l'ancien ; écrêtage p1/p99 du projet. Chacune peut déplacer une médiane de quelques pour cent. 10 % laisse la place à leur cumul et reste un vrai test : une erreur d'unité, de surface ou de périmètre le ferait échouer.
- Bruit d'échantillonnage du projet, mesuré à part (IC 95 % de la médiane, rangs binomiaux) : ± 2,3 %, ± 2,6 %, ± 3,0 %. Il doit rester petit devant la tolérance.
- Verdict par cellule : dans la tolérance, hors tolérance, ou non comparable. Résultat publié tel quel.