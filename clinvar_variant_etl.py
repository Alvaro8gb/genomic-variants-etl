import re
import sys
import gzip

from db_libs.etl import main
from db_libs.utils import clean_row_values, none_default


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


def insert_gene(cur, gene_symbol, gene_id, hgnc_id):
    
    if gene_symbol is not None:

        hgnc_id = none_default(hgnc_id)
        gene_id = int(none_default(gene_id))

        cur.execute("""
            INSERT INTO gene(
                gene_symbol,
                gene_id,
                hgnc_id)
            VALUES(?,?,?)
        """, (gene_symbol, gene_id, hgnc_id))


def insert_variant(cur, header_mapping, row_values, ref_allele_col, alt_allele_col):
    """Insert a variant row and return the new ventry_id."""
    variant_id = int(row_values[header_mapping["VariationID"]])
    allele_id = int(row_values[header_mapping["AlleleID"]])
    hgvs_id = row_values[header_mapping["Name"]]
    variant_type = row_values[header_mapping["Type"]]
    dbsnp_id = row_values[header_mapping["RS# (dbSNP)"]]
    phenotype_list = row_values[header_mapping["PhenotypeList"]]
    gene_symbol = row_values[header_mapping["GeneSymbol"]]
    assembly = row_values[header_mapping["Assembly"]]
    chro = none_default(row_values[header_mapping["Chromosome"]])
    chro_start = int(none_default(row_values[header_mapping["Start"]]))
    chro_stop = int(none_default(row_values[header_mapping["Stop"]]))
    ref_allele = row_values[ref_allele_col]
    alt_allele = row_values[alt_allele_col]
    cytogenetic = row_values[header_mapping["Cytogenetic"]]

    cur.execute("""
        INSERT INTO variant (
            allele_id, hgvs_id, variant_id, variant_type, dbsnp_id, phenotype_list, gene_symbol,
            assembly, chro, chro_start, chro_stop, ref_allele, alt_allele, cytogenetic)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (allele_id, hgvs_id, variant_id, variant_type, dbsnp_id, phenotype_list, gene_symbol,
          assembly, chro, chro_start, chro_stop, ref_allele, alt_allele, cytogenetic))

    ventry_id = cur.lastrowid

    return ventry_id


def insert_clinical_significance(cur, ventry_id, significance):
    """Insert clinical significance values."""
    if significance is not None:
        prep_sig = [(ventry_id, sig) for sig in re.split(r"/", significance)]
        cur.executemany("""
            INSERT INTO clinical_sig (ventry_id, significance) VALUES(?,?)
        """, prep_sig)


def insert_review_status(cur, ventry_id, status_str):
    """Insert review status values."""
    if status_str is not None:
        prep_status = [(ventry_id, status)
                       for status in re.split(r", ", status_str)]
        cur.executemany("""
            INSERT INTO review_status (ventry_id, status) VALUES(?,?)
        """, prep_status)


def insert_variant_phenotypes(cur, ventry_id, variant_pheno: str, allele_id, assembly, line):
    """Insert variant phenotypes."""

    if variant_pheno is not None:

        variant_pheno = variant_pheno.replace(
            "MONDO:MONDO:", "MONDO:")  # Improvent

        variant_pheno_list = re.split(r"[;|]", variant_pheno)
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
                else:
                    print(
                        f"DEBUG: {allele_id} {assembly} {variant_annot}\n\t{variant_pheno}\n\t{line}", file=sys.stderr)

        cur.executemany("""
            INSERT INTO variant_phenotypes (ventry_id, phen_group_id, phen_ns, phen_id) 
            VALUES(?,?,?,?)
        """, prep_pheno)


def etl(db, file):
    known_genes = set()

    with gzip.open(file, "rt", encoding="utf-8") as cf:

        header_mapping = None
        cur = db.cursor()

        first_line = next(cf)
        header_mapping, ref_allele_col, alt_allele_col = parse_header(
            first_line)

        with db:
            for i, line in enumerate(cf):

                if i % 100_000 == 0:
                    print(f"Processed {i} lines...")

                wline = line.rstrip("\n")

                if wline.startswith('#'):
                    continue  # skip comment lines

                row_values = clean_row_values(re.split(r"\t", wline))

                # Genes
                gene_symbol = row_values[header_mapping["GeneSymbol"]]

                if gene_symbol not in known_genes:
                    hgnc_id = row_values[header_mapping["HGNC_ID"]]
                    gene_id = row_values[header_mapping["GeneID"]]
                    insert_gene(cur, gene_symbol, gene_id, hgnc_id)
                    known_genes.add(gene_symbol)

                # Variants
                ventry_id = insert_variant(
                    cur, header_mapping, row_values, ref_allele_col, alt_allele_col)

                # Significance
                significance = row_values[header_mapping["ClinicalSignificance"]]
                insert_clinical_significance(cur, ventry_id, significance)

                # Status
                status_str = row_values[header_mapping["ReviewStatus"]]
                insert_review_status(cur, ventry_id, status_str)

                # Phenotype
                variant_pheno = row_values[header_mapping["PhenotypeIDS"]]
                allele_id = row_values[header_mapping["AlleleID"]]
                assembly = row_values[header_mapping["Assembly"]]
                insert_variant_phenotypes(
                    cur, ventry_id, variant_pheno, allele_id, assembly, line)

        cur.close()


if __name__ == '__main__':
    ddl_table_path = "schemas/clinvar/clinvar_variant.sql"
    main(etl, ddl_table_path)
