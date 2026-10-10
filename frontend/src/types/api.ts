// Types mirror the Phase 1 FastAPI Pydantic schemas. Money fields are serialized
// as strings (Decimal) by the backend and are kept as strings here.

export type SpaceType =
  | "retail"
  | "kiosk"
  | "advertising_panel"
  | "digital_screen";

export type SpaceStatus =
  | "vacant"
  | "occupied"
  | "under_maintenance"
  | "unavailable";

export interface Page<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

export interface Station {
  id: number;
  code: string;
  name: string;
  line: string | null;
  station_type: string | null;
  location_description: string | null;
  is_active: boolean;
}

export interface FootfallRecord {
  id: number;
  station_id: number;
  observation_date: string;
  hour: number;
  entries: number;
  exits: number | null;
  source: string;
}

export interface FootfallSummary {
  station_id: number | null;
  start_date: string | null;
  end_date: string | null;
  observation_count: number;
  distinct_days: number;
  total_entries: number;
  total_exits: number | null;
  avg_hourly_entries: number | null;
  avg_daily_entries: number | null;
  peak_hour: number | null;
  peak_hour_entries: number | null;
  peak_hours_tied: number[];
  weekday_avg_daily_entries: number | null;
  weekend_avg_daily_entries: number | null;
  hourly_distribution: Record<string, number>;
  coverage_ratio: number | null;
  notes: string[];
}

export interface CommercialSpace {
  id: number;
  station_id: number;
  space_code: string;
  space_type: SpaceType;
  area_sqm: string | null;
  floor_description: string | null;
  visibility_score: string | null;
  status: SpaceStatus;
  asking_monthly_rent: string | null;
  available_from: string | null;
}

export interface InventorySummary {
  station_id: number | null;
  total_spaces: number;
  count_by_status: Record<string, number>;
  count_by_type: Record<string, number>;
  occupancy_rate_by_count: number | null;
  vacancy_rate_by_count: number | null;
  occupied_area_sqm: string | null;
  vacant_area_sqm: string | null;
  occupancy_rate_by_area: number | null;
  spaces_with_known_area: number;
  current_monthly_revenue: string;
  current_annual_revenue: string;
  potential_vacant_monthly_rent: string;
  potential_vacant_rent_known_count: number;
  notes: string[];
}

export interface PricingFactor {
  name: string;
  value: number;
  description: string;
}

export interface PricingEstimate {
  available: boolean;
  is_indicative: boolean;
  currency: string;
  model_version: string;
  space_id: number | null;
  space_code: string | null;
  station_id: number | null;
  space_type: SpaceType;
  base_component: string | null;
  indicative_monthly_price: string | null;
  indicative_annual_price: string | null;
  factors: PricingFactor[];
  data_quality: string;
  data_quality_reasons: string[];
  assumptions: Record<string, unknown>;
  explanation: string;
  limitations: string[];
}

export interface PricingEstimateRequest {
  space_type: SpaceType;
  area_sqm?: number | null;
  visibility_score?: number | null;
  observed_daily_footfall?: number | null;
}

export interface RateCardItem {
  space_id: number;
  space_code: string;
  station_id: number;
  station_name: string;
  space_type: SpaceType;
  status: string;
  area_sqm: string | null;
  observed_daily_footfall: number | null;
  indicative_monthly_price: string | null;
  model_version: string;
  data_quality: string;
  available: boolean;
}

export interface StationFootfallRank {
  station_id: number;
  station_name: string;
  total_entries: number;
  avg_daily_entries: number | null;
  rank: number;
}

export interface AnalyticsOverview {
  station_count: number;
  active_station_count: number;
  footfall_observation_count: number;
  footfall_date_range: { start: string | null; end: string | null };
  total_entries_observed: number;
  total_spaces: number;
  occupancy_rate_by_count: number | null;
  current_monthly_revenue: string;
  potential_vacant_monthly_rent: string;
  notes: string[];
}

export interface PeakHourBucket {
  hour: number;
  total_entries: number;
  share: number;
}

export interface PeakHoursResult {
  station_id: number | null;
  observation_count: number;
  peak_hour: number | null;
  peak_hours_tied: number[];
  buckets: PeakHourBucket[];
  notes: string[];
}

export interface RevenueOpportunity {
  space_id: number;
  space_code: string;
  station_id: number;
  station_name: string;
  space_type: string;
  status: string;
  observed_daily_footfall: number | null;
  indicative_monthly_price: string | null;
  estimated_annual_asking_revenue: string | null;
  priority_score: number;
  score_breakdown: PricingFactor[];
  reasons: string[];
  limitations: string[];
  data_quality: string;
}

export interface RevenueScenario {
  name: string;
  occupancy_fraction_of_vacant: number;
  added_monthly_rent: string;
  projected_monthly_revenue: string;
  projected_annual_revenue: string;
  assumptions: string[];
}

export interface ForecastResult {
  method: string;
  is_predictive_model: boolean;
  currency: string;
  current_monthly_revenue: string;
  current_annual_revenue: string;
  eligible_vacant_potential_monthly_rent: string;
  eligible_vacant_space_count: number;
  scenarios: RevenueScenario[];
  assumptions: string[];
  limitations: string[];
}

// ---- Phase 3: proposals, tenant recommendations ----

export type ProposalStatus = "draft" | "ready_for_review" | "approved";

export interface ProposalMetric {
  label: string;
  value: string;
}

export interface ProposalContent {
  title: string;
  executive_summary: string;
  location_highlights: string[];
  verified_metrics: ProposalMetric[];
  commercial_opportunity: string;
  pricing_summary: string;
  suggested_usage: string;
  call_to_action: string;
  assumptions_and_limitations: string[];
}

export interface Proposal {
  id: number;
  reference_code: string;
  space_id: number;
  station_id: number;
  title: string;
  tenant_category: string | null;
  status: ProposalStatus;
  content: ProposalContent;
  context_snapshot: {
    station: Record<string, unknown>;
    space: Record<string, unknown>;
    footfall: Record<string, unknown>;
    pricing: Record<string, unknown>;
    user_input: Record<string, unknown>;
  };
  pricing_model_version: string | null;
  generation_source: string;
  ai_model: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProposalListItem {
  id: number;
  reference_code: string;
  space_id: number;
  station_id: number;
  title: string;
  tenant_category: string | null;
  status: ProposalStatus;
  generation_source: string;
  created_at: string;
  updated_at: string;
}

export interface ProposalGenerateRequest {
  space_id: number;
  tenant_category?: string | null;
  business_name?: string | null;
  campaign_objective?: string | null;
  target_audience?: string | null;
  budget?: number | null;
  language?: string;
}

export interface TenantRecommendation {
  category: string;
  score: number;
  confidence: string;
  evidence: string[];
  compatibility: string[];
  missing_information: string[];
  limitations: string[];
}

export interface TenantRecommendationResult {
  space_id: number;
  space_code: string;
  station_name: string;
  recommendations: TenantRecommendation[];
  notes: string[];
}
