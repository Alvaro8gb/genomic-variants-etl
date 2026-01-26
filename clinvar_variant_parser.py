import re
import sys
import gzip


from db_libs.read_sql import load_clinvar_table_defs
from db_libs.utils_sqlite import open_db
from db_libs.utils import clean_column_values


DDL_TABLE = "schemas/clinvar_variant_tables.sql"


def parse_header(line):
    """Parse the header line and return a mapping of column names to indices and VCF coordinate info."""
    line = line.lstrip("#")
    column_names = re.split(r"\t", line)
    header_mapping = {name: idx for idx, name in enumerate(column_names)}
    new_vcf_coords = 'PositionVCF' in header_mapping
    if new_vcf_coords:
        ref_allele_col = header_mapping["ReferenceAlleleVCF"]
        alt_allele_col = header_mapping["AlternateAlleleVCF"]
    else:
        ref_allele_col = header_mapping["ReferenceAllele"]
        alt_allele_col = header_mapping["AlternateAllele"]
    return header_mapping, ref_allele_col, alt_allele_col


def insert_variant(cur, header_mapping, column_values, ref_allele_col, alt_allele_col):
    """Insert a variant row and return the new ventry_id."""
    allele_id = int(column_values[header_mapping["AlleleID"]])
    name = column_values[header_mapping["Name"]]
    allele_type = column_values[header_mapping["Type"]]
    dbSNP_id = column_values[header_mapping["RS# (dbSNP)"]]
    phenotype_list = column_values[header_mapping["PhenotypeList"]]
    assembly = column_values[header_mapping["Assembly"]]
    chro = column_values[header_mapping["Chromosome"]]
    chro_start = column_values[header_mapping["Start"]]
    chro_stop = column_values[header_mapping["Stop"]]
    ref_allele = column_values[ref_allele_col]
    alt_allele = column_values[alt_allele_col]
    cytogenetic = column_values[header_mapping["Cytogenetic"]]
    variation_id = int(column_values[header_mapping["VariationID"]])
    gene_id = column_values[header_mapping["GeneID"]]
    gene_symbol = column_values[header_mapping["GeneSymbol"]]
    hgnc_id = column_values[header_mapping["HGNC_ID"]]
    cur.execute("""
        INSERT INTO variant(
            allele_id, name, type, dbsnp_id, phenotype_list, gene_id, gene_symbol, hgnc_id,
            assembly, chro, chro_start, chro_stop, ref_allele, alt_allele, cytogenetic, variation_id)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (allele_id, name, allele_type, dbSNP_id, phenotype_list, gene_id, gene_symbol, hgnc_id,
          assembly, chro, chro_start, chro_stop, ref_allele, alt_allele, cytogenetic, variation_id))
    
    return cur.lastrowid


def insert_clinical_significance(cur, ventry_id, significance):
    """Insert clinical significance values."""
    if significance is not None:
        prep_sig = [(ventry_id, sig) for sig in re.split(r"/", significance)]
        cur.executemany("""
            INSERT INTO clinical_sig(ventry_id, significance) VALUES(?,?)
        """, prep_sig)


def insert_review_status(cur, ventry_id, status_str):
    """Insert review status values."""
    if status_str is not None:
        prep_status = [(ventry_id, status)
                       for status in re.split(r", ", status_str)]
        cur.executemany("""
            INSERT INTO review_status(ventry_id, status) VALUES(?,?)
        """, prep_status)


def insert_variant_phenotypes(cur, ventry_id, variant_pheno_str, allele_id, assembly, line):
    """Insert variant phenotypes."""

    if variant_pheno_str is not None:

        variant_pheno_list = re.split(r"[;|]", variant_pheno_str)
        prep_pheno = []

        for phen_group_id, variant_pheno in enumerate(variant_pheno_list):

            if not variant_pheno:
                continue

            if re.search("^[1-9][0-9]* conditions$", variant_pheno):
                # print(f"INFO: Long PhenotypeIDs {allele_id} {assembly}: {variant_pheno}")
                continue

            variant_annots = re.split(r",", variant_pheno)

            for variant_annot in variant_annots:
                phen = variant_annot.split(":")

                if len(phen) > 1:
                    phen_ns, phen_id = phen[0:2]
                    prep_pheno.append(
                        (ventry_id, phen_group_id, phen_ns, phen_id))
                elif variant_annot != "na":
                    print(
                        f"DEBUG: {allele_id} {assembly} {variant_annot}\n\t{variant_pheno_str}\n\t{line}", file=sys.stderr)

        cur.executemany("""
            INSERT INTO variant_phenotypes(ventry_id, phen_group_id, phen_ns, phen_id) 
            VALUES(?,?,?,?)
        """, prep_pheno)


def store_clinvar_file(db, clinvar_file):
    with gzip.open(clinvar_file, "rt", encoding="utf-8") as cf:

        header_mapping = None
        cur = db.cursor()

        first_line = next(cf)
        header_mapping, ref_allele_col, alt_allele_col = parse_header(
            first_line)

        with db:
            for i, line in enumerate(cf):

                if i % 1000 == 0:
                    print(f"Processed {i} lines...")

                wline = line.rstrip("\n")

                if wline.startswith('#'):
                    continue  # skip comment lines

                column_values = clean_column_values(re.split(r"\t", wline))
                ventry_id = insert_variant(
                    cur, header_mapping, column_values, ref_allele_col, alt_allele_col)

                significance = column_values[header_mapping["ClinicalSignificance"]]
                insert_clinical_significance(cur, ventry_id, significance)

                status_str = column_values[header_mapping["ReviewStatus"]]
                insert_review_status(cur, ventry_id, status_str)

                variant_pheno_str = column_values[header_mapping["PhenotypeIDS"]]
                allele_id = column_values[header_mapping["AlleleID"]]
                assembly = column_values[header_mapping["Assembly"]]
                insert_variant_phenotypes(
                    cur, ventry_id, variant_pheno_str, allele_id, assembly, line)

        cur.close()


if __name__ == '__main__':

    if len(sys.argv) < 3:
        print("Usage: {0} {{database_file}} {{compressed_clinvar_file}}".format(
            sys.argv[0]), file=sys.stderr)

        sys.exit(1)

    db_file = sys.argv[1]
    clinvar_file = sys.argv[2]

    # Load Tables Schemas
    clinvar_tables = load_clinvar_table_defs(DDL_TABLE)

    # Create or open the database
    db = open_db(db_file, clinvar_tables)

    try:
        # Insert
        store_clinvar_file(db, clinvar_file)
    finally:
        db.close()
