-- Chargement brut du Code officiel geographique. Aucune transformation.
-- Les types sont forces ici parce que c'est une exigence de fidelite au
-- chargement, pas un choix de modelisation : sans cela, 01001 devient 1001.

CREATE OR REPLACE TABLE raw_communes AS
SELECT *
FROM read_csv(
    'data/raw/v_commune_2026.csv',
    types = {
        'COM': 'VARCHAR',
        'DEP': 'VARCHAR',
        'REG': 'VARCHAR',
        'COMPARENT': 'VARCHAR'
    }
);