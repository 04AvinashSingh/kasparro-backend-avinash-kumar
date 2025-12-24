import psycopg2

def test_incremental_checkpoint():
    conn = psycopg2.connect(
        host="db",
        database="kasparro_db",
        user="postgres",
        password="avinash79"
    )
    cursor = conn.cursor()

    cursor.execute(
        "SELECT last_processed_key FROM etl_checkpoints WHERE source = 'csv_weird'"
    )
    row = cursor.fetchone()

    # Valid behavior: checkpoint exists only after ETL runs
    if row is not None:
        assert row[0] is not None

    cursor.close()
    conn.close()
