import {
  Building2,
  LayoutDashboard,
  LineChart,
  Receipt,
  Tags,
  TrainFront,
  type LucideIcon,
} from "lucide-react";

export interface NavItem {
  to: string;
  label: string;
  icon: LucideIcon;
  end?: boolean;
}

export const NAV_ITEMS: NavItem[] = [
  { to: "/", label: "Overview", icon: LayoutDashboard, end: true },
  { to: "/stations", label: "Stations & Footfall", icon: TrainFront },
  { to: "/inventory", label: "Commercial Inventory", icon: Building2 },
  { to: "/pricing", label: "Pricing & Rate Cards", icon: Tags },
  { to: "/opportunities", label: "Revenue Opportunities", icon: LineChart },
  { to: "/scenarios", label: "Revenue Scenarios", icon: Receipt },
];
