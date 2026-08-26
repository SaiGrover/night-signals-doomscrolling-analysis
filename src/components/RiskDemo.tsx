import { useState } from "react";

const initial = { bedtime_screen_time_minutes: 75, doomscroll_sessions_per_night: 4, anxiety_score: 6,
  stress_score: 6, phone_checks_per_night: 5, exercise_minutes_per_day: 25,
  caffeine_intake_mg_per_day: 180, consumes_negative_news_content: "Yes" };

export default function RiskDemo() {
  const [values, setValues] = useState<Record<string, number | string>>(initial);
  const [result, setResult] = useState<{ probability: number; risk_band: string; threshold: number; model_version: string } | null>(null);
  const [status, setStatus] = useState<"idle" | "loading" | "error">("idle");
  const submit = async (event: React.FormEvent) => {
    event.preventDefault(); setStatus("loading"); setResult(null);
    try {
      const response = await fetch("/api/predict", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(values) });
      if (!response.ok) throw new Error(await response.text());
      setResult(await response.json()); setStatus("idle");
    } catch { setStatus("error"); }
  };
  const fields = [
    ["bedtime_screen_time_minutes", "Bedtime screen minutes", 0, 300], ["doomscroll_sessions_per_night", "Doomscroll sessions", 0, 20],
    ["anxiety_score", "Anxiety score", 1, 10], ["stress_score", "Stress score", 1, 10],
    ["phone_checks_per_night", "Phone checks", 0, 30], ["exercise_minutes_per_day", "Exercise minutes", 0, 180],
    ["caffeine_intake_mg_per_day", "Caffeine (mg)", 0, 600],
  ] as const;
  return <section className="risk-demo" aria-labelledby="risk-demo-title">
    <div><span className="section-label">MODEL v2.0 · DEMONSTRATION</span><h2 id="risk-demo-title">Try the pre-outcome model</h2><p>This is an educational estimate from self-reported survey data—not medical advice or an externally validated clinical score. Omitted fields use documented reference defaults.</p></div>
    <form onSubmit={submit}>{fields.map(([name, label, min, max]) => <label key={name}>{label}<input type="number" min={min} max={max} value={values[name]} onChange={(e) => setValues({ ...values, [name]: Number(e.target.value) })} /></label>)}
      <label>Consumes negative news<select value={values.consumes_negative_news_content} onChange={(e) => setValues({ ...values, consumes_negative_news_content: e.target.value })}><option>Yes</option><option>No</option></select></label>
      <button disabled={status === "loading"}>{status === "loading" ? "Estimating…" : "Estimate risk"}</button>
    </form>
    <div className="risk-result" aria-live="polite">{status === "error" ? <p>Prediction service unavailable. Please retry.</p> : result ? <><strong>{Math.round(result.probability * 100)}%</strong><span>{result.risk_band} estimated risk</span><small>Decision threshold {Math.round(result.threshold * 100)}% · model {result.model_version}</small></> : <p>No prediction has been made.</p>}</div>
  </section>;
}
