// Centralized, locale-aware formatting helpers. Currency defaults to INR because
// the Phase 1 dataset is configured in INR, but the currency code is passed
// explicitly so other datasets are not wrongly assumed to be INR.

export function formatCurrency(
  value: string | number | null | undefined,
  currency = "INR",
): string {
  if (value === null || value === undefined || value === "") return "—";
  const num = typeof value === "string" ? Number(value) : value;
  if (Number.isNaN(num)) return "—";
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(num);
}

export function formatNumber(
  value: number | null | undefined,
  opts: Intl.NumberFormatOptions = {},
): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return new Intl.NumberFormat("en-IN", opts).format(value);
}

export function formatPercent(
  fraction: number | null | undefined,
  digits = 1,
): string {
  if (fraction === null || fraction === undefined || Number.isNaN(fraction))
    return "—";
  return `${(fraction * 100).toFixed(digits)}%`;
}

export function formatHour(hour: number | null | undefined): string {
  if (hour === null || hour === undefined) return "—";
  const h = ((hour % 24) + 24) % 24;
  const period = h < 12 ? "AM" : "PM";
  const display = h % 12 === 0 ? 12 : h % 12;
  return `${display}:00 ${period}`;
}

export function formatDate(value: string | null | undefined): string {
  if (!value) return "—";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return new Intl.DateTimeFormat("en-IN", {
    year: "numeric",
    month: "short",
    day: "numeric",
  }).format(d);
}

const SPACE_TYPE_LABELS: Record<string, string> = {
  retail: "Retail",
  kiosk: "Kiosk",
  advertising_panel: "Advertising panel",
  digital_screen: "Digital screen",
};

const STATUS_LABELS: Record<string, string> = {
  vacant: "Vacant",
  occupied: "Occupied",
  under_maintenance: "Under maintenance",
  unavailable: "Unavailable",
};

export function labelSpaceType(t: string): string {
  return SPACE_TYPE_LABELS[t] ?? t;
}

export function labelStatus(s: string): string {
  return STATUS_LABELS[s] ?? s;
}

export function titleCase(s: string): string {
  return s.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}
