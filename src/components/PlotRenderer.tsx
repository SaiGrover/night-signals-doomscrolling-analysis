import createPlotlyComponent from "react-plotly.js/factory";
import Plotly from "plotly.js-dist-min";
import { useState } from "react";
import type { Config, Data, Layout } from "plotly.js";

const Plot = createPlotlyComponent(Plotly);

export type PlotSpec = { data: Data[]; layout: Partial<Layout> };
type AccessibleRow = { series: string; label: unknown; value: unknown };

function rowsFor(trace: Data): AccessibleRow[] {
  const item = trace as unknown as { name?: string; x?: unknown[]; y?: unknown[]; z?: unknown[][] };
  if (Array.isArray(item.z)) return item.z.flatMap((row, rowIndex) => row.map((value, columnIndex) => ({
    series: item.name ?? "Heatmap", label: `${item.y?.[rowIndex] ?? rowIndex} / ${item.x?.[columnIndex] ?? columnIndex}`, value,
  })));
  const count = Math.max(item.x?.length ?? 0, item.y?.length ?? 0);
  return Array.from({ length: count }, (_, index) => ({
    series: item.name ?? "Series", label: item.x?.[index] ?? index + 1, value: item.y?.[index] ?? "",
  }));
}

export default function PlotRenderer({ spec, title }: { spec: PlotSpec; title: string }) {
  const [showTable, setShowTable] = useState(false);
  const safeData = spec.data.map((trace) => trace.type === "scattergl" ? ({ ...trace, type: "scatter" } as Data) : trace);
  const axisDefaults = { gridcolor: "rgba(147,168,200,.12)", zerolinecolor: "rgba(147,168,200,.18)", tickfont: { color: "#aebed5", size: 11 }, title: { font: { color: "#d5deed" } } };
  const layout: Partial<Layout> = { ...spec.layout, autosize: true, width: undefined, height: undefined,
    paper_bgcolor: "rgba(0,0,0,0)", plot_bgcolor: "rgba(0,0,0,0)",
    font: { family: '"JetBrains Mono", monospace', color: "#b8c6d9", size: 11 },
    margin: { l: 55, r: 24, t: 42, b: 52, ...spec.layout?.margin },
    hoverlabel: { bgcolor: "#07111f", bordercolor: "#59d8e8", font: { color: "#fff", family: '"JetBrains Mono", monospace' } } };
  for (const key of ["xaxis", "xaxis2", "xaxis3", "xaxis4", "yaxis", "yaxis2", "yaxis3", "yaxis4"] as const) {
    const existing = (spec.layout as Record<string, unknown>)?.[key] as Record<string, unknown> | undefined;
    (layout as Record<string, unknown>)[key] = { ...axisDefaults, ...existing };
  }
  const rows = showTable ? safeData.flatMap(rowsFor) : [];
  return <figure className="accessible-plot">
    <Plot data={safeData} layout={layout as Layout}
      config={{ responsive: true, displaylogo: false, scrollZoom: false, modeBarButtonsToRemove: ["lasso2d", "select2d"] } as Partial<Config>}
      useResizeHandler style={{ width: "100%", height: "100%" }} aria-label={title} />
    <figcaption className="sr-only">{title}. Interactive visualization; an equivalent numeric table is available below.</figcaption>
    <details className="plot-data-disclosure" onToggle={(event) => setShowTable(event.currentTarget.open)}>
      <summary>Accessible data table</summary>
      {showTable && <div className="plot-table-wrap"><table><thead><tr><th>Series</th><th>Label / x</th><th>Value / y</th></tr></thead><tbody>{rows.map((row, index) => <tr key={index}><td>{String(row.series)}</td><td>{String(row.label)}</td><td>{String(row.value)}</td></tr>)}</tbody></table></div>}
    </details>
  </figure>;
}
