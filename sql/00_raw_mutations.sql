-- sql/00_raw_mutations.sql
-- Chargement brut des fichiers DVF. Aucune transformation.
CREATE OR REPLACE TABLE raw_mutations AS
SELECT 
    *,
    parse_filename(filename) AS fichier, -- provenance de la ligne (19/10)
    now() AS charge_le
FROM read_csv(
    'data/raw/dvf_*.csv.gz',
    union_by_name = true,
    types = {
        'code_commune': 'VARCHAR',
        'code_postal': 'VARCHAR',
        'code_departement': 'VARCHAR',
        'id_parcelle': 'VARCHAR'
    }
);