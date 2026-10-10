import { Card, CardContent } from "@/components/ui/card";
import { InfoTooltip } from "@/components/ui/info-tooltip";
import { Skeleton } from "@/components/ui/skeleton";

export function StatCard({
  label,
  value,
  hint,
  sublabel,
  loading,
}: {
  label: string;
  value: string;
  hint?: string;
  sublabel?: string;
  loading?: boolean;
}) {
  return (
    <Card>
      <CardContent className="p-5 pt-5">
        <div className="flex items-center gap-1.5">
          <p className="text-sm font-medium text-muted-foreground">{label}</p>
          {hint && <InfoTooltip text={hint} label={`About ${label}`} />}
        </div>
        {loading ? (
          <Skeleton className="mt-2 h-8 w-28" />
        ) : (
          <p className="mt-1 text-2xl font-semibold tabular-nums text-foreground">{value}</p>
        )}
        {sublabel && <p className="mt-1 text-xs text-muted-foreground">{sublabel}</p>}
      </CardContent>
    </Card>
  );
}
