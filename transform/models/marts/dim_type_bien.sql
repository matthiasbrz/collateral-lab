-- Grain : un type de bien du perimetre (regle 4). Arbitrage du 09/10.
-- La liste autorisee est une donnee, rangee ici. VALUES plutot qu'un seed :
-- un .csv versionne fait echouer la section 5 du rituel (regle 4).

SELECT type_local, ordre_affichage
FROM (VALUES
    ('Maison', 1),
    ('Appartement', 2)
) AS t(type_local, ordre_affichage)