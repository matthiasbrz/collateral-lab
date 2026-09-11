-- Grain : une mutation retenue dans le perimetre de la question directrice.
-- Regles et volume ecartes : docs/regles_filtrage.md
--
-- Les regles 1 a 5 sont dans int_mutations_perimetre.
-- Ce modele n'applique que la regle 6 : l'ecretage aux bornes p1/p99.

SELECT
    p.*,
    date_trunc('month', p.date_mutation)::DATE AS mois,
    year(p.date_mutation) AS annee,
    quarter(p.date_mutation) AS trimestre
FROM {{ ref('int_mutations_perimetre') }} p
CROSS JOIN {{ ref('ref_seuils_prix_m2') }} s
WHERE p.prix_m2 BETWEEN s.seuil_bas AND s.seuil_haut