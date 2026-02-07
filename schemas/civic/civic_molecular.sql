CREATE TABLE
    IF NOT EXISTS molecular_profile (
        molecular_profile_id INTEGER PRIMARY KEY,
        molecular_profile_name TEXT NOT NULL,
        summary TEXT,
        evidence_score REAL
    ) STRICT;

CREATE TABLE
    IF NOT EXISTS profile_evidence (
        molecular_profile_id INTEGER NOT NULL,
        evidence_item_id INTEGER NOT NULL,
        FOREIGN KEY (molecular_profile_id) REFERENCES molecular_profile (molecular_profile_id) ON DELETE CASCADE ON UPDATE CASCADE
    ) STRICT;

CREATE TABLE
    IF NOT EXISTS profile_variant (
        molecular_profile_id INTEGER NOT NULL,
        variant_id INTEGER NOT NULL,
        FOREIGN KEY (molecular_profile_id) REFERENCES molecular_profile (molecular_profile_id) ON DELETE CASCADE ON UPDATE CASCADE
    ) STRICT;