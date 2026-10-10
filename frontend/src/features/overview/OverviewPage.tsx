import { ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";

import { ChartCard } from "@/components/charts/chart-card";
import { SimpleBarChart, SimpleDonut, SimpleLineChart } from "@/components/charts/charts";
import { QueryState } from "@/components/feedback/state";
import { PageIntro, Section } from "@/components/layout/page";
import { Badge, qualityTone } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { StatCard } from "@/components/ui/stat-card";
import { TBody, TD, TH, THead, TR, Table } from "@/components/ui/table";
import {
  useInventorySummary,
  useOpportunities,
  useOverview,
  usePeakHours,
  useStationRanking,
} from "@/hooks/queries";
import {
  formatCurrency,
  formatHour,
  formatNumber,
  formatPercent,
  labelSpaceType,
  labelStatus,
} from "@/lib/formatters";

export function OverviewPage() {
  const overview = useOverview();
  const inventory = useInventorySummary();
  const peak = usePeakHours();
  const ranking = useStationRanking();
  const opportunities = useOpportunities(undefined, 5);

  const o = overview.data;
  const inv = inventory.data;
  const vacant = inv?.count_by_status?.vacant ?? null;

  return (
    <div>
      <PageIntro
        title="Executive overview"
        description="Portfolio-wide footfall and commercial inventory indicators from the Metro Revenue Intelligence backend. All figures are observed or indicative; synthetic demonstration data."
      />

      <Section>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <StatCard
            label="Stations"
            loading={overview.isPending}
            value={formatNumber(o?.station_count)}
            sublabel={o ? `${o.active_station_count} active` : undefined}
          />
          <StatCard
            label="Commercial spaces"
            loading={overview.isPending}
            value={formatNumber(o?.total_spaces)}
            sublabel={vacant !== null ? `${vacant} vacant` : undefined}
          />
          <StatCard
            label="Occupancy rate"
            loading={overview.isPending}
            value={formatPercent(o?.occupancy_rate_by_count)}
            hint="Share of all commercial spaces (any status) currently occupied — by count, not by area."
          />
          <StatCard
            label="Observed entries"
            loading={overview.isPending}
            value={formatNumber(o?.total_entries_observed)}
            sublabel={
              o?.footfall_date_range?.start
                ? `${o.footfall_date_range.start} → ${o.footfall_date_range.end}`
                : undefined
            }
            hint="Total passenger boardings recorded across all stations in the dataset period."
          />
          <StatCard
            label="Current monthly revenue"
            loading={overview.isPending}
            value={formatCurrency(o?.current_monthly_revenue)}
            hint="Signed, contractual revenue from active leases. Not asking or potential revenue."
          />
          <StatCard
            label="Potential vacant rent"
            loading={overview.isPending}
            value={formatCurrency(o?.potential_vacant_monthly_rent)}
            hint="Indicative monthly asking rent for eligible vacant spaces. Estimated, not contracted or guaranteed."
          />
        </div>
      </Section>

      <Section>
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <QueryState query={ranking}>
            {(rows) => (
              <ChartCard
                title="Station footfall comparison"
                description="Total observed entries by station."
                empty={rows.length === 0}
                summary={`Station footfall ranking. Top station: ${
                  rows[0]?.station_name ?? "none"
                } with ${formatNumber(rows[0]?.total_entries)} entries.`}
              >
                <SimpleBarChart
                  horizontal
                  data={rows.map((r) => ({ label: r.station_name, value: r.total_entries }))}
                  valueFormatter={(v) => formatNumber(v, { notation: "compact" })}
                />
              </ChartCard>
            )}
          </QueryState>

          <QueryState query={peak}>
            {(p) => (
              <ChartCard
                title="Hourly passenger traffic"
                description="Entries by hour of day, all stations."
                empty={p.buckets.length === 0}
                summary={`Hourly traffic profile. Peak hour: ${formatHour(p.peak_hour)}.`}
              >
                <SimpleLineChart
                  data={p.buckets.map((b) => ({ label: formatHour(b.hour), value: b.total_entries }))}
                  valueFormatter={(v) => formatNumber(v, { notation: "compact" })}
                />
              </ChartCard>
            )}
          </QueryState>

          <QueryState query={inventory}>
            {(s) => {
              const occ = s.count_by_status.occupied ?? 0;
              const vac = s.count_by_status.vacant ?? 0;
              const maint = s.count_by_status.under_maintenance ?? 0;
              const un = s.count_by_status.unavailable ?? 0;
              const data = [
                { label: "Occupied", value: occ },
                { label: "Vacant", value: vac },
                { label: "Under maintenance", value: maint },
                { label: "Unavailable", value: un },
              ].filter((d) => d.value > 0);
              return (
                <ChartCard
                  title="Occupied vs vacant inventory"
                  description="Distribution of spaces by status."
                  empty={data.length === 0}
                  summary={`Inventory by status: ${occ} occupied, ${vac} vacant, ${maint} under maintenance, ${un} unavailable.`}
                >
                  <SimpleDonut data={data} valueFormatter={(v) => formatNumber(v)} />
                </ChartCard>
              );
            }}
          </QueryState>

          <QueryState query={inventory}>
            {(s) => {
              const data = Object.entries(s.count_by_type).map(([k, v]) => ({
                label: labelSpaceType(k),
                value: v,
              }));
              return (
                <ChartCard
                  title="Inventory by space type"
                  description="Count of commercial spaces per type."
                  empty={data.length === 0}
                  summary={`Space types: ${data.map((d) => `${d.value} ${d.label}`).join(", ")}.`}
                >
                  <SimpleBarChart data={data} valueFormatter={(v) => formatNumber(v)} />
                </ChartCard>
              );
            }}
          </QueryState>
        </div>
      </Section>

      <Section
        title="Top revenue opportunities"
        action={
          <Link
            to="/opportunities"
            className="inline-flex items-center gap-1 text-sm font-medium text-accent hover:underline"
          >
            View all <ArrowRight className="h-4 w-4" />
          </Link>
        }
      >
        <QueryState
          query={opportunities}
          isEmpty={(rows) => rows.length === 0}
          emptyTitle="No vacant-space opportunities"
          emptyHint="There are currently no vacant spaces to rank."
        >
          {(rows) => (
            <Card>
              <CardContent className="p-0">
                <Table>
                  <THead>
                    <TR>
                      <TH>Space</TH>
                      <TH>Station</TH>
                      <TH>Type</TH>
                      <TH className="text-right">Indicative / mo</TH>
                      <TH className="text-right">Footfall / day</TH>
                      <TH className="text-right">Priority</TH>
                      <TH>Data</TH>
                      <TH className="sr-only">Actions</TH>
                    </TR>
                  </THead>
                  <TBody>
                    {rows.map((r) => (
                      <TR key={r.space_id}>
                        <TD className="font-medium">{r.space_code}</TD>
                        <TD>{r.station_name}</TD>
                        <TD>{labelSpaceType(r.space_type)}</TD>
                        <TD className="text-right tabular-nums">
                          {formatCurrency(r.indicative_monthly_price)}
                        </TD>
                        <TD className="text-right tabular-nums">
                          {formatNumber(r.observed_daily_footfall ?? null, {
                            maximumFractionDigits: 0,
                          })}
                        </TD>
                        <TD className="text-right tabular-nums font-semibold">
                          {r.priority_score.toFixed(1)}
                        </TD>
                        <TD>
                          <Badge tone={qualityTone(r.data_quality)}>{labelStatus(r.data_quality)}</Badge>
                        </TD>
                        <TD className="text-right">
                          <Link
                            to={`/inventory/${r.space_id}`}
                            className="text-sm font-medium text-accent hover:underline"
                          >
                            Details
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
