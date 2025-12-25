import csv
import uuid
import psycopg2
import json
import os
import time
from datetime import datetime

print("CSV WEIRD ETL STARTED")


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


conn = get_db_connection()
cursor = conn.cursor()

# -------------------------
# Ensure checkpoint table exists
# -------------------------
cursor.execute("""
    CREATE TABLE IF NOT EXISTS etl_checkpoints (
        source TEXT PRIMARY KEY,
        last_processed_key TEXT,
        last_run_time TIMESTAMP,
        status TEXT
    );
""")

# -------------------------
# Start ETL run tracking
# -------------------------
run_id = str(uuid.uuid4())
start_time = time.time()
processed = 0

cursor.execute("""
    INSERT INTO etl_runs (run_id, status, records_processed, duration_ms)
    VALUES (%s, %s, %s, %s)
""", (run_id, "running", 0, 0))

# -------------------------
# Get last checkpoint
# -------------------------
cursor.execute(
    "SELECT last_processed_key FROM etl_checkpoints WHERE source = %s",
    ("csv_weird",)
)
row = cursor.fetchone()
last_processed = row[0] if row else None

resume = last_processed is None

print("Last checkpoint:", last_processed)

# -------------------------
# CSV Processing
# -------------------------
with open("/app/data/assets_weird.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        symbol = row["coin_symbol"].strip()
        name = row["coin_name"].strip()
        price = float(row["usd_price"])

        if not resume:
            if symbol == last_processed:
                resume = True
            continue

        # RAW ingestion
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
                "csv_weird",
                symbol,
                price,
                json.dumps(row)
            )
        )

        processed += 1

        # Update checkpoint
        cursor.execute(
            """
            INSERT INTO etl_checkpoints (source, last_processed_key, last_run_time, status)
            VALUES (%s, %s, NOW(), %s)
            ON CONFLICT (source)
            DO UPDATE SET
                last_processed_key = EXCLUDED.last_processed_key,
                last_run_time = EXCLUDED.last_run_time,
                status = EXCLUDED.status
            """,
            ("csv_weird", symbol, "success")
        )

# -------------------------
# Finish ETL run
# -------------------------
duration_ms = int((time.time() - start_time) * 1000)

cursor.execute("""
    UPDATE etl_runs
    SET status = %s,
        records_processed = %s,
        duration_ms = %s
    WHERE run_id = %s
""", (
    "success",
    processed,
    duration_ms,
    run_id
))

conn.commit()
cursor.close()
conn.close()

print("CSV WEIRD ETL COMPLETED")
