CREATE TABLE IF NOT EXISTS variant (
    variant_id INTEGER PRIMARY KEY,
    variant_name TEXT,
    variant_aliases TEXT,
    variant_groups TEXT,
    variant_types TEXT,
    gene_symbol TEXT,
    entrez_id INTEGER,
    chro TEXT,
    chro_start INTEGER,
    chro_stop INTEGER,
    ref_allele TEXT,
    alt_allele TEXT, 
    ensembl_version INTEGER,
    assembly TEXT


) STRICT;

CREATE TABLE IF NOT EXISTS feature (
    feature_id INTEGER PRIMARY KEY,
    feature_name TEXT,
    feature_type TEXT,  
    variant_id INTEGER,
    FOREIGN KEY (variant_id) REFERENCES variant(variant_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) STRICT;


CREATE INDEX coords_variant ON variant(chro_start, chro_stop, chro);

CREATE INDEX assembly_variant ON variant(assembly);

CREATE INDEX gene_symbol_variant ON variant(gene_symbol);
