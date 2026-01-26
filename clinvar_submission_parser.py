#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-

import re
import sys
import gzip


from db_libs.utils_sqlite import open_db
from db_libs.read_sql import load_clinvar_table_defs
from db_libs.utils import is_header_line, parse_header, clean_column_values, text2date


DDL_TABLE = "schemas/clinvar_submission.sql"

def extract_pmids(text: str):
    pmids = re.findall(r'PMID:\s*(\d+)', text)
    return set(pmids)


def insert_submission(cur, header_mapping, column_values):
    """Insert a submission row and return the new id."""

    variation_id = column_values[header_mapping["VariationID"]]
    clinical_significance = column_values[header_mapping["ClinicalSignificance"]]
    date_last_evaluated = text2date(
        column_values[header_mapping["DateLastEvaluated"]])
    description = column_values[header_mapping["Description"]]
    submitted_phenotype_info = column_values[header_mapping["SubmittedPhenotypeInfo"]]
    reported_phenotype_info = column_values[header_mapping["ReportedPhenotypeInfo"]]
    review_status = column_values[header_mapping["ReviewStatus"]]
    collection_method = column_values[header_mapping["CollectionMethod"]]
    origin_counts = column_values[header_mapping["OriginCounts"]]
    submitter = column_values[header_mapping["Submitter"]]
    scv = column_values[header_mapping["SCV"]]
    submitted_gene_symbol = column_values[header_mapping["SubmittedGeneSymbol"]]
    explanation_of_interpretation = column_values[header_mapping["ExplanationOfInterpretation"]]
    somatic_clinical_impact = column_values[header_mapping["SomaticClinicalImpact"]]
    oncogenicity = column_values[header_mapping["Oncogenicity"]]

    cur.execute("""
        INSERT INTO clinvar_submission (
            variation_id, clinical_significance, date_last_evaluated, description,
            submitted_phenotype_info, reported_phenotype_info, review_status, collection_method,
            origin_counts, submitter, scv, submitted_gene_symbol, explanation_of_interpretation,
            somatic_clinical_impact, oncogenicity
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        variation_id, clinical_significance, date_last_evaluated, description,
        submitted_phenotype_info, reported_phenotype_info, review_status, collection_method,
        origin_counts, submitter, scv, submitted_gene_symbol, explanation_of_interpretation,
        somatic_clinical_impact, oncogenicity
    ))

    submission_id = cur.lastrowid

    if description:
        pmids = extract_pmids(description)

        if pmids:
            variants_pmids = [ (submission_id, pmid) for pmid in pmids]
            cur.executemany("""
                    INSERT INTO variant_pmid (
                        submission_id, pmid
                    ) VALUES (?, ?)
                """, variants_pmids)


def store_clinvar_file(db, clinvar_file):
    with gzip.open(clinvar_file, "rt", encoding="utf-8") as cf:

        cur = db.cursor()

        header_found = False
        while not header_found:
            line = next(cf)
            if is_header_line(line):
                header_mapping = parse_header(line)
                header_found = True

        with db:
            for i, line in enumerate(cf):

                wline = line.rstrip("\n")

                if wline.startswith('#'):
                    continue  # skip comment lines

                if i % 10_000 == 0:
                    print(f"Processed {i} lines...")

                column_values = clean_column_values(re.split(r"\t", wline))

                insert_submission(cur, header_mapping, column_values)

        cur.close()


if __name__ == '__main__':

    if len(sys.argv) < 3:
        print("Usage: {0} {{database_file}} {{compressed_clinvar_file}}".format(
            sys.argv[0]), file=sys.stderr)

        sys.exit(1)

    # Only the first and second parameters are considered
    db_file = sys.argv[1]
    clinvar_file = sys.argv[2]

    # Load Tables Schemas
    clinvar_tables = load_clinvar_table_defs(DDL_TABLE)

    # First, let's create or open the database
    db = open_db(db_file, clinvar_tables)

    try:
        # Second
        store_clinvar_file(db, clinvar_file)
    finally:
        db.close()
