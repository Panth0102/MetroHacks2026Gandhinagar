import { Info } from "lucide-react";
import { useId, useState } from "react";

// Small accessible tooltip: shows on hover and keyboard focus, dismissable via
// Escape, with an aria-describedby association.
export function InfoTooltip({ text, label = "More information" }: { text: string; label?: string }) {
  const [open, setOpen] = useState(false);
  const id = useId();
  return (
    <span className="relative inline-flex">
      <button
        type="button"
        aria-label={label}
        aria-describedby={open ? id : undefined}
        className="text-muted-foreground hover:text-foreground"
        onMouseEnter={() => setOpen(true)}
        onMouseLeave={() => setOpen(false)}
        onFocus={() => setOpen(true)}
        onBlur={() => setOpen(false)}
        onKeyDown={(e) => e.key === "Escape" && setOpen(false)}
      >
        <Info className="h-3.5 w-3.5" aria-hidden="true" />
      </button>
      {open && (
        <span
          role="tooltip"
          id={id}
          className="absolute left-1/2 top-6 z-20 w-56 -translate-x-1/2 rounded-md border border-border bg-surface p-2.5 text-xs font-normal text-muted-foreground shadow-card"
        >
          {text}
        </span>
      )}
    </span>
  );
}
