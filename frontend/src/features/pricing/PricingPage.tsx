import { Download } from "lucide-react";
import { useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { QueryState } from "@/components/feedback/state";
import { StationSelect } from "@/components/filters/station-select";
import { PageIntro, Section } from "@/components/layout/page";
import { Badge, qualityTone } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Label } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { TBody, TD, TH, THead, TR, Table } from "@/components/ui/table";
import { useRateCard } from "@/hooks/queries";
import { api } from "@/lib/api-client";
import { downloadCsv } from "@/lib/csv";
import { formatCurrency, formatNumber, labelSpaceType, labelStatus } from "@/lib/formatters";
import type { SpaceType } from "@/types/api";
import { EstimateForm } from "./EstimateForm";

const TYPE_OPTIONS = [
  { value: "retail", label: "Retail" },
  { value: "kiosk", label: "Kiosk" },
  { value: "advertising_panel", label: "Advertising panel" },
  { value: "digital_screen", label: "Digital screen" },
];
const AVAIL_OPTIONS = [
  { value: "vacant", label: "Vacant only" },
  { value: "all", label: "All statuses" },
];

export function PricingPage() {
  const [stationId, setStationId] = useState<number | undefined>(undefined);
  const [type, setType] = useState<SpaceType | "">("");
  const [availability, setAvailability] = useState("vacant");

  const rateCard = useRateCard({
    station_id: stationId,
    vacant_only: availability === "vacant",
    limit: 500,
  });

  const rows = useMemo(() => {
    const items = rateCard.data ?? [];
    return type ? items.filter((r) => r.space_type === type) : items;
  }, [rateCard.data, type]);

  const modelVersion = rows[0]?.model_version;

  const exportCsv = () =>
    downloadCsv(
      "rate-card.csv",
      [
        { key: "station_name", header: "Station" },
        { key: "space_code", header: "Space code" },
        { key: "space_type", header: "Type" },
        { key: "status", header: "Status" },
        { key: "area_sqm", header: "Area (sqm)" },
        { key: "observed_daily_footfall", header: "Footfall/day" },
        { key: "indicative_monthly_price", header: "Indicative /mo (INR)" },
        { key: "model_version", header: "Model version" },
        { key: "data_quality", header: "Data quality" },
      ],
      rows,
    );

  return (
    <div>
      <PageIntro
        title="Pricing & rate cards"
        description="Indicative monthly asking prices from the backend pricing engine. These are model-generated estimates, not approved or contracted rates."
      />

      <Section title="Price scenario calculator">
        <EstimateForm />
      </Section>

      <Section
        title={`Rate card${modelVersion ? ` — model ${modelVersion}` : ""}`}
        action={
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={exportCsv} disabled={rows.length === 0}>
              <Download className="h-4 w-4" aria-hidden="true" /> Export view (CSV)
            </Button>
            <a
              href={api.downloadUrl("/api/v1/pricing/rate-card.csv", {
                station_id: stationId,
                vacant_only: availability === "vacant",
              })}
              className="inline-flex h-8 items-center gap-2 rounded-md border border-input bg-surface px-3 text-sm font-medium hover:bg-muted/60"
            >
              <Download className="h-4 w-4" aria-hidden="true" /> Official CSV
            </a>
          </div>
        }
      >
        <Card className="mb-4">
          <CardContent className="grid grid-cols-1 gap-4 p-5 sm:grid-cols-3">
            <StationSelect value={stationId} onChange={setStationId} />
            <div>
              <Label htmlFor="rc-type">Type</Label>
              <Select
                id="rc-type"
                options={TYPE_OPTIONS}
                placeholder="All types"
                value={type}
                onChange={(e) => setType(e.target.value as SpaceType | "")}
              />
            </div>
            <div>
              <Label htmlFor="rc-avail">Availability</Label>
              <Select
                id="rc-avail"
                options={AVAIL_OPTIONS}
                value={availability}
                onChange={(e) => setAvailability(e.target.value)}
              />
            </div>
          </CardContent>
        </Card>

        <QueryState
          query={rateCard}
          isEmpty={() => rows.length === 0}
          emptyTitle="No priced spaces for this selection"
          emptyHint="Adjust the station, type, or availability filters."
        >
          {() => (
            <Card>
              <CardContent className="p-0">
                <Table>
                  <THead>
                    <TR>
                      <TH>Station</TH>
                      <TH>Space</TH>
                      <TH>Type</TH>
                      <TH>Status</TH>
                      <TH className="text-right">Area</TH>
                      <TH className="text-right">Footfall/day</TH>
                      <TH className="text-right">Indicative /mo</TH>
                      <TH>Data</TH>
                      <TH className="sr-only">Actions</TH>
                    </TR>
                  </THead>
                  <TBody>
                    {rows.map((r) => (
                      <TR key={r.space_id}>
                        <TD>{r.station_name}</TD>
                        <TD className="font-medium">{r.space_code}</TD>
                        <TD>{labelSpaceType(r.space_type)}</TD>
                        <TD>{labelStatus(r.status)}</TD>
                        <TD className="text-right tabular-nums">
                          {r.area_sqm === null ? "—" : `${formatNumber(Number(r.area_sqm))} m²`}
                        </TD>
                        <TD className="text-right tabular-nums">
                          {formatNumber(r.observed_daily_footfall ?? null, { maximumFractionDigits: 0 })}
                        </TD>
                        <TD className="text-right tabular-nums font-medium">
                          {r.available ? (
                            formatCurrency(r.indicative_monthly_price)
                          ) : (
                            <span className="text-muted-foreground">Unavailable</span>
                          )}
                        </TD>
                        <TD>
                          <Badge tone={qualityTone(r.data_quality)}>{labelStatus(r.data_quality)}</Badge>
                        </TD>
                        <TD className="text-right">
                          <Link
                            to={`/inventory/${r.space_id}`}
                            className="text-sm font-medium text-accent hover:underline"
                          >
                            Breakdown
                          </Link>
                        </TD>
                      </TR>
                    ))}
                  </TBody>
                </Table>
              </CardContent>
            </Card>
          )}
        </QueryState>
      </Section>
    </div>
  );
}
