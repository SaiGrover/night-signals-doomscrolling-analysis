"""Exploratory target sensitivity and adjusted habit associations.

All intervals/p-values describe this synthetic file's model fit, not population
uncertainty. Analyses were specified after prior inspection, not preregistered.
"""
from pathlib import Path
import json

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from sklearn.metrics import balanced_accuracy_score, cohen_kappa_score
from statsmodels.stats.multitest import multipletests

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "outputs/tables"


def main() -> None:
    frame = pd.read_csv(ROOT / "data/sleep_doomscrolling_habits.csv")
    observed = frame.dropna(subset=["sleep_quality_score"]).copy()
    observed["poor_label"] = observed.sleep_quality_category.eq("Poor").astype(int)
    observed["score_below_five"] = observed.sleep_quality_score.lt(5).astype(int)
    sensitivity = {
        "n_complete_score": len(observed),
        "poor_label_share": float(observed.poor_label.mean()),
        "score_below_five_share": float(observed.score_below_five.mean()),
        "agreement": float((observed.poor_label == observed.score_below_five).mean()),
        "balanced_accuracy_label_vs_score_proxy": float(balanced_accuracy_score(observed.score_below_five, observed.poor_label)),
        "cohen_kappa": float(cohen_kappa_score(observed.poor_label, observed.score_below_five)),
        "note": "Score <5 is an arbitrary alternative label sensitivity check, not a validated clinical threshold. The score is ceiling-compressed.",
    }
    (TABLES / "target_sensitivity.json").write_text(json.dumps(sensitivity, indent=2), encoding="utf-8")

    frame["poor_label"] = frame.sleep_quality_category.eq("Poor").astype(int)
    frame["news_yes"] = frame.consumes_negative_news_content.eq("Yes").astype(int)
    frame["night_yes"] = frame.uses_night_mode.eq("Yes").astype(int)
    frame["phone_in"] = frame.keeps_phone_in_bedroom.eq("Yes").astype(int)
    frame["doom_yes"] = frame.doomscroller.eq("Yes").astype(int)
    model_frame = frame.dropna(subset=["bedtime_routine_type", "bedtime_screen_time_minutes", "age", "gender", "occupation_status"])
    formula = (
        "poor_label ~ C(bedtime_routine_type, Treatment(reference='No Fixed Routine')) "
        "+ news_yes + night_yes + phone_in + doom_yes + bedtime_screen_time_minutes "
        "+ age + C(gender) + C(occupation_status)"
    )
    fit = smf.logit(formula, data=model_frame).fit(disp=False, maxiter=200)
    interval = fit.conf_int()
    rows = []
    for term in fit.params.index:
        if not term.startswith("C(bedtime_routine_type") and term not in {"news_yes", "night_yes", "phone_in"}:
            continue
        rows.append({
            "term": term, "n_complete_cases": len(model_frame),
            "odds_ratio": float(np.exp(fit.params[term])),
            "ci_low": float(np.exp(interval.loc[term, 0])),
            "ci_high": float(np.exp(interval.loc[term, 1])),
            "p_value": float(fit.pvalues[term]),
        })
    results = pd.DataFrame(rows)
    results["p_fdr_bh"] = multipletests(results.p_value, method="fdr_bh")[1]
    results.to_csv(TABLES / "adjusted_habit_associations.csv", index=False)
    print(json.dumps(sensitivity, indent=2))
    print(results.to_string(index=False))


if __name__ == "__main__":
    main()
