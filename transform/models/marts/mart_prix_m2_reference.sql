-- Grain : une cellule publiable = commune x type de bien x mois.
--
-- Couche de publication. Deux filtres, deux natures :
--  fenetre complete        : correctness - une fenetre tronquee n'est pas
--                            une glissante sur 12 mois.
--  nb_mutations_12m >= 5 : gouvernance ET fiabilite. Sous ce volume, un
--                          agregat redevient une transaction identifiable,
--                          et une mediane sur trois ventes n'est pas un prix
--                          de reference. Voir la section Gouvernance du README.
--
-- Le seuil 5 est en dur : dette inventoriee le 17/09, correction par
-- var() en semaine 7. Porte tel quel - regle 9.
--

SELECT 
    e.code_commune, 
    d.nom_commune, 
    e.type_local, 
    e.mois,
    e.prix_m2_median_12m, 
    e.prix_m2_q1_12m, 
    e.prix_m2_q3_12m,
    e.nb_mutations_12m, 
    e.evolution_pct, 
    e.ecart_interquartile, 
    e.dispersion_relative
FROM {{ ref('agg_prix_m2_evolution') }} e
LEFT JOIN {{ ref('dim_commune') }} d USING (code_commune)
WHERE e.fenetre_complete
    AND e.nb_mutations_12m >=5