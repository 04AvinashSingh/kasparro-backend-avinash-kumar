from fastapi import Depends, FastAPI, Request, HTTPException
import psycopg2
import os
import threading
import time
from psycopg2 import OperationalError

from ingestion.etl_runner import run_etl_periodically
from core.rate_limiter import is_rate_limited

app = FastAPI()

def wait_for_db_forever(delay=2):
    while True:
        try:
            conn = psycopg2.connect(
                host=os.getenv("POSTGRES_HOST"),
                database=os.getenv("POSTGRES_DB"),
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD"),
                port=os.getenv("POSTGRES_PORT"),
            )
            conn.close()
            print("Database is ready")
            return
        except OperationalError:
            print("Waiting for database...")
            time.sleep(delay)

def get_db_connection(retries=5, delay=2):
    for attempt in range(retries):
        try:
            return psycopg2.connect(
                host=os.getenv("POSTGRES_HOST"),
                database=os.getenv("POSTGRES_DB"),
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD"),
                port=os.getenv("POSTGRES_PORT"),
            )
        except OperationalError:
            print(f"DB not ready, retrying... ({attempt + 1}/{retries})")
            time.sleep(delay)
    raise Exception("Database not available")


def create_assets_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            id SERIAL PRIMARY KEY,
            canonical_symbol TEXT UNIQUE NOT NULL,
            canonical_name TEXT NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


def create_asset_sources_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS asset_sources (
            id SERIAL PRIMARY KEY,
            asset_id INTEGER REFERENCES assets(id),
            source TEXT NOT NULL,
            source_symbol TEXT NOT NULL,
            price_usd NUMERIC NOT NULL,
            raw JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


def create_etl_runs_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS etl_runs (
            id SERIAL PRIMARY KEY,
            run_id UUID NOT NULL,
            status TEXT NOT NULL,
            records_processed INT NOT NULL,
            duration_ms INT NOT NULL,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


def rate_limit(request: Request):
    if is_rate_limited(request.client.host):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")


@app.on_event("startup")
def start_background_etl():
    wait_for_db_forever()  

    create_assets_table()
    create_asset_sources_table()
    create_etl_runs_table()

    threading.Thread(
        target=run_etl_periodically,
        daemon=True
    ).start()



@app.get("/health")
def health():
    try:
        conn = get_db_connection()
        conn.close()
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.get("/stats", dependencies=[Depends(rate_limit)])
def get_stats():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT run_id, status, records_processed, duration_ms, created_at
        FROM etl_runs
        ORDER BY created_at DESC
        LIMIT 1
    """)
    row = cur.fetchone()

    cur.close()
    conn.close()

    if not row:
        return {"records_processed": 0}

    run_id, status, records, duration, created_at = row

    return {
        "records_processed": records,
        "duration_ms": duration,
        "last_success_time": created_at if status == "success" else None,
        "last_failure_time": created_at if status == "failure" else None,
        "run_metadata": {
            "run_id": str(run_id),
            "status": status
        }
    }
