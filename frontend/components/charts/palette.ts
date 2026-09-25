/** Categorical series colors, referenced as CSS custom properties so they resolve per-theme
 * automatically (see app/globals.css) — SVG presentation attributes accept var() in evergreen browsers.
 */
export const SERIES_COLORS = [
  "var(--chart-1)",
  "var(--chart-2)",
  "var(--chart-3)",
  "var(--chart-4)",
  "var(--chart-5)",
  "var(--chart-6)",
  "var(--chart-7)",
  "var(--chart-8)",
];

export const CHART_GRID = "var(--chart-grid)";
export const CHART_AXIS = "var(--chart-axis)";
export const CHART_TEXT_SECONDARY = "var(--chart-text-secondary)";
export const CHART_TEXT_MUTED = "var(--chart-text-muted)";

export function seriesColor(index: number): string {
  return SERIES_COLORS[index % SERIES_COLORS.length];
}
