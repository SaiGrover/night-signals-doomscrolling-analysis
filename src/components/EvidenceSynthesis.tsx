import { lazy, Suspense, useEffect, useState } from "react";
import type { CSSProperties } from "react";
import type { PlotSpec } from "./PlotRenderer";

// Layer B (NHANES) and Layer C (PhysioNet) are computed by build_nhanes_evidence.py
// and build_physionet_evidence.py and published to /data/*.json. This page renders
// those completed independent-evidence results (synopsis Sections 4.12, 7.5, RQ5).
// Charts are interactive Plotly specs rendered by the shared PlotRenderer, matching
// the convention used across the rest of the atlas (public/data/plotly_charts.json).

const PlotRenderer = lazy(() => import("./PlotRenderer"));

interface NhanesSummary {
  cycle: string;
  analytic_adults: number;
  B1_sleep_blood_pressure: {
    systolic_diff_short_minus_adequate: number;
    diastolic_diff_short_minus_adequate: number;
    systolic_p: number;
    diastolic_p: number;
  };
  B2_sleep_by_bmi: {
    spearman_bmi_vs_sleep: number;
    categories: { bmi_category: string; n: number; mean_sleep_hours: number }[];
  };
  B3_sleep_by_activity: {
    active_groups: { activity_group: string; n: number; mean_sleep_hours: number }[];
    spearman_sedentary_vs_sleep: number;
  };
  charts: Record<string, PlotSpec>;
}

interface PhysioSummary {
  subjects_analysed: number;
  total_scored_epochs: number;
  wake_minus_deep_hr: number;
  median_awakenings_after_onset: number;
  hr_by_stage: { stage_name: string; mean_hr: number; mean_hr_variability: number }[];
  mean_stage_composition_pct: Record<string, number>;
  charts: Record<string, PlotSpec>;
}

function EvidenceChart({ spec, title, caption }: { spec?: PlotSpec; title: string; caption: string }) {
  return <figure className="evidence-chart">
    <div className="chart-image plot-frame" style={{ "--plot-height": "380px" } as CSSProperties}>
      {spec
        ? <Suspense fallback={<div className="plot-loading">Loading chart renderer…</div>}><PlotRenderer spec={spec} title={title} /></Suspense>
        : <div className="plot-loading">Loading interactive figure…</div>}
    </div>
    <figcaption>{caption}</figcaption>
  </figure>;
}

const evidenceLayers = [
  {
    source: "Night Signals / Kaggle Sleep & Doomscrolling Habits",
    role: "Primary behavioural study",
    signal: "Digital exposure, doomscrolling, bedtime routines, self-reported sleep and wellbeing.",
    use: "Core research atlas and pre-outcome screening demonstration.",
  },
  {
    source: "NHANES 2021-2023",
    role: "Population-health context (analysed)",
    signal: "Usual sleep duration, blood pressure, BMI, and physical-activity measures on 8,040 adults.",
    use: "Independent check of whether sleep-health associations echo a large standardised survey.",
  },
  {
    source: "PhysioNet Sleep-Accel",
    role: "Objective wearable physiology (analysed)",
    signal: "Apple Watch heart rate summarised over polysomnography-scored sleep stages, 31 subjects.",
    use: "Independent objective picture of heart rate and stage architecture across sleep.",
  },
  {
    source: "PhysioNet multi-night wearable + EEG",
    role: "Longitudinal extension (planned)",
    signal: "Multiple nights of instantaneous heart rate, accelerometry, and EEG-based sleep stages.",
    use: "Move future work toward repeated-night, within-person recovery patterns.",
  },
];

const healthLayers = [
  ["Digital behaviour", "Bedtime screen time, doomscroll sessions, negative-news exposure, phone checks."],
  ["Sleep behaviour", "Latency, awakenings, duration, debt, subjective sleep quality."],
  ["Recovery physiology", "Heart rate, movement, sleep stages, rest regularity from wearable datasets."],
  ["Health context", "BMI, blood pressure, activity, fatigue, and longer-term risk indicators."],
];

const fmtP = (p: number) => (p < 0.001 ? "p < 0.001" : `p = ${p.toFixed(3)}`);

export default function EvidenceSynthesis() {
  const [nhanes, setNhanes] = useState<NhanesSummary | null>(null);
  const [physio, setPhysio] = useState<PhysioSummary | null>(null);

  useEffect(() => {
    fetch("/data/nhanes_summary.json").then((r) => (r.ok ? r.json() : null)).then(setNhanes).catch(() => setNhanes(null));
    fetch("/data/physionet_summary.json").then((r) => (r.ok ? r.json() : null)).then(setPhysio).catch(() => setPhysio(null));
  }, []);

  return <section className="page-section evidence-page">
    <div className="page-intro split-intro">
      <div>
        <span className="section-label">MULTI-DATASET EVIDENCE / RQ5</span>
        <h1>Independent external evidence</h1>
        <p>Night Signals is a behavioural analytics study first. Two independent public datasets are analysed as separate evidence layers for the same conceptual chain — never row-merged with the survey, because they describe different people, devices, and variable definitions.</p>
      </div>
      <div className="big-ratio evidence-ratio"><b>3</b><span>evidence layers analysed</span><small>primary survey · NHANES population health · PhysioNet physiology</small></div>
    </div>

    <div className="synthesis-warning">
      <span>Important boundary</span>
      <p>These datasets do not describe the same participants, time periods, or measurements. They are treated as independent evidence layers, not a combined training table. All results below are associations in cross-sectional or observational data — never causal or clinical claims.</p>
    </div>

    <section className="evidence-flow" aria-labelledby="evidence-flow-title">
      <div className="section-heading"><div><span className="section-label">CONCEPTUAL MODEL</span><h2 id="evidence-flow-title">Digital behaviour to health context</h2></div></div>
      <div className="evidence-flow-grid">
        {healthLayers.map(([name, copy], index) => <article key={name}><span>{String(index + 1).padStart(2, "0")}</span><b>{name}</b><p>{copy}</p></article>)}
      </div>
    </section>

    {/* ---- Layer B: NHANES ---- */}
    <section className="evidence-result" aria-labelledby="nhanes-title">
      <div className="section-heading"><div><span className="section-label">LAYER B · NHANES {nhanes ? `· ${nhanes.analytic_adults.toLocaleString()} ADULTS` : ""}</span><h2 id="nhanes-title">Population-health evidence (CDC NHANES 2021-2023)</h2><p>Independent analysis of usual sleep duration against blood pressure, BMI, and physical activity in a large national health survey. Not linked to any Night Signals respondent.</p></div></div>
      {nhanes ? <>
        <div className="evidence-stat-row">
          <div className="evidence-stat"><b>+{nhanes.B1_sleep_blood_pressure.diastolic_diff_short_minus_adequate}</b><span>mmHg higher diastolic BP for short sleepers (&lt;7h)</span><small>{fmtP(nhanes.B1_sleep_blood_pressure.diastolic_p)}</small></div>
          <div className="evidence-stat"><b>+{nhanes.B1_sleep_blood_pressure.systolic_diff_short_minus_adequate}</b><span>mmHg higher systolic BP for short sleepers</span><small>{fmtP(nhanes.B1_sleep_blood_pressure.systolic_p)}</small></div>
          <div className="evidence-stat"><b>{nhanes.B2_sleep_by_bmi.spearman_bmi_vs_sleep}</b><span>Spearman ρ, BMI vs sleep duration</span><small>sleep edges down as BMI rises</small></div>
        </div>
        <div className="evidence-mini-table" role="table" aria-label="NHANES mean sleep by BMI category">
          <div className="evidence-mini-head" role="row"><span>BMI category</span><span>n</span><span>Mean sleep (h)</span></div>
          {nhanes.B2_sleep_by_bmi.categories.map((c) => <div className="evidence-mini-row" role="row" key={c.bmi_category}><b>{c.bmi_category}</b><span>{c.n.toLocaleString()}</span><span>{c.mean_sleep_hours.toFixed(2)}</span></div>)}
        </div>
        <div className="evidence-charts">
          <EvidenceChart spec={nhanes.charts?.bp} title="NHANES blood pressure by usual sleep group" caption="B1 · Blood pressure by sleep group" />
          <EvidenceChart spec={nhanes.charts?.bmi} title="NHANES mean usual sleep by BMI category" caption="B2 · Usual sleep by BMI category" />
          <EvidenceChart spec={nhanes.charts?.sedentary} title="NHANES mean sleep by sedentary-time quartile" caption="B3 · Sleep by sedentary-time quartile" />
        </div>
        <p className="evidence-source">NHANES 2021-2023 — associations only. Full tables: <a href="/data/nhanes_summary.json">nhanes_summary.json</a>.</p>
      </> : <p className="plot-loading">Loading NHANES evidence…</p>}
    </section>

    {/* ---- Layer C: PhysioNet ---- */}
    <section className="evidence-result" aria-labelledby="physio-title">
      <div className="section-heading"><div><span className="section-label">LAYER C · PHYSIONET {physio ? `· ${physio.subjects_analysed} SUBJECTS` : ""}</span><h2 id="physio-title">Physiological evidence (PhysioNet Sleep-Accel)</h2><p>Apple Watch heart rate summarised over polysomnography-scored sleep stages. This answers a different question — what objective sleep physiology looks like — and is never used to claim doomscrolling changes heart rate.</p></div></div>
      {physio ? <>
        <div className="evidence-stat-row">
          <div className="evidence-stat"><b>{physio.wake_minus_deep_hr}</b><span>bpm drop from wake to deep (N3) sleep</span><small>heart rate quiets in deep sleep</small></div>
          <div className="evidence-stat"><b>{physio.mean_stage_composition_pct["N2"]?.toFixed(0)}%</b><span>of scored epochs in N2</span><small>typical adult sleep architecture</small></div>
          <div className="evidence-stat"><b>{physio.median_awakenings_after_onset}</b><span>median awakenings after sleep onset</span><small>across {physio.total_scored_epochs.toLocaleString()} scored epochs</small></div>
        </div>
        <div className="evidence-mini-table" role="table" aria-label="PhysioNet mean heart rate by sleep stage">
          <div className="evidence-mini-head" role="row"><span>Sleep stage</span><span>Mean HR (bpm)</span><span>HR variability</span></div>
          {physio.hr_by_stage.map((s) => <div className="evidence-mini-row" role="row" key={s.stage_name}><b>{s.stage_name}</b><span>{s.mean_hr.toFixed(1)}</span><span>{s.mean_hr_variability.toFixed(2)}</span></div>)}
        </div>
        <div className="evidence-charts">
          <EvidenceChart spec={physio.charts?.hr_stage} title="PhysioNet mean heart rate by sleep stage" caption="C1 · Mean heart rate by sleep stage" />
          <EvidenceChart spec={physio.charts?.stage_comp} title="PhysioNet mean sleep-stage composition" caption="C2 · Mean sleep-stage composition" />
          <EvidenceChart spec={physio.charts?.awakenings} title="PhysioNet awakenings vs recording length" caption="C3 · Awakenings vs hours scored" />
        </div>
        <p className="evidence-source">PhysioNet Sleep-Accel — objective physiology, associations only. Full tables: <a href="/data/physionet_summary.json">physionet_summary.json</a>.</p>
      </> : <p className="plot-loading">Loading PhysioNet evidence…</p>}
    </section>

    <section className="evidence-layer-table" aria-labelledby="evidence-layer-title">
      <div className="section-heading"><div><span className="section-label">DATASET ROLES</span><h2 id="evidence-layer-title">A validation architecture, not a data mashup</h2></div></div>
      <div className="evidence-table" role="table" aria-label="External evidence synthesis datasets">
        <div className="evidence-row evidence-head" role="row"><span>Source</span><span>Role</span><span>Signal</span><span>Use</span></div>
        {evidenceLayers.map((row) => <div className="evidence-row" role="row" key={row.source}><b>{row.source}</b><span>{row.role}</span><p>{row.signal}</p><p>{row.use}</p></div>)}
      </div>
    </section>

    <section className="resilience-frame">
      <div>
        <span className="section-label">RESEARCH POSITIONING</span>
        <h2>From sleep risk to resilience</h2>
        <p>The strongest version of the project asks why some people stay resilient under heavy exposure: which routines, contexts, or physiological recovery patterns keep high digital load from turning into poor sleep?</p>
      </div>
      <blockquote>An evidence-led behavioural analytics and predictive-modelling study on a self-reported sleep and doomscrolling survey — with leakage prevention, nested validation, calibration, uncertainty analysis, independent NHANES and PhysioNet evidence layers, and an interactive research interface.</blockquote>
    </section>
  </section>;
}
