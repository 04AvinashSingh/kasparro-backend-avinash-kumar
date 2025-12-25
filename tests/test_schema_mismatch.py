def test_schema_unification_columns():
    import psycopg2
    import os

    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "db"),
        database=os.getenv("POSTGRES_DB", "kasparro_db"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )
    cursor = conn.cursor()

    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'assets'
    """)

    columns = {row[0] for row in cursor.fetchall()}

    # Canonical schema (CORRECT)
    expected = {"canonical_symbol", "canonical_name"}

    assert expected.issubset(columns)

    cursor.close()
    conn.close()
