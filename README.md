# Metro Revenue Intelligence

> Turning Metro Station Footfall into Revenue Opportunities

A full-stack data platform that helps metro operators monetize vacant retail spaces and advertising panels. It analyzes passenger footfall, identifies commercially valuable locations, recommends indicative prices, and generates data-backed sales proposals for prospective tenants and advertisers.

Built for **Metro Hacks — Problem Statement PS-06: Footfall to Revenue**.

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Solution](#solution)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [API Reference](#api-reference)
- [Environment Variables](#environment-variables)
- [Database](#database)
- [Testing](#testing)
- [Disclaimer](#disclaimer)

---

## Problem Statement

Metro stations attract large numbers of passengers daily, making them valuable locations for retail businesses and advertisers. However, metro operators often struggle to:

- Demonstrate the commercial value of vacant spaces and advertising panels
- Set competitive, data-backed rental rates
- Identify high-potential locations across the network
- Quickly generate sales proposals for prospective tenants

## Solution

Metro Revenue Intelligence converts raw station footfall data into actionable commercial insights through a REST API backend and an interactive React dashboard.

## Features

| Feature | Description |
|---|---|
| Footfall Analytics | Passenger traffic by station, date, and hour — peak periods, trends, and comparisons |
| Commercial Inventory | Track vacant and occupied retail spaces and advertising panels |
| Smart Rate Cards | Explainable, heuristic-based pricing using footfall and space attributes |
| Revenue Opportunity Ranking | Rank vacant spaces by estimated commercial potential |
| AI Sales Proposals | Generate data-backed sales pitches via Claude API with PDF export |
| Revenue Forecasting | Scenario modelling for potential occupancy improvements |
| Tenant Recommendations | Suggest suitable business categories based on station demographics |

## Tech Stack

### Backend
| | |
|---|---|
| Language | Python 3.11+ |
| Framework | FastAPI |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| Database | SQLite (dev) / PostgreSQL (production) |
| Analytics | Pandas, NumPy |
| AI | Anthropic Claude API |
| PDF Generation | ReportLab |
| Testing | Pytest, pytest-cov |
| Linting | Ruff |

### Frontend
| | |
|---|---|
| Framework | React 18 + TypeScript |
| Build Tool | Vite |
| Styling | Tailwind CSS |
| Data Fetching | TanStack Query v5 |
| Routing | React Router v6 |
| Charts | Recharts |
| Icons | Lucide React |
| Testing | Vitest, Testing Library |

## Architecture

```
Footfall Data + Commercial Inventory
              │
              ▼
    FastAPI Backend (Python)
              │
    ┌─────────┴──────────┐
    ▼                    ▼
PostgreSQL/SQLite    Analytics &
   (SQLAlchemy)      Pricing Engine
    ▼                    ▼
Alembic Migrations  Revenue Insights
              │
              ▼
     REST API (/api/v1/*)
              │
              ▼
   React Dashboard (Vite + TS)
              │
     ┌────────┴────────┐
     ▼                 ▼
  Analytics UI    AI Proposal
  & Rate Cards    Generator
                       │
                       ▼
                  PDF / CSV Export
```

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── analytics.py       # Footfall analytics endpoints
│   │   │       ├── footfall.py        # Raw footfall records
│   │   │       ├── forecasts.py       # Revenue forecasting
│   │   │       ├── health.py          # Health check
│   │   │       ├── inventory.py       # Commercial spaces
│   │   │       ├── pricing.py         # Rate card engine
│   │   │       ├── proposals.py       # AI proposal generation
│   │   │       └── stations.py        # Station management
│   │   ├── core/
│   │   │   ├── config.py              # Settings (pydantic-settings)
│   │   │   └── logging.py
│   │   ├── db/
│   │   │   ├── base.py                # SQLAlchemy base & session
│   │   │   └── models/                # ORM models
│   │   ├── schemas/                   # Pydantic request/response schemas
│   │   ├── services/                  # Business logic
│   │   │   ├── analytics_service.py
│   │   │   ├── footfall_service.py
│   │   │   ├── forecasting_service.py
│   │   │   ├── inventory_service.py
│   │   │   ├── pdf_service.py
│   │   │   ├── pricing_service.py
│   │   │   ├── proposal_generation_service.py
│   │   │   ├── proposal_service.py
│   │   │   └── tenant_recommendation_service.py
│   │   └── main.py
│   ├── alembic/                       # DB migrations
│   ├── scripts/
│   │   ├── generate_sample_data.py    # Synthetic data generator
│   │   └── seed_database.py           # DB seeder
│   ├── tests/                         # Pytest test suite
│   ├── .env.example
│   └── pyproject.toml
│
└── frontend/
    ├── src/
    │   ├── app/                       # Router setup
    │   ├── components/                # Shared UI components
    │   ├── features/
    │   │   ├── overview/              # Dashboard overview
    │   │   ├── stations/              # Station explorer
    │   │   ├── inventory/             # Commercial spaces
    │   │   ├── pricing/               # Rate cards
    │   │   ├── opportunities/         # Revenue opportunities
    │   │   ├── proposals/             # AI proposal generator
    │   │   └── scenarios/             # Forecast scenarios
    │   ├── hooks/                     # Custom React hooks
    │   ├── lib/                       # API client, query client
    │   └── types/                     # TypeScript type definitions
    ├── .env.example
    └── package.json
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- Git
- PostgreSQL *(optional — SQLite works out of the box for development)*

### 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd metro-revenue-intelligence
```

### 2. Backend Setup

```bash
cd backend

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Create your .env file
cp .env.example .env
```

The default `.env` uses SQLite (`metro_dev.db`) — no database server needed for development.

To use PostgreSQL instead, update `DATABASE_URL` in `.env`:

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@localhost:5432/metro_revenue
```

### 3. Run Database Migrations

```bash
alembic upgrade head
```

### 4. Seed Sample Data

```bash
python scripts/seed_database.py
```

This populates the database with synthetic stations, footfall records, commercial spaces, and pricing configuration.

### 5. Start the Backend

```bash
uvicorn app.main:app --reload
```

| Endpoint | URL |
|---|---|
| API base | `http://127.0.0.1:8000` |
| Interactive docs (Swagger) | `http://127.0.0.1:8000/docs` |
| Alternative docs (ReDoc) | `http://127.0.0.1:8000/redoc` |

### 6. Frontend Setup

Open a **second terminal**:

```bash
cd frontend

# Install dependencies
npm install

# Create your .env file
cp .env.example .env

# Start the dev server
npm run dev
```

Vite will print the local URL — usually `http://localhost:5173`.

---

## API Reference

All business endpoints are prefixed with `/api/v1`.

| Route | Description |
|---|---|
| `GET /health` | Health check |
| `GET /api/v1/stations` | List all metro stations |
| `GET /api/v1/footfall` | Query footfall records |
| `GET /api/v1/analytics` | Aggregated footfall analytics |
| `GET /api/v1/inventory` | Commercial space inventory |
| `GET /api/v1/pricing` | Rate card calculations |
| `GET /api/v1/forecasts` | Revenue forecasting scenarios |
| `POST /api/v1/proposals` | Generate an AI sales proposal |

Full request/response schemas are available in the Swagger UI at `/docs`.

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./metro_dev.db` | Database connection string |
| `ANTHROPIC_API_KEY` | *(empty)* | Claude API key for AI proposals. Leave blank for template-only mode |
| `AI_MODEL` | `claude-sonnet-4-5` | Claude model to use |
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated allowed origins |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `PRICING_MODEL_VERSION` | `v1.0-heuristic` | Active pricing model identifier |
| `BASE_RATE_PER_SQM` | `1800` | Base monthly rate per m² (₹) |
| `BASE_PANEL_RATE` | `45000` | Base monthly advertising panel rate (₹) |
| `REFERENCE_DAILY_FOOTFALL` | `20000` | Footfall baseline for pricing normalization |

### Frontend (`frontend/.env`)

| Variable | Default | Description |
|---|---|---|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Backend API base URL |

---

## Database

The schema includes the following tables:

| Table | Description |
|---|---|
| `stations` | Metro station master data |
| `footfall_records` | Hourly entry/exit counts per station |
| `commercial_spaces` | Retail and advertising inventory |
| `leases` | Active and historical lease records |
| `pricing_configs` | Versioned pricing model configuration |
| `proposals` | Generated sales proposals |

Migrations are managed with Alembic. To create a new migration after model changes:

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

---

## Testing

### Backend

```bash
cd backend
source .venv/bin/activate
pytest                    # Run all tests
pytest --cov=app          # With coverage report
```

### Frontend

```bash
cd frontend
npm run test              # Single run (Vitest)
npm run test:watch        # Watch mode
npm run typecheck         # TypeScript type check
npm run lint              # ESLint
```

### Production Build

```bash
cd frontend
npm run build
npm run preview
```

---

## Disclaimer

All station and footfall data is **synthetic** unless explicitly stated otherwise. Pricing recommendations and revenue forecasts are **indicative estimates** produced by a heuristic model — they are not verified market rates or guaranteed earnings. Footfall indicates potential exposure but does not independently establish advertising impressions, customer conversion, or actual sales.

---

## Acknowledgements

Developed for **Metro Hacks**, addressing **PS-06: Footfall to Revenue**.

**Project:** Metro Revenue Intelligence  
**Domain:** Data Analytics · Urban Mobility · Commercial Revenue Optimization · AI-Assisted Reporting
