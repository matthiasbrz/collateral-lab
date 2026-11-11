# Robustesse de la chaîne

État au 11/11/2026 : ce que fait la chaîne quand une étape casse. Le relevé d'origine, antérieur au 01/09/2026, suit, conservé tel quel.

| Rupture | Comportement actuel | Depuis |
|---|---|---|
| Téléchargement interrompu | écrit en `.partiel`, renommé en fin de course : jamais de fichier partiel à l'emplacement final | 01/09 |
| Source indisponible (data.gouv, Insee) | arrêt avec l'URL, la cause et le geste à faire | 01/09 |
| Fichier tronqué ou illisible | refusé avant lecture : taille minimale, gzip décompressé en entier, en-tête du COG | 01/09 |
| Base verrouillée par une autre session | arrêt avec la cause et les sessions à fermer | 01/09 |
| Script SQL en échec | arrêt avec le nom du script et l'erreur DuckDB | 01/09 |
| Nouvelle livraison DVF | refusée par les empreintes SHA-256 déclarées : le passage du lundi échoue sur elle | 05/10 |
| Colonne retirée de tous les fichiers | refusée d'abord par les empreintes ; une fois déclarée, `stg_mutations` échoue s'il la lit | 05/10 |
| Incrémental différent du full refresh | la simulation d'une livraison échoue, code 1, à chaque construction en CI | 11/11 |
| Chaîne orchestrée lancée sur une base existante | refusée par sa première étape, `base_neuve` | 07/11 |

## Ce qui reste fragile, au 11/11/2026

- Un chargement interrompu laisse un état intermédiaire : les scripts `sql/00_*.sql` s'exécutent l'un après l'autre, sans transaction commune.
- Une colonne retirée ou renommée dans une partie des fichiers y passe en NULL (`union_by_name`) : seules les colonnes testées `not_null` l'arrêtent.
- Le millésime du COG est en dur dans l'URL de l'Insee : le COG 2027 demandera une nouvelle URL, puis une nouvelle empreinte.
- La signature du mart n'est pas comparée en CI (constat accepté) : seuls le rituel et la chaîne orchestrée la comparent.
- Le passage du lundi part avec 7 à 9 h de retard (constat ouvert) : une livraison se voit le lundi, pas à l'heure.
- La vraie livraison n'est pas encore passée : `docs/incremental.md` liste ce qui reste à mesurer.

## Relevé d'origine, antérieur au 01/09/2026

Rupture | Probabilité | Comportement au relevé
|---|---|---|
Téléchargement interrompu | élevée | fichier partiel écrit à l'emplacement final, puis ignoré à vie par le test d'idempotence
Base verrouillée par une autre session | élevée | duckdb.IOException brute, aucune indication
Script SQL en échec au milieu de la chaîne | moyenne | erreur DuckDB sans le nom du fichier fautif
Colonne absente après la livraison d'octobre | certaine en S10 | Binder Error au script 02
Source indisponible (data.gouv, Insee) | faible | trace de pile urllib

### Fragilités relevées alors :
- Aucune liste déclarée des tables attendues. Un script SQL supprimé n'est pas une absence détectée, juste un fichier de moins. Constaté hier sur la panne (b).
- Aucune détection de schéma modifié. La livraison DVF d'octobre peut renommer ou retirer une colonne : la chaîne s'arrêtera sur un "Binder Error" au script 02, sans indiquer laquelle.
- Le seuil de taille est globale, pas par fichier. Si "build" casse au script 05, les tables 00 à 04 restent en base : l'état est intermédiaire, ni ancien ni neuf.
- Le millésime COG est en dur dans l'URL comme dans le nom de fichier.