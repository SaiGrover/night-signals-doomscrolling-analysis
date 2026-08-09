import { readFile, writeFile } from "node:fs/promises";

const path = "public/data/plotly_charts.json";
const specs = JSON.parse(await readFile(path, "utf8"));
let replacements = 0;
for (const spec of Object.values(specs)) {
  for (const trace of spec.data ?? []) {
    if (trace.type === "scattergl") {
      trace.type = "scatter";
      replacements += 1;
    }
  }
}
if (process.argv.includes("--check")) {
  if (replacements) throw new Error(`${replacements} WebGL-only traces remain`);
} else {
  await writeFile(path, JSON.stringify(specs), "utf8");
  console.log(`converted ${replacements} WebGL-only traces to SVG`);
}
