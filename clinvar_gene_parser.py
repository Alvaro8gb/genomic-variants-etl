#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-

import os
import re
import sys
import gzip

from db_libs.read_sql import load_clinvar_table_defs
from db_libs.utils_sqlite import open_db
from db_libs.utils import clean_column_values


def parse_header(line):
    """Parse the header line and return a mapping of column names to indices and VCF coordinate info."""
    line = line.lstrip("#").rstrip("\n")
    column_names = re.split(r"\t", line)
    header_mapping = {name: idx for idx, name in enumerate(column_names)}

    print("Header mapping loaded", header_mapping)

    return header_mapping

def insert_gene(cur, header_mapping, column_values):
    """Insert a gene row and return the new gene_id."""
    gene_symbol = column_values[header_mapping["Symbol"]]
    gene_id = column_values[header_mapping["GeneID"]]
    total_submissions = column_values[header_mapping["Total_submissions"]]
    total_alleles = column_values[header_mapping["Total_alleles"]]
    submissions_reporting_this_gene = column_values[header_mapping["Submissions_reporting_this_gene"]]
    alleles_reported_pathogenic = column_values[header_mapping["Alleles_reported_Pathogenic_Likely_pathogenic"]]
    gene_mim_number = column_values[header_mapping["Gene_MIM_number"]]
    number_uncertain = column_values[header_mapping["Number_uncertain"]]
    number_with_conflicts = column_values[header_mapping["Number_with_conflicts"]]

    cur.execute("""
        INSERT INTO gene_stats (
            gene_symbol, gene_id, total_submissions, total_alleles, submissions_reporting_this_gene,
            alleles_reported_pathogenic, gene_mim_number, number_uncertain, number_with_conflicts
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        gene_symbol, gene_id, total_submissions, total_alleles, submissions_reporting_this_gene,
        alleles_reported_pathogenic, gene_mim_number, number_uncertain, number_with_conflicts
    ))
    return cur.lastrowid


def store_clinvar_file(db, clinvar_file):
    
    with gzip.open(clinvar_file, "rt", encoding="utf-8") as cf:
        
        cur = db.cursor()
        next(cf) # skip the first line as is a comment

        first_line = next(cf)
        header_mapping = parse_header(first_line)

        with db:
            for i, line in enumerate(cf):

                wline = line.rstrip("\n")

                if wline.startswith('#'):
                    continue  # skip comment lines

                if i % 10_000 == 0:
                    print(f"Processed {i} lines...")

                column_values = clean_column_values(re.split(r"\t", wline))

                insert_gene(cur, header_mapping, column_values)
                
                
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
    clinvar_tables = load_clinvar_table_defs("schemas/clinvar_gene.sql")

    # First, let's create or open the database
    db = open_db(db_file, clinvar_tables)

    try:
        # Second
        store_clinvar_file(db, clinvar_file)
    finally:
        db.close()
