import { ChartCard } from "@/components/charts/chart-card";
import { SimpleBarChart } from "@/components/charts/charts";
import { Badge, qualityTone } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TBody, TD, TH, THead, TR, Table } from "@/components/ui/table";
import { formatCurrency, labelStatus } from "@/lib/formatters";
import type { PricingEstimate } from "@/types/api";

export function PricingBreakdown({ estimate }: { estimate: PricingEstimate }) {
  if (!estimate.available) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Indicative price unavailable</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">{estimate.explanation}</p>
          {estimate.limitations.length > 0 && (
            <ul className="mt-3 list-inside list-disc text-sm text-muted-foreground">
              {estimate.limitations.map((l, i) => (
                <li key={i}>{l}</li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    );
  }

  const factorData = estimate.factors
    .filter((f) => f.name !== "base_component")
    .map((f) => ({ label: f.name.replace(/_/g, " "), value: f.value }));

  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Indicative monthly price</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-baseline gap-3">
            <p className="text-3xl font-semibold tabular-nums">
              {formatCurrency(estimate.indicative_monthly_price, estimate.currency)}
            </p>
            <Badge tone="neutral">per month</Badge>
          </div>
          <p className="mt-1 text-sm text-muted-foreground">
            {formatCurrency(estimate.indicative_annual_price, estimate.currency)} / year (indicative)
          </p>
          <div className="mt-4 flex flex-wrap items-center gap-2">
            <Badge tone={qualityTone(estimate.data_quality)}>
              Data quality: {labelStatus(estimate.data_quality)}
            </Badge>
            <Badge tone="neutral">Model {estimate.model_version}</Badge>
            <Badge tone="accent">Indicative, not a verified market rate</Badge>
          </div>
          <p className="mt-4 text-sm text-muted-foreground">{estimate.explanation}</p>
          {estimate.data_quality_reasons.length > 0 && (
            <p className="mt-2 text-xs text-muted-foreground">
              {estimate.data_quality_reasons.join("; ")}
            </p>
          )}
        </CardContent>
      </Card>

      <ChartCard
        title="Pricing factors"
        description="Each bounded adjustment applied to the base component."
        summary={`Pricing factors: ${estimate.factors
          .map((f) => `${f.name} ${f.value}`)
          .join(", ")}.`}
        empty={factorData.length === 0}
      >
        <SimpleBarChart data={factorData} valueFormatter={(v) => v.toFixed(3)} height={220} />
      </ChartCard>

      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle>Factor detail & assumptions</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <THead>
              <TR>
                <TH>Factor</TH>
                <TH className="text-right">Value</TH>
                <TH>Description</TH>
              </TR>
            </THead>
            <TBody>
              {estimate.factors.map((f) => (
                <TR key={f.name}>
                  <TD className="font-medium">{f.name.replace(/_/g, " ")}</TD>
                  <TD className="text-right tabular-nums">
                    {f.name === "base_component"
                      ? formatCurrency(f.value, estimate.currency)
                      : f.value.toFixed(3)}
                  </TD>
                  <TD className="text-muted-foreground">{f.description}</TD>
                </TR>
              ))}
            </TBody>
          </Table>

          {estimate.limitations.length > 0 && (
            <div className="mt-4">
              <p className="text-sm font-medium">Limitations</p>
              <ul className="mt-1 list-inside list-disc text-sm text-muted-foreground">
                {estimate.limitations.map((l, i) => (
                  <li key={i}>{l}</li>
                ))}
              </ul>
            </div>
          )}

          <details className="mt-4">
            <summary className="cursor-pointer text-sm font-medium">Model assumptions</summary>
            <pre className="mt-2 overflow-x-auto rounded-md bg-muted p-3 text-xs text-muted-foreground">
              {JSON.stringify(estimate.assumptions, null, 2)}
            </pre>
          </details>
        </CardContent>
      </Card>
    </div>
  );
}
