import psycopg2
import os

def test_no_duplicate_canonical_assets():
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "db"),
        database=os.getenv("POSTGRES_DB", "kasparro_db"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )
    cursor = conn.cursor()

    cursor.execute("""
        SELECT canonical_symbol, COUNT(*)
        FROM assets
        GROUP BY canonical_symbol
        HAVING COUNT(*) > 1
    """)

    duplicates = cursor.fetchall()

    assert len(duplicates) == 0

    cursor.close()
    conn.close()
