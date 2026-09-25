"use client";

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
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { formatNumber } from "@/lib/utils";
import type { ChartConfig } from "@/types/analytics";

import { CHART_AXIS, CHART_GRID, CHART_TEXT_MUTED, seriesColor } from "./palette";

interface DynamicChartProps {
  config: ChartConfig;
  data: Record<string, unknown>[];
}

const tickStyle = { fontSize: 11, fill: CHART_TEXT_MUTED };

function ChartTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: { name: string; value: number; color: string }[];
  label?: string;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border border-border bg-popover px-3 py-2 text-xs shadow-lg">
      {label !== undefined && <p className="mb-1 font-medium text-popover-foreground">{String(label)}</p>}
      {payload.map((p) => (
        <div key={p.name} className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full" style={{ background: p.color }} />
          <span className="text-muted-foreground">{p.name}:</span>
          <span className="font-medium tabular-nums text-popover-foreground">{formatNumber(p.value)}</span>
        </div>
      ))}
    </div>
  );
}

export function DynamicChart({ config, data }: DynamicChartProps) {
  if (!data.length || config.type === "none" || config.type === "table") return null;

  if (config.type === "bar" && config.x && config.y) {
    return (
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 8 }}>
          <CartesianGrid vertical={false} stroke={CHART_GRID} />
          <XAxis dataKey={config.x} tick={tickStyle} axisLine={{ stroke: CHART_AXIS }} tickLine={false} />
          <YAxis
            tick={tickStyle}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v) => formatNumber(v, { compact: true })}
          />
          <Tooltip content={<ChartTooltip />} cursor={{ fill: "var(--muted)", opacity: 0.4 }} />
          <Bar dataKey={config.y} radius={[4, 4, 0, 0]} maxBarSize={48}>
            {data.map((_, i) => (
              <Cell key={i} fill={seriesColor(0)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    );
  }

  if (config.type === "grouped_bar" && config.x && config.series?.length) {
    return (
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 8 }}>
          <CartesianGrid vertical={false} stroke={CHART_GRID} />
          <XAxis dataKey={config.x} tick={tickStyle} axisLine={{ stroke: CHART_AXIS }} tickLine={false} />
          <YAxis
            tick={tickStyle}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v) => formatNumber(v, { compact: true })}
          />
          <Tooltip content={<ChartTooltip />} cursor={{ fill: "var(--muted)", opacity: 0.4 }} />
          <Legend wrapperStyle={{ fontSize: 12, color: CHART_TEXT_MUTED }} />
          {config.series.map((key, i) => (
            <Bar key={key} dataKey={key} fill={seriesColor(i)} radius={[4, 4, 0, 0]} maxBarSize={32} />
          ))}
        </BarChart>
      </ResponsiveContainer>
    );
  }

  if (config.type === "line" && config.x && config.y) {
    return (
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 8 }}>
          <CartesianGrid vertical={false} stroke={CHART_GRID} />
          <XAxis dataKey={config.x} tick={tickStyle} axisLine={{ stroke: CHART_AXIS }} tickLine={false} />
          <YAxis
            tick={tickStyle}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v) => formatNumber(v, { compact: true })}
          />
          <Tooltip content={<ChartTooltip />} cursor={{ stroke: CHART_AXIS }} />
          <Line
            type="monotone"
            dataKey={config.y}
            stroke={seriesColor(0)}
            strokeWidth={2}
            dot={{ r: 3, fill: seriesColor(0), strokeWidth: 0 }}
            activeDot={{ r: 5 }}
          />
        </LineChart>
      </ResponsiveContainer>
    );
  }

  if (config.type === "pie" && config.x && config.y) {
    return (
      <ResponsiveContainer width="100%" height={280}>
        <PieChart margin={{ top: 8, right: 8, left: 8, bottom: 8 }}>
          <Tooltip content={<ChartTooltip />} />
          <Legend wrapperStyle={{ fontSize: 12, color: CHART_TEXT_MUTED }} />
          <Pie
            data={data}
            dataKey={config.y}
            nameKey={config.x}
            innerRadius="55%"
            outerRadius="80%"
            paddingAngle={2}
            stroke="var(--chart-surface)"
            strokeWidth={2}
          >
            {data.map((_, i) => (
              <Cell key={i} fill={seriesColor(i)} />
            ))}
          </Pie>
        </PieChart>
      </ResponsiveContainer>
    );
  }

  if (config.type === "scatter" && config.x && config.y) {
    return (
      <ResponsiveContainer width="100%" height={280}>
        <ScatterChart margin={{ top: 8, right: 8, left: 0, bottom: 8 }}>
          <CartesianGrid stroke={CHART_GRID} />
          <XAxis
            dataKey={config.x}
            type="number"
            name={config.x}
            tick={tickStyle}
            axisLine={{ stroke: CHART_AXIS }}
            tickLine={false}
          />
          <YAxis
            dataKey={config.y}
            type="number"
            name={config.y}
            tick={tickStyle}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<ChartTooltip />} cursor={{ strokeDasharray: "3 3" }} />
          <Scatter data={data} fill={seriesColor(0)} />
        </ScatterChart>
      </ResponsiveContainer>
    );
  }

  return null;
}
