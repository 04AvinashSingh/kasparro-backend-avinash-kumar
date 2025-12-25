# Kasparro Backend Assignment

This repository contains a production-ready backend system designed to ingest,
normalize, and expose asset data from multiple heterogeneous sources using a
canonical data model.

The system is built with a strong focus on **security**, **data normalization**,
and **deployment readiness**, aligned with real-world backend engineering
practices.

---

## Tech Stack

- **FastAPI** – API layer
- **PostgreSQL** – Persistent storage
- **Docker & Docker Compose** – Containerization
- **Python** – ETL pipelines
- **AWS EC2** – Deployment environment

---

## System Architecture

The system consists of:

- An API service exposing health and metadata endpoints
- A PostgreSQL database
- Multiple ETL pipelines for different data sources:
  - CSV
  - CSV Weird
  - CoinGecko API

All services are orchestrated using Docker Compose.

---

## Data Normalization Strategy

To ensure identity unification across multiple data sources, the system uses a
**canonical normalization model**.

### Canonical Assets
- Stored in the `assets` table
- Each asset is uniquely identified by `canonical_symbol`

### Source-Specific Records
- Stored in the `asset_sources` table
- Linked to `assets` via `asset_id`
- Preserves source-specific symbols, prices, and raw payloads

This design ensures:
- One canonical entity per asset
- Multiple sources can contribute data for the same asset
- No duplication of asset identities across sources

---

## Raw Data Preservation

Each ETL pipeline stores raw input data in source-specific raw tables
(e.g. `raw_csv_assets`, `raw_coingecko`) to allow:
- Auditing
- Debugging
- Replay or reprocessing if required

---

## ETL Observability & Reliability

ETL execution is tracked using:

- `etl_runs`
  - run ID
  - status
  - records processed
  - duration (ms)

- `etl_checkpoints`
  - Enables resumability for long-running or interrupted ETL jobs

This ensures visibility into ETL health and production reliability.

---

## Security

- All secrets and credentials are managed via environment variables
- No hardcoded secrets exist in the codebase
- `.env` files are excluded from version control using `.gitignore`

---

## Health Check

The API exposes a health endpoint to verify service and database availability:

GET /health


Example response:
```json
{
  "status": "ok",
  "database": "connected"
}
Deployment

The application is deployed on AWS EC2 using Docker Compose.

Public Health Endpoint
http://13.51.56.51:8000/health


The service runs continuously and is publicly verifiable.

Running Locally

To run the system locally:

docker-compose up --build
