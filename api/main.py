from fastapi import Depends, FastAPI
import psycopg2

import threading
from ingestion.etl_runner import run_etl_periodically


import time
import psycopg2
from psycopg2 import OperationalError
from core.cache import get_cache, set_cache
from fastapi import Request, HTTPException
from core.rate_limiter import is_rate_limited


app = FastAPI()

# ------------------------
# Database helper
# ------------------------
import time
import psycopg2
from psycopg2 import OperationalError

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
    client_ip = request.client.host

    if is_rate_limited(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again later."
        )


def get_db_connection(retries=5, delay=2):
    for attempt in range(retries):
        try:
            return psycopg2.connect(
                host="db",
                database="kasparro_db",
                user="postgres",
                password="avinash79"
            )
        except OperationalError:
            print(f"DB not ready, retrying... ({attempt + 1}/{retries})")
            time.sleep(delay)

    raise Exception("Database is not available after retries")


# ------------------------
# Startup: create table
# ------------------------
@app.on_event("startup")
def start_background_etl():
    create_assets_table()
    create_etl_runs_table()

    thread = threading.Thread(
        target=run_etl_periodically,
        daemon=True
    )
    thread.start()


def create_assets_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            id SERIAL PRIMARY KEY,
            symbol TEXT NOT NULL,
            name TEXT NOT NULL,
            price_usd NUMERIC NOT NULL,
            source TEXT NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

# ------------------------
# Health check
# ------------------------
@app.get("/health")
def health():
    try:
        conn = get_db_connection()
        conn.close()
        return {
            "status": "ok",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "not connected",
            "error": str(e)
        }

# ------------------------
# Data API
# ------------------------
@app.get("/stats", dependencies=[Depends(rate_limit)])
def get_stats():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT run_id, status, records_processed, duration_ms, end_time
        FROM etl_runs
        ORDER BY start_time DESC
        LIMIT 1
    """)
    row = cur.fetchone()

    cur.close()
    conn.close()

    if not row:
        return {
            "records_processed": 0,
            "duration_ms": 0,
            "last_success_time": None,
            "last_failure_time": None,
            "run_metadata": None
        }

    run_id, status, records, duration, end_time = row

    return {
        "records_processed": records,
        "duration_ms": duration,
        "last_success_time": end_time if status == "success" else None,
        "last_failure_time": end_time if status == "failure" else None,
        "run_metadata": {
            "run_id": run_id,
            "status": status,
            "source_count": 3
        }
    }
