-- Grain : une ligne par type de bien. Bornes de segmentation de la dispersion.
--
-- Feuille assumee : aucun modele ne la consomme. Elle documente les seuils
-- cites dans la section fiabilite du README. Decision du 19/09 : portee
-- plutot que supprimee, une documentation qui decrit un objet inexistant
-- etant pire qu'un objet inutile.
--
-- date_calcul retiree : meme defaut que ref_seuils_prix_m2, corrige le 18/09.

SELECT
    type_local,
    round(quantile_cont(dispersion_relative, 0.33), 3) AS borne_basse,
    round(quantile_cont(dispersion_relative, 0.67), 3) AS borne_haute,
    round(quantile_cont(dispersion_relative, 0.50), 3) AS mediane
FROM {{ ref('mart_prix_m2_reference') }}
GROUP BY type_local
    