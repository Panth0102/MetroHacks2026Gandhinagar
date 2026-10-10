import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

// Categorical palette: accent blue first, then distinct, color-blind-friendlier hues.
export const CHART_COLORS = ["#2f54b8", "#17a2a2", "#e08a1e", "#6b53c4", "#4b7f52", "#b2456b"];

const AXIS = { fontSize: 12, fill: "hsl(215 16% 42%)" };
const gridStroke = "hsl(214 20% 89%)";

interface BarDatum {
  label: string;
  value: number;
}

export function SimpleBarChart({
  data,
  valueFormatter,
  color = CHART_COLORS[0],
  horizontal = false,
  height = 280,
}: {
  data: BarDatum[];
  valueFormatter?: (v: number) => string;
  color?: string;
  horizontal?: boolean;
  height?: number;
}) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart
        data={data}
        layout={horizontal ? "vertical" : "horizontal"}
        margin={{ top: 8, right: 12, bottom: 8, left: horizontal ? 24 : 0 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} vertical={!horizontal} />
        {horizontal ? (
          <>
            <XAxis type="number" tick={AXIS} tickFormatter={valueFormatter} />
            <YAxis type="category" dataKey="label" tick={AXIS} width={120} />
          </>
        ) : (
          <>
            <XAxis dataKey="label" tick={AXIS} interval={0} angle={-20} textAnchor="end" height={56} />
            <YAxis tick={AXIS} tickFormatter={valueFormatter} width={56} />
          </>
        )}
        <Tooltip
          formatter={(v: number) => (valueFormatter ? valueFormatter(v) : v)}
          contentStyle={{ fontSize: 12, borderRadius: 8, border: `1px solid ${gridStroke}` }}
        />
        <Bar dataKey="value" fill={color} radius={[4, 4, 0, 0]} maxBarSize={48} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function SimpleLineChart({
  data,
  valueFormatter,
  height = 280,
}: {
  data: BarDatum[];
  valueFormatter?: (v: number) => string;
  height?: number;
}) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 8, right: 12, bottom: 8, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} />
        <XAxis dataKey="label" tick={AXIS} />
        <YAxis tick={AXIS} tickFormatter={valueFormatter} width={56} />
        <Tooltip
          formatter={(v: number) => (valueFormatter ? valueFormatter(v) : v)}
          contentStyle={{ fontSize: 12, borderRadius: 8, border: `1px solid ${gridStroke}` }}
        />
        <Line
          type="monotone"
          dataKey="value"
          stroke={CHART_COLORS[0]}
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 4 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

export function SimpleDonut({
  data,
  valueFormatter,
  height = 280,
}: {
  data: BarDatum[];
  valueFormatter?: (v: number) => string;
  height?: number;
}) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <PieChart>
        <Pie
          data={data}
          dataKey="value"
          nameKey="label"
          innerRadius={60}
          outerRadius={95}
          paddingAngle={2}
        >
          {data.map((_, i) => (
            <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
          ))}
        </Pie>
        <Tooltip
          formatter={(v: number) => (valueFormatter ? valueFormatter(v) : v)}
          contentStyle={{ fontSize: 12, borderRadius: 8, border: `1px solid ${gridStroke}` }}
        />
        <Legend wrapperStyle={{ fontSize: 12 }} />
      </PieChart>
    </ResponsiveContainer>
  );
}
