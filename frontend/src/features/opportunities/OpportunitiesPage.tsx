import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { ChartCard } from "@/components/charts/chart-card";
import { SimpleBarChart } from "@/components/charts/charts";
import { QueryState } from "@/components/feedback/state";
import { StationSelect } from "@/components/filters/station-select";
import { PageIntro, Section } from "@/components/layout/page";
import { Badge, qualityTone } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TBody, TD, TH, THead, TR, Table } from "@/components/ui/table";
import { useOpportunities } from "@/hooks/queries";
import { formatCurrency, formatNumber, labelSpaceType, labelStatus } from "@/lib/formatters";
import type { RevenueOpportunity } from "@/types/api";

function ExplanationPanel({ op }: { op: RevenueOpportunity }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>
          Why {op.space_code} ranks {op.priority_score.toFixed(1)}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <p className="text-sm font-medium">Score components (backend-weighted)</p>
          <ul className="mt-1 space-y-1 text-sm text-muted-foreground">
            {op.score_breakdown.map((f) => (
              <li key={f.name} className="flex justify-between gap-3">
                <span>{f.description}</span>
                <span className="tabular-nums font-medium text-foreground">{f.value.toFixed(3)}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="grid grid-cols-2 gap-3 border-t border-border pt-3 text-sm">
          <div>
            <p className="text-xs uppercase text-muted-foreground">Indicative monthly</p>
            <p className="font-semibold tabular-nums">{formatCurrency(op.indicative_monthly_price)}</p>
          </div>
          <div>
            <p className="text-xs uppercase text-muted-foreground">Annualized asking</p>
            <p className="font-semibold tabular-nums">
              {formatCurrency(op.estimated_annual_asking_revenue)}
            </p>
          </div>
          <div>
            <p className="text-xs uppercase text-muted-foreground">Footfall / day</p>
            <p className="font-semibold tabular-nums">
              {formatNumber(op.observed_daily_footfall ?? null, { maximumFractionDigits: 0 })}
            </p>
          </div>
          <div>
            <p className="text-xs uppercase text-muted-foreground">Data quality</p>
            <Badge tone={qualityTone(op.data_quality)}>{labelStatus(op.data_quality)}</Badge>
          </div>
        </div>

        {op.reasons.length > 0 && (
          <div>
            <p className="text-sm font-medium">Reasons</p>
            <ul className="mt-1 list-inside list-disc text-sm text-muted-foreground">
              {op.reasons.map((r, i) => (
                <li key={i}>{r}</li>
              ))}
            </ul>
          </div>
        )}

        {op.limitations.length > 0 && (
          <div>
            <p className="text-sm font-medium">Limitations</p>
            <ul className="mt-1 list-inside list-disc text-sm text-muted-foreground">
              {op.limitations.map((l, i) => (
                <li key={i}>{l}</li>
              ))}
            </ul>
          </div>
        )}

        <p className="rounded-md bg-muted p-3 text-xs text-muted-foreground">
          A high priority score reflects a blend of indicative price, footfall, and data
          completeness — not footfall alone. Annualized asking revenue is an estimate, not a
          forecast or guaranteed income.
        </p>

        <Link
          to={`/inventory/${op.space_id}`}
          className="inline-block text-sm font-medium text-accent hover:underline"
        >
          View full space & pricing detail →
        </Link>
      </CardContent>
    </Card>
  );
}

export function OpportunitiesPage() {
  const [stationId, setStationId] = useState<number | undefined>(undefined);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const query = useOpportunities(stationId, 50);

  useEffect(() => {
    if (query.data && query.data.length > 0) {
      setSelectedId((prev) =>
        prev && query.data.some((o) => o.space_id === prev) ? prev : query.data[0]!.space_id,
      );
    }
  }, [query.data]);

  return (
    <div>
      <PageIntro
        title="Revenue opportunities"
        description="Vacant spaces ranked by the backend's explainable priority score. Occupied, under-maintenance, and unavailable spaces are excluded as non-rentable."
      />

      <Section>
        <Card>
          <CardContent className="p-5 sm:max-w-xs">
            <StationSelect value={stationId} onChange={setStationId} />
          </CardContent>
        </Card>
      </Section>

      <QueryState
        query={query}
        isEmpty={(rows) => rows.length === 0}
        emptyTitle="No vacant-space opportunities"
        emptyHint="There are currently no vacant spaces to rank for this selection."
      >
        {(rows) => {
          const selected = rows.find((o) => o.space_id === selectedId) ?? rows[0]!;
          return (
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
              <div className="space-y-4 lg:col-span-2">
                <ChartCard
                  title="Priority ranking"
                  description="Top opportunities by priority score."
                  summary={`Top opportunity: ${rows[0]?.space_code} at ${rows[0]?.station_name}, priority ${rows[0]?.priority_score.toFixed(1)}.`}
                  empty={rows.length === 0}
                >
                  <SimpleBarChart
                    horizontal
                    height={Math.min(60 + rows.length * 28, 420)}
                    data={rows.slice(0, 10).map((o) => ({ label: o.space_code, value: o.priority_score }))}
                    valueFormatter={(v) => v.toFixed(1)}
                  />
                </ChartCard>

                <Card>
                  <CardContent className="p-0">
                    <Table>
                      <THead>
                        <TR>
                          <TH>Space</TH>
                          <TH>Station</TH>
                          <TH>Type</TH>
                          <TH className="text-right">Indicative /mo</TH>
                          <TH className="text-right">Footfall/day</TH>
                          <TH className="text-right">Priority</TH>
                          <TH className="sr-only">Select</TH>
                        </TR>
                      </THead>
                      <TBody>
                        {rows.map((o) => (
                          <TR
                            key={o.space_id}
                            className={o.space_id === selected.space_id ? "bg-accent/5" : ""}
                          >
                            <TD className="font-medium">{o.space_code}</TD>
                            <TD>{o.station_name}</TD>
                            <TD>{labelSpaceType(o.space_type)}</TD>
                            <TD className="text-right tabular-nums">
                              {formatCurrency(o.indicative_monthly_price)}
                            </TD>
                            <TD className="text-right tabular-nums">
                              {formatNumber(o.observed_daily_footfall ?? null, { maximumFractionDigits: 0 })}
                            </TD>
                            <TD className="text-right tabular-nums font-semibold">
                              {o.priority_score.toFixed(1)}
                            </TD>
                            <TD className="text-right">
                              <button
                                className="text-sm font-medium text-accent hover:underline"
                                onClick={() => setSelectedId(o.space_id)}
                                aria-label={`Explain ranking for ${o.space_code}`}
                              >
                                Explain
                              </button>
                            </TD>
                          </TR>
                        ))}
                      </TBody>
                    </Table>
                  </CardContent>
                </Card>
              </div>

              <div className="lg:col-span-1">
                <ExplanationPanel op={selected} />
              </div>
            </div>
          );
        }}
      </QueryState>
    </div>
  );
}
