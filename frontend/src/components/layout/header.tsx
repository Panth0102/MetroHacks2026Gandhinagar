import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Menu, RefreshCw } from "lucide-react";
import { Link, useLocation } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { api } from "@/lib/api-client";
import { cn } from "@/lib/cn";
import { NAV_ITEMS } from "./nav";

interface ReadyResponse {
  status: string;
  database: string;
  database_backend: string;
}

function usePageTitle(): string {
  const { pathname } = useLocation();
  if (pathname.startsWith("/inventory/")) return "Space Detail";
  if (pathname.startsWith("/pricing/")) return "Pricing Detail";
  const match = NAV_ITEMS.find((n) => (n.end ? n.to === pathname : pathname.startsWith(n.to)));
  return match?.label ?? "Overview";
}

function BackendStatus() {
  const { data, isError } = useQuery({
    queryKey: ["health", "ready"],
    queryFn: ({ signal }) => api.get<ReadyResponse>("/health/ready", undefined, signal),
    refetchInterval: 30_000,
    retry: false,
  });
  const up = !isError && data?.database === "up";
  return (
    <span className="hidden items-center gap-1.5 text-xs text-muted-foreground sm:inline-flex">
      <span
        className={cn("h-2 w-2 rounded-full", up ? "bg-success" : "bg-danger")}
        aria-hidden="true"
      />
      {up ? `API connected (${data?.database_backend ?? "db"})` : "API offline"}
    </span>
  );
}

export function Header({ onMenu }: { onMenu: () => void }) {
  const title = usePageTitle();
  const queryClient = useQueryClient();
  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-3 border-b border-border bg-surface/95 px-4 backdrop-blur md:px-6">
      <Button variant="ghost" size="icon" className="lg:hidden" onClick={onMenu} aria-label="Open navigation">
        <Menu className="h-5 w-5" />
      </Button>
      <div className="min-w-0 flex-1">
        <nav aria-label="Breadcrumb" className="text-xs text-muted-foreground">
          <Link to="/" className="hover:text-foreground">
            Metro Revenue
          </Link>
          <span aria-hidden="true"> / </span>
          <span className="text-foreground">{title}</span>
        </nav>
        <h1 className="truncate text-lg font-semibold">{title}</h1>
      </div>
      <BackendStatus />
      <Button
        variant="outline"
        size="sm"
        onClick={() => queryClient.invalidateQueries()}
        aria-label="Refresh data"
      >
        <RefreshCw className="h-4 w-4" aria-hidden="true" />
        <span className="hidden sm:inline">Refresh</span>
      </Button>
    </header>
  );
}
