import { Download, Search } from "lucide-react";
import { useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { QueryState } from "@/components/feedback/state";
import { StationSelect } from "@/components/filters/station-select";
import { PageIntro, Section } from "@/components/layout/page";
import { Badge, statusTone } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input, Label } from "@/components/ui/input";
import { Pagination } from "@/components/ui/pagination";
import { Select } from "@/components/ui/select";
import { TBody, TD, TH, THead, TR, Table } from "@/components/ui/table";
import { useInventory, useRateCard, useStations } from "@/hooks/queries";
import { downloadCsv } from "@/lib/csv";
import {
  formatCurrency,
  formatDate,
  formatNumber,
  labelSpaceType,
  labelStatus,
} from "@/lib/formatters";
import type { SpaceStatus, SpaceType } from "@/types/api";

const TYPE_OPTIONS = [
  { value: "retail", label: "Retail" },
  { value: "kiosk", label: "Kiosk" },
  { value: "advertising_panel", label: "Advertising panel" },
  { value: "digital_screen", label: "Digital screen" },
];
const STATUS_OPTIONS = [
  { value: "vacant", label: "Vacant" },
  { value: "occupied", label: "Occupied" },
  { value: "under_maintenance", label: "Under maintenance" },
  { value: "unavailable", label: "Unavailable" },
];
const SORT_OPTIONS = [
  { value: "code", label: "Space code" },
  { value: "price_desc", label: "Indicative price (high→low)" },
  { value: "footfall_desc", label: "Footfall (high→low)" },
  { value: "area_desc", label: "Area (high→low)" },
];

const PAGE_SIZE = 10;

export function InventoryPage() {
  const [stationId, setStationId] = useState<number | undefined>(undefined);
  const [type, setType] = useState<SpaceType | "">("");
  const [status, setStatus] = useState<SpaceStatus | "">("");
  const [search, setSearch] = useState("");
  const [minArea, setMinArea] = useState("");
  const [maxArea, setMaxArea] = useState("");
  const [sort, setSort] = useState("code");
  const [offset, setOffset] = useState(0);

  // Fetch all matching rows (dataset is small) so search/sort act on the full set,
  // not just a visual relabel of one page. Server handles station/status/type filters.
  const inventory = useInventory({
    station_id: stationId,
    status: status || undefined,
    space_type: type || undefined,
    limit: 200,
  });
  const rateCard = useRateCard({ vacant_only: false, limit: 500 });
  const stations = useStations({ limit: 200 });

  const priceMap = useMemo(() => {
    const m = new Map<number, { price: string | null; footfall: number | null; station: string }>();
    for (const r of rateCard.data ?? [])
      m.set(r.space_id, {
        price: r.indicative_monthly_price,
        footfall: r.observed_daily_footfall,
        station: r.station_name,
      });
    return m;
  }, [rateCard.data]);

  const stationName = useMemo(() => {
    const m = new Map<number, string>();
    for (const s of stations.data?.items ?? []) m.set(s.id, s.name);
    return m;
  }, [stations.data]);

  const rows = useMemo(() => {
    const items = (inventory.data?.items ?? []).map((sp) => {
      const extra = priceMap.get(sp.id);
      return {
        ...sp,
        indicative: extra?.price ?? null,
        footfall: extra?.footfall ?? null,
        stationLabel: extra?.station ?? stationName.get(sp.station_id) ?? `#${sp.station_id}`,
      };
    });
    const q = search.trim().toLowerCase();
    const min = minArea ? Number(minArea) : null;
    const max = maxArea ? Number(maxArea) : null;
    const filtered = items.filter((sp) => {
      if (q && !`${sp.space_code} ${sp.stationLabel}`.toLowerCase().includes(q)) return false;
      const area = sp.area_sqm === null ? null : Number(sp.area_sqm);
      if (min !== null && (area === null || area < min)) return false;
      if (max !== null && (area === null || area > max)) return false;
      return true;
    });
    const num = (v: string | null) => (v === null ? -Infinity : Number(v));
    filtered.sort((a, b) => {
      switch (sort) {
        case "price_desc":
          return num(b.indicative) - num(a.indicative);
        case "footfall_desc":
          return (b.footfall ?? -Infinity) - (a.footfall ?? -Infinity);
        case "area_desc":
          return num(b.area_sqm) - num(a.area_sqm);
        default:
          return a.space_code.localeCompare(b.space_code);
      }
    });
    return filtered;
  }, [inventory.data, priceMap, stationName, search, minArea, maxArea, sort]);

  const paged = rows.slice(offset, offset + PAGE_SIZE);

  const resetPage = () => setOffset(0);

  const exportCsv = () =>
    downloadCsv(
      "inventory.csv",
      [
        { key: "space_code", header: "Space code" },
        { key: "stationLabel", header: "Station" },
        { key: "space_type", header: "Type" },
        { key: "area_sqm", header: "Area (sqm)" },
        { key: "status", header: "Status" },
        { key: "visibility_score", header: "Visibility" },
        { key: "asking_monthly_rent", header: "Asking rent" },
        { key: "indicative", header: "Indicative /mo" },
      ],
      rows,
    );

  return (
    <div>
      <PageIntro
        title="Commercial inventory"
        description="Search and filter all retail and advertising spaces. Indicative prices come from the backend pricing engine; current contractual rent is aggregate-only and not shown per space."
      />

      <Section>
        <Card>
          <CardContent className="grid grid-cols-1 gap-4 p-5 md:grid-cols-3 xl:grid-cols-4">
            <div>
              <Label htmlFor="inv-search">Search</Label>
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" aria-hidden="true" />
                <Input
                  id="inv-search"
                  className="pl-9"
                  placeholder="Space code or station"
                  value={search}
                  onChange={(e) => {
                    setSearch(e.target.value);
                    resetPage();
                  }}
                />
              </div>
            </div>
            <StationSelect
              value={stationId}
              onChange={(v) => {
                setStationId(v);
                resetPage();
              }}
            />
            <div>
              <Label htmlFor="inv-type">Type</Label>
              <Select
                id="inv-type"
                options={TYPE_OPTIONS}
                placeholder="All types"
                value={type}
                onChange={(e) => {
                  setType(e.target.value as SpaceType | "");
                  resetPage();
                }}
              />
            </div>
            <div>
              <Label htmlFor="inv-status">Status</Label>
              <Select
                id="inv-status"
                options={STATUS_OPTIONS}
                placeholder="All statuses"
                value={status}
                onChange={(e) => {
                  setStatus(e.target.value as SpaceStatus | "");
                  resetPage();
                }}
              />
            </div>
            <div>
              <Label htmlFor="inv-min">Min area (sqm)</Label>
              <Input
                id="inv-min"
                type="number"
                min={0}
                value={minArea}
                onChange={(e) => {
                  setMinArea(e.target.value);
                  resetPage();
                }}
              />
            </div>
            <div>
              <Label htmlFor="inv-max">Max area (sqm)</Label>
              <Input
                id="inv-max"
                type="number"
                min={0}
                value={maxArea}
                onChange={(e) => {
                  setMaxArea(e.target.value);
                  resetPage();
                }}
              />
            </div>
            <div>
              <Label htmlFor="inv-sort">Sort by</Label>
              <Select id="inv-sort" options={SORT_OPTIONS} value={sort} onChange={(e) => setSort(e.target.value)} />
            </div>
            <div className="flex items-end">
              <Button variant="outline" onClick={exportCsv} disabled={rows.length === 0} className="w-full">
                <Download className="h-4 w-4" aria-hidden="true" /> Export CSV
              </Button>
            </div>
          </CardContent>
        </Card>
      </Section>

      <QueryState
        query={inventory}
        isEmpty={() => rows.length === 0}
        emptyTitle="No spaces match these filters"
        emptyHint="Adjust the search, station, type, status, or area filters."
      >
        {() => (
          <Card>
            <CardContent className="p-0">
              <Table>
                <THead>
                  <TR>
                    <TH>Space</TH>
                    <TH>Station</TH>
                    <TH>Type</TH>
                    <TH className="text-right">Area</TH>
                    <TH>Status</TH>
                    <TH className="text-right">Visibility</TH>
                    <TH className="text-right">Asking /mo</TH>
                    <TH className="text-right">Indicative /mo</TH>
                    <TH>Available</TH>
                    <TH className="sr-only">Actions</TH>
                  </TR>
                </THead>
                <TBody>
                  {paged.map((sp) => (
                    <TR key={sp.id}>
                      <TD className="font-medium">{sp.space_code}</TD>
                      <TD>{sp.stationLabel}</TD>
                      <TD>{labelSpaceType(sp.space_type)}</TD>
                      <TD className="text-right tabular-nums">
                        {sp.area_sqm === null ? "—" : `${formatNumber(Number(sp.area_sqm))} m²`}
                      </TD>
                      <TD>
                        <Badge tone={statusTone(sp.status)}>{labelStatus(sp.status)}</Badge>
                      </TD>
                      <TD className="text-right tabular-nums">
                        {sp.visibility_score === null ? "—" : Number(sp.visibility_score).toFixed(1)}
                      </TD>
                      <TD className="text-right tabular-nums">{formatCurrency(sp.asking_monthly_rent)}</TD>
                      <TD className="text-right tabular-nums">{formatCurrency(sp.indicative)}</TD>
                      <TD>{formatDate(sp.available_from)}</TD>
                      <TD className="text-right">
                        <Link
                          to={`/inventory/${sp.id}`}
                          className="text-sm font-medium text-accent hover:underline"
                        >
                          Details
                        </Link>
                      </TD>
                    </TR>
                  ))}
                </TBody>
              </Table>
              <div className="px-4 pb-3">
                <Pagination offset={offset} limit={PAGE_SIZE} total={rows.length} onChange={setOffset} />
              </div>
            </CardContent>
          </Card>
        )}
      </QueryState>
    </div>
  );
}
