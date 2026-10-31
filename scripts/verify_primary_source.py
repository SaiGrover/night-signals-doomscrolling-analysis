"""Verify the committed CSV against Kaggle dataset version 1 without replacing it."""
from __future__ import annotations

import hashlib
import io
import json
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data/sleep_doomscrolling_habits.csv"
URL = "https://www.kaggle.com/api/v1/datasets/download/harpartapsingh13/sleep-and-doomscrolling-habits-dataset?datasetVersionNumber=1"


def main() -> None:
    with urllib.request.urlopen(URL, timeout=60) as response:
        archive_bytes = response.read()
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        source_bytes = archive.read(CSV.name)
    local_hash = hashlib.sha256(CSV.read_bytes()).hexdigest()
    source_hash = hashlib.sha256(source_bytes).hexdigest()
    result = {
        "source": URL,
        "file": CSV.name,
        "local_sha256": local_hash,
        "kaggle_version_1_sha256": source_hash,
        "byte_identical": local_hash == source_hash,
        "scope": "File identity only; does not verify the synthetic generator, category rule, or predictor timing.",
    }
    target = ROOT / "outputs/tables/primary_source_verification.json"
    target.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not result["byte_identical"]:
        raise SystemExit("Local primary CSV differs from Kaggle version 1")


if __name__ == "__main__":
    main()
