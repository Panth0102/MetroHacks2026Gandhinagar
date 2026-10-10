# Metro Revenue Intelligence

**Turning Metro Station Footfall into Revenue Opportunities**

Metro Revenue Intelligence is a data-driven platform designed to help metro operators monetize vacant retail spaces and advertising panels. It analyzes passenger footfall, identifies commercially valuable locations, recommends indicative prices, and generates data-backed sales proposals for prospective tenants and advertisers.

Built for **Metro Hacks — Problem Statement PS-06: Footfall to Revenue**.

---

## Problem Statement

Metro stations attract large numbers of passengers, making them valuable locations for retail businesses and advertising. However, metro operators may struggle to demonstrate the commercial value of vacant spaces and advertising panels.

Without clear footfall insights and data-backed pricing, it becomes difficult to set competitive rates, identify high-potential locations, and convince prospective tenants or advertisers to invest.

## Our Solution

Metro Revenue Intelligence converts station footfall data into actionable commercial insights.

The platform aims to help metro operators understand passenger traffic patterns, evaluate vacant commercial inventory, estimate potential revenue, and generate sales proposals supported by data.

## Key Features

1. **Footfall Analytics** — Analyze passenger traffic by station, date, and time to identify high-footfall locations and peak periods.
2. **Commercial Inventory Management** — Track vacant and occupied retail spaces and advertising panels, including their locations and characteristics.
3. **Smart Rate Cards** — Calculate explainable, indicative prices using footfall and commercial-space attributes.
4. **Revenue Opportunity Ranking** — Rank vacant spaces by estimated commercial potential and highlight opportunities for improving revenue.
5. **AI-Powered Sales Proposals** — Generate data-backed sales pitches and downloadable PDF proposals for prospective tenants and advertisers.

## Target Users

- **Metro Operators:** Improve commercial space utilization and revenue planning.
- **Commercial Revenue Teams:** Evaluate inventory, prepare rate cards, and prioritize sales opportunities.
- **Retail Businesses:** Identify potentially valuable locations inside metro stations.
- **Advertisers and Agencies:** Compare advertising opportunities across stations.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, TypeScript, Vite |
| UI and Styling | Tailwind CSS, shadcn/ui |
| Data Visualization | Recharts |
| Icons | Lucide |
| Backend API | Python, FastAPI |
| Database | PostgreSQL |
| ORM and Migrations | SQLAlchemy, Alembic |
| Data Analytics | Pandas, NumPy |
| AI Integration | Claude API |
| Testing | Pytest, Vitest, Playwright |
| Development | Claude Code, Git, GitHub |

## System Architecture

```text
Footfall Data + Commercial Inventory
                  |
                  v
        FastAPI Backend
                  |
                  v
      Analytics and Pricing Engine
                  |
          +-------+-------+
          |               |
          v               v
    PostgreSQL       Revenue Insights
          |               |
          +-------+-------+
                  |
                  v
       React Dashboard
                  |
                  v
     AI Sales Proposal Generator
                  |
                  v
       PDF and CSV Exports
```

## How It Works

1. **Load data:** Import or generate station footfall records and commercial inventory information.
2. **Analyze traffic:** Calculate station-level passenger volumes, peak hours, and traffic trends.
3. **Evaluate inventory:** Identify vacant retail spaces and advertising panels.
4. **Estimate prices:** Apply a transparent pricing model to calculate indicative commercial rates.
5. **Identify opportunities:** Rank available spaces using their estimated commercial potential.
6. **Generate proposals:** Use validated analytics to prepare sales proposals for prospective tenants and advertisers.
7. **Export results:** Download rate cards, analytical reports, and sales proposals in supported formats.

## Data and Pricing Methodology

The prototype is designed to support realistic sample data because a production metro footfall dataset may not be available during the hackathon.

The analytics may include:

- Station-wise passenger footfall
- Hourly and daily traffic patterns
- Retail and advertising inventory
- Occupancy and vacancy status
- Indicative rental prices
- Potential revenue scenarios

**Important:** Sample data is synthetic unless explicitly identified otherwise. Pricing recommendations and revenue forecasts are estimates for decision support, not guaranteed earnings or validated market rates.

Footfall indicates potential exposure, but it does not independently establish advertising impressions, customer conversion, or actual sales.

## Project Development Phases

### Phase 1 — Backend and Analytics
- Set up the backend and database.
- Create realistic, reproducible sample datasets.
- Implement footfall analytics and inventory management.
- Develop explainable pricing and revenue opportunity calculations.
- Expose analytics through REST APIs.

### Phase 2 — Frontend and Integration
- Build the interactive analytics dashboard.
- Add station-level visualizations and inventory filters.
- Display rate cards, vacancy rankings, and revenue scenarios.
- Connect the frontend to the backend APIs.

### Phase 3 — AI Intelligence and Reporting
- Generate AI-assisted sales proposals.
- Produce downloadable, one-page PDF proposals.
- Support CSV exports and commercial reporting.
- Add recommendations for potential tenants and advertising opportunities.

## Getting Started

### Prerequisites

Install the following before running the project:

- Python 3.11 or a compatible version supported by the project's dependencies
- Node.js and npm
- PostgreSQL
- Git

### 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd metro-revenue-intelligence
```

Replace the repository URL with your actual GitHub repository URL.

### 2. Configure the Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file using the project's `.env.example` as a reference.

Example configuration:

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@localhost:5432/metro_revenue
ANTHROPIC_API_KEY=
```

Replace the database credentials with your local PostgreSQL configuration. Keep API keys and credentials out of version control.

### 3. Set Up PostgreSQL

Create the project database:

```sql
CREATE DATABASE metro_revenue;
```

Run the database migrations and sample-data initialization commands documented in the backend setup instructions.

### 4. Start the Backend

From the backend directory, activate the virtual environment and run:

```bash
uvicorn app.main:app --reload
```

The API will normally be available at:

- API base URL: `http://127.0.0.1:8000`
- Interactive API documentation: `http://127.0.0.1:8000/docs`

### 5. Start the Frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite in your browser.

> **Setup note:** These commands assume the repository uses `backend/` and `frontend/` directories. Adjust them to match the actual project structure and scripts.

## Testing

Run the tests supported by each project component.

**Backend:**

```bash
pytest
```

**Frontend:**

```bash
npm run test
```

**Production build:**

```bash
npm run build
```

Use the scripts actually defined in the repository's configuration files.

## Security and Reliability

- Store secrets in environment variables.
- Validate API inputs and database operations.
- Keep pricing calculations deterministic and explainable.
- Use AI to communicate validated results rather than invent financial figures.
- Handle missing data and API failures gracefully.
- Clearly label synthetic data, assumptions, and estimates.
- Provide an editable proposal template if AI services are not configured.

## Expected Impact

Metro Revenue Intelligence aims to help metro operators:

- Reduce the time required to evaluate vacant commercial inventory.
- Make pricing recommendations more consistent and transparent.
- Prioritize potentially valuable retail and advertising locations.
- Prepare sales materials more efficiently.
- Make better-informed commercial revenue decisions.

Actual revenue improvements would need to be validated using real footfall data, market rental rates, occupancy records, and observed commercial performance.

## Current Project Status

The project is being developed in three phases: backend analytics, frontend integration, and AI-assisted reporting.

Features should be marked as complete only after implementation and testing. Until then, they represent planned capabilities rather than verified functionality.

## Future Enhancements

- Integration with real-time metro passenger data.
- Historical revenue and occupancy analysis.
- Market-rate calibration using actual lease data.
- Campaign planning for advertisers.
- Advanced demand forecasting.
- Multi-station portfolio optimization.

## Acknowledgements

Developed for **Metro Hacks**, addressing **PS-06: Footfall to Revenue**.

**Project:** Metro Revenue Intelligence  
**Domain:** Data Analytics, Urban Mobility, Commercial Revenue Optimization, and AI-Assisted Reporting
