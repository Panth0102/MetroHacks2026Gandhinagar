import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import type { Proposal } from "@/types/api";

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="mb-3">
      <h4 className="text-[11px] font-semibold uppercase tracking-wide text-accent">{title}</h4>
      <div className="mt-1 text-sm text-foreground">{children}</div>
    </div>
  );
}

export function ProposalPreview({ proposal }: { proposal: Proposal }) {
  const c = proposal.content;
  const station = String(proposal.context_snapshot.station?.["name"] ?? "");
  const spaceCode = String(proposal.context_snapshot.space?.["space_code"] ?? "");
  return (
    <Card>
      <CardContent className="p-6">
        {/* A4-proportion document preview */}
        <div className="mx-auto max-w-[640px]">
          <div className="mb-3 h-1 w-full rounded bg-accent" />
          <div className="mb-3 flex items-start justify-between gap-3">
            <div>
              <h3 className="text-lg font-semibold leading-tight">{c.title}</h3>
              <p className="text-xs text-muted-foreground">
                {station} · Space {spaceCode}
              </p>
            </div>
            <div className="text-right text-xs text-muted-foreground">
              <p>{proposal.reference_code}</p>
              <Badge tone={proposal.generation_source === "ai" ? "accent" : "neutral"}>
                {proposal.generation_source === "ai" ? "AI-generated" : "Template"}
              </Badge>
            </div>
          </div>

          {c.verified_metrics.length > 0 && (
            <div className="mb-3 grid grid-cols-3 gap-2 rounded-md bg-muted/50 p-3">
              {c.verified_metrics.map((m, i) => (
                <div key={i}>
                  <p className="text-[10px] uppercase text-muted-foreground">{m.label}</p>
                  <p className="text-sm font-semibold tabular-nums">{m.value}</p>
                </div>
              ))}
            </div>
          )}

          <Section title="Executive summary">{c.executive_summary}</Section>
          {c.location_highlights.length > 0 && (
            <Section title="Location highlights">
              <ul className="list-inside list-disc">
                {c.location_highlights.map((h, i) => (
                  <li key={i}>{h}</li>
                ))}
              </ul>
            </Section>
          )}
          <Section title="Commercial opportunity">{c.commercial_opportunity}</Section>
          <Section title="Indicative pricing">{c.pricing_summary}</Section>
          {c.suggested_usage && <Section title="Suggested usage">{c.suggested_usage}</Section>}
          <Section title="Next steps">{c.call_to_action}</Section>
          {c.assumptions_and_limitations.length > 0 && (
            <Section title="Assumptions & limitations">
              <ul className="list-inside list-disc text-xs text-muted-foreground">
                {c.assumptions_and_limitations.map((a, i) => (
                  <li key={i}>{a}</li>
                ))}
              </ul>
            </Section>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export function statusLabel(status: string): string {
  return { draft: "Draft", ready_for_review: "Ready for review", approved: "Approved" }[status] ?? status;
}

export function statusTone(status: string): "neutral" | "warning" | "success" {
  return status === "approved" ? "success" : status === "ready_for_review" ? "warning" : "neutral";
}
