import re
from db_libs.etl import main
from db_libs.utils import clean_row_values, parse_header


def insert_molecular_profiles(cur, header_mapping, row_values):
    """Insert a variant row and return the new ventry_id."""
    molecular_profile_id = int(
        row_values[header_mapping["molecular_profile_id"]])
    molecular_profile_name = row_values[header_mapping["name"]]
    summary = row_values[header_mapping["summary"]]
    evidence_score = float(row_values[header_mapping["evidence_score"]])

    cur.execute("""
        INSERT INTO molecular_profile (
            molecular_profile_id, molecular_profile_name,
            summary,
            evidence_score)
        VALUES(?,?,?,?)
    """, (molecular_profile_id, molecular_profile_name,
          summary,
          evidence_score))

    evidence_item_ids_str = row_values[header_mapping["evidence_item_ids"]]

    if evidence_item_ids_str:
        evidence_item_ids = [(molecular_profile_id, int(e))
                             for e in evidence_item_ids_str.split(",")]

        cur.executemany("""
                INSERT INTO profile_evidence (molecular_profile_id, evidence_item_id) VALUES(?,?)
            """, evidence_item_ids)

    variant_ids_str = str(row_values[header_mapping["variant_ids"]])

    if variant_ids_str:
        variant_ids = [(molecular_profile_id, int(e))
                       for e in variant_ids_str.split(",")]

        cur.executemany("""
                INSERT INTO profile_variant (molecular_profile_id, variant_id) VALUES(?,?)
            """, variant_ids)


def etl(db, file):

    with open(file, "rt", encoding="utf-8") as cf:

        first_line = next(cf)
        header_mapping = parse_header(first_line)

        cur = db.cursor()
        with db:
            for i, line in enumerate(cf):
                print(f"Loading row {i}")

                wline = line.rstrip("\n")

                row_values = clean_row_values(re.split(r"\t", wline))

                insert_molecular_profiles(cur, header_mapping, row_values)

        cur.close()


if __name__ == '__main__':
    ddl_table_path = "schemas/civic/civic_molecular.sql"
    main(etl, ddl_table_path)
