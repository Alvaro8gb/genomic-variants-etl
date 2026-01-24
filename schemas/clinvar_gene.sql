CREATE TABLE IF NOT EXISTS gene_stats (
    gen_id_stats INTEGER PRIMARY KEY AUTOINCREMENT,
    gene_symbol TEXT NOT NULL,
    gene_id INTEGER NOT NULL,
    total_submissions INTEGER,
    total_alleles INTEGER,
    submissions_reporting_this_gene INTEGER,
    alleles_reported_pathogenic TEXT,
    gene_mim_number INTEGER,
    number_uncertain INTEGER,
    number_with_conflicts INTEGER
) STRICT;

CREATE INDEX gene_idx ON gene_stats(gene_symbol, gene_mim_number);
