import re
import sys
import gzip


from db_libs.read_sql import load_clinvar_table_defs
from db_libs.utils_sqlite import open_db
from db_libs.utils import clean_column_values, parse_header

DDL_TABLE = "schemas/civiv_variant.sql"


def insert_variant(cur, variant_id:int, header_mapping, column_values):
    """Insert a variant row and return the new ventry_id."""
    variant_name = column_values[header_mapping["variant"]]
    variant_aliases = column_values[header_mapping["variant_aliases"]]
    variant_groups = column_values[header_mapping["variant_groups"]]
    variant_types = column_values[header_mapping["variant_types"]]
    gene_symbol = column_values[header_mapping["gene"]]
    entrez_id = column_values[header_mapping["entrez_id"]]
    chro = column_values[header_mapping["chromosome"]]
    chro_start = column_values[header_mapping["start"]]
    chro_stop = column_values[header_mapping["stop"]]
    ref_allele = column_values[header_mapping["reference_bases"]]
    alt_allele = column_values[header_mapping["variant_bases"]]
    ensembl_version = column_values[header_mapping["ensembl_version"]]
    assembly = column_values[header_mapping["reference_build"]]

    cur.execute("""
        INSERT INTO variant(
            variant_id, variant_name, variant_aliases, variant_groups, variant_types,
            gene_symbol, entrez_id,
            chro, chro_start, chro_stop, ref_allele, alt_allele, 
            ensembl_version, assembly)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (variant_id, variant_name, variant_aliases, variant_groups, variant_types, 
          gene_symbol, entrez_id,
          chro, chro_start, chro_stop, ref_allele, alt_allele, 
          ensembl_version, assembly))


def insert_feature(cur, variant_id:int, header_mapping, column_values):
    """Insert a variant row and return the new ventry_id."""
    feature_name = column_values[header_mapping["feature_name"]]
    feature_type = column_values[header_mapping["feature_type"]]

    cur.execute("""
        INSERT INTO feature(
            variant_id, 
            feature_name, feature_type)
        VALUES(?,?,?)
    """, (variant_id, feature_name, feature_type))
    
def store_clinvar_file(db, clinvar_file):
    with open(clinvar_file, "rt", encoding="utf-8") as cf:

        first_line = next(cf)
        header_mapping = parse_header(first_line)
            
        cur = db.cursor()
        with db:
            for i, line in enumerate(cf):

                wline = line.rstrip("\n")

                column_values = clean_column_values(re.split(r"\t", wline))

                variant_id = int(column_values[header_mapping["variant_id"]])

                print("variant_id:", variant_id)

                insert_variant(cur, variant_id, header_mapping, column_values)
                insert_feature(cur, variant_id, header_mapping, column_values)

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
