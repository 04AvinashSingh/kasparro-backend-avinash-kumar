import psycopg2
import os

def test_incremental_checkpoint():
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "db"),
        database=os.getenv("POSTGRES_DB", "kasparro_db"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )
    cursor = conn.cursor()

    cursor.execute(
        "SELECT last_processed_key FROM etl_checkpoints WHERE source = 'csv_weird'"
    )
    row = cursor.fetchone()

    # If a checkpoint exists, it must have a key
    if row is not None:
        assert row[0] is not None

    cursor.close()
    conn.close()
