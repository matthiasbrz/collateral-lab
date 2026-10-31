-- Attendu : 0 ligne. Aucune evolution publiee ne repose sur une fenetre N-1
-- tronquee ou sous le seuil de publication : a cote de la mediane publiee,
-- elle rendrait la mediane N-1 lisible, N-1 = N / (1 + evolution).
-- Constat du 28/10.

SELECT m.code_commune, m.type_local, m.mois, m.evolution_pct,
    n1.fenetre_complete AS fenetre_complete_n1,
    n1.nb_mutations_12m AS nb_mutations_12m_n1
FROM {{ ref('mart_prix_m2_reference') }} m
JOIN {{ ref('agg_prix_m2_glissant') }} n1
    ON n1.code_commune = m.code_commune
    AND n1.type_local = m.type_local
    AND n1.mois = m.mois - INTERVAL 12 MONTH
WHERE m.evolution_pct IS NOT NULL
    AND (NOT n1.fenetre_complete
        OR n1.nb_mutations_12m < {{ var('seuil_publication') }})