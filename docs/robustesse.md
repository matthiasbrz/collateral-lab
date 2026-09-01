Rupture | Probabilité | Comportement actuel
Téléchargement interrompu | élevée | fichier partiel écrit à l'emplacement final, puis ignoré à vie par le test d'idempotence
Base verrouillée par une autre session | élevée | duckdb.IOException brute, aucune indication
Script SQL en échec au milieu de la chaîne | moyenne | erreur DuckDB sans le nom du fichier fautif
Colonne absente après la livraison d'octobre | certaine en S10 | Binder Error au script 02
Source indisponible (data.gouv, Insee) | faible | trace de pile urllib

## Ce qui reste fragile :
- Aucune liste déclarée des tables attendues. Un script SQL supprimé n'est pas une absence détectée, juste un fichier de moins. Constaté hier sur la panne (b).
- Aucune détection de schéma modifié. La livraison DVF d'octobre peut renommer ou retirer une colonne : la chaîne s'arrêtera sur un "Binder Error" au script 02, sans indiquer laquelle.
- Le seuil de taille est globale, pas par fichier. Si "build" casse au script 05, les tables 00 à 04 restent en base : l'état est intermédiaire, ni ancien ni neuf.
- Le millésime COG est en dur dans l'URL comme dans le nom de fichier.