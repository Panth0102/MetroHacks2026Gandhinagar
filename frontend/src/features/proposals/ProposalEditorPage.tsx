import { ArrowLeft, Download, RefreshCw, Save } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { ProposalPreview, statusLabel, statusTone } from "@/components/proposals/ProposalPreview";
import { ErrorBlock, QueryState } from "@/components/feedback/state";
import { PageIntro } from "@/components/layout/page";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input, Label, Textarea } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { api } from "@/lib/api-client";
import { formatDate } from "@/lib/formatters";
import { useProposal, useRegenerateProposal, useUpdateProposal } from "@/hooks/queries";
import type { Proposal, ProposalContent, ProposalStatus } from "@/types/api";

const STATUS_OPTIONS = [
  { value: "draft", label: "Draft" },
  { value: "ready_for_review", label: "Ready for review" },
  { value: "approved", label: "Approved" },
];

type Draft = {
  title: string;
  executive_summary: string;
  location_highlights: string;
  commercial_opportunity: string;
  pricing_summary: string;
  suggested_usage: string;
  call_to_action: string;
  assumptions_and_limitations: string;
  status: ProposalStatus;
};

function toDraft(p: Proposal): Draft {
  const c = p.content;
  return {
    title: c.title,
    executive_summary: c.executive_summary,
    location_highlights: c.location_highlights.join("\n"),
    commercial_opportunity: c.commercial_opportunity,
    pricing_summary: c.pricing_summary,
    suggested_usage: c.suggested_usage,
    call_to_action: c.call_to_action,
    assumptions_and_limitations: c.assumptions_and_limitations.join("\n"),
    status: p.status,
  };
}

function draftToContent(draft: Draft, original: ProposalContent): ProposalContent {
  return {
    ...original, // keeps verified_metrics (facts) unchanged
    title: draft.title,
    executive_summary: draft.executive_summary,
    location_highlights: draft.location_highlights.split("\n").map((s) => s.trim()).filter(Boolean),
    commercial_opportunity: draft.commercial_opportunity,
    pricing_summary: draft.pricing_summary,
    suggested_usage: draft.suggested_usage,
    call_to_action: draft.call_to_action,
    assumptions_and_limitations: draft.assumptions_and_limitations
      .split("\n")
      .map((s) => s.trim())
      .filter(Boolean),
  };
}

function EditorInner({ proposal }: { proposal: Proposal }) {
  const update = useUpdateProposal(proposal.id);
  const regenerate = useRegenerateProposal(proposal.id);
  const [draft, setDraft] = useState<Draft>(() => toDraft(proposal));
  const [dirty, setDirty] = useState(false);

  // Re-seed the draft only when regeneration replaces the server content.
  useEffect(() => {
    if (!dirty) setDraft(toDraft(proposal));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [proposal.updated_at, proposal.generation_source]);

  const set = <K extends keyof Draft>(key: K, value: Draft[K]) => {
    setDraft((d) => ({ ...d, [key]: value }));
    setDirty(true);
  };

  const previewProposal: Proposal = {
    ...proposal,
    status: draft.status,
    content: draftToContent(draft, proposal.content),
  };

  function onSave() {
    update.mutate(
      { content: draftToContent(draft, proposal.content), status: draft.status },
      { onSuccess: () => setDirty(false) },
    );
  }

  function onRegenerate() {
    if (dirty && !window.confirm("Regenerating replaces the current text with a fresh draft. Your unsaved edits will be lost. Continue?"))
      return;
    setDirty(false);
    regenerate.mutate();
  }

  return (
    <div>
      <Link
        to="/proposals"
        className="mb-4 inline-flex items-center gap-1 text-sm font-medium text-accent hover:underline"
      >
        <ArrowLeft className="h-4 w-4" /> All proposals
      </Link>

      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2">
          <h2 className="text-xl font-semibold">{proposal.reference_code}</h2>
          <Badge tone={statusTone(draft.status)}>{statusLabel(draft.status)}</Badge>
          <Badge tone={proposal.generation_source === "ai" ? "accent" : "neutral"}>
            {proposal.generation_source === "ai"
              ? `AI-generated (${proposal.ai_model ?? "model"})`
              : "Template-generated"}
          </Badge>
          {dirty && <Badge tone="warning">Unsaved edits</Badge>}
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={onRegenerate} disabled={regenerate.isPending}>
            <RefreshCw className="h-4 w-4" aria-hidden="true" /> Regenerate
          </Button>
          <a
            href={api.downloadUrl(`/api/v1/proposals/${proposal.id}/pdf`)}
            target="_blank"
            rel="noreferrer"
            className="inline-flex h-8 items-center gap-2 rounded-md border border-input bg-surface px-3 text-sm font-medium hover:bg-muted/60"
          >
            <Download className="h-4 w-4" aria-hidden="true" /> Download PDF
          </a>
          <Button size="sm" onClick={onSave} disabled={update.isPending || !dirty}>
            <Save className="h-4 w-4" aria-hidden="true" /> {update.isPending ? "Saving…" : "Save"}
          </Button>
        </div>
      </div>

      {update.isError && (
        <div className="mb-4">
          <ErrorBlock error={update.error} />
          <p className="mt-1 text-xs text-muted-foreground">Your edits are preserved — try saving again.</p>
        </div>
      )}
      {regenerate.isError && <div className="mb-4"><ErrorBlock error={regenerate.error} /></div>}

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Edit content</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="e-title">Title</Label>
              <Input id="e-title" value={draft.title} onChange={(e) => set("title", e.target.value)} />
            </div>
            <div>
              <Label htmlFor="e-status">Status</Label>
              <Select
                id="e-status"
                options={STATUS_OPTIONS}
                value={draft.status}
                onChange={(e) => set("status", e.target.value as ProposalStatus)}
              />
            </div>
            <div>
              <Label htmlFor="e-sum">Executive summary</Label>
              <Textarea id="e-sum" rows={3} value={draft.executive_summary} onChange={(e) => set("executive_summary", e.target.value)} />
            </div>
            <div>
              <Label htmlFor="e-high">Location highlights (one per line)</Label>
              <Textarea id="e-high" rows={3} value={draft.location_highlights} onChange={(e) => set("location_highlights", e.target.value)} />
            </div>
            <div>
              <Label htmlFor="e-opp">Commercial opportunity</Label>
              <Textarea id="e-opp" rows={3} value={draft.commercial_opportunity} onChange={(e) => set("commercial_opportunity", e.target.value)} />
            </div>
            <div>
              <Label htmlFor="e-price">Pricing summary</Label>
              <Textarea id="e-price" rows={2} value={draft.pricing_summary} onChange={(e) => set("pricing_summary", e.target.value)} />
            </div>
            <div>
              <Label htmlFor="e-use">Suggested usage</Label>
              <Textarea id="e-use" rows={2} value={draft.suggested_usage} onChange={(e) => set("suggested_usage", e.target.value)} />
            </div>
            <div>
              <Label htmlFor="e-cta">Call to action</Label>
              <Textarea id="e-cta" rows={2} value={draft.call_to_action} onChange={(e) => set("call_to_action", e.target.value)} />
            </div>
            <div>
              <Label htmlFor="e-assume">Assumptions & limitations (one per line)</Label>
              <Textarea id="e-assume" rows={3} value={draft.assumptions_and_limitations} onChange={(e) => set("assumptions_and_limitations", e.target.value)} />
            </div>
            <p className="text-xs text-muted-foreground">
              Verified metrics are backend facts and are not editable here. Last updated{" "}
              {formatDate(proposal.updated_at)}.
            </p>
          </CardContent>
        </Card>

        <div>
          <p className="mb-2 text-sm font-medium text-muted-foreground">Live preview</p>
          <ProposalPreview proposal={previewProposal} />
        </div>
      </div>
    </div>
  );
}

export function ProposalEditorPage() {
  const { id } = useParams();
  const proposalId = id ? Number(id) : undefined;
  const query = useProposal(proposalId);

  return (
    <div>
      <PageIntro title="Proposal editor" description="Review, edit, regenerate, and download the one-page proposal." />
      <QueryState query={query}>{(p) => <EditorInner proposal={p} />}</QueryState>
    </div>
  );
}
