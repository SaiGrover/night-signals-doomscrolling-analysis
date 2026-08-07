from pathlib import Path
import json
import shutil
import re

from matplotlib import get_data_path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Image, Table,
    TableStyle, PageBreak, KeepTogether, NextPageTemplate,
)

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "Sleep_Doomscrolling_Report.pdf"
CHARTS = ROOT / "assets" / "charts"
S = json.loads((ROOT / "analysis_summary.json").read_text(encoding="utf-8"))

FONT_DIR = Path(get_data_path()) / "fonts" / "ttf"
pdfmetrics.registerFont(TTFont("CMRoman", FONT_DIR / "cmr10.ttf"))
pdfmetrics.registerFont(TTFont("CMBold", FONT_DIR / "cmb10.ttf"))
pdfmetrics.registerFont(TTFont("CMMono", FONT_DIR / "cmtt10.ttf"))

NAVY = colors.HexColor("#081120")
INK = colors.HexColor("#152238")
MUTED = colors.HexColor("#586A86")
PALE = colors.HexColor("#EEF4FB")
LINE = colors.HexColor("#CBD8E8")
BLUE = colors.HexColor("#335C9F")
CYAN = colors.HexColor("#1F9EB5")
VIOLET = colors.HexColor("#7259B8")
PINK = colors.HexColor("#B84B82")
GOLD = colors.HexColor("#A87518")
MINT = colors.HexColor("#248267")

PAGE_W, PAGE_H = letter
MARGIN_X = 0.72 * inch
MARGIN_TOP = 0.64 * inch
MARGIN_BOTTOM = 0.62 * inch

styles = getSampleStyleSheet()
BODY = ParagraphStyle("BodyCM", parent=styles["BodyText"], fontName="CMRoman", fontSize=9.6, leading=13.2, textColor=INK, spaceAfter=6)
SMALL = ParagraphStyle("SmallCM", parent=BODY, fontSize=7.7, leading=10, textColor=MUTED)
KICKER = ParagraphStyle("KickerCM", parent=SMALL, fontName="CMMono", fontSize=7.2, leading=9, tracking=1.2, textColor=CYAN, spaceBefore=5, spaceAfter=4)
H1 = ParagraphStyle("H1CM", parent=BODY, fontName="CMBold", fontSize=21, leading=24, textColor=INK, spaceBefore=7, spaceAfter=8, keepWithNext=True)
H2 = ParagraphStyle("H2CM", parent=BODY, fontName="CMBold", fontSize=14, leading=17, textColor=BLUE, spaceBefore=10, spaceAfter=6, keepWithNext=True)
CAPTION = ParagraphStyle("CaptionCM", parent=SMALL, alignment=TA_CENTER, fontSize=7.5, leading=9.5, spaceBefore=3, spaceAfter=4)
CALLOUT = ParagraphStyle("CalloutCM", parent=BODY, fontName="CMBold", fontSize=9.4, leading=12.5, textColor=INK, leftIndent=7, rightIndent=7, spaceBefore=5, spaceAfter=5)


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE); canvas.setLineWidth(0.45)
    canvas.line(MARGIN_X, PAGE_H - 0.42 * inch, PAGE_W - MARGIN_X, PAGE_H - 0.42 * inch)
    canvas.setFont("CMMono", 6.8); canvas.setFillColor(MUTED)
    canvas.drawString(MARGIN_X, PAGE_H - 0.32 * inch, "NIGHT SIGNALS / SLEEP x DOOMSCROLLING")
    canvas.drawRightString(PAGE_W - MARGIN_X, 0.32 * inch, f"{doc.page}")
    canvas.restoreState()


def cover_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY); canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#0F2B45")); canvas.circle(PAGE_W * 0.78, PAGE_H * 0.65, 2.45 * inch, fill=1, stroke=0)
    canvas.setStrokeColor(colors.HexColor("#3DA7B5")); canvas.setLineWidth(0.6)
    for radius in (1.25, 1.75, 2.25): canvas.circle(PAGE_W * 0.78, PAGE_H * 0.65, radius * inch, fill=0, stroke=1)
    canvas.setFillColor(colors.HexColor("#E7FAFF")); canvas.circle(PAGE_W * 0.78, PAGE_H * 0.65, 0.82 * inch, fill=1, stroke=0)
    canvas.setFillColor(NAVY); canvas.circle(PAGE_W * 0.84, PAGE_H * 0.69, 0.82 * inch, fill=1, stroke=0)
    canvas.restoreState()


doc = BaseDocTemplate(str(OUT), pagesize=letter, leftMargin=MARGIN_X, rightMargin=MARGIN_X, topMargin=MARGIN_TOP, bottomMargin=MARGIN_BOTTOM,
                      title="Night Signals: Sleep, Doomscrolling and the Night", author="Night Signals")
frame = Frame(MARGIN_X, MARGIN_BOTTOM, PAGE_W - 2 * MARGIN_X, PAGE_H - MARGIN_TOP - MARGIN_BOTTOM, id="body")
doc.addPageTemplates([PageTemplate(id="cover", frames=frame, onPage=cover_page), PageTemplate(id="body", frames=frame, onPage=header_footer)])


def p(text, style=BODY):
    return Paragraph(text, style)


def section(title, subtitle, accent=BLUE):
    data = [[p(title, ParagraphStyle("SectionTitle", parent=H1, textColor=colors.white, spaceBefore=0, spaceAfter=0)),
             p(subtitle, ParagraphStyle("SectionSub", parent=SMALL, textColor=colors.HexColor("#D5E4F5"), spaceAfter=0))]]
    table = Table(data, colWidths=[2.35 * inch, 4.67 * inch], hAlign="LEFT")
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, 0), accent), ("BACKGROUND", (1, 0), (1, 0), NAVY),
                               ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 11),
                               ("RIGHTPADDING", (0, 0), (-1, -1), 11), ("TOPPADDING", (0, 0), (-1, -1), 9),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 9)]))
    return [Spacer(1, 8), table, Spacer(1, 7)]


def stat_strip(items, fill=NAVY):
    cells = []
    for value, label in items:
        cells.append(p(f'<font name="CMBold" size="17" color="#FFFFFF">{value}</font><br/><font name="CMMono" size="6.5" color="#BDD0E7">{label.upper()}</font>', ParagraphStyle("Stat", parent=BODY, alignment=TA_CENTER, leading=14, spaceAfter=0)))
    table = Table([cells], colWidths=[7.02 * inch / len(cells)] * len(cells), hAlign="LEFT")
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), fill), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                               ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#45617F")), ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#45617F")),
                               ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 10)]))
    return table


def callout(label, text, accent=CYAN):
    table = Table([["", p(f'<font name="CMMono" size="6.8" color="{accent.hexval()}">{label.upper()}</font><br/>{text}', CALLOUT)]], colWidths=[0.08 * inch, 6.94 * inch])
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, 0), accent), ("BACKGROUND", (1, 0), (1, 0), PALE),
                               ("LEFTPADDING", (0, 0), (0, 0), 0), ("RIGHTPADDING", (0, 0), (0, 0), 0),
                               ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    return table


def figure(filename, number, caption, takeaway, accent=CYAN):
    img = Image(str(CHARTS / filename), width=6.2 * inch, height=3.45 * inch)
    img.hAlign = "CENTER"
    return KeepTogether([img, p(f'<font name="CMBold">Figure {number}.</font> {caption}', CAPTION), callout("Read this", takeaway, accent), Spacer(1, 5)])


def bullets(items):
    out = []
    for item in items:
        out.append(p(f'<font name="CMBold" color="#1F9EB5">-</font>&nbsp;&nbsp;{item}', ParagraphStyle("BulletCM", parent=BODY, leftIndent=10, firstLineIndent=-10, spaceAfter=5)))
    return out


story = []
story += [Spacer(1, 0.45 * inch), p("NIGHT SIGNALS / 2026", ParagraphStyle("CoverKicker", parent=KICKER, textColor=colors.HexColor("#8BD9E8"), fontSize=8.5)),
          Spacer(1, 2.62 * inch), p("Sleep, Doomscrolling<br/>and the Night", ParagraphStyle("CoverTitle", parent=H1, fontSize=31, leading=34, textColor=colors.white)),
          p("How late-night scrolling, negative news, and protective routines relate to sleep quality across 1,000 respondents", ParagraphStyle("CoverSub", parent=BODY, fontSize=12.5, leading=17, textColor=colors.HexColor("#C9D8EF"), spaceAfter=23)),
          stat_strip([("47.6%", "Doomscrollers"), ("+10.6 min", "Latency gap"), ("11 / 204", "Heavy-scroller exceptions")], BLUE),
          Spacer(1, 14), p("DATA ANALYSIS REPORT  /  29 ANALYTIC VARIABLES  /  11 REPORT FIGURES", ParagraphStyle("CoverFoot", parent=KICKER, textColor=colors.HexColor("#AFC1DE"), alignment=TA_CENTER))]
story += [NextPageTemplate("body"), PageBreak()]

story += section("Executive summary", "The answer first: the strongest signal is the bedtime-disruption chain", BLUE)
story += [p("Doomscrolling is consistently associated with a harder night in this dataset. Respondents labeled doomscrollers take longer to fall asleep, wake more often, carry more weekly sleep debt, and sleep slightly less. Bedtime screen time is the clearest continuous marker."),
          p("The relationship is not destiny. A small group of heavy scrollers still reports good sleep. Their profile shifts the useful question from who scrolls to what surrounds the scrolling."),
          stat_strip([(f"{S['latency_gap_minutes']:.1f} min", "Longer latency"), (f"{S['sleep_debt_gap_hours']:.1f} h", "More weekly debt"), (f"{abs(S['sleep_duration_gap_hours'])*60:.0f} min", "Less sleep nightly")]), Spacer(1, 8)]
story += bullets(["Doomscrolling plus negative-news consumption aligns with the highest anxiety, stress, and fatigue averages.",
                  "Reading, meditation or journaling, a phone outside the bedroom, and regular exercise show more protective patterns than night mode alone.",
                  "Behavioral variables predict sleep-quality category more strongly than most demographics.",
                  "The data appear synthetic or simulation-assisted; findings are descriptive, non-causal, and not population prevalence."])
story += [callout("Central thread", "Exposure links to latency; latency, wakeups, and short sleep accumulate into debt and fatigue.", VIOLET), Spacer(1, 9)]
story += [p("HERO FINDING", KICKER), p("More scrolling shifts the night toward poorer sleep", H1), p("Nightly doomscroll load combines session count with average duration. Poor sleepers sit farther to the right, while the overlap makes clear that exposure raises risk without determining the outcome."),
          figure("02_hero_doomscroll_sleep.png", 1, "Nightly doomscroll load by reported sleep-quality category.", "Poor sleepers carry the highest median nightly doomscroll load; good sleepers cluster lower, with meaningful overlap.")]

story += section("Core relationship", "Q1-2 / Sleep quality, latency, wakeups, duration, and debt", VIOLET)
story += [p("Across five outcomes, the doomscroller label points in the same direction: longer latency, more wakeups, more debt, shorter sleep, and greater fatigue. Shared causes such as stress, habit intensity, or chronotype may explain part of every gap."),
          figure("03_doomscroller_comparison.png", 2, "Mean sleep outcomes for doomscrollers and non-doomscrollers.", "Doomscrollers average 10.6 extra minutes of latency and 1.5 additional hours of weekly debt, plus more wakeups and fatigue.", VIOLET),
          p("Dose response", KICKER), p("Bedtime exposure matters beyond the binary label", H2),
          p("Quartiles reveal a graded pattern: as bedtime exposure rises, latency and weekly sleep debt increase. Wakeups rise and sleep duration declines, suggesting the binary label compresses a richer relationship."),
          figure("04_dose_response.png", 3, "Average outcomes across quartiles of bedtime screen time.", "Latency and debt climb across exposure quartiles while sleep duration declines and wakeups rise.", PINK)]

story += section("Mental health angle", "Q3-4 / Anxiety, stress, fatigue, and negative-news consumption", PINK)
story += [p("Doomscrolling involves content and emotional activation as well as minutes. When negative-news consumption accompanies doomscrolling, average anxiety, stress, and fatigue are highest. A feedback loop is plausible, but direction cannot be established."),
          figure("05_mental_health.png", 4, "Average anxiety, stress, and fatigue by doomscrolling and negative-news status.", "The dual-exposure group shows the heaviest mental-wellbeing burden.", PINK),
          callout("Interpret carefully", "The dataset cannot tell whether distress drives scrolling, scrolling drives distress, or both.", PINK)]

story += section("Protective habits", "Q5-6 / What appears to soften the pattern?", MINT)
story += [p("The most useful signals are structural: what a respondent does before bed, where the phone sleeps, and whether daytime movement is protected. Night mode is convenient, but its profile is weaker than a genuinely different bedtime routine."),
          figure("06_protective_habits.png", 5, "Good-sleep share and sleep latency for selected habits and routines.", "Reading and meditation or journaling stand out; social scrolling performs worst, and night mode is not a substitute for routine change.", MINT),
          figure("07_exercise_gradient.png", 6, "Good-sleep share and daytime fatigue across exercise bands.", "Exercise looks modestly protective, but the pattern is not perfectly monotonic and is not a cure-all.", MINT)]

story += section("Demographic context", "Q7-8 / Age buckets, occupation, country, and descriptive gender context", GOLD)
story += [p("Age buckets replace raw age where they clarify the story: Teens (15-19), 20s (20-29), and 30s+. Age-occupation cells reveal pockets of elevated doomscrolling. Country rates vary across samples of very different sizes, so these are segmentation clues rather than rankings."),
          figure("08_demographics.png", 7, "Doomscrolling by age bucket and occupation, plus country-level doomscrolling and poor-sleep shares.", "Younger and student pockets are often elevated, but small cells and uneven country samples prevent definitive comparisons.", GOLD),
          callout("Gender", "Gender differences are modest and descriptive only; behavior remains the more actionable signal.", GOLD)]

story += section("The Exceptions", "Counter-narrative / Heavy scrollers who still report good sleep", CYAN)
story += [p(f"Heavy doomscrollers are self-identified doomscrollers at or above {S['heavy_threshold']:.0f} minutes of bedtime screen time. There are {S['heavy_n']} such respondents, yet only {S['exception_n']} report good sleep. The group is small enough to demand caution, but distinct enough to challenge a simplistic conclusion."),
          figure("10_exceptions.png", 8, "Standardized differences between good-sleep exceptions and other heavy scrollers.", "The exceptions realize more sleep and less debt or latency, with restorative routines appearing more often.", CYAN),
          callout("Counter-narrative", "Exposure raises risk; routine and realized sleep appear to shape whether that risk becomes an outcome.", CYAN)]

story += section("Personas", "Transparent combinations for product and behavior design - not diagnoses", VIOLET)
persona_rows = [
    ("THE NIGHT SCROLLER", "n=204", "High bedtime exposure. First lever: environmental friction and a hard stop cue.", PINK),
    ("THE ANXIOUS NEWS SEEKER", "n=51", "High negative-news load and distress. First lever: a content boundary and decompression ritual.", GOLD),
    ("THE DISCIPLINED SLEEPER", "n=130", "Lower exposure with reading or reflection. Opportunity: protect and reinforce the routine.", MINT),
]
for name, count, desc, accent in persona_rows:
    card = Table([[p(f'<font name="CMMono" size="7" color="{accent.hexval()}">{count}</font><br/><font name="CMBold" size="12">{name}</font><br/>{desc}', BODY)]], colWidths=[7.02 * inch])
    card.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), PALE), ("BOX", (0, 0), (-1, -1), 1.2, accent), ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12), ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    story += [card, Spacer(1, 6)]
story += [figure("11_personas.png", 9, "Relative persona profiles with observed metric values.", "Different mechanisms imply different interventions: friction, content boundaries, or routine reinforcement.", VIOLET)]

story += section("Synthesis", "Q9 / Correlation structure and predictive ranking", BLUE)
story += [p("The correlation structure resembles a bedtime-disruption chain. Exposure relates to latency; latency, wakeups, and shorter sleep accumulate into debt and fatigue. This coherence also heightens the synthetic-data caveat."),
          figure("12_correlation_heatmap.png", 10, "Pearson correlations among selected behavioral, sleep, and wellbeing measures.", "Bedtime screen time, doomscroll sessions, and latency form the strongest exposure cluster; sleep duration moves opposite sleep debt.", BLUE),
          p("Predictive view", KICKER), p("The behavior label leads; the night's mechanics follow", H2),
          p(f"A random-forest classifier evaluated with five-fold cross-validation reaches {S['cv_balanced_accuracy']:.1%} balanced accuracy against a {S['baseline_accuracy']:.1%} majority-class baseline. The outcome-adjacent sleep-quality score is excluded to reduce leakage."),
          figure("13_feature_importance.png", 11, "Cross-validated permutation importance for predicting sleep-quality category.", "The doomscroller label leads, followed by wakeups, sleep duration, sleep debt, and latency. Prediction does not identify causes.", BLUE)]

story += section("Conclusion", "Practical takeaways and limits", MINT)
story += [p("The defensible conclusion is not that every minute of scrolling destroys sleep. A repeatable pattern - longer exposure, more checking, delayed sleep, more wakeups, and accumulated debt - appears throughout the data. Action should target the chain rather than moralize the behavior."), p("Practical takeaways", H2)]
story += bullets(["Create friction before bedtime: charge the phone outside the bedroom or beyond arm's reach.",
                  "Replace, do not merely remove: use reading, meditation, or journaling for the final 20-30 minutes.",
                  "Treat negative news as a separate lever: schedule a news window and disable late alerts.",
                  "Protect daytime movement without expecting exercise to offset severe nighttime disruption.",
                  "Track latency, wakeups, and weekly debt - not only total screen time.",
                  "Test by persona: friction for exposure, content boundaries for distress, maintenance cues for disciplined sleepers."])
story += [callout("Best next test", "A two-week phone-outside-bedroom experiment with a fixed replacement routine and daily latency tracking.", MINT),
          p("Limitations", H2)]
story += bullets(["The dataset appears synthetic or simulation-assisted: target classes are unusually balanced, relationships are unusually clean, and valid sleep-quality scores are concentrated at 5/5.",
                  "The design is cross-sectional and self-reported; temporal direction and causal effects cannot be established.",
                  "Median imputation and an Unknown category preserve all 1,000 records but can attenuate associations.",
                  "Some subgroup cells - especially the good-sleep heavy-scroller exception group - are small and exploratory.",
                  "Country and gender comparisons are descriptive only; unequal samples and unmeasured context prevent broad generalization."])
story += [p("Method in brief", H2), p("The workflow validates IDs, dtypes, missingness, ranges, and formulaic patterns; creates age buckets; compares groups and quartiles; defines exceptions and personas; visualizes correlations; and evaluates a random forest with stratified five-fold cross-validation. The executed notebook remains viewable on the methodology page.")]

audit_data = [[p("SANITY-CHECK SIGNAL", KICKER), p("OBSERVATION", KICKER), p("REPORTING CONSEQUENCE", KICKER)],
              [p("Target balance", SMALL), p("Only ten rows separate the three sleep-quality classes.", SMALL), p("Do not treat class shares as population prevalence.", SMALL)],
              [p("Ceiling effect", SMALL), p("More than 86% of valid quality scores are 5/5.", SMALL), p("Use categories cautiously; retain the caveat in every synthesis.", SMALL)],
              [p("Orderly dependence", SMALL), p("Sleep duration and weekly debt correlate at about -0.89.", SMALL), p("Keep effect sizes inside this file; avoid causal or external claims.", SMALL)],
              [p("Formula scan", SMALL), p("No exact one-variable arithmetic formula reproduces the target.", SMALL), p("Synthetic appearance is a limitation, not proof of a generator.", SMALL)]]
audit = Table(audit_data, colWidths=[1.55 * inch, 2.25 * inch, 3.22 * inch], repeatRows=1)
audit.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), NAVY), ("GRID", (0, 0), (-1, -1), 0.35, LINE),
                           ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 7),
                           ("RIGHTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 6),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 6), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE])]))
story += [p("Synthetic-data audit", H2), audit, Spacer(1, 8),
          callout("Reproducibility", "The PDF is the sole report export. The executed notebook remains embedded as a read-only methodology artifact on the website; chart interactions are powered by Plotly from a generated JSON specification.", BLUE),
          p("Interpretation boundary", H2)]
boundary = Table([[
    p('<font name="CMMono" size="7" color="#1F9EB5">OBSERVATION</font><br/><br/><font name="CMBold" size="11">Pattern, not proof</font><br/><br/>A repeated association is a reason to test a bedtime intervention. It is not evidence that one behavior caused an individual outcome.', SMALL),
    p('<font name="CMMono" size="7" color="#7259B8">PREDICTION</font><br/><br/><font name="CMBold" size="11">Rank, not mechanism</font><br/><br/>Feature importance shows which variables help classify sleep quality in this file. It does not reveal a biological or behavioral mechanism.', SMALL),
    p('<font name="CMMono" size="7" color="#A87518">SEGMENTATION</font><br/><br/><font name="CMBold" size="11">Context, not ranking</font><br/><br/>Age, occupation, country, and gender describe where patterns concentrate. Unequal samples prevent cultural or demographic league tables.', SMALL),
]], colWidths=[2.34 * inch] * 3, rowHeights=[1.72 * inch])
boundary.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), PALE), ("GRID", (0, 0), (-1, -1), 0.4, LINE),
                              ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 10),
                              ("RIGHTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, -1), 10)]))
closing = Table([[p('<font name="CMMono" size="7" color="#8BD9E8">THE USEFUL QUESTION</font><br/><br/><font name="CMBold" size="17" color="#FFFFFF">What can change around the scrolling?</font><br/><br/><font color="#C9D8EF">Start with friction, content boundaries, and a replacement routine; then watch latency, wakeups, and weekly debt.</font>', ParagraphStyle("Closing", parent=BODY, textColor=colors.white, leading=14, spaceAfter=0))]], colWidths=[7.02 * inch], rowHeights=[1.55 * inch])
closing.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), NAVY), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                             ("LEFTPADDING", (0, 0), (-1, -1), 18), ("RIGHTPADDING", (0, 0), (-1, -1), 18)]))
story += [boundary, Spacer(1, 9), closing]

doc.build(story)

# ReportLab initializes empty Helvetica text states on each canvas. They draw no
# glyphs, but removing them keeps the exported artifact strictly Computer Modern.
from pypdf import PdfReader, PdfWriter
from pypdf.generic import DecodedStreamObject, NameObject

reader = PdfReader(str(OUT))
writer = PdfWriter()
for page in reader.pages:
    stream = page.get_contents().get_data()
    stream = re.sub(rb"BT\s+/F1\s+[\d.]+\s+Tf\s+[\d.]+\s+TL\s+ET", b"", stream)
    replacement = DecodedStreamObject(); replacement.set_data(stream)
    page[NameObject("/Contents")] = replacement
    resources = page.get("/Resources", {}).get_object()
    fonts = resources.get("/Font", {}).get_object()
    if NameObject("/F1") in fonts: del fonts[NameObject("/F1")]
    writer.add_page(page)
writer.add_metadata({"/Title": "Night Signals: Sleep, Doomscrolling and the Night", "/Author": "Night Signals"})
tmp = OUT.with_suffix(".clean.pdf")
with tmp.open("wb") as handle: writer.write(handle)
tmp.replace(OUT)

(ROOT / "public" / "downloads").mkdir(parents=True, exist_ok=True)
shutil.copy2(OUT, ROOT / "public" / "downloads" / OUT.name)
print(f"Saved {OUT}")
