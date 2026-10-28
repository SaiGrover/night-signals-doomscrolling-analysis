from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parent


def _existing(*candidates: Path) -> Path:
    """Use packaged artifacts when present, otherwise source-project artifacts."""
    return next((candidate for candidate in candidates if candidate.exists()), candidates[0])


DATA_DIR = _existing(ROOT / "data", PROJECT_ROOT / "data")
OUTPUT_DIR = _existing(
    ROOT / "outputs" if (ROOT / "outputs" / "tables" / "production_model_summary.json").exists() else PROJECT_ROOT / "outputs",
    PROJECT_ROOT / "outputs",
)
TABLE_DIR = OUTPUT_DIR / "tables"
MODEL_DIR = OUTPUT_DIR / "models"
NOTEBOOK_DIR = _existing(ROOT / "notebooks", PROJECT_ROOT / "notebooks")
RANDOM_STATE = 42

# Canonical exception-cohort definition shared by scripts, notebooks, and UI.
HIGH_EXPOSURE_SCREEN_MINUTES = 66
HIGH_EXPOSURE_DOOMSCROLLER = "Yes"

PRIMARY_DATA = _existing(
    DATA_DIR / "sleep_doomscrolling_habits.csv",
    PROJECT_ROOT / "sleep_doomscrolling_habits.csv",
)
PORTABLE_MODEL = MODEL_DIR / "poor_sleep_preoutcome_model.json"
MODEL_SUMMARY = TABLE_DIR / "production_model_summary.json"
ANALYSIS_SUMMARY = OUTPUT_DIR / "analysis_summary.json"

OUTCOME_COLUMNS = [
    "sleep_hours_per_night",
    "sleep_latency_minutes",
    "number_of_night_wakeups",
    "weekly_sleep_debt_hours",
    "daytime_fatigue_score",
    "sleep_quality_score",
]

POST_OUTCOME_COLUMNS = {
    "respondent_id",
    "sleep_hours_per_night",
    "sleep_latency_minutes",
    "number_of_night_wakeups",
    "weekly_sleep_debt_hours",
    "daytime_fatigue_score",
    "sleep_quality_score",
    "sleep_quality_category",
}
