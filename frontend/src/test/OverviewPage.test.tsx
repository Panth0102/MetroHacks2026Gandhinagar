import { screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const { mockGet } = vi.hoisted(() => ({ mockGet: vi.fn() }));
vi.mock("@/lib/api-client", async (importActual) => {
  const actual = await importActual<typeof import("@/lib/api-client")>();
  return { ...actual, api: { ...actual.api, get: mockGet } };
});

import { OverviewPage } from "@/features/overview/OverviewPage";
import { renderWithProviders } from "./utils";

const OVERVIEW = {
  station_count: 8,
  active_station_count: 8,
  footfall_observation_count: 4320,
  footfall_date_range: { start: "2026-09-02", end: "2026-10-01" },
  total_entries_observed: 6377190,
  total_spaces: 42,
  occupancy_rate_by_count: 0.2857,
  current_monthly_revenue: "1921000.00",
  potential_vacant_monthly_rent: "1468000.00",
  notes: [],
};
const INV_SUMMARY = {
  station_id: null,
  total_spaces: 42,
  count_by_status: { vacant: 20, occupied: 12, under_maintenance: 6, unavailable: 4 },
  count_by_type: { retail: 15, kiosk: 10, advertising_panel: 10, digital_screen: 7 },
  occupancy_rate_by_count: 0.2857,
  vacancy_rate_by_count: 0.476,
  occupied_area_sqm: "500.00",
  vacant_area_sqm: "600.00",
  occupancy_rate_by_area: 0.45,
  spaces_with_known_area: 30,
  current_monthly_revenue: "1921000.00",
  current_annual_revenue: "23052000.00",
  potential_vacant_monthly_rent: "1468000.00",
  potential_vacant_rent_known_count: 17,
  notes: [],
};
const PEAK = {
  station_id: null,
  observation_count: 4320,
  peak_hour: 18,
  peak_hours_tied: [18],
  buckets: [
    { hour: 8, total_entries: 500000, share: 0.1 },
    { hour: 18, total_entries: 700000, share: 0.14 },
  ],
  notes: [],
};
const RANKING = [
  { station_id: 1, station_name: "Riverfront", total_entries: 1200000, avg_daily_entries: 40000, rank: 1 },
  { station_id: 2, station_name: "Old Town", total_entries: 900000, avg_daily_entries: 30000, rank: 2 },
];
const OPPS = [
  {
    space_id: 22, space_code: "STN05-S03", station_id: 5, station_name: "Stadium", space_type: "retail",
    status: "vacant", observed_daily_footfall: 33771, indicative_monthly_price: "135446",
    estimated_annual_asking_revenue: "1625352", priority_score: 94.9, score_breakdown: [],
    reasons: [], limitations: [], data_quality: "high",
  },
];

function route(path: string) {
  if (path.startsWith("/api/v1/analytics/overview")) return Promise.resolve(OVERVIEW);
  if (path.startsWith("/api/v1/inventory/summary")) return Promise.resolve(INV_SUMMARY);
  if (path.startsWith("/api/v1/analytics/peak-hours")) return Promise.resolve(PEAK);
  if (path.startsWith("/api/v1/analytics/stations")) return Promise.resolve(RANKING);
  if (path.startsWith("/api/v1/analytics/revenue-opportunities")) return Promise.resolve(OPPS);
  return Promise.reject(new Error(`unhandled ${path}`));
}

describe("OverviewPage", () => {
  beforeEach(() => {
    mockGet.mockReset();
    mockGet.mockImplementation((path: string) => route(path));
  });

  it("renders key metrics from the API", async () => {
    renderWithProviders(<OverviewPage />);
    expect(await screen.findByText("28.6%")).toBeInTheDocument(); // occupancy rate
    expect(screen.getByText("Station footfall comparison")).toBeInTheDocument();
    expect(await screen.findByText("STN05-S03")).toBeInTheDocument(); // opportunity row
  });

  it("shows an error state when a request fails", async () => {
    mockGet.mockImplementation(() => Promise.reject(new Error("boom")));
    renderWithProviders(<OverviewPage />);
    expect(await screen.findAllByRole("alert")).not.toHaveLength(0);
  });
});
