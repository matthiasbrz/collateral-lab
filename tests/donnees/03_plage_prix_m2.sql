-- tests/03_plage_prix_m2.sql
SELECT f.id_mutation, f.prix_m2, s.seuil_bas, s.seuil_haut
FROM stg_mutations_filtrees f
CROSS JOIN ref_seuils_prix_m2 s
WHERE f.prix_m2 < s.seuil_bas
OR f.prix_m2 > s.seuil_haut
OR f.prix_m2 IS NULL; 