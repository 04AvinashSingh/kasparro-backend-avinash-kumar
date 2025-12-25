DROP TABLE IF EXISTS asset_sources;
DROP TABLE IF EXISTS assets;
DROP TABLE IF EXISTS etl_runs;

CREATE TABLE assets (
    id SERIAL PRIMARY KEY,
    canonical_symbol TEXT UNIQUE NOT NULL,
    canonical_name TEXT NOT NULL
);

CREATE TABLE asset_sources (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER REFERENCES assets(id),
    source TEXT NOT NULL,
    source_symbol TEXT NOT NULL,
    price_usd NUMERIC NOT NULL,
    raw JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE etl_runs (
    id SERIAL PRIMARY KEY,
    run_id UUID NOT NULL,
    status TEXT NOT NULL,
    records_processed INT NOT NULL,
    duration_ms INT NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
