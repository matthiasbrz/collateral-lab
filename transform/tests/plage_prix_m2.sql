-- Attendu : 0 ligne. Chaque prix retenu est dans les bornes d'ecretage.
-- Porte depuis tests/donnees/03_plage_prix_m2.sql le 21/09.
SELECT f.id_mutation, f.prix_m2, s.seuil_bas, s.seuil_haut
FROM {{ ref('stg_mutations_filtrees') }} f
CROSS JOIN {{ ref('ref_seuils_prix_m2') }} s
WHERE f.prix_m2 < s.seuil_bas
    OR f.prix_m2 > s.seuil_haut
    OR f.prix_m2 IS NULL