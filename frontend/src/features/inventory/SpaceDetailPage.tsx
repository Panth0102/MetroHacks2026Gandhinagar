import { ArrowLeft, FileText } from "lucide-react";
import { Link, useParams } from "react-router-dom";

import { QueryState } from "@/components/feedback/state";
import { PricingBreakdown } from "@/components/pricing/pricing-breakdown";
import { Section } from "@/components/layout/page";
import { Badge, qualityTone, statusTone } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  useFootfallSummary,
  usePriceSpace,
  useSpace,
  useStation,
  useTenantRecommendations,
} from "@/hooks/queries";
import {
  formatDate,
  formatHour,
  formatNumber,
  labelSpaceType,
  labelStatus,
} from "@/lib/formatters";

function Field({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div>
      <dt className="text-xs uppercase tracking-wide text-muted-foreground">{label}</dt>
      <dd className="mt-0.5 text-sm font-medium text-foreground">{value}</dd>
    </div>
  );
}

function TenantRecommendations({ spaceId }: { spaceId: number }) {
  const query = useTenantRecommendations(spaceId);
  return (
    <QueryState
      query={query}
      isEmpty={(r) => r.recommendations.length === 0}
      emptyTitle="No category recommendations"
      emptyHint="No rules-based category matches this space type."
    >
      {(res) => (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {res.recommendations.map((r) => (
            <Card key={r.category}>
              <CardHeader>
                <div className="flex items-center justify-between gap-2">
                  <CardTitle>{r.category}</CardTitle>
                  <Badge tone={qualityTone(r.confidence)}>{r.confidence} confidence</Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <p className="text-xs text-muted-foreground">
                  Compatibility score {(r.score * 100).toFixed(0)} / 100
                </p>
                {r.evidence.length > 0 && (
                  <div>
                    <p className="font-medium">Evidence</p>
                    <ul className="list-inside list-disc text-muted-foreground">
                      {r.evidence.map((e, i) => (
                        <li key={i}>{e}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {r.missing_information.length > 0 && (
                  <div>
                    <p className="font-medium">Missing information</p>
                    <ul className="list-inside list-disc text-muted-foreground">
                      {r.missing_information.map((m, i) => (
                        <li key={i}>{m}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </QueryState>
  );
}

export function SpaceDetailPage() {
  const { id } = useParams();
  const spaceId = id ? Number(id) : undefined;
  const space = useSpace(spaceId);
  const stationId = space.data?.station_id;
  const station = useStation(stationId);
  const footfall = useFootfallSummary(stationId);
  const pricing = usePriceSpace(spaceId);

  return (
    <div>
      <Link
        to="/inventory"
        className="mb-4 inline-flex items-center gap-1 text-sm font-medium text-accent hover:underline"
      >
        <ArrowLeft className="h-4 w-4" /> Back to inventory
      </Link>

      <QueryState query={space}>
        {(sp) => (
          <>
            <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
              <div className="flex flex-wrap items-center gap-3">
                <h2 className="text-xl font-semibold">{sp.space_code}</h2>
                <Badge tone={statusTone(sp.status)}>{labelStatus(sp.status)}</Badge>
                <Badge tone="neutral">{labelSpaceType(sp.space_type)}</Badge>
              </div>
              <Link
                to={`/proposals/new?space_id=${sp.id}`}
                className="inline-flex h-10 items-center gap-2 rounded-md bg-accent px-4 text-sm font-medium text-accent-foreground hover:bg-accent/90"
              >
                <FileText className="h-4 w-4" aria-hidden="true" /> Generate sales proposal
              </Link>
            </div>

            <Section>
              <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
                <Card>
                  <CardHeader>
                    <CardTitle>Space information</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <dl className="grid grid-cols-2 gap-4">
                      <Field label="Space code" value={sp.space_code} />
                      <Field label="Type" value={labelSpaceType(sp.space_type)} />
                      <Field
                        label="Area"
                        value={sp.area_sqm === null ? "Not recorded" : `${formatNumber(Number(sp.area_sqm))} m²`}
                      />
                      <Field
                        label="Visibility"
                        value={
                          sp.visibility_score === null
                            ? "Not recorded"
                            : `${Number(sp.visibility_score).toFixed(1)} / 10`
                        }
                      />
                      <Field label="Floor" value={sp.floor_description ?? "—"} />
                      <Field label="Status" value={labelStatus(sp.status)} />
                      <Field label="Available from" value={formatDate(sp.available_from)} />
                      <Field
                        label="Asking rent"
                        value={
                          sp.asking_monthly_rent === null
                            ? "Not set"
                            : formatNumber(Number(sp.asking_monthly_rent))
                        }
                      />
                    </dl>
                    <p className="mt-4 text-xs text-muted-foreground">
                      Current contractual rent is sensitive lease data and is reported only in
                      aggregate, not per space.
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Station & footfall</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <QueryState query={station}>
                      {(st) => (
                        <dl className="grid grid-cols-2 gap-4">
                          <Field label="Station" value={st.name} />
                          <Field label="Code" value={st.code} />
                          <Field label="Line" value={st.line ?? "—"} />
                          <Field label="Type" value={st.station_type ?? "—"} />
                        </dl>
                      )}
                    </QueryState>
                    <QueryState query={footfall} isEmpty={(f) => f.observation_count === 0} emptyTitle="No footfall data for this station">
                      {(f) => (
                        <dl className="mt-4 grid grid-cols-2 gap-4 border-t border-border pt-4">
                          <Field label="Avg daily entries" value={formatNumber(f.avg_daily_entries, { maximumFractionDigits: 0 })} />
                          <Field label="Peak hour" value={formatHour(f.peak_hour)} />
                          <Field label="Observed days" value={formatNumber(f.distinct_days)} />
                          <Field label="Total entries" value={formatNumber(f.total_entries)} />
                        </dl>
                      )}
                    </QueryState>
                  </CardContent>
                </Card>
              </div>
            </Section>

            <Section title="Indicative pricing recommendation">
              <QueryState query={pricing}>{(est) => <PricingBreakdown estimate={est} />}</QueryState>
            </Section>

            <Section title="Suggested tenant categories">
              <TenantRecommendations spaceId={sp.id} />
            </Section>
          </>
        )}
      </QueryState>
    </div>
  );
}
