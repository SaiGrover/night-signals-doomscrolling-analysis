"""Generate ten sequential, executable research notebooks."""
import json
from pathlib import Path

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "notebooks"
COMMON = "from pathlib import Path; import json; import pandas as pd; import matplotlib.pyplot as plt; from IPython.display import display; ROOT=Path.cwd(); ROOT=ROOT if (ROOT/'data').exists() else ROOT.parent; DATA=ROOT/'data'/'sleep_doomscrolling_habits.csv'; OUTPUTS=ROOT/'outputs'; TABLES=OUTPUTS/'tables'; raw=pd.read_csv(DATA)\n"
TOPICS = [
    ("01_dataset_acquisition_provenance_quality", "Dataset acquisition, provenance, and quality auditing", "from night_signals.data import range_audit; print(raw.shape); print('duplicates', raw.duplicated().sum()); print('unique IDs', raw.respondent_id.nunique()); quality=pd.DataFrame({'dtype':raw.dtypes.astype(str),'missing_n':raw.isna().sum(),'unique_n':raw.nunique(dropna=True)}); quality['missing_pct']=quality.missing_n/len(raw)*100; display(quality.sort_values('missing_n', ascending=False)); display(raw.sleep_quality_category.value_counts(dropna=False)); display(range_audit(raw))"),
    ("02_cleaning_preprocessing_feature_engineering", "Cleaning, preprocessing, and feature engineering", "from night_signals.data import load_survey; df=load_survey(DATA); display(df[['doomscroll_load_minutes','exposure_quartile','protective_habit_count','high_exposure','age_group']].head()); post={'respondent_id','sleep_hours_per_night','sleep_latency_minutes','number_of_night_wakeups','weekly_sleep_debt_hours','daytime_fatigue_score','sleep_quality_score','sleep_quality_category'}; display(pd.DataFrame({'feature':raw.columns,'excluded_from_preoutcome_model':[c in post for c in raw.columns]}))"),
    ("03_comprehensive_eda", "Comprehensive exploratory data analysis", "from night_signals.data import load_survey; df=load_survey(DATA); fig,axes=plt.subplots(1,3,figsize=(15,4)); df.bedtime_screen_time_minutes.plot.hist(ax=axes[0],bins=24,color='#5eead4',title='Bedtime screen time'); df.doomscroll_load_minutes.plot.hist(ax=axes[1],bins=24,color='#8b9cff',title='Doomscroll load'); df.boxplot(column='sleep_latency_minutes',by='sleep_quality_category',ax=axes[2],grid=False); plt.suptitle(''); plt.tight_layout(); plt.show(); display(df.groupby('sleep_quality_category',observed=True)[['sleep_hours_per_night','sleep_latency_minutes','weekly_sleep_debt_hours','daytime_fatigue_score']].agg(['mean','median','count']))"),
    ("04_statistical_hypothesis_testing", "Statistical hypothesis testing, association analysis, and confidence intervals", "from night_signals.data import load_survey; from night_signals.statistics import association_matrix,mean_ci,cohens_d; df=load_survey(DATA); display(association_matrix(df).sort_values('p_fdr_bh')); [print(o,'Cohen d',cohens_d(df.loc[df.favorable_sleep,o],df.loc[df.poor_sleep,o]),'CI',mean_ci(df.loc[df.favorable_sleep,o])) for o in ['sleep_latency_minutes','weekly_sleep_debt_hours','sleep_hours_per_night']]"),
    ("05_exposure_gradient_resilience_protective_factors", "Exposure gradients, resilience, and protective factors", "from night_signals.data import load_survey; from night_signals.statistics import exposure_gradient,resilience_effects; df=load_survey(DATA); display(exposure_gradient(df)); display(resilience_effects(df)); display(df.groupby('sleep_quality_category',observed=True).protective_habit_count.agg(['mean','median','count']))"),
    ("06_ml_baselines_training_cross_validation_tuning", "ML baselines, training, cross-validation, and hyperparameter tuning", "comparison=pd.read_csv(TABLES/'production_model_comparison.csv'); multiclass=pd.read_csv(TABLES/'multi_model_comparison.csv'); display(comparison); display(multiclass); print('training script',ROOT/'scripts'/'train_production_model.py')"),
    ("07_model_evaluation_calibration_thresholds_explainability", "Model evaluation, calibration, threshold optimization, and explainability", "summary=json.loads((TABLES/'production_model_summary.json').read_text()); print(summary['selected_model'],summary['nested_cv'],summary['holdout'],summary['holdout_95_ci']); display(pd.read_csv(TABLES/'production_feature_importance.csv').sort_values('importance',ascending=False)); display(pd.read_csv(TABLES/'subgroup_performance.csv')); print('Diagnostic figure:',OUTPUTS/'figures'/'15_production_risk_model.png')"),
    ("08_nhanes_independent_population_health_analysis", "NHANES independent population-health analysis", "summary=json.loads((TABLES/'nhanes_summary.json').read_text()); print(summary['dataset'],summary['cycle'],summary['analytic_adults']); display(pd.read_csv(TABLES/'nhanes_sleep_by_bmi.csv')); display(pd.read_csv(TABLES/'nhanes_sleep_by_activity.csv'))"),
    ("09_physionet_physiological_signal_analysis", "PhysioNet physiological signal analysis", "summary=json.loads((TABLES/'physionet_summary.json').read_text()); print(summary['dataset'],summary['subjects_analysed'],summary['total_scored_epochs']); display(pd.read_csv(TABLES/'physionet_hr_by_stage.csv')); display(pd.read_csv(TABLES/'physionet_stage_composition.csv'))"),
    ("10_final_results_cross_dataset_synthesis_limitations", "Final results, cross-dataset synthesis, limitations, and conclusions", "analysis=json.loads((OUTPUTS/'analysis_summary.json').read_text()); model=json.loads((TABLES/'production_model_summary.json').read_text()); nhanes=json.loads((TABLES/'nhanes_summary.json').read_text()); physio=json.loads((TABLES/'physionet_summary.json').read_text()); results=pd.DataFrame([{'layer':'Primary survey','n':analysis['n'],'claim':'Associations only; self-reported and cross-sectional.'},{'layer':'Primary model','n':model['untouched_holdout_rows'],'claim':str(round(model['holdout']['balanced_accuracy']*100,1))+'% holdout balanced accuracy; internal validation only.'},{'layer':'NHANES','n':nhanes['analytic_adults'],'claim':'Independent population-health evidence; not row-merged.'},{'layer':'PhysioNet','n':physio['subjects_analysed'],'claim':'Independent physiological evidence; not causal validation.'}]); display(results); print('Limitations: self-report, incomplete sampling metadata, ceiling effects, small subgroup, no independent validation, no causal claims')"),
]

def build(title, source):
    source_text = (COMMON + source).replace('\\n', '\n')
    return {'cells':[{'cell_type':'markdown','metadata':{},'source':[f'# {title}\n','\n','Sequential Night Signals research workflow.\n']},{'cell_type':'code','execution_count':None,'metadata':{},'outputs':[],'source':source_text.splitlines(keepends=True)}],'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}},'nbformat':4,'nbformat_minor':5}

if __name__ == '__main__':
    OUT.mkdir(exist_ok=True)
    processor = ExecutePreprocessor(timeout=180, kernel_name="python3")
    for stem, title, source in TOPICS:
        path = OUT / f"{stem}.ipynb"
        path.write_text(json.dumps(build(title, source), indent=1), encoding="utf-8")
        notebook = nbformat.read(path, as_version=4)
        processor.preprocess(notebook, {"metadata": {"path": str(ROOT)}})
        nbformat.write(notebook, path)
    print(f'Generated {len(TOPICS)} notebooks in {OUT}')
