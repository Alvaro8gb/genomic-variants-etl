from db_libs.utils_sqlite import open_db
from db_libs.io import get_and_check_paths, load_clinvar_table_defs


def main(etl, ddl_query):

    # Load Args
    db_file, data_file = get_and_check_paths()

    # Load Tables Schemas
    clinvar_tables = load_clinvar_table_defs(ddl_query)

    # Create or open the database
    db = open_db(db_file, clinvar_tables)

    try:
        # Transform & Load
        etl(db, data_file)
    finally:
        db.close()