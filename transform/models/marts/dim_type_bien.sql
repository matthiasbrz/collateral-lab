-- Grain : un type de bien du perimetre (regle 4). Arbitrage du 09/10.
-- La liste autorisee est une donnee, rangee ici. VALUES plutot qu'un seed :
-- un .csv versionne fait echouer la section 5 du rituel (regle 4).
-- ordre_affichage retire le 20/10 : aucun lecteur, il reviendra avec son consommateur.

SELECT type_local
FROM (VALUES
    ('Maison'),
    ('Appartement')
) AS t(type_local)