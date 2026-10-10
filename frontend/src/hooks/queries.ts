import { useMutation, useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api-client";
import type {
  AnalyticsOverview,
  CommercialSpace,
  FootfallSummary,
  ForecastResult,
  Page,
  PeakHoursResult,
  PricingEstimate,
  PricingEstimateRequest,
  RateCardItem,
  RevenueOpportunity,
  Station,
  StationFootfallRank,
} from "@/types/api";

export const keys = {
  overview: ["analytics", "overview"] as const,
  stationRanking: ["analytics", "stations"] as const,
  peakHours: (stationId?: number) => ["analytics", "peak-hours", stationId ?? "all"] as const,
  opportunities: (stationId?: number, limit?: number) =>
    ["analytics", "opportunities", stationId ?? "all", limit ?? 20] as const,
  stations: (params: object) => ["stations", params] as const,
  station: (id: number) => ["stations", id] as const,
  footfallSummary: (stationId?: number, start?: string, end?: string) =>
    ["footfall", "summary", stationId ?? "all", start ?? "", end ?? ""] as const,
  inventory: (params: object) => ["inventory", params] as const,
  space: (id: number) => ["inventory", id] as const,
  inventorySummary: (stationId?: number) => ["inventory", "summary", stationId ?? "all"] as const,
  rateCard: (params: object) => ["pricing", "rate-card", params] as const,
  priceSpace: (id: number) => ["pricing", "space", id] as const,
  forecast: (stationId?: number) => ["forecasts", "revenue", stationId ?? "all"] as const,
};

export function useOverview() {
  return useQuery({
    queryKey: keys.overview,
    queryFn: ({ signal }) => api.get<AnalyticsOverview>("/api/v1/analytics/overview", undefined, signal),
  });
}

export function useStationRanking() {
  return useQuery({
    queryKey: keys.stationRanking,
    queryFn: ({ signal }) =>
      api.get<StationFootfallRank[]>("/api/v1/analytics/stations", undefined, signal),
  });
}

export function usePeakHours(stationId?: number) {
  return useQuery({
    queryKey: keys.peakHours(stationId),
    queryFn: ({ signal }) =>
      api.get<PeakHoursResult>("/api/v1/analytics/peak-hours", { station_id: stationId }, signal),
  });
}

export function useOpportunities(stationId?: number, limit = 20) {
  return useQuery({
    queryKey: keys.opportunities(stationId, limit),
    queryFn: ({ signal }) =>
      api.get<RevenueOpportunity[]>(
        "/api/v1/analytics/revenue-opportunities",
        { station_id: stationId, limit },
        signal,
      ),
  });
}

export function useStations(params: { active_only?: boolean; limit?: number; offset?: number } = {}) {
  return useQuery({
    queryKey: keys.stations(params),
    queryFn: ({ signal }) => api.get<Page<Station>>("/api/v1/stations", params, signal),
  });
}

export function useStation(id: number | undefined) {
  return useQuery({
    queryKey: keys.station(id ?? -1),
    enabled: id !== undefined,
    queryFn: ({ signal }) => api.get<Station>(`/api/v1/stations/${id}`, undefined, signal),
  });
}

export function useFootfallSummary(stationId?: number, start?: string, end?: string) {
  return useQuery({
    queryKey: keys.footfallSummary(stationId, start, end),
    queryFn: ({ signal }) =>
      api.get<FootfallSummary>(
        "/api/v1/footfall/summary",
        { station_id: stationId, start_date: start, end_date: end },
        signal,
      ),
  });
}

export function useInventory(params: {
  station_id?: number;
  status?: string;
  space_type?: string;
  limit?: number;
  offset?: number;
}) {
  return useQuery({
    queryKey: keys.inventory(params),
    queryFn: ({ signal }) => api.get<Page<CommercialSpace>>("/api/v1/inventory", params, signal),
  });
}

export function useSpace(id: number | undefined) {
  return useQuery({
    queryKey: keys.space(id ?? -1),
    enabled: id !== undefined,
    queryFn: ({ signal }) => api.get<CommercialSpace>(`/api/v1/inventory/${id}`, undefined, signal),
  });
}

export function useInventorySummary(stationId?: number) {
  return useQuery({
    queryKey: keys.inventorySummary(stationId),
    queryFn: ({ signal }) =>
      api.get<import("@/types/api").InventorySummary>(
        "/api/v1/inventory/summary",
        { station_id: stationId },
        signal,
      ),
  });
}

export function useRateCard(params: {
  station_id?: number;
  vacant_only?: boolean;
  limit?: number;
}) {
  return useQuery({
    queryKey: keys.rateCard(params),
    queryFn: ({ signal }) => api.get<RateCardItem[]>("/api/v1/pricing/rate-card", params, signal),
  });
}

export function usePriceSpace(id: number | undefined) {
  return useQuery({
    queryKey: keys.priceSpace(id ?? -1),
    enabled: id !== undefined,
    queryFn: ({ signal }) =>
      api.get<PricingEstimate>(`/api/v1/pricing/spaces/${id}`, undefined, signal),
  });
}

export function useForecast(stationId?: number) {
  return useQuery({
    queryKey: keys.forecast(stationId),
    queryFn: ({ signal }) =>
      api.get<ForecastResult>("/api/v1/forecasts/revenue", { station_id: stationId }, signal),
  });
}

export function useEstimateMutation() {
  return useMutation({
    mutationFn: (body: PricingEstimateRequest) =>
      api.post<PricingEstimate>("/api/v1/pricing/estimate", body),
  });
}
