-- Attendu : 0 ligne.
-- Exactement une ligne, bornes strictement positives et strictement ordonnees.

SELECT
    count(*) AS nb_lignes,
    min(seuil_bas) AS seuil_bas,
    min(seuil_haut) AS seuil_haut,
    min(mutations_perimetre) AS perimetre
FROM {{ ref('ref_seuils_prix_m2') }}
HAVING count(*) <> 1
    OR min(seuil_bas) <= 0
    OR min(seuil_haut) <= min(seuil_bas)
    OR min(mutations_perimetre) <= 0