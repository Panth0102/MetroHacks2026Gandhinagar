import { screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const { mockGet } = vi.hoisted(() => ({ mockGet: vi.fn() }));
vi.mock("@/lib/api-client", async (importActual) => {
  const actual = await importActual<typeof import("@/lib/api-client")>();
  return { ...actual, api: { ...actual.api, get: mockGet } };
});

import { OpportunitiesPage } from "@/features/opportunities/OpportunitiesPage";
import { renderWithProviders } from "./utils";

const OPPS = [
  {
    space_id: 1, space_code: "A-01", station_id: 1, station_name: "Alpha", space_type: "retail",
    status: "vacant", observed_daily_footfall: 30000, indicative_monthly_price: "100000",
    estimated_annual_asking_revenue: "1200000", priority_score: 92.1,
    score_breakdown: [{ name: "revenue_component", value: 1, description: "price vs max" }],
    reasons: ["high indicative asking rent relative to peers"], limitations: [], data_quality: "high",
  },
  {
    space_id: 2, space_code: "B-02", station_id: 2, station_name: "Beta", space_type: "kiosk",
    status: "vacant", observed_daily_footfall: 10000, indicative_monthly_price: "40000",
    estimated_annual_asking_revenue: "480000", priority_score: 55.4,
    score_breakdown: [], reasons: [], limitations: ["no visibility score"], data_quality: "low",
  },
];
const STATIONS = { items: [], total: 0, limit: 200, offset: 0 };

describe("OpportunitiesPage", () => {
  beforeEach(() => {
    mockGet.mockReset();
    mockGet.mockImplementation((path: string) => {
      if (path.startsWith("/api/v1/analytics/revenue-opportunities")) return Promise.resolve(OPPS);
      if (path.startsWith("/api/v1/stations")) return Promise.resolve(STATIONS);
      return Promise.reject(new Error(`unhandled ${path}`));
    });
  });

  it("lists opportunities and defaults the explanation to the top-ranked space", async () => {
    renderWithProviders(<OpportunitiesPage />);
    expect(await screen.findByText("A-01")).toBeInTheDocument();
    expect(screen.getByText(/Why A-01 ranks/i)).toBeInTheDocument();
    expect(screen.getByText(/price vs max/i)).toBeInTheDocument();
  });

  it("shows the backend reason for the top opportunity", async () => {
    renderWithProviders(<OpportunitiesPage />);
    expect(
      await screen.findByText(/high indicative asking rent relative to peers/i),
    ).toBeInTheDocument();
  });
});
