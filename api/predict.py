import hashlib
import json
import os
import time
from collections import defaultdict, deque
from http.server import BaseHTTPRequestHandler
from pathlib import Path

import joblib
import pandas as pd

ARTIFACT = Path(__file__).resolve().parents[1] / "outputs/models/poor_sleep_preoutcome_model.joblib"
BUNDLE = joblib.load(ARTIFACT)
REQUESTS = defaultdict(deque)


class handler(BaseHTTPRequestHandler):
    def _send(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status); self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store"); self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers(); self.wfile.write(body)

    def do_POST(self):
        started = time.time(); request_id = self.headers.get("x-vercel-id", "local")
        configured_key = os.getenv("PREDICTION_API_KEY")
        if configured_key and self.headers.get("x-api-key") != configured_key:
            return self._send(401, {"error": "unauthorized"})
        client = self.headers.get("x-forwarded-for", "local").split(",")[0]
        now = time.time(); bucket = REQUESTS[client]
        while bucket and now - bucket[0] > 60: bucket.popleft()
        if len(bucket) >= 30: return self._send(429, {"error": "rate_limit", "retry_after_seconds": 60})
        bucket.append(now)
        try:
            length = int(self.headers.get("content-length", "0"))
            if length <= 0 or length > 16384: return self._send(413, {"error": "invalid_payload_size"})
            supplied = json.loads(self.rfile.read(length))
            if not isinstance(supplied, dict): return self._send(400, {"error": "object_required"})
            unknown = sorted(set(supplied) - set(BUNDLE["features"]))
            if unknown: return self._send(400, {"error": "unknown_features", "fields": unknown})
            row, warnings = dict(BUNDLE["defaults"]), []
            for key, value in supplied.items():
                if key in BUNDLE["ranges"]:
                    value = float(value); bounds = BUNDLE["ranges"][key]
                    if value < bounds["min"] or value > bounds["max"]:
                        return self._send(422, {"error": "out_of_range", "field": key, "bounds": bounds})
                    baseline = BUNDLE.get("drift_baseline", {}).get("numeric", {}).get(key)
                    if baseline and baseline["sd"] and abs(value - baseline["mean"]) / baseline["sd"] > 3:
                        warnings.append(f"Input distribution warning for {key}")
                elif str(value) not in BUNDLE["categories"].get(key, []):
                    warnings.append(f"Unseen category for {key}")
                row[key] = value
            probability = float(BUNDLE["model"].predict_proba(pd.DataFrame([row]))[0, 1])
            threshold = float(BUNDLE["threshold"])
            payload = {"probability": probability, "classification": int(probability >= threshold),
                       "risk_band": "higher" if probability >= threshold else "lower",
                       "threshold": threshold, "model_version": BUNDLE["version"],
                       "validation_status": "internal synthetic-data validation only", "warnings": warnings}
            audit = {"level": "info", "event": "prediction", "request_id": request_id,
                     "model_version": BUNDLE["version"], "input_hash": hashlib.sha256(json.dumps(supplied, sort_keys=True).encode()).hexdigest()[:16],
                     "risk_band": payload["risk_band"], "warning_count": len(warnings),
                     "duration_ms": round((time.time()-started)*1000)}
            print(json.dumps(audit), flush=True)
            self._send(200, payload)
        except Exception as error:
            print(json.dumps({"level": "error", "event": "prediction_failed", "request_id": request_id,
                              "error": type(error).__name__, "duration_ms": round((time.time()-started)*1000)}), flush=True)
            self._send(400, {"error": "invalid_request"})
