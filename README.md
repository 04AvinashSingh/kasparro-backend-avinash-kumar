# Backend & ETL System – Kasparro Assignment

This repository contains a **production-style Backend & ETL system** built as part of the **Kasparro Backend & ETL Systems assignment**.

The goal of this project was not only to make things work, but to design a system that is **deployable, resilient, maintainable, and easy to reason about**, similar to real-world backend systems.

---

##  Assignment Focus

This assignment emphasizes **production-grade backend engineering**, including:

- Data ingestion pipelines (ETL)
- Backend APIs
- Dockerization and reproducibility
- Recovery and startup resilience
- Clean, scalable architecture
- Cloud deployment readiness

🔗 **Assignment Document**  
https://drive.google.com/file/d/1KYZ9XLV6ByF7fBcCgHfHmhUsG7yW1all/view

---

## Tech Stack

- **Backend Framework**: FastAPI (Python)
- **Database**: PostgreSQL 14
- **ETL**: Python-based ingestion and transformation
- **Containerization**: Docker & Docker Compose
- **Cloud**: AWS EC2 (Ubuntu)

---

##  System Architecture

## 🧠 System Architecture

- **AWS EC2 (Ubuntu)**
  - **FastAPI Backend (Docker)**
    - API layer (health & data endpoints)
    - Startup logic with recovery handling
    - ETL-related initialization
  - **PostgreSQL Database (Docker)**
    - Normalized asset data storage
  - **Docker Compose**
    - Service orchestration
    - Health checks
    - Environment-based configuration




### Key Architectural Decisions
- Backend and database run as **separate containers**
- Containers communicate using Docker’s internal network
- Database readiness is handled explicitly using **health checks**
- API startup is designed to be **resilient**, not fragile

---

##  Folder Structure

Root Directory

api/
FastAPI application entry point and API route definitions

core/
Core application logic, shared utilities, and configuration helpers

data/
Local data files used for ingestion, testing, or development reference

db/
Database-related logic such as connection handling, migrations, or helpers

ingestion/
ETL pipelines and data ingestion workflows from external sources

schemas/
Data models and schemas used for validation and serialization

tests/
Unit and integration tests for backend and ETL components

.pytest_cache/
Pytest cache directory (auto-generated during test runs)

.env
Environment variables for local and containerized execution

Dockerfile
Docker image definition for the FastAPI backend

docker-compose.yml
Service orchestration, health checks, and environment-based configuration

Makefile
Helper commands for running, testing, and managing the project

pytest.ini
Pytest configuration for test discovery and execution

requirements.txt
Python dependencies required by the project

README.md
Project documentation, architecture overview, and deployment details


This structure makes it easy to:
- Extend ETL logic
- Add new API endpoints
- Test components independently
- Maintain the system long-term

---

## 🌐 External Data Sources (APIs)

The assignment specifies two cryptocurrency APIs:

### API 1: CoinPaprika
- Authenticated API
- Requires an API key
- Intended to test secure credential handling

### API 2: CoinGecko
- Free, open API
- No API key required

### API Usage Note
The system is **architected to support both authenticated and unauthenticated APIs** using environment variables.

- CoinGecko was used as an open data source during development.
- CoinPaprika integration is structured to accept an API key securely via environment variables but was not activated due to the absence of provided credentials.

No API keys are hardcoded.

---

Live Deployment (AWS EC2)

The backend system is deployed on AWS EC2 and is publicly accessible.
Health Check Endpoint:   http://13.51.56.51:8000/health

Sample response:
{
  "status": "ok",
  "database": "connected"
}

This endpoint confirms:
The API service is running
The PostgreSQL database is reachable
The system has started successfully in a cloud environment

## ⚙️ Environment Configuration

All configuration is handled through environment variables to ensure security and portability:

```env
DB_HOST=db
DB_PORT=5432
DB_NAME=kasparro
DB_USER=postgres
DB_PASSWORD=avinash79




