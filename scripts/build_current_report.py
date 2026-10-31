"""Regenerate the current, evidence-limited Night Signals PDF from saved tables."""
from pathlib import Path
import json

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "outputs/tables"
DEST = ROOT / "deliverables/Sleep_Doomscrolling_Report.pdf"


def main() -> None:
    model = json.loads((TABLES / "production_model_summary.json").read_text())
    tests = pd.read_csv(TABLES / "habit_association_tests.csv")
    routines = pd.read_csv(TABLES / "routine_outcomes.csv")
    baseline = pd.read_csv(TABLES / "development_baselines_ablations.csv")
    calibration = json.loads((TABLES / "holdout_calibration_slope.json").read_text())
    nhanes = json.loads((TABLES / "nhanes_summary.json").read_text())
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleNS", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=23, leading=27, textColor=colors.HexColor("#102a3d"), spaceAfter=16))
    styles.add(ParagraphStyle(name="H1NS", parent=styles["Heading2"], fontSize=13, leading=17, textColor=colors.HexColor("#127c83"), spaceBefore=15, spaceAfter=7))
    styles.add(ParagraphStyle(name="BodyNS", parent=styles["BodyText"], fontSize=9.5, leading=14, spaceAfter=7))
    styles.add(ParagraphStyle(name="SmallNS", parent=styles["BodyText"], fontSize=8, leading=11))
    styles.add(ParagraphStyle(name="CellNS", parent=styles["BodyText"], fontSize=7.5, leading=10))
    doc = SimpleDocTemplate(str(DEST), pagesize=(8.27*inch, 11.69*inch), leftMargin=49, rightMargin=49, topMargin=48, bottomMargin=45)
    story = []

    def p(text, style="BodyNS"):
        story.append(Paragraph(text, styles[style]))

    def section(title, body):
        story.append(KeepTogether([Paragraph(title, styles["H1NS"]), Paragraph(body, styles["BodyNS"])]))

    def table(headers, rows, widths):
        cells = [[Paragraph(str(v), styles["CellNS"]) for v in row] for row in [headers, *rows]]
        item = Table(cells, colWidths=widths, repeatRows=1, hAlign="LEFT")
        item.setStyle(TableStyle([
            ("BACKGROUND", (0,0),(-1,0), colors.HexColor("#dceef0")),
            ("ROWBACKGROUNDS", (0,1),(-1,-1), [colors.white, colors.HexColor("#f3f7f8")]),
            ("VALIGN", (0,0),(-1,-1), "TOP"),
            ("BOTTOMPADDING",(0,0),(-1,-1),6),
            ("TOPPADDING",(0,0),(-1,-1),6),
            ("LINEBELOW",(0,0),(-1,0),.7,colors.HexColor("#127c83")),
        ]))
        story.extend([item, Spacer(1, 8)])

    p("Night Signals", "TitleNS")
    p("A public synthetic-data audit and internal model evaluation")
    section("Source and scope", "The primary file contains 1,000 Kaggle records described by the uploader as synthetic. This project did not design or conduct a survey. No sampling frame, item wording, generation algorithm or within-night timestamps are provided. The results below describe this file; they are not estimates for a real population. Source: kaggle.com/datasets/harpartapsingh13/sleep-and-doomscrolling-habits-dataset. Local source checksum and field caveats are documented in data/PROVENANCE.md and DATA_DICTIONARY.md.")
    section("Target validity", "A direct category-by-score check finds that 213 of 330 records labeled Poor have sleep_quality_score 5/5. The category derivation is undocumented. The classifier should be read as recovery of a synthetic file label, not detection of clinical poor sleep.")
    section("Research questions and exploratory tests", "The five habit/category checks were specified after prior inspection and are exploratory, not preregistered. Pearson chi-square tests use complete cases; Benjamini-Hochberg FDR adjusts these five comparisons. Cramer's V is descriptive; statistical significance does not establish a protective effect.")
    table(["Variable", "n", "Cramer's V", "FDR p"], [(r.variable.replace("_"," "), int(r.n), f"{r.cramers_v:.3f}", f"{r.p_fdr_bh:.3g}") for r in tests.itertuples()], [220,45,95,105])
    section("Routines and negative news", "The unadjusted routine association is small. Reading does not stand out as protective: its Good share is below the 34% file-wide base rate. The no-fixed-routine group has the highest Good share. Negative-news exposure has a weak association with the category (chi-square p about 0.742). None of these contrasts establishes causality.")
    table(["Routine", "n", "Good %", "Poor %"], [(str(r.bedtime_routine_type), int(r.n), f"{r.good_share*100:.1f}", f"{r.poor_share*100:.1f}") for r in routines.dropna(subset=["bedtime_routine_type"]).itertuples()], [230,50,90,90])
    section("Model protocol", "The binary target is Poor versus all other categories. Measured sleep outcomes, quality score and record ID are excluded. Numeric imputation/scaling and categorical encoding occur in model pipelines. Five-by-three nested cross-validation compares candidates on 750 development records. A sigmoid-calibrated logistic ensemble and a cost-weighted threshold were fitted using development data. Earlier experiments may have inspected overlapping holdout rows, so prospective test independence is unverified. The cross-sectional source also cannot establish predictor availability at bedtime.")
    h = model["holdout"]
    ci = model["holdout_95_ci"]["balanced_accuracy"]
    section("Internal evaluation", f"Selected logistic model nested-CV balanced accuracy: {model['nested_cv']['balanced_accuracy']:.3f} (fold SD {model['nested_cv']['balanced_accuracy_sd']:.3f}). Historical 250-row holdout: balanced accuracy {h['balanced_accuracy']:.3f} (bootstrap 95% interval {ci['low']:.3f}-{ci['high']:.3f}), ROC AUC {h['roc_auc']:.3f}, PR AUC {h['pr_auc']:.3f}, Brier {h['brier']:.3f}, sensitivity {h['sensitivity']:.3f}, specificity {h['specificity']:.3f}; threshold {model['decision_threshold']:.3f}. These are internal label-recovery metrics.")
    p(f"Retrospective holdout calibration: intercept {calibration['calibration_intercept']:.3f} (95% CI {calibration['calibration_intercept_95_ci'][0]:.3f} to {calibration['calibration_intercept_95_ci'][1]:.3f}); slope {calibration['calibration_slope']:.3f} (95% CI {calibration['calibration_slope_95_ci'][0]:.3f} to {calibration['calibration_slope_95_ci'][1]:.3f}). This is not external calibration.")
    table(["Development-only comparator", "Features", "BA at 0.5", "OOF ROC AUC"], [(r.model, int(r.features), f"{r.oof_balanced_accuracy_0_5:.3f}", f"{r.oof_roc_auc:.3f}") for r in baseline.itertuples()], [225,55,90,90])
    p("The fixed-threshold logistic comparisons are diagnostic and are not directly equivalent to the tuned, calibrated nested-CV production estimate.", "SmallNS")
    section("Independent context and limitations", f"NHANES includes {nhanes['analytic_adults']:,} analytic adults. Age/sex-adjusted weighted WLS with stratum fixed effects and PSU-clustered covariance is an approximation, not full survey-design inference. PAD800/PAD820 are minutes per occasion; the observed activity comparison does not support a protective claim. PhysioNet subjects are unrelated to the Kaggle file. Neither dataset validates the classifier or its doomscrolling association. The high-exposure favorable-sleep subgroup is small, and contrasts in sleep duration, debt or fatigue are circular because those quantities track the outcome. External real-world model validation has not been performed.")
    p("Reproducibility: python scripts/audit_research_claims.py; python scripts/compare_simple_baselines.py; python scripts/train_production_model.py. The report is generated by scripts/build_current_report.py. Legacy figures remain historical and should not be cited as current-model results.", "SmallNS")
    def footer(canvas, document):
        canvas.setStrokeColor(colors.HexColor("#ccd9dd")); canvas.line(49,37,doc.pagesize[0]-49,37)
        canvas.setFont("Helvetica",8); canvas.setFillColor(colors.HexColor("#526875"))
        canvas.drawString(49,26,"Night Signals | synthetic-data case study")
        canvas.drawRightString(doc.pagesize[0]-49,26,str(document.page))
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(DEST)


if __name__ == "__main__":
    main()
