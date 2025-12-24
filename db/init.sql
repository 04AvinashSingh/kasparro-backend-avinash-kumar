CREATE TABLE IF NOT EXISTS assets (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    name TEXT NOT NULL,
    price_usd NUMERIC NOT NULL,
    source TEXT NOT NULL,
    UNIQUE(symbol, source)
);

CREATE TABLE IF NOT EXISTS raw_csv_assets (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE etl_runs (
    id SERIAL PRIMARY KEY,
    run_id UUID DEFAULT gen_random_uuid(),
    source TEXT,
    status TEXT,
    records_processed INTEGER,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration_ms INTEGER
);


CREATE TABLE IF NOT EXISTS etl_checkpoints (
    source TEXT PRIMARY KEY,
    last_processed_key TEXT,
    last_run_time TIMESTAMP,
    status TEXT
);
