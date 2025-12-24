import csv
import uuid
import psycopg2
import json
from datetime import datetime

print("CSV WEIRD ETL STARTED")

conn = psycopg2.connect(
    host="db",
    database="kasparro_db",
    user="postgres",
    password="avinash79"
)
cursor = conn.cursor()


# Start ETL run

run_id = str(uuid.uuid4())
start_time = datetime.utcnow()

cursor.execute("""
    INSERT INTO etl_runs (
        run_id, source, status, records_processed, start_time
    )
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id
""", (
    run_id,
    "csv_weird",
    "running",
    0,
    start_time
))


# -------------------------
# Get last checkpoint
# -------------------------
cursor.execute(
    "SELECT last_processed_key FROM etl_checkpoints WHERE source = %s",
    ("csv_weird",)
)
row = cursor.fetchone()
last_processed = row[0] if row else None

print("Last checkpoint:", last_processed)

processed = 0
resume = last_processed is None

# -------------------------
# CSV Processing
# -------------------------
with open("/app/data/assets_weird.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        symbol = row["coin_symbol"].strip().lower()

        # Resume logic (safe)
        if not resume:
            if symbol == last_processed:
                resume = True
            print("Skipping already processed:", symbol)
            continue

        print("Processing:", symbol)

        # RAW insert
        cursor.execute(
            "INSERT INTO raw_csv_assets (data) VALUES (%s)",
            (json.dumps(row),)
        )

        # Idempotent insert
        cursor.execute(
            """
            INSERT INTO assets (symbol, name, price_usd, source)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (symbol, source) DO NOTHING
            """,
            (
                symbol,
                row["coin_name"].strip(),
                float(row["usd_price"]),
                "csv_weird"
            )
        )

        processed += 1

        # Update checkpoint AFTER success
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
# -------------------------
# Finish ETL run
# -------------------------
end_time = datetime.utcnow()
duration_ms = int((end_time - start_time).total_seconds() * 1000)

cursor.execute("""
    UPDATE etl_runs
    SET end_time = %s,
        status = %s,
        records_processed = %s,
        duration_ms = %s
    WHERE run_id = %s
""", (
    end_time,
    "success",
    processed,
    duration_ms,
    run_id
))

conn.commit()
cursor.close()
conn.close()

print("CSV WEIRD ETL COMPLETED")
