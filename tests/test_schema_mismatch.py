def test_schema_unification_columns():
    import psycopg2

    conn = psycopg2.connect(
        host="db",
        database="kasparro_db",
        user="postgres",
        password="avinash79"
    )
    cursor = conn.cursor()

    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'assets'
    """)

    columns = {row[0] for row in cursor.fetchall()}

    expected = {"symbol", "name", "price_usd", "source"}

    assert expected.issubset(columns)

    cursor.close()
    conn.close()
