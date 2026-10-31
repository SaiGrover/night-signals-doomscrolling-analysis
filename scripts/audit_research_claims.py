"""Recompute descriptive claim checks from the immutable primary CSV."""
from pathlib import Path

import pandas as pd
from scipy.stats import chi2_contingency
from statsmodels.stats.multitest import multipletests

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/sleep_doomscrolling_habits.csv"
OUT = ROOT / "outputs/tables"


def main() -> None:
    df = pd.read_csv(DATA)
    target = df["sleep_quality_category"]
    score = pd.crosstab(target, df["sleep_quality_score"], dropna=False)
    score.to_csv(OUT / "target_quality_score_crosstab.csv")
    rows = []
    for field in ["bedtime_routine_type", "uses_night_mode", "keeps_phone_in_bedroom",
                  "consumes_negative_news_content", "doomscroller"]:
        pair = df[[field, "sleep_quality_category"]].dropna()
        table = pd.crosstab(pair[field], pair["sleep_quality_category"])
        chi2, p, _, expected = chi2_contingency(table)
        v = (chi2 / (len(pair) * min(table.shape[0] - 1, table.shape[1] - 1))) ** .5
        rows.append({"variable": field, "n": len(pair), "chi2_p": p,
                     "cramers_v": v, "minimum_expected_cell": expected.min()})
    tests = pd.DataFrame(rows)
    tests["p_fdr_bh"] = multipletests(tests.chi2_p, method="fdr_bh")[1]
    tests.to_csv(OUT / "habit_association_tests.csv", index=False)
    habit = df.groupby("bedtime_routine_type", dropna=False).agg(
        n=("sleep_quality_category", "size"),
        good_share=("sleep_quality_category", lambda x: x.eq("Good").mean()),
        poor_share=("sleep_quality_category", lambda x: x.eq("Poor").mean()),
        mean_bedtime_screen_min=("bedtime_screen_time_minutes", "mean"),
    )
    habit.to_csv(OUT / "routine_outcomes.csv")
    print("Poor with quality score 5:", int(score.loc["Poor", 5.0]), "/", int(target.eq("Poor").sum()))
    print(tests.to_string(index=False))
    print(habit.to_string())


if __name__ == "__main__":
    main()
