import { createContext, useContext, useEffect, useMemo, useRef, useState } from "react";
import createPlotlyComponent from "react-plotly.js/factory";
import Plotly from "plotly.js-dist-min";
import type { Config, Data, Layout } from "plotly.js";
import type { CSSProperties } from "react";

const Plot = createPlotlyComponent(Plotly);

type Route = "landing" | "overview" | "analysis" | "exceptions" | "personas" | "methodology";
type ChartGroup = "Overview" | "Core" | "Mind" | "Protection" | "Demographics" | "Exceptions" | "Personas" | "Synthesis";
type PlotSpec = { data: Data[]; layout: Partial<Layout> };
const PlotSpecsContext = createContext<Record<string, PlotSpec>>({});

const plotHeights: Record<string, number> = {
  "01_descriptive_overview.png": 620,
  "02_hero_doomscroll_sleep.png": 520,
  "03_doomscroller_comparison.png": 460,
  "04_dose_response.png": 480,
  "05_mental_health.png": 480,
  "06_protective_habits.png": 560,
  "07_exercise_gradient.png": 470,
  "08_demographics.png": 570,
  "10_exceptions.png": 490,
  "11_personas.png": 440,
  "12_correlation_heatmap.png": 630,
  "13_model_comparison.png": 500,
  "14_feature_importance.png": 540,
};

const chartCards: Array<{
  file: string;
  number: string;
  group: ChartGroup;
  title: string;
  kicker: string;
  takeaway: string;
}> = [
  { file: "01_descriptive_overview.png", number: "01", group: "Overview", title: "Who answered the survey?", kicker: "Sample composition", takeaway: "The sample is concentrated in the 20s and 30s+, with India and the United States the largest country groups. Full-time workers and students make up most respondents." },
  { file: "02_hero_doomscroll_sleep.png", number: "02", group: "Core", title: "Heavier scrolling clusters around poorer sleep", kicker: "Hero relationship", takeaway: "Poor sleepers carry the highest median nightly doomscroll load. The overlap matters: exposure raises risk without making the outcome inevitable." },
  { file: "03_doomscroller_comparison.png", number: "03", group: "Core", title: "A consistently harder night", kicker: "Doomscroller comparison", takeaway: "Doomscrollers average 10.6 extra minutes of latency, more wakeups, 1.5 more hours of weekly debt, and roughly 15 minutes less sleep per night." },
  { file: "04_dose_response.png", number: "04", group: "Core", title: "The relationship is dose-shaped", kicker: "Screen-time quartiles", takeaway: "Each higher bedtime-screen quartile brings longer latency and more debt. The highest-exposure quartile also sleeps less and wakes more often." },
  { file: "05_mental_health.png", number: "05", group: "Mind", title: "Doomscrolling and negative news stack up", kicker: "Mental wellbeing", takeaway: "Anxiety, stress, and fatigue are highest when doomscrolling and negative-news consumption coexist. Direction remains unresolved in cross-sectional data." },
  { file: "06_protective_habits.png", number: "06", group: "Protection", title: "Routine beats a single screen setting", kicker: "Protective habits", takeaway: "Reading and meditation/journaling stand out more consistently than night mode alone. Environment and routine look more important than display settings." },
  { file: "07_exercise_gradient.png", number: "07", group: "Protection", title: "Exercise helps, but is not a cure-all", kicker: "Movement gradient", takeaway: "More active respondents are somewhat more likely to report good sleep and lower fatigue, though the gradient is modest and not perfectly monotonic." },
  { file: "08_demographics.png", number: "08", group: "Demographics", title: "Context, not destiny", kicker: "Age × occupation × country", takeaway: "Younger and student pockets are often elevated, but small cells and uneven country sample sizes make these descriptive signals rather than rankings." },
  { file: "10_exceptions.png", number: "09", group: "Exceptions", title: "What separates resilient heavy scrollers?", kicker: "The counter-narrative", takeaway: "Only 11 of 204 heavy scrollers report good sleep. They realize more sleep and less debt or latency, with restorative routines appearing more often." },
  { file: "11_personas.png", number: "10", group: "Personas", title: "Three patterns, three intervention needs", kicker: "Transparent personas", takeaway: "The Night Scroller is exposure-heavy, the Anxious News Seeker is emotion-heavy, and the Disciplined Sleeper is routine-protected." },
  { file: "12_correlation_heatmap.png", number: "11", group: "Synthesis", title: "A coherent bedtime-disruption chain", kicker: "Correlation structure", takeaway: "Bedtime exposure connects to doomscroll sessions and latency; wakeups and short sleep accumulate into debt and fatigue." },
  { file: "13_model_comparison.png", number: "12", group: "Synthesis", title: "Which model predicts sleep quality best?", kicker: "Five-model comparison", takeaway: "Random Forest leads nested cross-validation, narrowly ahead of RBF SVM and Extra Trees. Every candidate uses the same leakage-safe SMOTENC and tuning protocol." },
  { file: "14_feature_importance.png", number: "13", group: "Synthesis", title: "What drives the selected model?", kicker: "Random Forest", takeaway: "Doomscrolling, wakeups, latency, and sleep duration lead held-out permutation importance. Predictive contribution does not establish causation." },
];

const nav: Array<{ id: Route; label: string }> = [
  { id: "overview", label: "Overview" },
  { id: "analysis", label: "All analysis" },
  { id: "exceptions", label: "The Exceptions" },
  { id: "personas", label: "Personas" },
  { id: "methodology", label: "Methodology" },
];

function NavIcon({ route }: { route: Route }) {
  const common = { width: 18, height: 18, viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: 1.6, strokeLinecap: "round" as const, strokeLinejoin: "round" as const, "aria-hidden": true };
  if (route === "overview") return <svg {...common}><path d="M4 12a8 8 0 1 0 16 0 8 8 0 1 0-16 0" /><path d="M12 4a8 8 0 0 0 0 16Z" fill="currentColor" stroke="none" opacity=".36" /></svg>;
  if (route === "analysis") return <svg {...common}><path d="M4 17V9" /><path d="M10 17V5" /><path d="M16 17v-6" /><path d="M22 17V7" /><path d="M3 20h20" /></svg>;
  if (route === "exceptions") return <svg {...common}><path d="M5 19 19 5" /><path d="M10 5h9v9" /><path d="M5 7v12h12" opacity=".45" /></svg>;
  if (route === "personas") return <svg {...common}><circle cx="12" cy="8" r="3" /><path d="M5.5 19c.8-3.2 3-5 6.5-5s5.7 1.8 6.5 5" /><circle cx="12" cy="12" r="10" opacity=".38" /></svg>;
  return <svg {...common}><path d="M6 5h12" /><path d="M6 19h12" /><path d="M8 5c0 4.4 8 4.6 8 9s-3 5-8 5" /><path d="M16 5c0 4.4-8 4.6-8 9" opacity=".5" /></svg>;
}

const pathFor = (route: Route) => route === "landing" ? "/" : `/${route}`;
const routeFromPath = (): Route => {
  const value = window.location.pathname.replace(/^\//, "").split("/")[0];
  if (!value) return "landing";
  return nav.some((item) => item.id === value) ? value as Route : "landing";
};

function Logo() {
  return <div className="logo-wrap" aria-label="Night Signals">
    <div className="moon-logo"><span /></div>
    <div><b>Night Signals</b><small>Sleep × Doomscrolling</small></div>
  </div>;
}

function Sidebar({ route, onRoute }: { route: Route; onRoute: (route: Route) => void }) {
  return <aside className="sidebar">
    <Logo />
    <p className="nav-eyebrow">Research atlas</p>
    <nav aria-label="Primary navigation">
      {nav.map((item) => <a key={item.id} href={pathFor(item.id)} className={route === item.id ? "active" : ""} onClick={(event) => { event.preventDefault(); onRoute(item.id); }}>
        <span><NavIcon route={item.id} /></span>{item.label}
      </a>)}
    </nav>
    <div className="sidebar-status">
      <i /><div><b>Dataset validated</b><small>1,000 rows · 29 variables</small></div>
    </div>
    <div className="sidebar-foot">
      <span>SYNTHETIC DATA</span>
      <p>Descriptive patterns, not medical advice or causal estimates.</p>
    </div>
  </aside>;
}

function Topbar({ route }: { route: Route }) {
  return <header className="topbar">
    <div><span className="pulse" /> Live analysis <i>/</i> {nav.find((n) => n.id === route)?.label}</div>
    <div className="top-actions">
      <a className="primary-action" href="/downloads/Sleep_Doomscrolling_Report.pdf" download>Report PDF ↓</a>
    </div>
  </header>;
}

function InteractiveChart({ file, title }: { file: string; title: string }) {
  const specs = useContext(PlotSpecsContext);
  const spec = specs[file];
  if (!spec) return <div className="plot-loading">Loading interactive figure…</div>;
  const axisDefaults = { gridcolor: "rgba(147,168,200,.12)", zerolinecolor: "rgba(147,168,200,.18)", tickfont: { color: "#93a8c8" }, title: { font: { color: "#c7d5e9" } } };
  const layout: Partial<Layout> = {
    ...spec.layout,
    autosize: true,
    width: undefined,
    height: undefined,
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    font: { family: '"JetBrains Mono", monospace', color: "#aebed5", size: 10 },
    margin: { l: 55, r: 24, t: 42, b: 52, ...spec.layout?.margin },
    hoverlabel: { bgcolor: "#07111f", bordercolor: "#59d8e8", font: { color: "#fff", family: '"JetBrains Mono", monospace' } },
  };
  for (const key of ["xaxis", "xaxis2", "xaxis3", "xaxis4", "yaxis", "yaxis2", "yaxis3", "yaxis4"] as const) {
    const existing = (spec.layout as Record<string, unknown>)?.[key] as Record<string, unknown> | undefined;
    (layout as Record<string, unknown>)[key] = { ...axisDefaults, ...existing };
  }
  return <Plot data={spec.data} layout={layout as Layout} config={{ responsive: true, displaylogo: false, scrollZoom: false, modeBarButtonsToRemove: ["lasso2d", "select2d"] } as Partial<Config>} useResizeHandler style={{ width: "100%", height: "100%" }} aria-label={title} />;
}

function StatCard({ label, value, note, tone }: { label: string; value: string; note: string; tone: string }) {
  return <article className={`stat-card tone-${tone}`}>
    <div className="stat-top"><span>{label}</span><i /></div>
    <strong>{value}</strong><p>{note}</p>
    <div className="spark"><span /><span /><span /><span /><span /><span /></div>
  </article>;
}

function ChartCard({ chart, featured = false }: { chart: typeof chartCards[number]; featured?: boolean }) {
  const [open, setOpen] = useState(featured);
  return <article className={`chart-card ${featured ? "featured" : ""}`}>
    <div className="chart-head">
      <div className="chart-index">{chart.number}</div>
      <div><span className="section-label">{chart.kicker}</span><h3>{chart.title}</h3></div>
      <button onClick={() => setOpen(!open)} aria-expanded={open} aria-label={open ? "Hide interpretation" : "Show interpretation"}>{open ? "−" : "+"}</button>
    </div>
    <div className="chart-image plot-frame" style={{ "--plot-height": `${plotHeights[chart.file] ?? 520}px` } as CSSProperties}><InteractiveChart file={chart.file} title={chart.title} /></div>
    <div className={`chart-takeaway ${open ? "open" : ""}`}><span>Read this</span><p>{chart.takeaway}</p></div>
  </article>;
}

const landingLinks: Array<{ label: string; route: Route }> = [
  { label: "Overview", route: "overview" },
  { label: "Analysis", route: "analysis" },
  { label: "Exceptions", route: "exceptions" },
  { label: "Methodology", route: "methodology" },
];

function Landing({ go }: { go: (route: Route) => void }) {
  const [open, setOpen] = useState(false);
  const toggleRef = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    document.body.classList.toggle("landing-menu-open", open);
    const close = (event: KeyboardEvent) => { if (event.key === "Escape") { setOpen(false); toggleRef.current?.focus(); } };
    const desktop = () => { if (window.innerWidth >= 901) setOpen(false); };
    window.addEventListener("keydown", close); window.addEventListener("resize", desktop);
    return () => { document.body.classList.remove("landing-menu-open"); window.removeEventListener("keydown", close); window.removeEventListener("resize", desktop); };
  }, [open]);
  const navigate = (route: Route) => { setOpen(false); go(route); };
  return <section className="cinematic-hero">
    <div className="cinematic-media">
      <video autoPlay muted loop playsInline preload="auto" poster="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260806_132328_5f9029c8-218f-4489-82b6-29ff2849920e.png">
        <source src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260806_133255_956f653f-5d80-4b06-abd5-0f46c98b60fa.mp4" type="video/mp4" />
      </video>
    </div>
    <div className="cinematic-scrim" />
    <header className="cinematic-nav">
      <a className="cinematic-logo" href="/" onClick={(e) => e.preventDefault()}>NIGHT SIGNALS</a>
      <div className="cinematic-nav-right">
        <nav className="cinematic-links" aria-label="Atlas navigation">{landingLinks.map((item) => <a key={item.route} href={pathFor(item.route)} onClick={(e) => { e.preventDefault(); navigate(item.route); }}>{item.label}</a>)}</nav>
        <button className="cinematic-cta" onClick={() => navigate("overview")}>Enter atlas</button>
        <button ref={toggleRef} className={`cinematic-toggle ${open ? "is-open" : ""}`} aria-expanded={open} aria-controls="mobileMenu" aria-label={open ? "Close menu" : "Open menu"} onClick={() => setOpen(!open)}><span /><span /><span /></button>
      </div>
    </header>
    <div id="mobileMenu" className={`cinematic-menu ${open ? "is-open" : ""}`} role="dialog" aria-modal="true" aria-label="Site menu" aria-hidden={!open} inert={!open} onClick={(e) => { if (e.target === e.currentTarget) setOpen(false); }}>
      <div>{landingLinks.map((item, index) => <a style={{ "--i": index } as CSSProperties} key={item.route} href={pathFor(item.route)} onClick={(e) => { e.preventDefault(); navigate(item.route); }}>{item.label}</a>)}<button style={{ "--i": 4 } as CSSProperties} onClick={() => navigate("overview")}>Enter atlas</button></div>
    </div>
    <div className="cinematic-body">
      <div className="cinematic-panel">
        <span className="cinematic-chip">[ Evidence entry ]</span>
        <h1>NIGHT<br />SIGNALS</h1>
        <p className="cinematic-tagline">Your sleep ID to the signal behind the scroll.</p>
        <div className="cinematic-form" aria-label="Enter the research atlas">
          <div className="cinematic-datum">1,000 RESPONDENTS / 29 VARIABLES</div>
          <button className="cinematic-button ghost" onClick={() => navigate("analysis")}>Proceed to analysis</button>
          <button className="cinematic-button solid" onClick={() => navigate("methodology")}>Access methodology</button>
        </div>
        <button className="cinematic-referral" onClick={() => navigate("exceptions")}>Read the exceptions</button>
      </div>
    </div>
    <footer className="cinematic-legal">Synthetic observational analysis. <a href="/methodology" onClick={(e) => { e.preventDefault(); navigate("methodology"); }}>Methodology</a> and <a href="/methodology#limitations" onClick={(e) => { e.preventDefault(); navigate("methodology"); }}>limitations</a>.</footer>
  </section>;
}

function Overview({ go }: { go: (route: Route) => void }) {
  return <>
    <section className="hero">
      <div className="hero-copy">
        <span className="hero-kicker">NIGHT BEHAVIOR / SLEEP QUALITY / WELLBEING</span>
        <h1>The screen goes dark.<br /><em>The mind doesn’t.</em></h1>
        <p>An evidence-led atlas of how doomscrolling, negative news, and bedtime routines relate to sleep across 1,000 respondents.</p>
        <div className="hero-actions"><button onClick={() => go("analysis")}>Explore the evidence <span>→</span></button><button className="ghost" onClick={() => go("methodology")}>How we analyzed it</button></div>
      </div>
      <div className="hero-orbit" aria-hidden="true">
        <div className="orbit orbit-one" /><div className="orbit orbit-two" /><div className="hero-moon" />
        <div className="orbit-note one"><b>+10.6 min</b><span>sleep latency</span></div>
        <div className="orbit-note two"><b>47.6%</b><span>doomscrollers</span></div>
        <div className="orbit-note three"><b>11</b><span>exceptions</span></div>
      </div>
    </section>
    <section className="stats-grid">
      <StatCard label="Doomscrollers" value="47.6%" note="476 of 1,000 respondents" tone="cyan" />
      <StatCard label="Latency gap" value="+10.6 min" note="Doomscrollers vs others" tone="violet" />
      <StatCard label="Weekly debt gap" value="+1.5 h" note="Across the doomscroller label" tone="pink" />
      <StatCard label="Model lift" value="60.3%" note="Balanced accuracy vs 34% baseline" tone="gold" />
    </section>
    <section className="story-grid">
      <div className="story-lead"><span className="section-label">THE CENTRAL THREAD</span><h2>A bedtime-disruption chain, not a morality tale.</h2><p>Exposure links to delayed sleep; delayed sleep links to wakeups and debt; debt leaves a daytime trace. The useful levers are friction, content boundaries, and routine.</p></div>
      {[{n:"01",t:"Exposure",d:"Bedtime screen time rises with sessions and latency."},{n:"02",t:"Arousal",d:"Negative news compounds anxiety, stress, and fatigue."},{n:"03",t:"Protection",d:"Reading, meditation, phone distance, and movement help."},{n:"04",t:"Exceptions",d:"A small group shows that exposure is risk, not destiny."}].map((x)=><div className="story-step" key={x.n}><span>{x.n}</span><b>{x.t}</b><p>{x.d}</p></div>)}
    </section>
    <section className="section-block"><div className="section-heading"><div><span className="section-label">HERO EVIDENCE</span><h2>The relationship in one frame</h2></div><button className="text-button" onClick={() => go("analysis")}>All 12 figures →</button></div><ChartCard chart={chartCards[1]} featured /></section>
  </>;
}

function Analysis() {
  const groups = ["All", "Overview", "Core", "Mind", "Protection", "Demographics", "Exceptions", "Personas", "Synthesis"];
  const [group, setGroup] = useState("All");
  const visible = group === "All" ? chartCards : chartCards.filter((c) => c.group === group);
  return <section className="page-section">
    <div className="page-intro"><span className="section-label">12 FIGURES / 9 QUESTIONS</span><h1>The evidence atlas</h1><p>Every chart from the executed notebook, grouped by the question it answers. Open each interpretation to keep the visual and its meaning together.</p></div>
    <div className="filter-row">{groups.map((item) => <button className={group === item ? "active" : ""} key={item} onClick={() => setGroup(item)}>{item}</button>)}</div>
    <div className="analysis-grid">{visible.map((chart) => <ChartCard key={chart.file} chart={chart} />)}</div>
  </section>;
}

function Exceptions() {
  return <section className="page-section">
    <div className="page-intro split-intro"><div><span className="section-label">COUNTER-NARRATIVE / N=11</span><h1>The Exceptions</h1><p>Heavy doomscrollers who still report good sleep force a more useful question: what prevents exposure from becoming an outcome?</p></div><div className="big-ratio"><b>11</b><span>of 204 heavy scrollers</span><small>5.4% report good sleep</small></div></div>
    <div className="exception-definition"><span>RULE</span><p>Self-identified doomscroller <i>+</i> at or above <b>66 minutes</b> of bedtime screen time <i>+</i> reports <b>Good</b> sleep quality.</p></div>
    <ChartCard chart={chartCards[8]} featured />
    <div className="exception-grid">
      <article><span>01</span><h3>They realize more sleep</h3><p>The exception group averages longer actual sleep, suggesting that schedule capacity or recovery opportunity still matters.</p></article>
      <article><span>02</span><h3>Debt stays lower</h3><p>Exposure is high, but realized weekly debt and latency are markedly better than among other heavy scrollers.</p></article>
      <article><span>03</span><h3>Routine changes the context</h3><p>Reading and meditation/journaling appear more often than the social-scrolling routine that dominates the wider heavy group.</p></article>
    </div>
    <div className="caveat-banner"><b>Small-group warning.</b> Eleven respondents are enough to reveal a counter-pattern, not enough to estimate a stable protective effect.</div>
  </section>;
}

const personas = [
  { name: "The Night Scroller", mark: "01", n: "n=204", tone: "pink", quote: "One more swipe, then sleep.", copy: "High bedtime exposure with a self-identified doomscrolling pattern. The first lever is environmental friction.", metrics: [["Exposure","Top quartile"],["Primary lever","Friction"],["Sleep risk","High"]], actions: ["Charge beyond arm’s reach", "Add a hard stop cue", "Track latency, not just minutes"] },
  { name: "The Anxious News Seeker", mark: "02", n: "n=51", tone: "gold", quote: "I need to know what happened.", copy: "Negative-news consumption paired with high anxiety and stress. The first lever is a content boundary.", metrics: [["Mental load","High"],["Primary lever","Content"],["Sleep risk","Elevated"]], actions: ["Schedule a news window", "Disable late alerts", "Use a decompression ritual"] },
  { name: "The Disciplined Sleeper", mark: "03", n: "n=130", tone: "mint", quote: "The routine does the deciding.", copy: "Lower bedtime exposure paired with reading or meditation/journaling. The opportunity is maintenance.", metrics: [["Exposure","Lower"],["Primary lever","Routine"],["Sleep profile","Protective"]], actions: ["Protect the final 30 minutes", "Keep the cue visible", "Reinforce consistency"] },
];

function Personas() {
  return <section className="page-section">
    <div className="page-intro"><span className="section-label">TRANSPARENT RULES / NOT DIAGNOSES</span><h1>Three people inside the pattern</h1><p>Personas translate variable combinations into intervention needs without pretending an opaque cluster is a human identity.</p></div>
    <div className="persona-stack">{personas.map((p) => <article className={`persona-card ${p.tone}`} key={p.name}>
      <div className="persona-number">{p.mark}</div><div className="persona-copy"><div className="persona-title"><span>{p.n}</span><h2>{p.name}</h2><em>“{p.quote}”</em></div><p>{p.copy}</p><div className="persona-metrics">{p.metrics.map(([a,b])=><div key={a}><span>{a}</span><b>{b}</b></div>)}</div></div><div className="persona-actions"><span className="section-label">DESIGN RESPONSE</span>{p.actions.map((a)=><p key={a}>↗ {a}</p>)}</div>
    </article>)}</div>
    <ChartCard chart={chartCards[9]} featured />
  </section>;
}

type NotebookCell = { cell_type: "markdown" | "code" | string; source: string | string[]; execution_count?: number | null; outputs?: Array<{ output_type: string; text?: string | string[]; data?: Record<string, string | string[]> }> };

function NotebookViewer() {
  const [cells, setCells] = useState<NotebookCell[]>([]);
  const [showCode, setShowCode] = useState(true);
  const [limit, setLimit] = useState(12);
  const [notebook, setNotebook] = useState<"analysis" | "modeling">("analysis");
  const notebookFile = notebook === "analysis" ? "sleep_doomscrolling_analysis.ipynb" : "sleep_doomscrolling_predictive_modeling.ipynb";
  useEffect(() => {
    setCells([]); setLimit(12);
    fetch(`/methodology/${notebookFile}`).then((r) => r.json()).then((n) => setCells(n.cells || [])).catch(() => setCells([]));
  }, [notebookFile]);
  const visible = cells.filter((cell) => showCode || cell.cell_type !== "code").slice(0, limit);
  return <div className="notebook-shell">
    <div className="notebook-tabs"><button className={notebook === "analysis" ? "active" : ""} onClick={() => setNotebook("analysis")}>Exploratory analysis</button><button className={notebook === "modeling" ? "active" : ""} onClick={() => setNotebook("modeling")}>Predictive modelling</button></div>
    <div className="notebook-bar"><div><i /><i /><i /><span>{notebookFile}</span></div><label><input type="checkbox" checked={showCode} onChange={(e) => setShowCode(e.target.checked)} /> Show code</label></div>
    <div className="notebook-cells">{visible.length ? visible.map((cell, index) => {
      const source = Array.isArray(cell.source) ? cell.source.join("") : cell.source;
      if (cell.cell_type === "markdown") return <div className="nb-cell markdown-cell" key={index}><div className="cell-rail">M</div><div>{source.split("\n").map((line, i) => line.startsWith("#") ? <h4 key={i}>{line.replace(/^#+\s*/, "")}</h4> : line.trim() ? <p key={i}>{line.replace(/\*\*/g, "")}</p> : null)}</div></div>;
      return <div className="nb-cell code-cell" key={index}><div className="cell-rail">[{cell.execution_count ?? " "}]</div><pre>{source}</pre></div>;
    }) : <div className="notebook-loading">Loading executed notebook…</div>}</div>
    {limit < cells.length && <button className="load-more" onClick={() => setLimit(limit + 12)}>Load 12 more cells</button>}
  </div>;
}

function Methodology() {
  const steps = [
    ["01", "Load & audit", "1,000 unique IDs, 30 columns, six fields with missing values."],
    ["02", "Clean & bucket", "Median numeric imputation, Unknown categorical label, three age buckets."],
    ["03", "Stress-test realism", "Exact-formula checks, ceiling effects, balance checks, correlation scan."],
    ["04", "Compare & segment", "Groups, quartiles, exceptions, transparent persona rules."],
    ["05", "Model & compare", "Five tuned classifiers, SMOTENC, nested five-fold CV, and an untouched holdout."],
  ];
  return <section className="page-section methodology-page">
    <div className="page-intro"><span className="section-label">REPRODUCIBLE / EXECUTED / AUDITABLE</span><h1>Methodology</h1><p>The analysis is shown, not hidden. Explore the workflow, synthetic-data checks, model boundary, and the executed notebook itself.</p></div>
    <div className="method-grid">{steps.map(([n,t,d])=><article key={n}><span>{n}</span><h3>{t}</h3><p>{d}</p></article>)}</div>
    <div className="sanity-panel"><div><span className="section-label">SYNTHETIC-DATA SANITY CHECK</span><h2>The data are unusually orderly.</h2><p>This does not prove how the file was produced. It does mean effect sizes should remain inside this dataset and causal language should stay out.</p></div><div className="sanity-metrics"><p><b>−0.893</b><span>sleep hours ↔ weekly debt</span></p><p><b>86%+</b><span>valid quality scores at 5/5</span></p><p><b>10</b><span>row spread across 3 target classes</span></p></div></div>
    <div className="method-boundaries"><article><span>Handled</span><p>Missingness, dtypes, IDs, duplicates, range checks, age buckets, feature leakage, class balance.</p></article><article><span>Not claimed</span><p>Causality, medical advice, population prevalence, cultural ranking, stable effects for tiny groups.</p></article></div>
    <div className="section-heading"><div><span className="section-label">LIVE ARTIFACTS</span><h2>Executed notebook viewer</h2></div><div><a className="text-button" href="/methodology/sleep_doomscrolling_predictive_modeling.ipynb" download>Modelling notebook ↓</a><a className="text-button" href="/data/sleep_doomscrolling_habits.csv" download>Dataset ↓</a></div></div>
    <NotebookViewer />
  </section>;
}

export default function App() {
  const [route, setRoute] = useState<Route>(routeFromPath());
  const [menu, setMenu] = useState(false);
  const [plotSpecs, setPlotSpecs] = useState<Record<string, PlotSpec>>({});
  useEffect(() => {
    const onPop = () => setRoute(routeFromPath());
    window.addEventListener("popstate", onPop); return () => window.removeEventListener("popstate", onPop);
  }, []);
  useEffect(() => { fetch("/data/plotly_charts.json").then((response) => response.json()).then(setPlotSpecs).catch(() => setPlotSpecs({})); }, []);
  const go = (next: Route) => { history.pushState({}, "", pathFor(next)); setRoute(next); setMenu(false); window.scrollTo({ top: 0, behavior: "smooth" }); };
  const page = useMemo(() => ({ landing: <Landing go={go} />, overview: <Overview go={go} />, analysis: <Analysis />, exceptions: <Exceptions />, personas: <Personas />, methodology: <Methodology /> })[route], [route]);
  if (route === "landing") return <PlotSpecsContext.Provider value={plotSpecs}>{page}</PlotSpecsContext.Provider>;
  return <PlotSpecsContext.Provider value={plotSpecs}><div className={`app-shell ${menu ? "menu-open" : ""}`}>
    <div className="ambient ambient-a" /><div className="ambient ambient-b" /><div className="grid-overlay" />
    <Sidebar route={route} onRoute={go} />
    <button className="mobile-menu" onClick={() => setMenu(!menu)} aria-label="Toggle navigation">{menu ? "×" : "☰"}</button>
    <main><Topbar route={route} /><div className="content">{page}</div><footer><Logo /><p>Observational synthetic-data analysis · 2026</p><div>{nav.map((n)=><a key={n.id} href={pathFor(n.id)} onClick={(e)=>{e.preventDefault();go(n.id)}}>{n.label}</a>)}</div></footer></main>
  </div></PlotSpecsContext.Provider>;
}
