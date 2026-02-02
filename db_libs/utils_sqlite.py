import os
import sys
import sqlite3


def open_db(db_file, tables):
    """
        This method creates a SQLITE3 database with the needed
        tables or opens it if it already exists
    """

    if not os.path.exists(db_file):
        # First time database is created, its mode is switched to WAL
        db = sqlite3.connect(db_file, isolation_level=None)
        cur = db.cursor()
        try:
            cur.execute("PRAGMA journal_mode=WAL")
        except sqlite3.Error as e:
            print("An error occurred: {}".format(str(e)), file=sys.stderr)
        finally:
            cur.close()
            db.close()

    db = sqlite3.connect(db_file)

    cur = db.cursor()
    try:
        # See https://phiresky.github.io/blog/2020/sqlite-performance-tuning/
        cur.execute("PRAGMA synchronous = normal;")
        # Let's enable the foreign keys integrity checks
        cur.execute("PRAGMA FOREIGN_KEYS=ON")

        # And create the tables, in case they were not previously
        # created in a previous use
        for table in tables:
            print("Procesing", "\n-\n", table[:40], "\n-\n")

            cur.execute(table)

    except sqlite3.Error as e:
        print("An error occurred: {}".format(str(e)), file=sys.stderr)
    finally:
        cur.close()

    return db
