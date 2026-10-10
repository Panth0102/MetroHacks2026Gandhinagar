# Metro Revenue Intelligence — Phase 1 Backend

Backend and analytics foundation for **Metro Hacks PS-06: Footfall to Revenue**.
It turns station footfall + commercial inventory into occupancy metrics, an
explainable indicative rate card, ranked vacant-space opportunities, and
transparent revenue scenarios — all exposed via a documented FastAPI REST API.

> **All bundled data is SYNTHETIC** (fixed-seed generator). It is **not** official
> Ahmedabad Metro, GMRC, AMTS, BRTS, or any real operator data. Pricing is an
> **indicative heuristic**, not a verified market rate or a statistical forecast.

---

## 1. Scope

**Phase 1 implements** (this repo):

- Relational schema: stations, footfall, commercial spaces, leases, pricing config.
- Deterministic synthetic data generation + **idempotent** seeding.
- Footfall analytics (totals, averages, peak hours, weekday/weekend, ranking,
  period comparison, coverage).
- Inventory analytics (occupancy/vacancy by count and by area, current vs
  potential revenue, with documented denominators).
- **Explainable deterministic pricing engine** with bounded factors + breakdown.
- Ranked, explainable vacant-space revenue opportunities.
- Transparent scenario-based revenue forecasting (50/75/100%).
- Versioned FastAPI endpoints under `/api/v1`, OpenAPI docs, pagination, validation.
- Tests (pytest), lint/format (Ruff), Alembic migrations.

**Out of scope for Phase 1** (deliberately not built): React frontend, LLM sales
copy, authentication, deployment infrastructure.

---

## 2. Technology stack

Python 3.11+ (verified on 3.14) · FastAPI · Uvicorn · Pydantic v2 ·
pydantic-settings · SQLAlchemy 2.x · psycopg 3 · Alembic · Pandas/NumPy ·
pytest · HTTPX · pytest-cov · Ruff.

---

## 3. Project structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app + health routes
│   ├── core/                # config (env), logging
│   ├── db/                  # base, session, models/
│   ├── schemas/             # Pydantic request/response contracts
│   ├── api/                 # router + routes/ (health, stations, footfall, …)
│   └── services/            # business logic (footfall, inventory, pricing, …)
├── scripts/                 # generate_sample_data.py, seed_database.py
├── data/sample/             # generated synthetic JSON (git-ignored output)
├── alembic/                 # migrations
├── tests/                   # pytest suite
├── pyproject.toml  .env.example  .gitignore  alembic.ini
```

---

## 4. Setup (macOS)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env            # adjust DATABASE_URL if using Postgres
```

### Database

**Option A — SQLite (zero setup, default).** `DATABASE_URL=sqlite:///./metro_dev.db`.

**Option B — PostgreSQL.** Create a DB and point `DATABASE_URL` at it:

```bash
createdb metro      # or: psql -c "CREATE DATABASE metro;"
# .env:
# DATABASE_URL=postgresql+psycopg://USER:PASSWORD@localhost:5432/metro
```

### Migrations + seed

```bash
alembic upgrade head                 # create schema (both SQLite & Postgres)
python scripts/generate_sample_data.py   # (optional) dump synthetic JSON to data/sample/
python scripts/seed_database.py          # idempotent; safe to re-run
# SQLite without Alembic? use: python scripts/seed_database.py --create-tables
```

Seeding is **idempotent** (re-running creates 0 duplicates) and refuses to run
against `ENVIRONMENT=production` without `--force`.

### Run the server

```bash
uvicorn app.main:app --reload
```

- Swagger UI: http://localhost:8000/docs
- ReDoc:      http://localhost:8000/redoc
- OpenAPI:    http://localhost:8000/openapi.json

### Tests, lint, format

```bash
pytest -q                         # test suite
pytest --cov=app --cov-report=term-missing
ruff check .                      # lint
ruff format --check .             # format check
```

---

## 5. API endpoints

All collection endpoints are paginated (`limit`, `offset`) and return
`{items, total, limit, offset}`.

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness |
| GET | `/health/ready` | Readiness + real DB connectivity |
| GET | `/api/v1/stations` | List stations (`active_only`) |
| GET | `/api/v1/stations/{id}` | Station by id (404 if missing) |
| GET | `/api/v1/footfall` | Raw footfall rows (`station_id`, `start_date`, `end_date`) |
| GET | `/api/v1/footfall/summary` | Aggregated footfall metrics |
| GET | `/api/v1/footfall/stations/{id}` | Summary for one station |
| GET | `/api/v1/inventory` | List spaces (`station_id`, `status`, `space_type`) |
| GET | `/api/v1/inventory/{id}` | Space by id |
| GET | `/api/v1/inventory/summary` | Occupancy / revenue metrics |
| GET | `/api/v1/analytics/overview` | Portfolio snapshot |
| GET | `/api/v1/analytics/stations` | Footfall ranking |
| GET | `/api/v1/analytics/occupancy` | Occupancy metrics (= inventory summary) |
| GET | `/api/v1/analytics/peak-hours` | Hourly demand distribution + peak |
| GET | `/api/v1/analytics/revenue-opportunities` | Ranked vacant spaces |
| GET | `/api/v1/pricing/rate-card` | Indicative rate card (vacant by default) |
| GET | `/api/v1/pricing/spaces/{id}` | Full pricing breakdown for a space |
| POST | `/api/v1/pricing/estimate` | Ad-hoc estimate from supplied attributes |
| GET | `/api/v1/forecasts/revenue` | Scenario-based revenue estimate |
| GET | `/api/v1/forecasts/scenarios` | Alias of `/revenue` |

---

## 6. Pricing formula (v1 heuristic)

Deterministic, bounded, fully configurable (DB `pricing_config` row, falling back
to env settings). Final currency in **Decimal**, rounded half-up to whole INR.
Dimensionless factors are computed in float then converted to Decimal **before**
the money multiplication, so no binary float touches a rupee amount.

```
footfall_factor  = clamp( (observed_daily_footfall / reference_daily_footfall) ^ elasticity,
                          min_footfall_factor, max_footfall_factor )
visibility_factor= clamp( 1 + (visibility - reference_visibility) * visibility_weight,
                          min_visibility_factor, max_visibility_factor )
type_factor      = space_type_multipliers[space_type]

# area-priced (retail, kiosk): area required, else UNAVAILABLE (area never fabricated)
base_component   = base_rate_per_sqm * area_sqm
# unit-priced (advertising_panel, digital_screen): area optional
base_component   = base_panel_rate

indicative_monthly_price = round( base_component * footfall_factor
                                  * visibility_factor * type_factor )
```

**Missing-input policy (never fabricated):**
- Area-priced space with no area → `available=false`, no price.
- No station footfall → neutral `factor=1.0`, flagged in `limitations`, quality lowered.
- No visibility → neutral `factor=1.0`, flagged, quality lowered.

`data_quality` is `high|medium|low` by **input completeness only** — it is **not**
a probability or calibrated confidence. Each response returns `factors`
(per-factor contribution), `assumptions`, `model_version`, `explanation`, and
`limitations`.

---

## 7. Analytics metric definitions

**Footfall.** `entries` = boardings (primary demand signal); `exits` tracked
separately and **never summed** into "visitors". `avg_daily_entries` =
total entries / distinct observed days. `coverage_ratio` = observed hour-slots /
expected over the span (distinguishes missing data from genuine zeros). Peak hour
reports **all tied hours**. Period comparison returns `pct_change=null` when the
baseline is zero and flags unequal-length periods.

**Inventory.**
- `occupancy_rate_by_count` = occupied / **all** spaces.
- `occupancy_rate_by_area` = occupied area / **(occupied+vacant known-area pool)**.
- `current_monthly_revenue` = sum of **signed ACTIVE lease** rents.
- `potential_vacant_monthly_rent` = sum of **asking** rent on **vacant** spaces only.
- Under-maintenance / unavailable spaces are **never** counted as vacant inventory.

**Opportunities.** Priority score (0–100) = `0.5·revenue + 0.3·footfall +
0.2·data_quality`, each normalized against candidate peers. Revenue (which already
embeds area, visibility, and type) dominates, so ranking is **not** driven by raw
passenger count alone. `estimated_annual_asking_revenue` = asking × 12, explicitly
**not** a forecast.

---

## 8. Forecast assumptions & limitations

Method = `scenario-baseline` (`is_predictive_model: false`). Not an ML model.
- `current_*_revenue` from active leases.
- `eligible_vacant_potential_monthly_rent` = pricing-engine output on vacant spaces.
- Scenarios let 50% / 75% / 100% of eligible vacant inventory at indicative asking.
- Annualized = monthly × 12 (no churn, seasonality, ramp-up, or lease-up rate).
- Assumes asking prices are achieved; real outcomes will differ.

---

## 9. Sample requests & responses

```bash
curl "http://localhost:8000/api/v1/analytics/overview"
```
```json
{
  "station_count": 8, "active_station_count": 8,
  "footfall_observation_count": 4320,
  "footfall_date_range": {"start": "2026-09-02", "end": "2026-10-01"},
  "total_entries_observed": 6377190, "total_spaces": 42,
  "occupancy_rate_by_count": 0.2857,
  "current_monthly_revenue": "1921000.00",
  "potential_vacant_monthly_rent": "1468000.00",
  "notes": ["All footfall figures are observed entries; synthetic demo data."]
}
```

```bash
curl -X POST "http://localhost:8000/api/v1/pricing/estimate" \
  -H "Content-Type: application/json" \
  -d '{"space_type":"retail","area_sqm":25,"visibility_score":7,"observed_daily_footfall":30000}'
```
```json
{
  "available": true, "is_indicative": true, "currency": "INR",
  "model_version": "v1.0-heuristic", "space_type": "retail",
  "base_component": "45000", "indicative_monthly_price": "58952",
  "indicative_annual_price": "707424",
  "factors": [
    {"name":"base_component","value":45000.0,"description":"25 sqm x base 1800/sqm"},
    {"name":"footfall_factor","value":1.1279,"description":"demand adjustment (bounded)"},
    {"name":"visibility_factor","value":1.16,"description":"visibility adjustment (bounded)"},
    {"name":"space_type_factor","value":1.0,"description":"multiplier for retail"}
  ],
  "data_quality": "high",
  "explanation": "Indicative monthly asking price INR 58952 for a retail space ...",
  "limitations": []
}
```

A ranked opportunity (`GET /api/v1/analytics/revenue-opportunities`) additionally
returns `priority_score`, `score_breakdown`, `reasons`, and `limitations` — the
data needed to generate a Phase 3 one-page sales pitch.

---

## 10. Phase 2 integration contract

The frontend can rely on these **stable** response schemas (see `/openapi.json`):

- **Lists** → `Page[T]`: `{items, total, limit, offset}`.
- **Station** → `StationOut`.
- **Footfall** → `FootfallSummary` (totals, peaks, weekday/weekend, hourly dist, coverage).
- **Inventory** → `SpaceOut`, `InventorySummary` (documented denominators).
- **Pricing** → `PricingEstimate` (price + `factors` + `data_quality` + `explanation`),
  `RateCardItem` for the rate card.
- **Opportunities** → `RevenueOpportunity` (price, `priority_score`, `score_breakdown`,
  `reasons`, `limitations`) — the sales-pitch payload.
- **Forecast** → `ForecastResult` with `scenarios[]`.

Money fields are strings (Decimal). Enums: `space_type` ∈
{retail, kiosk, advertising_panel, digital_screen}; `status` ∈
{vacant, occupied, under_maintenance, unavailable}.

---

## 11. Known limitations

- Synthetic demo data only; pricing coefficients are indicative assumptions.
- Scenario forecasts, not trained predictions.
- No auth/rate-limiting (Phase 1 scope); do not expose publicly as-is.
- Timezone is a documented convention (`Asia/Kolkata`); footfall uses date + hour band.
- No lease write API ships in Phase 1; the seeder enforces one active lease per
  space and the DB enforces lease date ordering. A general overlap-validating
  write endpoint is Phase 2+.

See `data/sample/README.txt` (after generation) for the synthetic dataset summary.

