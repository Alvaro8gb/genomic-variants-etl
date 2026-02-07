CREATE TABLE
    IF NOT EXISTS clinical_evidence (
        evidence_id INTEGER PRIMARY KEY,
        molecular_profile_id INTEGER NOT NULL,
        doid INTEGER NOT NULL,
        phenotypes TEXT,
        therapies TEXT,
        therapy_interaction_type TEXT,
        evidence_type TEXT,
        evidence_direction TEXT,
        evidence_level TEXT,
        significance TEXT,
        evidence_statement TEXT,
        citation_id TEXT,
        source_type TEXT,
        asco_abstract_id TEXT,
        citation TEXT,
        nct_ids TEXT,
        rating INTEGER,
        evidence_status TEXT,
        variant_origin TEXT
    ) STRICT;


CREATE TABLE
    IF NOT EXISTS disease (
        doid INTEGER PRIMARY KEY,
        disease_name TEXT NOT NULL
    ) STRICT;