"""Finish the optional multi-night evidence layer once the resumable ZIP exists.

Run with --wait in the background while download_bidsleep.py is active. Raw files
remain under ignored external/; only aggregate tables enter the repository.
"""
from __future__ import annotations

import argparse
import json
import shutil
import time
import zipfile
from pathlib import Path

from build_bidsleep_evidence import ROOT, TABLES, source_manifest, summarize_local

ZIP = ROOT / "external/physionet/bidsleep-dataset-1.0.0.zip"
DEST = ROOT / "external/physionet/bidsleep-dataset/1.0.0"
EXPECTED_BYTES = 6_354_227_911


def finalize(wait: bool) -> dict:
    if wait:
        deadline = time.monotonic() + 24 * 60 * 60
        while not ZIP.exists() and time.monotonic() < deadline:
            time.sleep(30)
    if not ZIP.exists() or ZIP.stat().st_size != EXPECTED_BYTES:
        raise RuntimeError("Complete PhysioNet ZIP is unavailable; leave the manifest-only status in place")

    DEST.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP) as archive:
        for item in archive.infolist():
            parts = Path(item.filename.replace("\\", "/")).parts
            subject_at = next((i for i, part in enumerate(parts) if part.startswith("Bidslab")), None)
            if subject_at is None or item.is_dir():
                continue
            relative = Path(*parts[subject_at:])
            if relative.name not in {"labels.mat", "hr.csv", "motion.csv"}:
                continue
            target = DEST / relative
            if target.exists() and target.stat().st_size == item.file_size:
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.with_suffix(target.suffix + ".partial")
            with archive.open(item) as source, temporary.open("wb") as output:
                shutil.copyfileobj(source, output, length=1024 * 1024)
            if temporary.stat().st_size != item.file_size:
                raise RuntimeError(f"Extracted size mismatch: {relative}")
            temporary.replace(target)

    result = summarize_local(DEST)
    expected = source_manifest()
    if result["subjects_analysed"] != expected["expected_subjects"] or result["nights_analysed"] != expected["expected_nights"]:
        raise RuntimeError(f"Incomplete extracted cohort: {result['subjects_analysed']} subjects, {result['nights_analysed']} nights")
    TABLES.mkdir(parents=True, exist_ok=True)
    (TABLES / "bidsleep_manifest.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--wait", action="store_true")
    args = parser.parse_args()
    print(json.dumps(finalize(args.wait), indent=2), flush=True)
