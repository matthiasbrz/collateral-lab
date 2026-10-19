-- Une ligne par fichier DVF charge : son millesime et son empreinte SHA-256,
-- la meme que docs/empreintes_attendues.txt. stg_mutations reconstruit un
-- millesime quand l'empreinte de son fichier change (docs/incremental.md).

CREATE OR REPLACE TABLE raw_fichiers AS
SELECT
    parse_filename(filename) AS fichier,
    CAST(regexp_extract(parse_filename(filename), 'dvf_\d+_(\d{4})', 1) AS INTEGER) AS millesime,
    sha256(content) AS empreinte,
    now() AS charge_le
FROM read_blob('data/raw/dvf_*.csv.gz');