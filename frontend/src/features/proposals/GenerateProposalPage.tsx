import { FileText, Sparkles } from "lucide-react";
import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

import { ErrorBlock, QueryState } from "@/components/feedback/state";
import { PageIntro } from "@/components/layout/page";
import { Badge, qualityTone } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input, Label, Textarea } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { useGenerateProposal, usePriceSpace, useSpace } from "@/hooks/queries";
import { formatCurrency, labelSpaceType } from "@/lib/formatters";

const CATEGORY_OPTIONS = [
  { value: "Food & beverage (grab-and-go)", label: "Food & beverage (grab-and-go)" },
  { value: "Convenience retail", label: "Convenience retail" },
  { value: "Consumer electronics accessories", label: "Consumer electronics accessories" },
  { value: "Local brands / specialty retail", label: "Local brands / specialty retail" },
  { value: "Brand-awareness advertising", label: "Brand-awareness advertising" },
  { value: "Digital / experiential advertising", label: "Digital / experiential advertising" },
];
const LANGUAGES = [
  { value: "English", label: "English" },
  { value: "Hindi", label: "Hindi" },
  { value: "Gujarati", label: "Gujarati" },
];

export function GenerateProposalPage() {
  const [params] = useSearchParams();
  const spaceId = params.get("space_id") ? Number(params.get("space_id")) : undefined;
  const navigate = useNavigate();

  const space = useSpace(spaceId);
  const pricing = usePriceSpace(spaceId);
  const generate = useGenerateProposal();

  const [category, setCategory] = useState(CATEGORY_OPTIONS[0]!.value);
  const [businessName, setBusinessName] = useState("");
  const [objective, setObjective] = useState("");
  const [audience, setAudience] = useState("");
  const [budget, setBudget] = useState("");
  const [language, setLanguage] = useState("English");

  if (spaceId === undefined) {
    return <ErrorBlock error={new Error("No space selected. Open a space from inventory first.")} />;
  }

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    generate.mutate(
      {
        space_id: spaceId!,
        tenant_category: category,
        business_name: businessName || null,
        campaign_objective: objective || null,
        target_audience: audience || null,
        budget: budget ? Number(budget) : null,
        language,
      },
      { onSuccess: (p) => navigate(`/proposals/${p.id}`) },
    );
  }

  return (
    <div>
      <PageIntro
        title="Generate sales proposal"
        description="Create a one-page, evidence-grounded proposal from verified backend data. If an AI provider is configured it drafts the copy; otherwise a deterministic template is used. Either way, figures come from the backend."
      />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <QueryState query={space}>
          {(sp) => (
            <Card>
              <CardHeader>
                <CardTitle>Space & evidence</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <p>
                  <span className="text-muted-foreground">Space:</span> {sp.space_code} ·{" "}
                  {labelSpaceType(sp.space_type)}
                </p>
                <p>
                  <span className="text-muted-foreground">Area:</span>{" "}
                  {sp.area_sqm === null ? "Not recorded" : `${sp.area_sqm} m²`}
                </p>
                <QueryState query={pricing}>
                  {(est) => (
                    <div className="rounded-md bg-muted/50 p-3">
                      <p className="flex items-center gap-2">
                        <span className="text-muted-foreground">Indicative price:</span>
                        <span className="font-semibold">
                          {est.available
                            ? formatCurrency(est.indicative_monthly_price, est.currency)
                            : "Unavailable"}
                        </span>
                        <Badge tone={qualityTone(est.data_quality)}>{est.data_quality}</Badge>
                      </p>
                      <p className="mt-1 text-xs text-muted-foreground">{est.explanation}</p>
                    </div>
                  )}
                </QueryState>
              </CardContent>
            </Card>
          )}
        </QueryState>

        <Card>
          <CardHeader>
            <CardTitle>Proposal inputs</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={onSubmit} className="space-y-4">
              <div>
                <Label htmlFor="gp-cat">Tenant / advertiser category</Label>
                <Select
                  id="gp-cat"
                  options={CATEGORY_OPTIONS}
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="gp-name">Business name (optional)</Label>
                <Input id="gp-name" value={businessName} onChange={(e) => setBusinessName(e.target.value)} />
              </div>
              <div>
                <Label htmlFor="gp-obj">Campaign / usage objective (optional)</Label>
                <Textarea
                  id="gp-obj"
                  rows={2}
                  value={objective}
                  onChange={(e) => setObjective(e.target.value)}
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <Label htmlFor="gp-aud">Target audience (optional)</Label>
                  <Input id="gp-aud" value={audience} onChange={(e) => setAudience(e.target.value)} />
                </div>
                <div>
                  <Label htmlFor="gp-budget">Budget (optional)</Label>
                  <Input
                    id="gp-budget"
                    type="number"
                    min={0}
                    value={budget}
                    onChange={(e) => setBudget(e.target.value)}
                  />
                </div>
              </div>
              <div>
                <Label htmlFor="gp-lang">Language</Label>
                <Select
                  id="gp-lang"
                  options={LANGUAGES}
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                />
              </div>

              {generate.isError && <ErrorBlock error={generate.error} />}

              <Button type="submit" disabled={generate.isPending} className="w-full">
                {generate.isPending ? (
                  <>
                    <Sparkles className="h-4 w-4 animate-pulse" aria-hidden="true" /> Generating…
                  </>
                ) : (
                  <>
                    <FileText className="h-4 w-4" aria-hidden="true" /> Generate proposal
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
