"""Resumably download the PhysioNet BIDSleep ZIP using parallel byte ranges."""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import subprocess
import shutil
import time
import urllib.request
from pathlib import Path

URL = "https://physionet.org/content/bidsleep-dataset/get-zip/1.0.0/"
EXPECTED_BYTES = 6_354_227_911


def download_part(args: tuple[int, int, int, Path]) -> tuple[int, int]:
    index, start, end, folder = args
    target = folder / f"part-{index:04d}.bin"
    expected = end - start + 1
    if target.exists() and target.stat().st_size == expected:
        return index, target.stat().st_size
    temporary = target.with_suffix(".download")
    curl = shutil.which("curl") or shutil.which("curl.exe")
    last_error: Exception | None = None
    # PhysioNet occasionally resets long-running ranged responses. Retry the
    # individual chunk so one transient connection error cannot kill the job.
    for attempt in range(1, 21):
        temporary.unlink(missing_ok=True)
        try:
            if curl:
                command = [
                    curl, "--fail", "--location", "--silent", "--show-error",
                    "--retry", "5", "--retry-all-errors", "--retry-delay", "4",
                    "--connect-timeout", "30", "--max-time", "600", "--http1.1",
                    "--range", f"{start}-{end}", "--output", str(temporary), URL,
                ]
                subprocess.run(command, check=True)
            else:
                request = urllib.request.Request(
                    URL, headers={"Range": f"bytes={start}-{end}", "Accept-Encoding": "identity"}
                )
                with urllib.request.urlopen(request, timeout=180) as response, temporary.open("wb") as handle:
                    shutil.copyfileobj(response, handle, length=1024 * 1024)
            actual = temporary.stat().st_size if temporary.exists() else 0
            if actual != expected:
                raise RuntimeError(f"part {index} expected {expected} bytes, got {actual}")
            temporary.replace(target)
            return index, expected
        except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
            last_error = error
            temporary.unlink(missing_ok=True)
            if attempt < 20:
                time.sleep(min(30, 2 + attempt * 2))
    raise RuntimeError(f"part {index} failed after 20 attempts: {last_error}") from last_error


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("external/physionet/bidsleep-dataset-1.0.0.zip"))
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--part-mib", type=int, default=8)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    parts = args.output.with_suffix(args.output.suffix + ".parts")
    parts.mkdir(parents=True, exist_ok=True)
    part_bytes = args.part_mib * 1024 * 1024
    jobs = [(i, start, min(start + part_bytes - 1, EXPECTED_BYTES - 1), parts)
            for i, start in enumerate(range(0, EXPECTED_BYTES, part_bytes))]
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        completed = 0
        for index, size in pool.map(download_part, jobs):
            completed += size
            if completed % (512 * 1024 * 1024) < size:
                print(json.dumps({"downloaded_gb": round(completed / 1024**3, 2), "total_gb": round(EXPECTED_BYTES / 1024**3, 2)}), flush=True)
    with args.output.open("wb") as destination:
        for index, *_ in jobs:
            with (parts / f"part-{index:04d}.bin").open("rb") as source:
                shutil.copyfileobj(source, destination, length=1024 * 1024)
    if args.output.stat().st_size != EXPECTED_BYTES:
        raise RuntimeError("assembled ZIP size does not match the PhysioNet Content-Length")
    print(f"Downloaded {args.output} ({args.output.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
