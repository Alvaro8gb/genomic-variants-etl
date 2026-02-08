CREATE TABLE
    IF NOT EXISTS disease (
        doid INTEGER PRIMARY KEY,
        disease_name TEXT NOT NULL
    ) STRICT;

CREATE TABLE
    IF NOT EXISTS citation (
        citation_id TEXT PRIMARY KEY,
        citation TEXT,
        source_type TEXT
    ) STRICT;

CREATE TABLE
    IF NOT EXISTS clinical_evidence (
        evidence_id INTEGER PRIMARY KEY,
        molecular_profile_id INTEGER NOT NULL,
        doid INTEGER,
        phenotypes TEXT,
        therapies TEXT,
        therapy_interaction_type TEXT,
        evidence_type TEXT,
        evidence_direction TEXT,
        evidence_level TEXT,
        significance TEXT,
        evidence_statement TEXT,
        citation_id TEXT NOT NULL,
        nct_ids TEXT,
        rating INTEGER,
        evidence_status TEXT,
        variant_origin TEXT, 
        FOREIGN KEY (doid) REFERENCES disease (doid),
        FOREIGN KEY (citation_id) REFERENCES citation (citation_id)
    ) STRICT;

