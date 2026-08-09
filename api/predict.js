import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";

const model = JSON.parse(readFileSync(new URL("../outputs/models/poor_sleep_preoutcome_model.json", import.meta.url), "utf8"));
const requests = new Map();

function probability(row) {
  return model.estimators.reduce((total, estimator) => {
    const values = estimator.numeric.map((field) => ((Number(row[field.name] ?? field.impute) - field.mean) / field.scale));
    for (const field of estimator.categorical) {
      const value = String(row[field.name] ?? field.impute);
      values.push(...field.categories.map((category) => value === category ? 1 : 0));
    }
    const score = estimator.intercept + values.reduce((sum, value, index) => sum + value * estimator.coefficients[index], 0);
    const calibrated = 1 / (1 + Math.exp(estimator.calibration.a * score + estimator.calibration.b));
    return total + calibrated;
  }, 0) / model.estimators.length;
}

export default function handler(request, response) {
  const started = Date.now();
  response.setHeader("Cache-Control", "no-store");
  response.setHeader("X-Content-Type-Options", "nosniff");
  if (request.method !== "POST") return response.status(405).json({ error: "method_not_allowed" });
  if (process.env.PREDICTION_API_KEY && request.headers["x-api-key"] !== process.env.PREDICTION_API_KEY) return response.status(401).json({ error: "unauthorized" });
  const client = String(request.headers["x-forwarded-for"] ?? "local").split(",")[0];
  const now = Date.now();
  const bucket = (requests.get(client) ?? []).filter((timestamp) => now - timestamp < 60_000);
  if (bucket.length >= 30) return response.status(429).json({ error: "rate_limit", retry_after_seconds: 60 });
  bucket.push(now); requests.set(client, bucket);
  try {
    const supplied = request.body;
    if (!supplied || typeof supplied !== "object" || Array.isArray(supplied)) return response.status(400).json({ error: "object_required" });
    const unknown = Object.keys(supplied).filter((key) => !model.features.includes(key));
    if (unknown.length) return response.status(400).json({ error: "unknown_features", fields: unknown.sort() });
    const row = { ...model.defaults }; const warnings = [];
    for (const [key, raw] of Object.entries(supplied)) {
      if (model.ranges[key]) {
        const value = Number(raw); const bounds = model.ranges[key];
        if (!Number.isFinite(value)) return response.status(422).json({ error: "number_required", field: key });
        if (value < bounds.min || value > bounds.max) return response.status(422).json({ error: "out_of_range", field: key, bounds });
        const baseline = model.drift_baseline.numeric[key];
        if (baseline.sd && Math.abs(value - baseline.mean) / baseline.sd > 3) warnings.push(`Input distribution warning for ${key}`);
        row[key] = value;
      } else {
        const value = String(raw);
        if (!model.categories[key]?.includes(value)) warnings.push(`Unseen category for ${key}`);
        row[key] = value;
      }
    }
    const risk = probability(row); const riskBand = risk >= model.threshold ? "higher" : "lower";
    console.log(JSON.stringify({ level: "info", event: "prediction", model_version: model.version,
      input_hash: createHash("sha256").update(JSON.stringify(supplied)).digest("hex").slice(0, 16), risk_band: riskBand,
      warning_count: warnings.length, duration_ms: Date.now() - started }));
    return response.status(200).json({ probability: risk, classification: Number(risk >= model.threshold), risk_band: riskBand,
      threshold: model.threshold, model_version: model.version, validation_status: "internal synthetic-data validation only", warnings });
  } catch (error) {
    console.error(JSON.stringify({ level: "error", event: "prediction_failed", error: error?.name ?? "Error", duration_ms: Date.now() - started }));
    return response.status(400).json({ error: "invalid_request" });
  }
}
