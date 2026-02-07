import re
import gzip

from db_libs.utils import clean_row_values, parse_header
from db_libs.etl import main


def insert_gene_stats(cur, header_mapping, row_values):
    """Insert a gene row and return the new gene_id."""
    gene_symbol = row_values[header_mapping["Symbol"]]
    gene_id = row_values[header_mapping["GeneID"]]
    total_submissions = row_values[header_mapping["Total_submissions"]]
    total_alleles = row_values[header_mapping["Total_alleles"]]
    submissions_reporting_this_gene = row_values[header_mapping["Submissions_reporting_this_gene"]]
    alleles_reported_pathogenic = row_values[header_mapping["Alleles_reported_Pathogenic_Likely_pathogenic"]]
    gene_mim_number = row_values[header_mapping["Gene_MIM_number"]]
    number_uncertain = row_values[header_mapping["Number_uncertain"]]
    number_with_conflicts = row_values[header_mapping["Number_with_conflicts"]]

    cur.execute("""
        INSERT INTO gene_stats (
            gene_symbol, gene_id, total_submissions, total_alleles, submissions_reporting_this_gene,
            alleles_reported_pathogenic, gene_mim_number, number_uncertain, number_with_conflicts
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        gene_symbol, gene_id, total_submissions, total_alleles, submissions_reporting_this_gene,
        alleles_reported_pathogenic, gene_mim_number, number_uncertain, number_with_conflicts
    ))


def etl(db, file):

    with gzip.open(file, "rt", encoding="utf-8") as cf:

        cur = db.cursor()
        next(cf)  # skip the first line as is a comment

        first_line = next(cf)
        header_mapping = parse_header(first_line)

        with db:
            for i, line in enumerate(cf):

                wline = line.rstrip("\n")

                if wline.startswith('#'):
                    continue  # skip comment lines

                if i % 10_000 == 0:
                    print(f"Processed {i} lines...")

                row_values = clean_row_values(re.split(r"\t", wline))

                insert_gene_stats(cur, header_mapping, row_values)

        cur.close()


if __name__ == '__main__':
    ddl_table_path = "schemas/clinvar/clinvar_gene.sql"
    main(etl, ddl_table_path)
