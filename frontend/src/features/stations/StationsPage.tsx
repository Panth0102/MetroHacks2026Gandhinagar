import { useMemo, useState } from "react";

import { ChartCard } from "@/components/charts/chart-card";
import { SimpleBarChart, SimpleLineChart } from "@/components/charts/charts";
import { QueryState } from "@/components/feedback/state";
import { StationSelect } from "@/components/filters/station-select";
import { PageIntro, Section } from "@/components/layout/page";
import { Card, CardContent } from "@/components/ui/card";
import { Input, Label } from "@/components/ui/input";
import { StatCard } from "@/components/ui/stat-card";
import { useFootfallSummary, useStationRanking } from "@/hooks/queries";
import { formatHour, formatNumber, formatPercent } from "@/lib/formatters";

function previousRange(start: string, end: string): { start: string; end: string } | null {
  const s = new Date(start);
  const e = new Date(end);
  if (Number.isNaN(s.getTime()) || Number.isNaN(e.getTime()) || e < s) return null;
  const days = Math.round((e.getTime() - s.getTime()) / 86_400_000) + 1;
  const prevEnd = new Date(s.getTime() - 86_400_000);
  const prevStart = new Date(prevEnd.getTime() - (days - 1) * 86_400_000);
  const iso = (d: Date) => d.toISOString().slice(0, 10);
  return { start: iso(prevStart), end: iso(prevEnd) };
}

export function StationsPage() {
  const [stationId, setStationId] = useState<number | undefined>(undefined);
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");

  const summary = useFootfallSummary(stationId, start || undefined, end || undefined);
  const ranking = useStationRanking();

  const prev = start && end ? previousRange(start, end) : null;
  const prevSummary = useFootfallSummary(stationId, prev?.start, prev?.end);

  const pctChange = useMemo(() => {
    if (!prev || !summary.data || !prevSummary.data) return null;
    const base = prevSummary.data.total_entries;
    if (base === 0) return null;
    return (summary.data.total_entries - base) / base;
  }, [prev, summary.data, prevSummary.data]);

  const hourly = summary.data?.hourly_distribution ?? {};
  const hourlyData = Object.keys(hourly)
    .map((h) => Number(h))
    .sort((a, b) => a - b)
    .map((h) => ({ label: formatHour(h), value: hourly[String(h)] ?? 0 }));

  return (
    <div>
      <PageIntro
        title="Stations & footfall"
        description="Observed passenger entries by station and time band. Select a station and date range; charts reflect only observed data."
      />

      <Section>
        <Card>
          <CardContent className="grid grid-cols-1 gap-4 p-5 sm:grid-cols-3">
            <StationSelect value={stationId} onChange={setStationId} />
            <div>
              <Label htmlFor="start">From</Label>
              <Input id="start" type="date" value={start} onChange={(e) => setStart(e.target.value)} />
            </div>
            <div>
              <Label htmlFor="end">To</Label>
              <Input id="end" type="date" value={end} onChange={(e) => setEnd(e.target.value)} />
            </div>
          </CardContent>
        </Card>
      </Section>

      <QueryState
        query={summary}
        isEmpty={(s) => s.observation_count === 0}
        emptyTitle="No footfall for this selection"
        emptyHint="The selected station and date range has no observations. Try a different station or widen the date range."
      >
        {(s) => (
          <>
            <Section>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
                <StatCard
                  label="Total entries"
                  value={formatNumber(s.total_entries)}
                  sublabel={s.start_date ? `${s.start_date} → ${s.end_date}` : undefined}
                />
                <StatCard
                  label="Avg daily entries"
                  value={formatNumber(s.avg_daily_entries, { maximumFractionDigits: 0 })}
                  sublabel={`${s.distinct_days} observed days`}
                />
                <StatCard
                  label="Peak hour"
                  value={formatHour(s.peak_hour)}
                  sublabel={
                    s.peak_hours_tied.length > 1
                      ? `Tied: ${s.peak_hours_tied.map(formatHour).join(", ")}`
                      : `${formatNumber(s.peak_hour_entries)} entries`
                  }
                />
                <StatCard
                  label="Period-over-period"
                  value={pctChange === null ? "—" : formatPercent(pctChange)}
                  hint="Change in total entries vs the immediately preceding equal-length period. Shown only when a date range is set and the prior period has data."
                  sublabel={
                    pctChange === null && start && end
                      ? "No comparable prior-period data"
                      : "vs previous equal period"
                  }
                />
              </div>
            </Section>

            <Section>
              <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
                <ChartCard
                  title="Hourly footfall"
                  description="Entries by hour band for the current selection."
                  empty={hourlyData.length === 0}
                  summary={`Hourly footfall. Peak at ${formatHour(s.peak_hour)}.`}
                >
                  <SimpleLineChart
                    data={hourlyData}
                    valueFormatter={(v) => formatNumber(v, { notation: "compact" })}
                  />
                </ChartCard>

                <QueryState query={ranking}>
                  {(rows) => (
                    <ChartCard
                      title="Station comparison"
                      description="Total observed entries by station."
                      empty={rows.length === 0}
                      summary={`Station footfall comparison across ${rows.length} stations.`}
                    >
                      <SimpleBarChart
                        horizontal
                        data={rows.map((r) => ({ label: r.station_name, value: r.total_entries }))}
                        valueFormatter={(v) => formatNumber(v, { notation: "compact" })}
                      />
                    </ChartCard>
                  )}
                </QueryState>
              </div>
            </Section>

            <Section>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <StatCard
                  label="Weekday avg daily entries"
                  value={formatNumber(s.weekday_avg_daily_entries, { maximumFractionDigits: 0 })}
                />
                <StatCard
                  label="Weekend avg daily entries"
                  value={formatNumber(s.weekend_avg_daily_entries, { maximumFractionDigits: 0 })}
                />
              </div>
              {s.coverage_ratio !== null && s.coverage_ratio < 1 && (
                <p className="mt-3 text-sm text-muted-foreground">
                  Data coverage: {formatPercent(s.coverage_ratio)} of expected hour-slots in range.
                  Missing observations are excluded, not treated as zero.
                </p>
              )}
              {s.notes.length > 0 && (
                <ul className="mt-2 list-inside list-disc text-sm text-muted-foreground">
                  {s.notes.map((n, i) => (
                    <li key={i}>{n}</li>
                  ))}
                </ul>
              )}
            </Section>
          </>
        )}
      </QueryState>
    </div>
  );
}
