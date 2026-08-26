import { readFile, writeFile } from "node:fs/promises";

const path = "public/data/plotly_charts.json";
const dimPalette = ["#7f9eaa", "#8d7baa", "#aa788c", "#a68e62", "#74a08f", "#6f789f", "#9a82a0"];
const replacements = new Map([
  ["#59d8e8", "#7f9eaa"],
  ["#56d0df", "#7f9eaa"],
  ["#6f8cff", "#6f789f"],
  ["#aa8dff", "#8d7baa"],
  ["#a78bfa", "#8d7baa"],
  ["#b99aff", "#8d7baa"],
  ["#c8a8ff", "#9a82a0"],
  ["#d49cff", "#9a82a0"],
  ["#ef83bb", "#aa788c"],
  ["#f39ccc", "#aa788c"],
  ["#ff7187", "#a86075"],
  ["#efc36b", "#a68e62"],
  ["#f0c987", "#a68e62"],
  ["#ffd166", "#a68e62"],
  ["#64d6ad", "#74a08f"],
  ["#7bd4b8", "#74a08f"],
  ["#4ecdc4", "#74a08f"],
  ["#101f36", "#151225"],
  ["#93a8c8", "#8b8299"],
  ["#888", "#776f83"],
]);

const brightColors = [...replacements.keys()].filter((color) => !["#101f36", "#93a8c8", "#888"].includes(color));

function restyle(value) {
  if (typeof value === "string") {
    const lower = value.toLowerCase();
    return replacements.get(lower) ?? value;
  }
  if (Array.isArray(value)) return value.map(restyle);
  if (value && typeof value === "object") {
    const next = {};
    for (const [key, child] of Object.entries(value)) next[key] = restyle(child);
    if ("layout" in next && next.layout && typeof next.layout === "object") {
      next.layout.colorway = dimPalette;
      next.layout.font = { ...(next.layout.font ?? {}), color: "#aaa0b5" };
      next.layout.paper_bgcolor = "rgba(0,0,0,0)";
      next.layout.plot_bgcolor = "rgba(0,0,0,0)";
    }
    return next;
  }
  return value;
}

const raw = await readFile(path, "utf8");
const parsed = JSON.parse(raw.charCodeAt(0) === 0xfeff ? raw.slice(1) : raw);
const styled = restyle(parsed);
const output = JSON.stringify(styled, null, 0);

if (process.argv.includes("--check")) {
  const lower = output.toLowerCase();
  const found = brightColors.filter((color) => lower.includes(color));
  if (found.length) {
    console.error(`Bright chart colors remain: ${found.join(", ")}`);
    process.exit(1);
  }
  console.log(`Plotly specs use muted chart palette (${Object.keys(styled).length} figures).`);
} else {
  await writeFile(path, output, "utf8");
  console.log(`Restyled ${Object.keys(styled).length} Plotly specs.`);
}
