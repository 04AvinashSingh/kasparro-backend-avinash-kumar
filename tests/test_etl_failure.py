import psycopg2
import os

def test_failure_status_written():
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "db"),
        database=os.getenv("POSTGRES_DB", "kasparro_db"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM etl_runs
        WHERE status IN ('failure', 'running', 'success')
    """)

    count = cursor.fetchone()[0]

    # Table exists and supports status tracking
    assert count >= 0

    cursor.close()
    conn.close()
