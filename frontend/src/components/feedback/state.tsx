import { AlertTriangle, Inbox, RefreshCw } from "lucide-react";
import type { UseQueryResult } from "@tanstack/react-query";

import { ApiError } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

export function LoadingBlock({ rows = 3 }: { rows?: number }) {
  return (
    <div className="space-y-3" role="status" aria-live="polite" aria-busy="true">
      <span className="sr-only">Loading…</span>
      {Array.from({ length: rows }).map((_, i) => (
        <Skeleton key={i} className="h-10 w-full" />
      ))}
    </div>
  );
}

export function ErrorBlock({ error, onRetry }: { error: unknown; onRetry?: () => void }) {
  const message = error instanceof Error ? error.message : "Something went wrong.";
  const isDown = error instanceof ApiError && error.status === 0;
  return (
    <div
      role="alert"
      className="flex flex-col items-start gap-3 rounded-lg border border-danger/30 bg-danger/5 p-5"
    >
      <div className="flex items-center gap-2 text-danger">
        <AlertTriangle className="h-5 w-5" aria-hidden="true" />
        <p className="font-medium">{isDown ? "Backend unavailable" : "Could not load data"}</p>
      </div>
      <p className="text-sm text-muted-foreground">{message}</p>
      {onRetry && (
        <Button variant="outline" size="sm" onClick={onRetry}>
          <RefreshCw className="h-4 w-4" aria-hidden="true" /> Try again
        </Button>
      )}
    </div>
  );
}

export function EmptyBlock({ title, hint }: { title: string; hint?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-border bg-surface p-10 text-center">
      <Inbox className="h-7 w-7 text-muted-foreground" aria-hidden="true" />
      <p className="font-medium text-foreground">{title}</p>
      {hint && <p className="max-w-md text-sm text-muted-foreground">{hint}</p>}
    </div>
  );
}

interface QueryStateProps<T> {
  query: UseQueryResult<T>;
  children: (data: T) => React.ReactNode;
  isEmpty?: (data: T) => boolean;
  emptyTitle?: string;
  emptyHint?: string;
  loadingRows?: number;
}

export function QueryState<T>({
  query,
  children,
  isEmpty,
  emptyTitle = "No data",
  emptyHint,
  loadingRows,
}: QueryStateProps<T>) {
  if (query.isPending) return <LoadingBlock rows={loadingRows} />;
  if (query.isError) return <ErrorBlock error={query.error} onRetry={() => query.refetch()} />;
  if (isEmpty && isEmpty(query.data)) return <EmptyBlock title={emptyTitle} hint={emptyHint} />;
  return <>{children(query.data)}</>;
}
