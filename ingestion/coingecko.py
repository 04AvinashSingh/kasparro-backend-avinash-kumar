import requests
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

    # --- Fetch from CoinGecko ---
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "per_page": 5
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    coins = response.json()

    # --- Raw ingestion (optional but OK) ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS raw_coingecko (
            id SERIAL PRIMARY KEY,
            data JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    for coin in coins:
        cursor.execute(
            "INSERT INTO raw_coingecko (data) VALUES (%s)",
            (json.dumps(coin),)
        )

    # --- Normalized ingestion (REQUIRED) ---
    for coin in coins:
        symbol = coin["symbol"]
        name = coin["name"]
        price = coin["current_price"]

        asset_id = get_or_create_asset(cursor, symbol, name)

        cursor.execute(
            """
            INSERT INTO asset_sources
            (asset_id, source, source_symbol, price_usd, raw)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                asset_id,
                "coingecko",
                symbol,
                price,
                json.dumps(coin)
            )
        )

    conn.commit()
    cursor.close()
    conn.close()

    print("CoinGecko ETL finished successfully")


if __name__ == "__main__":
    run()
