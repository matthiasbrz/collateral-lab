SELECT count(*) AS lignes, sum(hash(t)) AS signature
FROM mart_prix_m2_reference t;