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

## Sources

Notaires de l'Eure et de la Seine-Maritime, [dossier de presse immobilier 2025](https://ci-eureseinemaritime.notaires.fr/storage/file_manager_files/2026/01/dossier-de-presse-immobilier-notaires-2025-002.pdf),
publié en octobre 2025 selon le document, consulté le 24/10/2026. Base immobilière Perval.
Prix médians, « hors droits, hors commissions, hors frais et hors mobilier ».
Ventes du 01/07/2024 au 30/06/2025.

| Cellule | Chiffre publié | Nature |
|---|---|---|
| Rouen, appartements | 2 640 €/m² | médiane du prix au m², appartements anciens |
| Le Havre, appartements | 2 170 €/m² | médiane du prix au m², appartements anciens |
| Le Havre, maisons | non publié | la liste des maisons anciennes donne 30 communes, de 395 000 € à 194 000 € ; Le Havre n'y figure pas |

Les médianes départementales du dossier (2 200 €/m², 180 000 €) ne sont pas comparées :
le protocole compare des communes.

## Comparaison

Écart = (projet − publié) / publié. Fenêtre du projet : la glissante qui finit le même mois
que la période publiée, règle du protocole, soit juin 2025.

| Cellule | Fenêtre du projet | Projet (ventes) | Publié | Écart | Verdict |
|---|---|---|---|---|---|
| Rouen, appartements | 12 mois à fin juin 2025 | 2 639 €/m² (1819 ventes) | 2 640 €/m² | -0,0 % | dans la tolérance |
| Le Havre, appartements | 12 mois à fin juin 2025 | 2 208 €/m² (1546 ventes) | 2 170 €/m² | +1,8 % | dans la tolérance |
| Le Havre, maisons | — | — | non publié | — | non comparable |

## Écarts de périmètre

- Période : identique. La fenêtre du projet qui finit en juin 2025 couvre les mêmes douze mois ;
  la fenêtre par défaut du protocole, décembre 2025, n'est donc pas celle comparée.
- Base : Perval, alimentée par les notaires, contre DVF, tous les actes enregistrés.
  L'exhaustivité de Perval n'est pas documentée par la source.
- Ancien : la source publie l'ancien, et le neuf à part. Le projet écarte la VEFA
  (3 214 mutations en 2023-2025, nature distincte de « Vente ») mais garde un logement récent
  vendu après achèvement. La définition de l'ancien n'est pas documentée par la source.
- Surface : habitable côté notaires, d'après les tableaux de ventes d'exception ; surface réelle
  bâtie côté DVF. La source ne dit pas quelle surface entre dans sa médiane au m².
- Prix : hors droits, commissions, frais et mobilier côté notaires ; valeur foncière de l'acte
  côté DVF, dépendances de la même mutation comprises, ce qui majore légèrement le prix au m²
  d'un bien avec dépendance.
- Écrêtage : le projet écarte les prix au m² hors des centiles 1 et 99 de son périmètre
  (règle 6) ; la source ne documente aucun écrêtage.

## Refaire la comparaison

Côté projet, une cellule : `SELECT prix_m2_median_12m, nb_mutations_12m FROM dbt.mart_prix_m2_reference
WHERE code_commune = '76540' AND type_local = 'Appartement' AND mois = DATE '2025-06-01'`.
