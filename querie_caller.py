import os
import sys
import sqlite3
from queries import ClinvarQuery, CivicQuery


def parse_arguments(args):
    """Parse command line arguments with --ddbb flag"""
    databases = {}
    current_type = None

    for arg in args:
        if arg == "--ddbb":
            current_type = None  # Next arg will be the db type
        elif current_type is None and arg != "--ddbb":
            # This is the database type (clinvar or civic)
            current_type = arg.lower()
            if current_type not in databases:
                databases[current_type] = []
        else:
            # This is a database path
            if current_type:
                databases[current_type].append(arg)

    return databases


def get_db_alias(db_path):
    """Extract filename without 'clinvar_' prefix to use as alias"""
    filename = os.path.basename(db_path)
    # Remove .db extension
    filename_no_ext = os.path.splitext(filename)[0]
    
    filename_no_ext = filename_no_ext.replace("clinvar_", "")
    filename_no_ext = filename_no_ext.replace("civic_", "")
        
    return filename_no_ext


def execute_queries(databases: dict):
    """Execute all queries for ClinVar and Civic databases"""

    clinvar_query = ClinvarQuery()
    civic_query = CivicQuery()

    # Define query methods for each database type
    query_methods = {
        "clinvar": [clinvar_query.query_1, clinvar_query.query_2, clinvar_query.query_3,
                    clinvar_query.query_4, clinvar_query.query_5, clinvar_query.query_6,
                    clinvar_query.query_7, clinvar_query.query_8, clinvar_query.query_9,
                    clinvar_query.query_10],
        "civic": [civic_query.query_1, civic_query.query_2,
                  civic_query.query_4,
                  civic_query.query_7,
                  civic_query.query_10]
    }

    # Execute queries for each database type
    for db_type, db_paths in databases.items():
        if db_type not in query_methods:
            print(f"Unknown database type: {db_type}")
            continue

        methods = query_methods[db_type]

        try:
            # Connect to the first database as main
            main_db = db_paths[0]
            conn = sqlite3.connect(main_db)
            print(f"Connected to {db_type} database: {main_db}")
            cursor = conn.cursor()

            print("=" * 50)
            print(f"QUERIES (Main DB: {main_db})")
            print("=" * 50)

            # Attach additional databases
            for attach_db in db_paths[1:]:
                alias = get_db_alias(attach_db)
                cursor.execute(f"ATTACH DATABASE '{attach_db}' AS {alias}")
                print(f"Attached {attach_db} as '{alias}'")

            # Execute queries
            for query_method in methods:
                try:
                    print(f"\n{query_method.__name__}:")
                    query_method(cursor, conn)
                except Exception as e:
                    print(f"Error executing query_{i}: {e}")

            conn.close()
        except Exception as e:
            print(f"Error with {db_type} databases: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(
            "Usage: python querie_caller.py --ddbb clinvar <clinvar_db> [<clinvar_db>...] --ddbb civic <civic_db> [<civic_db>...]", file=sys.stderr)
        sys.exit(1)

    databases = parse_arguments(sys.argv[1:])
    execute_queries(databases)
