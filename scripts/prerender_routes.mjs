import { mkdir, readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";

const origin = "https://night-signals-doomscrolling-analysi.vercel.app";
const pages = {
  overview: ["Overview · Night Signals", "Key findings on doomscrolling, sleep, mental wellbeing, and protective routines."],
  problem: ["Problem Statement · Night Signals", "A detailed problem statement for studying how doomscrolling, negative news, and bedtime routines relate to sleep."],
  analysis: ["Evidence Atlas · Night Signals", "Fourteen interactive figures with interpretations, practical relevance, accessible tables, and analytical boundaries."],
  modeling: ["Predictive Modelling · Night Signals", "Leakage-safe pre-outcome modelling with nested validation, calibration, uncertainty, subgroup audits, and an untouched holdout."],
  exceptions: ["The Exceptions · Night Signals", "An exploratory look at the eleven high-exposure respondents who still report good sleep."],
  personas: ["Personas · Night Signals", "Transparent, rule-based research personas for intervention design—not diagnoses."],
  methodology: ["Methodology · Night Signals", "Executed exploratory and predictive notebooks, reproducibility details, synthetic-data checks, and validation boundaries."],
};

const template = await readFile("dist/index.html", "utf8");
for (const [route, [title, description]] of Object.entries(pages)) {
  const url = `${origin}/${route}`;
  const html = template
    .replace(/<title>.*?<\/title>/, `<title>${title}</title>`)
    .replace(/<meta name="description" content=".*?" \/>/, `<meta name="description" content="${description}" />`)
    .replace(/<link rel="canonical" href=".*?" \/>/, `<link rel="canonical" href="${url}" />`)
    .replace(/<meta property="og:title" content=".*?" \/>/, `<meta property="og:title" content="${title}" />`)
    .replace(/<meta property="og:description" content=".*?" \/>/, `<meta property="og:description" content="${description}" />`)
    .replace(/<meta property="og:url" content=".*?" \/>/, `<meta property="og:url" content="${url}" />`);
  const directory = join("dist", route);
  await mkdir(directory, { recursive: true });
  await writeFile(join(directory, "index.html"), html);
}
