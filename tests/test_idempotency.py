import psycopg2

def test_no_duplicates():
    conn = psycopg2.connect(
        host="db",
        database="kasparro_db",
        user="postgres",
        password="avinash79"
    )
    cursor = conn.cursor()

    cursor.execute("""
        SELECT symbol, source, COUNT(*)
        FROM assets
        GROUP BY symbol, source
        HAVING COUNT(*) > 1
    """)

    duplicates = cursor.fetchall()

    assert len(duplicates) == 0

    cursor.close()
    conn.close()
