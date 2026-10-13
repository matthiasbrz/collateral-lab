-- Chargement brut du COG 2024, dernier millesime ou Le Heron (76358) est une
-- commune. Aucune transformation ; memes types forces que le millesime courant.

CREATE OR REPLACE TABLE raw_communes_2024 AS
SELECT
    *,
    now() AS charge_le
FROM read_csv(
    'data/raw/v_commune_2024.csv',
    types = {
        'COM': 'VARCHAR',
        'DEP': 'VARCHAR',
        'REG': 'VARCHAR',
        'COMPARENT': 'VARCHAR'
    }
);