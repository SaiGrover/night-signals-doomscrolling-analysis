from pathlib import Path
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

root = Path(__file__).resolve().parents[1]
nb = nbformat.v4.new_notebook()
nb.cells = [
    nbformat.v4.new_markdown_cell("# Production predictive modelling\n\nThis notebook reports model v2.0. The final holdout was split before comparison; all tuning and threshold selection use development data only."),
    nbformat.v4.new_code_cell("from pathlib import Path\nimport json, pandas as pd\nfrom IPython.display import display, Image\nROOT=Path.cwd()\nsummary=json.loads((ROOT/'outputs/tables/production_model_summary.json').read_text())\ndisplay(pd.Series(summary, name='value').to_frame())"),
    nbformat.v4.new_markdown_cell("## Prediction timing and leakage controls\n\nThe prediction moment is bedtime, before sleep outcomes occur. Sleep duration, latency, wakeups, fatigue, sleep debt, quality score, target, and respondent ID are excluded."),
    nbformat.v4.new_code_cell("display(pd.DataFrame({'excluded_post_outcome_feature':summary['excluded_post_outcome_features']}))"),
    nbformat.v4.new_markdown_cell("## Nested model comparison\n\nCandidates are tuned inside nested cross-validation on the 750-row development partition. Nominal variables use one-hot encoding; no ordinal distances are imposed."),
    nbformat.v4.new_code_cell("comparison=pd.read_csv(ROOT/'outputs/tables/production_model_comparison.csv')\ndisplay(comparison)"),
    nbformat.v4.new_markdown_cell("## Calibration, decision policy, and primary-model importance\n\nThe threshold is selected from development-only out-of-fold probabilities with false negatives weighted twice as heavily as false positives."),
    nbformat.v4.new_code_cell("display(Image(filename=str(ROOT/'outputs/figures/15_production_risk_model.png')))"),
    nbformat.v4.new_markdown_cell("## Untouched holdout and uncertainty"),
    nbformat.v4.new_code_cell("display(pd.Series(summary['holdout'],name='holdout').to_frame())\ndisplay(pd.DataFrame(summary['holdout_95_ci']).T)"),
    nbformat.v4.new_markdown_cell("## Subgroup diagnostic\n\nThese are diagnostics, not fairness certification. Small cells are omitted and all estimates remain uncertain."),
    nbformat.v4.new_code_cell("display(pd.read_csv(ROOT/'outputs/tables/subgroup_performance.csv'))"),
    nbformat.v4.new_markdown_cell("## External-validation boundary\n\nNo independent real-world validation has been performed. The model must not be treated as clinical, diagnostic, or deployment-ready evidence until the external validation contract is satisfied."),
]
nb.metadata.kernelspec = {"display_name": "Python 3", "language": "python", "name": "python3"}
processor = ExecutePreprocessor(timeout=120, kernel_name="python3")
processor.preprocess(nb, {"metadata": {"path": str(root)}})
for target in [root/'notebooks/sleep_doomscrolling_predictive_modeling.ipynb', root/'public/methodology/sleep_doomscrolling_predictive_modeling.ipynb']:
    nbformat.write(nb, target)
print("production notebook written")
