import { cn } from "@/lib/cn";

type Tone = "neutral" | "success" | "warning" | "danger" | "accent";

const TONES: Record<Tone, string> = {
  neutral: "bg-muted text-muted-foreground",
  success: "bg-success/10 text-success",
  warning: "bg-warning/10 text-warning",
  danger: "bg-danger/10 text-danger",
  accent: "bg-accent/10 text-accent",
};

export function Badge({
  tone = "neutral",
  className,
  ...props
}: React.HTMLAttributes<HTMLSpanElement> & { tone?: Tone }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-medium",
        TONES[tone],
        className,
      )}
      {...props}
    />
  );
}

// Status → tone, so meaning is not conveyed by color alone (label text is always shown).
export function statusTone(status: string): Tone {
  switch (status) {
    case "vacant":
      return "accent";
    case "occupied":
      return "success";
    case "under_maintenance":
      return "warning";
    case "unavailable":
      return "neutral";
    default:
      return "neutral";
  }
}

export function qualityTone(quality: string): Tone {
  switch (quality) {
    case "high":
      return "success";
    case "medium":
      return "warning";
    case "low":
      return "danger";
    default:
      return "neutral";
  }
}
