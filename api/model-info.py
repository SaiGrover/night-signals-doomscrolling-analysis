import json
from http.server import BaseHTTPRequestHandler
from pathlib import Path

REGISTRY = Path(__file__).resolve().parents[1] / "public/data/model_registry.json"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = REGISTRY.read_bytes(); self.send_response(200)
        self.send_header("Content-Type", "application/json"); self.send_header("Cache-Control", "public, max-age=300")
        self.end_headers(); self.wfile.write(body)
