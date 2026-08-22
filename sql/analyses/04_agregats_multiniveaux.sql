-- sql/analyses/04_agregats_multiniveaux.sql
-- Question : prix median par commune, par type de bien, et tous niveaux confondus, en une seule passe sur les donnees.
SELECT
    coalesce(d.nom_commune, '— toutes communes —') AS commune,
    coalesce(f.type_local,  '— tous types —')      AS type_bien,
    count(*)                                       AS nb_mutations,
    round(quantile_cont(f.prix_m2, 0.5), 0)        AS prix_m2_median,
    grouping(d.nom_commune)                        AS agrege_sur_commune,
    grouping(f.type_local)                         AS agrege_sur_type
FROM stg_mutations_filtrees f
LEFT JOIN dim_commune d USING (code_commune)
GROUP BY GROUPING SETS ((d.nom_commune, f.type_local), (d.nom_commune), (f.type_local), ())
ORDER BY agrege_sur_commune, agrege_sur_type, nb_mutations DESC