import { Calculator } from "lucide-react";
import { useState } from "react";

import { ErrorBlock } from "@/components/feedback/state";
import { PricingBreakdown } from "@/components/pricing/pricing-breakdown";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input, Label } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { useEstimateMutation } from "@/hooks/queries";
import type { SpaceType } from "@/types/api";

const TYPE_OPTIONS = [
  { value: "retail", label: "Retail" },
  { value: "kiosk", label: "Kiosk" },
  { value: "advertising_panel", label: "Advertising panel" },
  { value: "digital_screen", label: "Digital screen" },
];

export function EstimateForm() {
  const [spaceType, setSpaceType] = useState<SpaceType>("retail");
  const [area, setArea] = useState("");
  const [visibility, setVisibility] = useState("");
  const [footfall, setFootfall] = useState("");
  const [error, setError] = useState<string | null>(null);
  const mutation = useEstimateMutation();

  const unitPriced = spaceType === "advertising_panel" || spaceType === "digital_screen";

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (!unitPriced && !area) {
      setError("Area is required for retail and kiosk spaces.");
      return;
    }
    if (visibility && (Number(visibility) < 1 || Number(visibility) > 10)) {
      setError("Visibility must be between 1 and 10.");
      return;
    }
    mutation.mutate({
      space_type: spaceType,
      area_sqm: area ? Number(area) : null,
      visibility_score: visibility ? Number(visibility) : null,
      observed_daily_footfall: footfall ? Number(footfall) : null,
    });
  }

  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
      <Card className="lg:col-span-1">
        <CardHeader>
          <CardTitle>Price scenario</CardTitle>
          <CardDescription>
            Estimate an indicative price for hypothetical inputs. The backend performs the
            authoritative calculation. This is a what-if scenario, not an approved rate.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} className="space-y-4" noValidate>
            <div>
              <Label htmlFor="est-type">Space type</Label>
              <Select
                id="est-type"
                options={TYPE_OPTIONS}
                value={spaceType}
                onChange={(e) => setSpaceType(e.target.value as SpaceType)}
              />
            </div>
            <div>
              <Label htmlFor="est-area">
                Area (m²){!unitPriced ? " *" : " (optional for panels)"}
              </Label>
              <Input
                id="est-area"
                type="number"
                min={0}
                step="0.1"
                value={area}
                onChange={(e) => setArea(e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="est-vis">Visibility score (1–10)</Label>
              <Input
                id="est-vis"
                type="number"
                min={1}
                max={10}
                step="0.1"
                value={visibility}
                onChange={(e) => setVisibility(e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="est-foot">Observed daily footfall</Label>
              <Input
                id="est-foot"
                type="number"
                min={0}
                value={footfall}
                onChange={(e) => setFootfall(e.target.value)}
              />
            </div>
            {error && (
              <p role="alert" className="text-sm text-danger">
                {error}
              </p>
            )}
            <Button type="submit" disabled={mutation.isPending} className="w-full">
              <Calculator className="h-4 w-4" aria-hidden="true" />
              {mutation.isPending ? "Calculating…" : "Estimate price"}
            </Button>
          </form>
        </CardContent>
      </Card>

      <div className="lg:col-span-2">
        {mutation.isError && <ErrorBlock error={mutation.error} />}
        {mutation.data ? (
          <PricingBreakdown estimate={mutation.data} />
        ) : (
          !mutation.isError && (
            <Card>
              <CardContent className="flex h-full min-h-40 items-center justify-center p-8 text-center text-sm text-muted-foreground">
                Enter inputs and run an estimate to see the backend pricing breakdown.
              </CardContent>
            </Card>
          )
        )}
      </div>
    </div>
  );
}
