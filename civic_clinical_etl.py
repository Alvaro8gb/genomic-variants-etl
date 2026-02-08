import re
from db_libs.etl import main
from db_libs.utils import clean_row_values, parse_header, none_default


def insert_disease(cur, doid: int, disease_name: str):

    cur.execute("""
        INSERT INTO disease (
            doid, disease_name
        ) VALUES(?,?)
    """, (doid, disease_name))


def insert_citation(cur, citation_id: str, header_mapping, row_values):

    source_type = row_values[header_mapping["source_type"]]
    citation = row_values[header_mapping["citation"]]

    cur.execute("""
        INSERT INTO citation (
            citation_id, source_type, citation
        ) VALUES(?,?,?)
    """, (citation_id, source_type, citation))


def insert_clinical_evidence(cur, doid: int, citation_id:str, header_mapping, row_values):
    """Insert a clinical evidence row."""
    evidence_id = int(row_values[header_mapping["evidence_id"]])
    molecular_profile_id = int(
        row_values[header_mapping["molecular_profile_id"]])
    phenotypes = row_values[header_mapping["phenotypes"]]
    therapies = row_values[header_mapping["therapies"]]
    therapy_interaction_type = row_values[header_mapping["therapy_interaction_type"]]
    evidence_type = row_values[header_mapping["evidence_type"]]
    evidence_direction = row_values[header_mapping["evidence_direction"]]
    evidence_level = row_values[header_mapping["evidence_level"]]
    significance = row_values[header_mapping["significance"]]
    evidence_statement = row_values[header_mapping["evidence_statement"]]
    nct_ids = row_values[header_mapping["nct_ids"]]
    rating = int(none_default(row_values[header_mapping["rating"]]))
    evidence_status = row_values[header_mapping["evidence_status"]]
    variant_origin = row_values[header_mapping["variant_origin"]]

    cur.execute("""
        INSERT INTO clinical_evidence (
            evidence_id, molecular_profile_id,
            doid, phenotypes, therapies, therapy_interaction_type,
            evidence_type, evidence_direction, evidence_level, significance,
            evidence_statement, citation_id, 
            nct_ids, rating, evidence_status, variant_origin
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (evidence_id, molecular_profile_id,
          doid, phenotypes, therapies, therapy_interaction_type,
          evidence_type, evidence_direction, evidence_level, significance,
          evidence_statement, citation_id, nct_ids, 
          rating, evidence_status, variant_origin
          ))


def etl(db, file):
    known_disease = set()
    known_cites = set()

    with open(file, "rt", encoding="utf-8") as cf:

        first_line = next(cf)
        header_mapping = parse_header(first_line)

        cur = db.cursor()
        with db:
            for i, line in enumerate(cf):
                print(f"Loading row {i}")

                wline = line.rstrip("\n")

                row_values = clean_row_values(re.split(r"\t", wline))

                doid_str = row_values[header_mapping["doid"]]
                doid = int(doid_str) if doid_str is not None else None

                if doid and doid not in known_disease:
                    disease_name = row_values[header_mapping["disease"]]
                    insert_disease(cur, doid, disease_name)
                    known_disease.add(doid)

                citation_id = row_values[header_mapping["citation_id"]]

                if citation_id not in known_cites:
                    insert_citation(cur, citation_id, header_mapping, row_values)
                    known_cites.add(citation_id)

                insert_clinical_evidence(cur, doid, citation_id, header_mapping, row_values)

        cur.close()


if __name__ == '__main__':
    ddl_table_path = "schemas/civic/civic_clinical.sql"
    main(etl, ddl_table_path)
