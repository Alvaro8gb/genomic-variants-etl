CREATE TABLE
    IF NOT EXISTS feature (
        feature_id INTEGER PRIMARY KEY,
        feature_name TEXT,
        feature_type TEXT
    ) STRICT;

CREATE TABLE
    IF NOT EXISTS variant (
        variant_id INTEGER PRIMARY KEY,
        caid TEXT, 
        variant_name TEXT,
        variant_aliases TEXT,
        variant_groups TEXT,
        variant_types TEXT,
        feature_id INTEGER NOT NULL,
        gene_symbol TEXT,
        entrez_id INTEGER,
        chro TEXT NOT NULL,
        chro_start INTEGER NOT NULL,
        chro_stop INTEGER NOT NULL,
        ref_allele TEXT,
        alt_allele TEXT,
        ensembl_version INTEGER,
        assembly TEXT,
        FOREIGN KEY (feature_id) REFERENCES feature (feature_id)
    ) STRICT;
    
CREATE INDEX coords_variant ON variant (chro_start, chro_stop, chro);

CREATE INDEX assembly_variant ON variant (assembly);

CREATE INDEX gene_symbol_variant ON variant (gene_symbol);