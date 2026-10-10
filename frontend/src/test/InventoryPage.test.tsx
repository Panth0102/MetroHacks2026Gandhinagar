import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

const { mockGet } = vi.hoisted(() => ({ mockGet: vi.fn() }));
vi.mock("@/lib/api-client", async (importActual) => {
  const actual = await importActual<typeof import("@/lib/api-client")>();
  return { ...actual, api: { ...actual.api, get: mockGet } };
});

import { InventoryPage } from "@/features/inventory/InventoryPage";
import { renderWithProviders } from "./utils";

const SPACES = {
  items: [
    { id: 1, station_id: 1, space_code: "STN01-S01", space_type: "retail", area_sqm: "30.00", floor_description: "Concourse", visibility_score: "8.00", status: "vacant", asking_monthly_rent: "80000.00", available_from: null },
    { id: 2, station_id: 1, space_code: "STN01-S02", space_type: "kiosk", area_sqm: "10.00", floor_description: null, visibility_score: null, status: "occupied", asking_monthly_rent: null, available_from: null },
    { id: 3, station_id: 2, space_code: "STN02-S01", space_type: "advertising_panel", area_sqm: null, floor_description: null, visibility_score: "6.00", status: "vacant", asking_monthly_rent: null, available_from: null },
  ],
  total: 3,
  limit: 200,
  offset: 0,
};
const RATE_CARD = [
  { space_id: 1, space_code: "STN01-S01", station_id: 1, station_name: "Riverfront", space_type: "retail", status: "vacant", area_sqm: "30.00", observed_daily_footfall: 30000, indicative_monthly_price: "95000", model_version: "v1.0-heuristic", data_quality: "high", available: true },
  { space_id: 2, space_code: "STN01-S02", station_id: 1, station_name: "Riverfront", space_type: "kiosk", status: "occupied", area_sqm: "10.00", observed_daily_footfall: 30000, indicative_monthly_price: "22000", model_version: "v1.0-heuristic", data_quality: "medium", available: true },
  { space_id: 3, space_code: "STN02-S01", station_id: 2, station_name: "Old Town", space_type: "advertising_panel", status: "vacant", area_sqm: null, observed_daily_footfall: 15000, indicative_monthly_price: "48000", model_version: "v1.0-heuristic", data_quality: "medium", available: true },
];
const STATIONS = {
  items: [
    { id: 1, code: "STN01", name: "Riverfront", line: "Blue", station_type: null, location_description: null, is_active: true },
    { id: 2, code: "STN02", name: "Old Town", line: "Blue", station_type: null, location_description: null, is_active: true },
  ],
  total: 2,
  limit: 200,
  offset: 0,
};

function route(path: string) {
  if (path.startsWith("/api/v1/inventory")) return Promise.resolve(SPACES);
  if (path.startsWith("/api/v1/pricing/rate-card")) return Promise.resolve(RATE_CARD);
  if (path.startsWith("/api/v1/stations")) return Promise.resolve(STATIONS);
  return Promise.reject(new Error(`unhandled ${path}`));
}

describe("InventoryPage", () => {
  beforeEach(() => {
    mockGet.mockReset();
    mockGet.mockImplementation((path: string) => route(path));
  });

  it("renders fetched spaces with merged indicative prices", async () => {
    renderWithProviders(<InventoryPage />);
    expect(await screen.findByText("STN01-S01")).toBeInTheDocument();
    const row = screen.getByText("STN01-S01").closest("tr")!;
    expect(within(row).getByText(/95,000/)).toBeInTheDocument();
  });

  it("filters rows by the search box", async () => {
    const user = userEvent.setup();
    renderWithProviders(<InventoryPage />);
    await screen.findByText("STN01-S01");
    await user.type(screen.getByLabelText("Search"), "STN02");
    await waitFor(() => {
      expect(screen.queryByText("STN01-S01")).not.toBeInTheDocument();
      expect(screen.getByText("STN02-S01")).toBeInTheDocument();
    });
  });

  it("shows an empty state when no rows match", async () => {
    const user = userEvent.setup();
    renderWithProviders(<InventoryPage />);
    await screen.findByText("STN01-S01");
    await user.type(screen.getByLabelText("Search"), "ZZZ-nonexistent");
    expect(await screen.findByText(/No spaces match these filters/i)).toBeInTheDocument();
  });

  it("sorts by indicative price descending", async () => {
    const user = userEvent.setup();
    renderWithProviders(<InventoryPage />);
    await screen.findByText("STN01-S01");
    await user.selectOptions(screen.getByLabelText("Sort by"), "price_desc");
    const codes = screen.getAllByText(/STN0\d-S\d\d/).map((el) => el.textContent);
    expect(codes[0]).toBe("STN01-S01"); // 95000 is highest
  });
});
