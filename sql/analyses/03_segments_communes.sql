-- sql/analyses/03_segments_communes.sql
-- Question : comment segmenter les communes en gammes de prix comparables ?
-- Note : NTILE découpe en groupes de taille égale, pas en tranches de valeurs de valeur égale. Deux communes à 2480 et 2490€/m² peuvent tomber de part et d'autre d'une frontière.
-- Surtout, la frontière bouge à chaque rafraichissement des données : une commune peut changer de segment sans que son prix ait varié d'un euro, simplement parce que les autres ont bougé.
-- Un segment défini par rang de population est instable ; un segment défini par des seuils fixes et stable et opposable.
SELECT
    code_commune,
    nom_commune,
    type_local,
    prix_m2_median_12m,
    nb_mutations_12m,
    ntile(4) OVER (PARTITION BY type_local ORDER BY prix_m2_median_12m) AS quartile,
    CASE ntile(4) OVER (PARTITION BY type_local ORDER BY prix_m2_median_12m)
        WHEN 1 THEN 'Accessible'
        WHEN 2 THEN 'Intermediaire bas'
        WHEN 1 THEN 'Intermediaire haut'
        WHEN 1 THEN 'Premium'
    END AS segment
FROM mart_prix_m2_reference
WHERE mois = (SELECT max(mois) FROM mart_prix_m2_reference)
ORDER BY type_local, prix_m2_median_12m DESC

SELECT type_local, quartile, count(*) AS communes,
    min(prix_m2_median_12m) AS borne_basse,
    max(prix_m2_median_12m) AS borne_haute
FROM (SELECT
    code_commune,
    nom_commune,
    type_local,
    prix_m2_median_12m,
    nb_mutations_12m,
    ntile(4) OVER (PARTITION BY type_local ORDER BY prix_m2_median_12m) AS quartile,
    CASE ntile(4) OVER (PARTITION BY type_local ORDER BY prix_m2_median_12m)
        WHEN 1 THEN 'Accessible'
        WHEN 2 THEN 'Intermediaire bas'
        WHEN 1 THEN 'Intermediaire haut'
        WHEN 1 THEN 'Premium'
    END AS segment
FROM mart_prix_m2_reference
WHERE mois = (SELECT max(mois) FROM mart_prix_m2_reference)
ORDER BY type_local, prix_m2_median_12m DESC;)
GROUP BY 1, 2 ORDER BY 1, 2