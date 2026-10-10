import { TrainFront, X } from "lucide-react";
import { NavLink } from "react-router-dom";

import { cn } from "@/lib/cn";
import { NAV_ITEMS } from "./nav";

export function SidebarContent({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center gap-2.5 px-5 py-5">
        <div className="flex h-9 w-9 items-center justify-center rounded-md bg-accent text-accent-foreground">
          <TrainFront className="h-5 w-5" aria-hidden="true" />
        </div>
        <div className="leading-tight">
          <p className="text-sm font-semibold">Metro Revenue</p>
          <p className="text-xs text-muted-foreground">Intelligence</p>
        </div>
      </div>
      <nav className="flex-1 space-y-1 px-3 py-2" aria-label="Primary">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            onClick={onNavigate}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-accent/10 text-accent"
                  : "text-muted-foreground hover:bg-muted/60 hover:text-foreground",
              )
            }
          >
            {({ isActive }) => (
              <>
                <item.icon className="h-4 w-4 shrink-0" aria-hidden="true" />
                <span>{item.label}</span>
                {isActive && <span className="sr-only"> (current page)</span>}
              </>
            )}
          </NavLink>
        ))}
      </nav>
      <div className="border-t border-border px-5 py-4">
        <p className="text-xs text-muted-foreground">
          Synthetic demo data. Pricing is indicative, not a verified market rate.
        </p>
      </div>
    </div>
  );
}

export function Sidebar() {
  return (
    <aside className="hidden w-64 shrink-0 border-r border-border bg-surface lg:block">
      <SidebarContent />
    </aside>
  );
}

export function MobileSidebar({ open, onClose }: { open: boolean; onClose: () => void }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-40 lg:hidden">
      <div
        className="absolute inset-0 bg-foreground/40"
        onClick={onClose}
        aria-hidden="true"
      />
      <div
        className="absolute left-0 top-0 h-full w-64 bg-surface shadow-xl"
        role="dialog"
        aria-modal="true"
        aria-label="Navigation"
      >
        <button
          className="absolute right-3 top-4 text-muted-foreground hover:text-foreground"
          onClick={onClose}
          aria-label="Close navigation"
        >
          <X className="h-5 w-5" />
        </button>
        <SidebarContent onNavigate={onClose} />
      </div>
    </div>
  );
}
