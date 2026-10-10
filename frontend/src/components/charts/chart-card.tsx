import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyBlock } from "@/components/feedback/state";

export function ChartCard({
  title,
  description,
  summary,
  empty,
  emptyTitle = "No data to chart",
  children,
}: {
  title: string;
  description?: string;
  summary: string;
  empty?: boolean;
  emptyTitle?: string;
  children: React.ReactNode;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      <CardContent>
        {empty ? (
          <EmptyBlock title={emptyTitle} />
        ) : (
          <>
            {/* Text alternative so the chart is not purely visual. */}
            <p className="sr-only">{summary}</p>
            <div role="img" aria-label={summary}>
              {children}
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
