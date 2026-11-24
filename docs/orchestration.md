# Orchestration : comment la chaîne tombe

Etat au 24/11/2026 : trois pannes provoquées sous Dagster, une par étage, lues dans les journaux. Aucun montage ne touche au code de `main` ni aux empreintes. Après les pannes n°2 et 3, base neuve : `11383 104651625292808720823545`. Ce document complète [Robustesse de la chaîne](robustesse.md), qui dit ce que fait chaque étape quand elle casse : il ne le répète pas.

| Panne | Date | Statut | Etape fautive | Etapes en aval | Code de sortie | Ligne du journal qui dit pourquoi | Etat après la chute |
|---||---||---||---||---||---||---||---|
| n°1, en bout de chaîne : l'étalon faux | 13/11 | échec (`RUN_FAILURE`) | `controler` | aucune, c'est la dernière ; les cinq autres réussies | 1 | `RuntimeError: signature modifiée : attendue 11383 104651625292808720823546, obtenue 11383 104651625292808720823545`, dans le message de Dagster, après le traceback | base construite (71 PASS, 3 WARN), données justes, étalon faux |
| n°2, au milieu : un test dbt en échec | 19/11 | échec (`RUN_FAILURE`) | `construire` | `controler` non lancée | 1 | `[ERROR]: in test accepted_values_dim_type_bien_type_local__Maison (models\marts\etoile.yml) Got 1 result, configured to fail if != 0`, dans la sortie de dbt | base entière (PASS=70 WARN=3 ERROR=1 SKIP=0 : aucun modèle ne lit `dim_type_bien`, signature non contrôlée) |
| n°3, en tête : le téléchargement impossible | 23/11 | échec (`RUN_FAILURE`) | `telecharger` | `charger`, `capturer`, , `construire`, `controler` non lancées | 1 | `telechargement impossible depuis https://files.data.gouv.fr/geo-dvf/latest/csv/2025/departements/76.csv.gz` puis `cause : <urlopen error [Errno 11001] getaddrinfo failed>` et `que faire : verifier votre connexion, puis relancez python -m collateral.download`, dans la sortie du téléchargement | aucune base ; les quatre autres fichiers bruts intacts, aucun `.partiel` |

## Ce que les pannes montrent

 - Aucune étape en aval n'a été lancée après une chute, et le code de sortie a été 1 les trois fois.
 - La cause de `controler` est dans le message de Dagster, mais derrière une vingtaine de lignes de traceback, répétées dans `STEP_FAILURE` et `RUN_FAILURE` : retrouvée à froid en 5 min le 17/11, pour une minute visée. Défaut ouvert le 17/11 ; correction prévue en S16, vérifiée en reprovoquant la panne n°1.
 - Pour une étape qui lance une commande, le message de Dagster ne dit que `CalledProcessError` et le code de retour de la commande ; la cause est dans la sortie de la commande, juste au-dessus de l'échec dans le terminal, et dans les journaux de l'étape. Vu sur `construire` (n°2) et `telecharger` (n°3) ; `charger` et `capturer` lancent leur commande de la même façon. Lue à chaud en 1 min 30 et en 45 s ; à froid le 24/11 : 1 min (n°2) et 1 min (n°3). Constat ouvert le 23/11 : ce n'est pas la correction de `controler`.
 - La panne n°3 confirme sous Dasgter la ligne "Source indisponible" de [Robustesse de la chaîne](robustesse.md). Elle ne test pas la ligne "Téléchargement interrompu" : le réseau était coupé avant le lancement, le téléchargement n'a pas commencé.

## Montages

 - n°1 : l'étalon `docs/signature_attendue.txt` faussé sur une branche jetable, supprimée sans fusion.
 - n°2 : dans `transform/models/marts/etoile.yml`, `values: ['Maison', 'Appartement']` réduit à `['Maison', 'Appartement']` sur une branche jetable, supprimée sans fusion.
 - n°3 : sans branche ni code : un fichier DVF de `data/raw` déplacé hors du dépôt, réseau coupé, puis le fichier remis avant le réseau ; empreintes conformes ensuite.