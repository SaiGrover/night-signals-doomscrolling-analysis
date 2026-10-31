"""Download checksum-verified BIDSleep stage labels and heart rate for all nights.

This is a compact physiological evidence layer. Accelerometry remains pending
until the full archive is downloaded and finalized separately.
"""
from __future__ import annotations

import concurrent.futures
import hashlib
import time
import urllib.request
from pathlib import Path

from build_bidsleep_evidence import DEFAULT_ROOT, TABLES, source_manifest, summarize_local
import json

BASE = "https://physionet.org/files/bidsleep-dataset/1.0.0/"
DEST = DEFAULT_ROOT


def download_one(item: tuple[str, str]) -> str:
    expected_hash, relative = item
    target = DEST / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() == expected_hash:
        return relative
    for attempt in range(5):
        try:
            request = urllib.request.Request(BASE + relative, headers={"User-Agent": "NightSignalsResearch/1.0"})
            with urllib.request.urlopen(request, timeout=60) as response:
                payload = response.read()
            if hashlib.sha256(payload).hexdigest() != expected_hash:
                raise ValueError(f"SHA-256 mismatch: {relative}")
            temporary = target.with_suffix(target.suffix + ".partial")
            temporary.write_bytes(payload)
            temporary.replace(target)
            return relative
        except (OSError, ValueError):
            if attempt == 4:
                raise
            time.sleep(2 * (attempt + 1))
    raise AssertionError("unreachable")


def main() -> None:
    with urllib.request.urlopen(BASE + "SHA256SUMS.txt", timeout=60) as response:
        checksums = response.read().decode("utf-8")
    items = []
    for line in checksums.splitlines():
        digest, relative = line.split(maxsplit=1)
        if relative.endswith(("/hr.csv", "/labels.mat")):
            items.append((digest, relative))
    if len(items) != 506:
        raise RuntimeError(f"Expected 253 heart-rate and 253 label files; found {len(items)}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        for count, _ in enumerate(pool.map(download_one, items), start=1):
            if count % 50 == 0:
                print(f"verified {count}/{len(items)} files", flush=True)
    result = summarize_local(DEST)
    expected = source_manifest()
    if (result["subjects_analysed"], result["nights_analysed"]) != (
        expected["expected_subjects"], expected["expected_nights"]
    ):
        raise RuntimeError(f"Incomplete cohort: {result['subjects_analysed']} subjects, {result['nights_analysed']} nights")
    result["local_status"] = "analysed_hr_labels_motion_pending"
    result["modalities_analysed"] = ["EEG-derived stage labels", "Apple Watch heart rate"]
    result["motion_status"] = "Accelerometry is pending the full archive download; motion statistics are unavailable."
    (TABLES / "bidsleep_manifest.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"subjects": result["subjects_analysed"], "nights": result["nights_analysed"], "status": result["local_status"]}), flush=True)


if __name__ == "__main__":
    main()
