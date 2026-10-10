# Metro Revenue Intelligence — Phase 2 Frontend

A premium enterprise dashboard for metro commercial-revenue operations, built on
the Phase 1 FastAPI backend (Metro Hacks PS-06: Footfall to Revenue).

> All data is **synthetic** and served by the backend. Pricing is an **indicative
> heuristic**, not a verified market rate. No figure is fabricated in the frontend.

## Stack

React 18 · TypeScript (strict) · Vite 5 · Tailwind CSS · TanStack Query ·
React Router · Recharts · Lucide · Vitest + Testing Library.

## Prerequisites

- Node 18+ (verified on Node 26) and npm.
- The Phase 1 backend running (see `../backend/README.md`).

## Setup

```bash
cd frontend
npm install
cp .env.example .env     # set VITE_API_BASE_URL if the backend is not on :8000
```

`.env`:

```
VITE_API_BASE_URL=http://localhost:8000
```

## Run (backend + frontend together)

Terminal 1 — backend (from `backend/`, venv active):

```bash
uvicorn app.main:app --reload           # http://localhost:8000
```

Terminal 2 — frontend (from `frontend/`):

```bash
npm run dev                              # http://localhost:5173
```

The backend allows the `http://localhost:5173` origin via CORS (configurable with
`CORS_ORIGINS` in the backend `.env`).

## Checks

```bash
npm run typecheck     # tsc --noEmit (strict)
npm run lint          # eslint
npm run test          # vitest + Testing Library
npm run build         # production build (tsc + vite)
npm run preview       # serve the production build
```

## Pages

| Route | Page | Key backend endpoints |
|---|---|---|
| `/` | Executive overview | `/analytics/overview`, `/inventory/summary`, `/analytics/peak-hours`, `/analytics/stations`, `/analytics/revenue-opportunities` |
| `/stations` | Stations & footfall | `/footfall/summary`, `/analytics/stations` |
| `/inventory` | Commercial inventory (search, filter, sort, paginate, CSV) | `/inventory`, `/pricing/rate-card` |
| `/inventory/:id` | Space detail + pricing breakdown | `/inventory/{id}`, `/stations/{id}`, `/footfall/summary`, `/pricing/spaces/{id}` |
| `/pricing` | Rate card + price scenario calculator (CSV) | `/pricing/rate-card`, `/pricing/estimate` |
| `/opportunities` | Ranked vacant-space opportunities | `/analytics/revenue-opportunities` |
| `/scenarios` | Revenue scenarios | `/forecasts/revenue` |
| `/proposals` | Saved sales proposals (list, open, PDF) | `/proposals` |
| `/proposals/new?space_id=` | Generate a proposal from a space | `/proposals/generate`, `/inventory/{id}`, `/pricing/spaces/{id}` |
| `/proposals/:id` | Proposal editor + live preview, save, regenerate, PDF | `/proposals/{id}` (GET/PATCH), `/regenerate`, `/pdf` |

The space detail page (`/inventory/:id`) also shows rules-based **tenant category
recommendations** and a "Generate sales proposal" action. The pricing page offers
both a client-side CSV of the current view and an "Official CSV" from the backend
export (with disclaimer + formula-injection protection).

### Phase 3 notes

- Proposal copy is drafted by the backend (AI when configured, deterministic
  template otherwise). The editor labels AI-generated vs template-generated
  content, keeps unsaved edits when a save fails, and warns before a regenerate
  discards edits. AI credentials live only on the backend.
- PDF/CSV downloads are real backend endpoints opened via direct links.

## Architecture

- `src/lib/api-client.ts` — single typed fetch wrapper; structured `ApiError`.
  No component makes a raw `fetch`.
- `src/types/api.ts` — TypeScript types mirroring the backend Pydantic schemas.
  Money fields are strings (Decimal); no `any` is used for API data.
- `src/hooks/queries.ts` — TanStack Query hooks with stable keys, request
  cancellation (via `signal`), and sensible stale/cache times.
- `src/components/` — layout, charts, tables, filters, feedback, and `ui`
  primitives using design tokens defined in `src/index.css` / `tailwind.config.js`.
- `src/features/` — one folder per page.

## Behaviour under adverse conditions

- **Backend offline** → honest "Backend unavailable" error with a retry action
  (no fabricated data).
- **No data for a station / empty filter** → explicit empty states, not
  zero-filled charts.
- **Missing optional fields** (area, visibility, footfall) → shown as "—" or a
  clearly labelled unavailable state; the pricing breakdown surfaces the backend's
  own limitations.

## Accessibility

Semantic HTML, keyboard-navigable sidebar/drawer, visible focus rings, labelled
form controls, `role="img"` + text summaries for every chart, status/priority
never conveyed by colour alone (text labels + tones), and reduced-motion support.

## Known limitations

- Client-side search/sort/area-range operate over the full filtered result set
  fetched from the server (dataset is small). For a very large dataset, add
  server-side search/sort.
- Playwright end-to-end tests are **not** included/executed here; integration is
  verified via Vitest with mocked schemas, a live CORS check, and the shared
  backend contract. Browser console was checked during development.
- Custom-percentage revenue scenarios are not offered because the backend exposes
  fixed 50/75/100% scenarios only.
- Phase 3 (AI sales proposals, PDF export) is intentionally not implemented.
