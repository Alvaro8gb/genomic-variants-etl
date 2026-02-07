#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-

import re
import gzip

from db_libs.etl import main
from db_libs.utils import is_header_line, parse_header, clean_row_values, text2date


def extract_pmids(text: str):
    pmids = re.findall(r'PMID:\s*(\d+)', text)
    return set(pmids)


def insert_submission(cur, header_mapping, row_values):
    """Insert a submission row and return the new id."""

    variant_id = int(row_values[header_mapping["VariationID"]])
    clinical_significance = row_values[header_mapping["ClinicalSignificance"]]
    date_last_evaluated = text2date(
        row_values[header_mapping["DateLastEvaluated"]])
    description = row_values[header_mapping["Description"]]
    submitted_phenotype_info = row_values[header_mapping["SubmittedPhenotypeInfo"]]
    reported_phenotype_info = row_values[header_mapping["ReportedPhenotypeInfo"]]
    review_status = row_values[header_mapping["ReviewStatus"]]
    collection_method = row_values[header_mapping["CollectionMethod"]]
    origin_counts = row_values[header_mapping["OriginCounts"]]
    submitter = row_values[header_mapping["Submitter"]]
    scv = row_values[header_mapping["SCV"]]
    submitted_gene_symbol = row_values[header_mapping["SubmittedGeneSymbol"]]
    explanation_of_interpretation = row_values[header_mapping["ExplanationOfInterpretation"]]
    somatic_clinical_impact = row_values[header_mapping["SomaticClinicalImpact"]]
    oncogenicity = row_values[header_mapping["Oncogenicity"]]

    cur.execute("""
        INSERT INTO submission (
            variant_id, clinical_significance, date_last_evaluated, description,
            submitted_phenotype_info, reported_phenotype_info, review_status, collection_method,
            origin_counts, submitter, scv, submitted_gene_symbol, explanation_of_interpretation,
            somatic_clinical_impact, oncogenicity
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        variant_id, clinical_significance, date_last_evaluated, description,
        submitted_phenotype_info, reported_phenotype_info, review_status, collection_method,
        origin_counts, submitter, scv, submitted_gene_symbol, explanation_of_interpretation,
        somatic_clinical_impact, oncogenicity
    ))

    submission_id = cur.lastrowid

    if description:
        pmids = extract_pmids(description)

        if pmids:
            cur.executemany("""
                    INSERT INTO submission_pmid (
                        submission_id, pmid
                    ) VALUES (?, ?)
                """, [ (submission_id, pmid) for pmid in pmids])


def etl(db, file):
    with gzip.open(file, "rt", encoding="utf-8") as cf:

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

                if i % 100_000 == 0:
                    print(f"Processed {i} lines...")

                row_values = clean_row_values(re.split(r"\t", wline))

                insert_submission(cur, header_mapping, row_values)

        cur.close()


if __name__ == '__main__':

    ddl_table_path = "schemas/clinvar/clinvar_submission.sql"
    main(etl, ddl_table_path)