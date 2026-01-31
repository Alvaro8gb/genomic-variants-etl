import re
import sys


from db_libs.read_sql import load_clinvar_table_defs
from db_libs.utils_sqlite import open_db
from db_libs.utils import clean_row_values, parse_header, none_for_unique

DDL_TABLE = "schemas/civiv_variant.sql"


def insert_feature(cur, feature_id: int, header_mapping, row_values):
    """Insert a variant row and return the new ventry_id."""

    feature_name = row_values[header_mapping["feature_name"]]
    feature_type = row_values[header_mapping["feature_type"]]

    cur.execute("""
        INSERT INTO feature(
            feature_id, 
            feature_name, feature_type)
        VALUES(?,?,?)
    """, (feature_id, feature_name, feature_type))


def insert_variant(cur, variant_id: int, feature_id: int, header_mapping, row_values):
    """Insert a variant row and return the new ventry_id."""
    variant_name = row_values[header_mapping["variant"]]
    variant_aliases = row_values[header_mapping["variant_aliases"]]
    variant_groups = row_values[header_mapping["variant_groups"]]
    variant_types = row_values[header_mapping["variant_types"]]
    caid = row_values[header_mapping["allele_registry_id"]] 
    gene_symbol = row_values[header_mapping["gene"]]
    entrez_id = row_values[header_mapping["entrez_id"]]
    chro = none_for_unique(row_values[header_mapping["chromosome"]])
    chro_start = int(none_for_unique(row_values[header_mapping["start"]]))
    chro_stop = int(none_for_unique(row_values[header_mapping["stop"]]))
    ref_allele = row_values[header_mapping["reference_bases"]]
    alt_allele = row_values[header_mapping["variant_bases"]]
    ensembl_version = row_values[header_mapping["ensembl_version"]]
    assembly = row_values[header_mapping["reference_build"]]

    cur.execute("""
        INSERT INTO variant(
            variant_id, caid, variant_name, variant_aliases, variant_groups, variant_types,
            feature_id,
            entrez_id, gene_symbol,
            chro, chro_start, chro_stop, ref_allele, alt_allele, 
            ensembl_version, assembly)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (variant_id, caid, variant_name, variant_aliases, variant_groups, variant_types,
          feature_id,
          entrez_id, gene_symbol,
          chro, chro_start, chro_stop, ref_allele, alt_allele,
          ensembl_version, assembly))


def store_clinvar_file(db, clinvar_file):

    known_features = set()

    with open(clinvar_file, "rt", encoding="utf-8") as cf:

        first_line = next(cf)
        header_mapping = parse_header(first_line)

        cur = db.cursor()
        with db:
            for i, line in enumerate(cf):

                wline = line.rstrip("\n")

                row_values = clean_row_values(re.split(r"\t", wline))

                variant_id = int(row_values[header_mapping["variant_id"]])
                feature_id = int(row_values[header_mapping["feature_id"]])

                print("variant_id:", variant_id)
                if feature_id not in known_features: 
                    insert_feature(cur, feature_id, header_mapping, row_values)
                    known_features.add(feature_id)
            
                insert_variant(cur, variant_id, feature_id,
                               header_mapping, row_values)

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
