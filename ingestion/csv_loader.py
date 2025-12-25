import csv
import psycopg2
import json
import os


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        port=os.getenv("POSTGRES_PORT"),
    )


def get_or_create_asset(cursor, symbol, name):
    cursor.execute(
        "SELECT id FROM assets WHERE canonical_symbol = %s",
        (symbol.upper(),)
    )
    row = cursor.fetchone()

    if row:
        return row[0]

    cursor.execute(
        """
        INSERT INTO assets (canonical_symbol, canonical_name)
        VALUES (%s, %s)
        RETURNING id
        """,
        (symbol.upper(), name)
    )
    return cursor.fetchone()[0]


def run():
    conn = get_db_connection()
    cursor = conn.cursor()

    # --- Ensure raw table exists ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS raw_csv_assets (
            id SERIAL PRIMARY KEY,
            data JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    with open("data/assets.csv", "r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            symbol = row["symbol"]
            name = row["name"]
            price = row["price"]

            # Raw ingestion
            cursor.execute(
                "INSERT INTO raw_csv_assets (data) VALUES (%s)",
                (json.dumps(row),)
            )

            # Normalized ingestion
            asset_id = get_or_create_asset(cursor, symbol, name)

            cursor.execute(
                """
                INSERT INTO asset_sources
                (asset_id, source, source_symbol, price_usd, raw)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    asset_id,
                    "csv",
                    symbol,
                    price,
                    json.dumps(row)
                )
            )

    conn.commit()
    cursor.close()
    conn.close()

    print("CSV ETL completed successfully")


if __name__ == "__main__":
    run()
