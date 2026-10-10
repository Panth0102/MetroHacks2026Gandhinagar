import { useState } from "react";

import { ChartCard } from "@/components/charts/chart-card";
import { SimpleBarChart } from "@/components/charts/charts";
import { QueryState } from "@/components/feedback/state";
import { StationSelect } from "@/components/filters/station-select";
import { PageIntro, Section } from "@/components/layout/page";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { StatCard } from "@/components/ui/stat-card";
import { TBody, TD, TH, THead, TR, Table } from "@/components/ui/table";
import { useForecast } from "@/hooks/queries";
import { formatCurrency, formatPercent, titleCase } from "@/lib/formatters";

export function ScenariosPage() {
  const [stationId, setStationId] = useState<number | undefined>(undefined);
  const query = useForecast(stationId);

  return (
    <div>
      <PageIntro
        title="Revenue scenarios"
        description="Transparent, scenario-based revenue estimates from the backend. These assume indicative asking prices are achieved for a share of eligible vacant inventory — they are not statistically trained forecasts."
      />

      <Section>
        <Card>
          <CardContent className="p-5 sm:max-w-xs">
            <StationSelect value={stationId} onChange={setStationId} />
          </CardContent>
        </Card>
      </Section>

      <QueryState query={query}>
        {(f) => {
          const currentMonthly = Number(f.current_monthly_revenue);
          const chartData = [
            { label: "Current", value: currentMonthly },
            ...f.scenarios.map((s) => ({
              label: `${Math.round(s.occupancy_fraction_of_vacant * 100)}%`,
              value: Number(s.projected_monthly_revenue),
            })),
          ];
          return (
            <>
              <Section>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                  <StatCard
                    label="Current monthly revenue"
                    value={formatCurrency(f.current_monthly_revenue, f.currency)}
                    hint="Signed, contractual revenue from active leases."
                  />
                  <StatCard
                    label="Eligible vacant potential"
                    value={formatCurrency(f.eligible_vacant_potential_monthly_rent, f.currency)}
                    sublabel={`${f.eligible_vacant_space_count} eligible vacant spaces`}
                    hint="Indicative asking rent across priced vacant spaces if fully let."
                  />
                  <StatCard
                    label="Method"
                    value={f.is_predictive_model ? "Predictive" : "Scenario baseline"}
                    sublabel="Not a trained forecast"
                  />
                </div>
              </Section>

              <Section>
                <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
                  <ChartCard
                    title="Projected monthly revenue by scenario"
                    description="Current revenue plus a share of eligible vacant potential."
                    summary={`Scenarios compared to current monthly revenue of ${formatCurrency(
                      f.current_monthly_revenue,
                      f.currency,
                    )}.`}
                    empty={chartData.length === 0}
                  >
                    <SimpleBarChart
                      data={chartData}
                      valueFormatter={(v) => formatCurrency(v, f.currency)}
                    />
                  </ChartCard>

                  <Card>
                    <CardContent className="p-0">
                      <Table>
                        <THead>
                          <TR>
                            <TH>Scenario</TH>
                            <TH className="text-right">Occupancy</TH>
                            <TH className="text-right">Added /mo</TH>
                            <TH className="text-right">Projected /mo</TH>
                            <TH className="text-right">Projected /yr</TH>
                            <TH className="text-right">Δ vs current</TH>
                          </TR>
                        </THead>
                        <TBody>
                          {f.scenarios.map((s) => {
                            const delta = Number(s.projected_monthly_revenue) - currentMonthly;
                            return (
                              <TR key={s.name}>
                                <TD className="font-medium">{titleCase(s.name)}</TD>
                                <TD className="text-right tabular-nums">
                                  {formatPercent(s.occupancy_fraction_of_vacant, 0)}
                                </TD>
                                <TD className="text-right tabular-nums">
                                  {formatCurrency(s.added_monthly_rent, f.currency)}
                                </TD>
                                <TD className="text-right tabular-nums font-medium">
                                  {formatCurrency(s.projected_monthly_revenue, f.currency)}
                                </TD>
                                <TD className="text-right tabular-nums">
                                  {formatCurrency(s.projected_annual_revenue, f.currency)}
                                </TD>
                                <TD className="text-right tabular-nums text-success">
                                  +{formatCurrency(delta, f.currency)}
                                </TD>
                              </TR>
                            );
                          })}
                        </TBody>
                      </Table>
                    </CardContent>
                  </Card>
                </div>
              </Section>

              <Section title="Assumptions & limitations">
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <Card>
                    <CardContent className="p-5">
                      <div className="mb-2 flex items-center gap-2">
                        <Badge tone="accent">Assumptions</Badge>
                      </div>
                      <ul className="list-inside list-disc space-y-1 text-sm text-muted-foreground">
                        {f.assumptions.map((a, i) => (
                          <li key={i}>{a}</li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-5">
                      <div className="mb-2 flex items-center gap-2">
                        <Badge tone="warning">Limitations</Badge>
                      </div>
                      <ul className="list-inside list-disc space-y-1 text-sm text-muted-foreground">
                        {f.limitations.map((l, i) => (
                          <li key={i}>{l}</li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>
                </div>
              </Section>
            </>
          );
        }}
      </QueryState>
    </div>
  );
}
