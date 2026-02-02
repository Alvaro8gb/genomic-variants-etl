CREATE TABLE
    IF NOT EXISTS gene (
        gene_symbol TEXT PRIMARY KEY,
        gene_id INTEGER NOT NULL,
        hgnc_id TEXT NOT NULL
    ) STRICT;

CREATE TABLE
    IF NOT EXISTS variant (
        ventry_id INTEGER PRIMARY KEY AUTOINCREMENT,
        allele_id INTEGER NOT NULL,
        variant_id INTEGER NOT NULL,
        variant_type TEXT NOT NULL,
        hgvs_id TEXT,
        gene_symbol TEXT,
        dbsnp_id INTEGER NOT NULL,
        phenotype_list TEXT,
        assembly TEXT,
        chro TEXT NOT NULL,
        chro_start INTEGER NOT NULL,
        chro_stop INTEGER NOT NULL,
        ref_allele TEXT,
        alt_allele TEXT,
        cytogenetic TEXT,
        FOREIGN KEY (gene_symbol) REFERENCES gene (gene_symbol)
    ) STRICT;

CREATE INDEX coords_variant ON variant (chro_start, chro_stop, chro);

CREATE INDEX assembly_variant ON variant (assembly);

CREATE INDEX gene_symbol_variant ON variant (gene_symbol);


CREATE TABLE
    IF NOT EXISTS clinical_sig (
        ventry_id INTEGER NOT NULL,
        significance TEXT NOT NULL,
        FOREIGN KEY (ventry_id) REFERENCES variant (ventry_id) ON DELETE CASCADE ON UPDATE CASCADE
    ) STRICT;

CREATE TABLE
    IF NOT EXISTS review_status (
        ventry_id INTEGER NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (ventry_id) REFERENCES variant (ventry_id) ON DELETE CASCADE ON UPDATE CASCADE
    ) STRICT;

CREATE TABLE
    IF NOT EXISTS variant_phenotypes (
        ventry_id INTEGER NOT NULL,
        phen_group_id INTEGER NOT NULL,
        phen_ns TEXT NOT NULL,
        phen_id TEXT NOT NULL,
        FOREIGN KEY (ventry_id) REFERENCES variant (ventry_id) ON DELETE CASCADE ON UPDATE CASCADE
    ) STRICT;