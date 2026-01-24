CREATE TABLE IF NOT EXISTS clinvar_submission (
    submission_id INTEGER PRIMARY KEY AUTOINCREMENT,
    variation_id INTEGER,
    clinical_significance TEXT,
    date_last_evaluated DATE,
    description TEXT,
    submitted_phenotype_info TEXT,
    reported_phenotype_info TEXT,
    review_status TEXT,
    collection_method TEXT,
    origin_counts TEXT,
    submitter TEXT,
    scv VARCHAR(20),
    submitted_gene_symbol TEXT,
    explanation_of_interpretation TEXT,
    somatic_clinical_impact TEXT,
    oncogenicity TEXT
);