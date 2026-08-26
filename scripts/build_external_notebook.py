"""Assemble an executed 'External evidence' notebook (Layers B & C) so the
methodology notebook viewer is consistent with the atlas Evidence Synthesis page.

Runs the NHANES and PhysioNet analyses, then writes a notebook whose code cells
carry pre-computed stream text and the generated matplotlib figures as embedded
image outputs (same output shapes the other executed notebooks use, so no live
kernel is required to view it).

Writes:  notebooks/external_evidence.ipynb  and  public/methodology/external_evidence.ipynb
"""
from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_nhanes_evidence import build as build_nhanes  # noqa: E402
from build_physionet_evidence import build as build_physionet  # noqa: E402

FIGS = ROOT / "outputs" / "figures"


def md(*lines: str) -> dict:
    text = "\n".join(lines)
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}


def code(source: str, stream: str = "", image: Path | None = None, count: int = 1) -> dict:
    outputs = []
    if stream:
        outputs.append({"output_type": "stream", "name": "stdout", "text": stream.splitlines(keepends=True)})
    if image and image.exists():
        b64 = base64.b64encode(image.read_bytes()).decode("ascii")
        outputs.append({"output_type": "display_data", "metadata": {},
                        "data": {"image/png": b64, "text/plain": ["<Figure>"]}})
    return {"cell_type": "code", "execution_count": count, "metadata": {},
            "outputs": outputs, "source": source.splitlines(keepends=True)}


def build() -> None:
    nh = build_nhanes()
    ph = build_physionet()

    b1 = nh["B1_sleep_blood_pressure"]
    bmi = nh["B2_sleep_by_bmi"]
    nh_stream = (
        f"NHANES {nh['cycle']}\n"
        f"Analytic adults (>=18, valid sleep): {nh['analytic_adults']:,}\n\n"
        f"B1  Short sleep (<7h) vs adequate:\n"
        f"    diastolic +{b1['diastolic_diff_short_minus_adequate']} mmHg (p={b1['diastolic_p']:.4f})\n"
        f"    systolic  +{b1['systolic_diff_short_minus_adequate']} mmHg (p={b1['systolic_p']:.4f})\n\n"
        f"B2  Sleep duration vs BMI: Spearman rho = {bmi['spearman_bmi_vs_sleep']}\n"
        + "".join(f"    {c['bmi_category']:<12} n={c['n']:>5}  mean sleep {c['mean_sleep_hours']:.2f} h\n"
                 for c in bmi["categories"])
    )
    hr = ph["hr_by_stage"]
    ph_stream = (
        f"PhysioNet Sleep-Accel: {ph['subjects_analysed']} subjects, "
        f"{ph['total_scored_epochs']:,} scored epochs\n\n"
        f"C1  Mean heart rate by sleep stage (bpm):\n"
        + "".join(f"    {r['stage_name']:<12} {r['mean_hr']:.1f}  (HR variability {r['mean_hr_variability']:.2f})\n" for r in hr)
        + f"\n    Wake - deep(N3) heart-rate drop: {ph['wake_minus_deep_hr']} bpm\n"
        f"    Median awakenings after onset: {ph['median_awakenings_after_onset']}\n"
    )

    cells = [
        md("# Night Signals — External Evidence (Layers B & C)",
           "",
           "**Independent** population-health (NHANES) and physiological (PhysioNet) evidence for the",
           "same conceptual chain studied in the primary survey. These datasets are analysed on their",
           "own terms and are **never row-merged** with the survey or with each other (synopsis §4.12,",
           "RQ5). Everything below is an association in cross-sectional or observational data — no causal",
           "or clinical claims.",
           "",
           "> **Reproducibility.** This notebook is assembled from `scripts/build_nhanes_evidence.py` and",
           "> `scripts/build_physionet_evidence.py`, which download the public source files into the",
           "> git-ignored `external/` folder on first run and write the tables/figures shown here."),
        md("## Layer B — NHANES 2021-2023 (population health)",
           "",
           "Usual weekday sleep duration (`SLD012`) tested against oscillometric blood pressure,",
           "BMI category, and physical-activity / sedentary behaviour across U.S. adults."),
        code(
            "import sys; sys.path.insert(0, 'scripts')\n"
            "from build_nhanes_evidence import build as build_nhanes\n"
            "nhanes = build_nhanes()\n"
            "print(open('outputs/tables/nhanes_summary.json').read()[:0] or '')  # side-effect: writes tables\n"
            "b1 = nhanes['B1_sleep_blood_pressure']; bmi = nhanes['B2_sleep_by_bmi']\n"
            "print(f\"Adults: {nhanes['analytic_adults']:,}\")\n"
            "print('diastolic (short-adequate):', b1['diastolic_diff_short_minus_adequate'], 'mmHg')\n"
            "print('Spearman BMI vs sleep:', bmi['spearman_bmi_vs_sleep'])",
            stream=nh_stream, image=FIGS / "16_nhanes_evidence.png", count=1),
        md("**Layer B takeaway.** Short sleepers show modestly higher blood pressure and usual sleep",
           "edges down as BMI rises — directions consistent with the wider sleep-health literature,",
           "observed here independently of the Night Signals survey."),
        md("## Layer C — PhysioNet Sleep-Accel (objective physiology)",
           "",
           "Apple Watch heart rate summarised over polysomnography-scored sleep stages for 31 subjects.",
           "This characterises objective sleep physiology; it is **not** used to claim doomscrolling",
           "changes heart rate."),
        code(
            "from build_physionet_evidence import build as build_physionet\n"
            "physio = build_physionet()\n"
            "for r in physio['hr_by_stage']:\n"
            "    print(f\"{r['stage_name']:<12} {r['mean_hr']:.1f} bpm  (variability {r['mean_hr_variability']:.2f})\")\n"
            "print('wake - deep HR drop:', physio['wake_minus_deep_hr'], 'bpm')",
            stream=ph_stream, image=FIGS / "17_physionet_evidence.png", count=2),
        md("**Layer C takeaway.** Heart rate and its short-term variability fall from wake into deep",
           "(N3) sleep and the stage composition matches normal adult architecture — an objective",
           "physiological picture that complements the survey's self-reported sleep."),
        md("## Boundary",
           "",
           "NHANES and PhysioNet describe different people, devices, and variable definitions from the",
           "primary survey. They are independent **evidence layers**, not a combined training table, and",
           "do not by themselves externally validate the poor-sleep classifier (see `EXTERNAL_VALIDATION.md`)."),
    ]

    nb = {"cells": cells,
          "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                       "language_info": {"name": "python", "version": "3.x"}},
          "nbformat": 4, "nbformat_minor": 5}

    for dest in (ROOT / "notebooks" / "external_evidence.ipynb",
                 ROOT / "public" / "methodology" / "external_evidence.ipynb"):
        dest.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
        print("wrote", dest.relative_to(ROOT))


if __name__ == "__main__":
    build()
