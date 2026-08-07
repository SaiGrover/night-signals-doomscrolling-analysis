from pathlib import Path
import json

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "sleep_doomscrolling_habits.csv"
OUTPUT = ROOT / "public" / "data" / "plotly_charts.json"

COLORS = {
    "cyan": "#59D8E8", "blue": "#6F8CFF", "violet": "#AA8DFF",
    "pink": "#EF83BB", "gold": "#EFC36B", "mint": "#64D6AD",
    "red": "#FF7187", "muted": "#93A8C8", "grid": "rgba(147,168,200,.14)",
}


def clean_records(frame):
    return json.loads(frame.to_json(orient="records"))


df = pd.read_csv(DATA)
for col in df.select_dtypes(include=["object", "string"]).columns:
    if col != "respondent_id":
        df[col] = df[col].fillna("Unknown")
for col in df.select_dtypes(include=np.number).columns:
    df[col] = df[col].fillna(df[col].median())

df["age_bucket"] = pd.cut(
    df["age"], bins=[14, 19, 29, np.inf], labels=["Teens (15-19)", "20s (20-29)", "30s+"]
)
df["doomscroll_load_minutes"] = df["doomscroll_sessions_per_night"] * df["avg_doomscroll_session_minutes"]
df["screen_quartile"] = pd.qcut(
    df["bedtime_screen_time_minutes"], 4, labels=["Lowest", "Low-mid", "High-mid", "Highest"]
)

charts = {}

# 01 - four independent demographic bars.
overview = []
overview_defs = [
    ("age_bucket", "Age bucket", COLORS["cyan"], "x", "y"),
    ("gender", "Gender", COLORS["violet"], "x2", "y2"),
    ("country_region", "Country / region", COLORS["gold"], "x3", "y3"),
    ("occupation_status", "Occupation", COLORS["mint"], "x4", "y4"),
]
for col, name, color, xaxis, yaxis in overview_defs:
    counts = df[col].value_counts().sort_values()
    overview.append({
        "type": "bar", "orientation": "h", "name": name,
        "x": counts.values.tolist(), "y": counts.index.astype(str).tolist(),
        "xaxis": xaxis, "yaxis": yaxis, "marker": {"color": color},
        "hovertemplate": "%{y}<br>%{x} respondents<extra></extra>",
    })
charts["01_descriptive_overview.png"] = {
    "data": overview,
    "layout": {
        "grid": {"rows": 2, "columns": 2, "pattern": "independent", "xgap": .18, "ygap": .25},
        "annotations": [
            {"text": d[1], "xref": "paper", "yref": "paper", "showarrow": False,
             "x": [.2, .8, .2, .8][i], "y": [1.06, 1.06, .44, .44][i], "font": {"color": COLORS["muted"], "size": 11}}
            for i, d in enumerate(overview_defs)
        ],
        "height": 620, "margin": {"l": 105, "r": 30, "t": 55, "b": 35}, "showlegend": False,
    },
}

# 02 - doomscroll load jittered by sleep category.
category_y = {"Poor": 0, "Fair": 1, "Good": 2}
rng = np.random.default_rng(42)
hero = []
for category, color in [("Good", COLORS["mint"]), ("Fair", COLORS["gold"]), ("Poor", COLORS["red"])]:
    subset = df[df.sleep_quality_category.eq(category)]
    hero.append({
        "type": "scattergl", "mode": "markers", "name": category,
        "x": subset.doomscroll_load_minutes.round(2).tolist(),
        "y": (category_y[category] + rng.normal(0, .055, len(subset))).round(3).tolist(),
        "text": subset.bedtime_screen_time_minutes.round(0).astype(int).astype(str).tolist(),
        "marker": {"color": color, "size": 7, "opacity": .58},
        "hovertemplate": f"{category} sleep<br>Load: %{{x:.1f}} min<br>Bedtime screen: %{{text}} min<extra></extra>",
    })
charts["02_hero_doomscroll_sleep.png"] = {
    "data": hero,
    "layout": {"height": 520, "margin": {"l": 70, "r": 30, "t": 25, "b": 65},
               "xaxis": {"title": "Nightly doomscroll load (sessions x average minutes)"},
               "yaxis": {"tickvals": [0, 1, 2], "ticktext": ["Poor", "Fair", "Good"], "range": [-.3, 2.3], "title": "Sleep quality"},
               "legend": {"orientation": "h", "y": 1.09}},
}

# 03 - five independent outcome panels.
outcomes = [
    ("sleep_latency_minutes", "Latency", "min"),
    ("number_of_night_wakeups", "Wakeups", "count"),
    ("weekly_sleep_debt_hours", "Debt", "h/wk"),
    ("sleep_hours_per_night", "Duration", "h"),
    ("daytime_fatigue_score", "Fatigue", "1-10"),
]
doom_group = df.groupby("doomscroller")
doom_traces = []
for idx, (col, label, unit) in enumerate(outcomes):
    axis = "" if idx == 0 else str(idx + 1)
    vals = [float(doom_group[col].mean().loc["No"]), float(doom_group[col].mean().loc["Yes"])]
    doom_traces.append({
        "type": "bar", "x": ["No", "Yes"], "y": vals, "xaxis": f"x{axis}", "yaxis": f"y{axis}",
        "name": label, "marker": {"color": [COLORS["blue"], COLORS["pink"]]},
        "text": [f"{v:.1f}" for v in vals], "textposition": "outside",
        "hovertemplate": f"%{{x}} doomscroller<br>%{{y:.2f}} {unit}<extra>{label}</extra>",
    })
charts["03_doomscroller_comparison.png"] = {
    "data": doom_traces,
    "layout": {"grid": {"rows": 1, "columns": 5, "pattern": "independent", "xgap": .08}, "height": 430,
               "margin": {"l": 45, "r": 20, "t": 35, "b": 55}, "showlegend": False,
               "annotations": [{"text": x[1], "xref": "paper", "yref": "paper", "x": (i + .5) / 5, "y": 1.08, "showarrow": False, "font": {"size": 10, "color": COLORS["muted"]}} for i, x in enumerate(outcomes)]},
}

# 04 - dose response.
dose = df.groupby("screen_quartile", observed=True).agg(
    latency=("sleep_latency_minutes", "mean"), debt=("weekly_sleep_debt_hours", "mean"),
    wakeups=("number_of_night_wakeups", "mean"), sleep=("sleep_hours_per_night", "mean")
).reset_index()
quartiles = dose.screen_quartile.astype(str).tolist()
charts["04_dose_response.png"] = {
    "data": [
        {"type": "scatter", "mode": "lines+markers", "name": "Latency (min)", "x": quartiles, "y": dose.latency.round(2).tolist(), "line": {"color": COLORS["pink"], "width": 3}},
        {"type": "scatter", "mode": "lines+markers", "name": "Debt (h/wk)", "x": quartiles, "y": dose.debt.round(2).tolist(), "line": {"color": COLORS["gold"], "width": 3}},
        {"type": "scatter", "mode": "lines+markers", "name": "Sleep hours", "x": quartiles, "y": dose.sleep.round(2).tolist(), "yaxis": "y2", "line": {"color": COLORS["mint"], "width": 3, "dash": "dot"}},
        {"type": "scatter", "mode": "lines+markers", "name": "Wakeups", "x": quartiles, "y": dose.wakeups.round(2).tolist(), "yaxis": "y2", "line": {"color": COLORS["violet"], "width": 3, "dash": "dot"}},
    ],
    "layout": {"height": 460, "margin": {"l": 60, "r": 65, "t": 35, "b": 60},
               "xaxis": {"title": "Bedtime screen-time quartile"}, "yaxis": {"title": "Latency / debt"},
               "yaxis2": {"title": "Sleep hours / wakeups", "overlaying": "y", "side": "right"},
               "legend": {"orientation": "h", "y": 1.13}},
}

# 05 - mental health stacked groups.
mental_cols = [("anxiety_score", "Anxiety"), ("stress_score", "Stress"), ("daytime_fatigue_score", "Fatigue")]
mental_traces = []
groups = [("No", "No"), ("No", "Yes"), ("Yes", "No"), ("Yes", "Yes")]
for (doom, news), color in zip(groups, [COLORS["blue"], COLORS["cyan"], COLORS["violet"], COLORS["pink"]]):
    subset = df[df.doomscroller.eq(doom) & df.consumes_negative_news_content.eq(news)]
    mental_traces.append({"type": "bar", "name": f"Doom {doom} / News {news}",
                          "x": [x[1] for x in mental_cols], "y": [round(float(subset[x[0]].mean()), 2) for x in mental_cols],
                          "marker": {"color": color}, "hovertemplate": "%{x}<br>%{y:.2f}/10<extra>%{fullData.name}</extra>"})
charts["05_mental_health.png"] = {"data": mental_traces, "layout": {"barmode": "group", "height": 460, "margin": {"l": 55, "r": 25, "t": 35, "b": 80}, "yaxis": {"range": [0, 10], "title": "Average score"}, "legend": {"orientation": "h", "y": 1.16}}}

# 06 - protective habits.
habit_defs = [
    ("Phone outside bedroom", df.keeps_phone_in_bedroom.eq("No")),
    ("Night mode", df.uses_night_mode.eq("Yes")),
    ("Reading routine", df.bedtime_routine_type.eq("Reading")),
    ("Meditation / journaling", df.bedtime_routine_type.eq("Meditation/Journaling")),
    ("Recent detox (<=14d)", df.days_since_last_digital_detox.le(14)),
    ("Exercise >=45 min", df.exercise_minutes_per_day.ge(45)),
    ("No fixed routine", df.bedtime_routine_type.eq("No Fixed Routine")),
    ("Social scrolling", df.bedtime_routine_type.eq("Scrolling Social Media")),
]
habit_rows = []
for label, mask in habit_defs:
    subset = df[mask]
    habit_rows.append((label, 100 * subset.sleep_quality_category.eq("Good").mean(), subset.sleep_latency_minutes.mean()))
habit_rows.sort(key=lambda x: x[1])
charts["06_protective_habits.png"] = {
    "data": [
        {"type": "bar", "orientation": "h", "x": [round(x[1], 2) for x in habit_rows], "y": [x[0] for x in habit_rows], "name": "Good sleep %", "marker": {"color": COLORS["mint"]}, "xaxis": "x", "yaxis": "y"},
        {"type": "bar", "orientation": "h", "x": [round(x[2], 2) for x in habit_rows], "y": [x[0] for x in habit_rows], "name": "Latency (min)", "marker": {"color": COLORS["pink"]}, "xaxis": "x2", "yaxis": "y2"},
    ],
    "layout": {"grid": {"rows": 1, "columns": 2, "pattern": "independent", "xgap": .22}, "height": 540,
               "margin": {"l": 150, "r": 25, "t": 45, "b": 50}, "showlegend": False,
               "annotations": [{"text": "Good sleep share", "xref": "paper", "yref": "paper", "x": .2, "y": 1.08, "showarrow": False}, {"text": "Sleep latency", "xref": "paper", "yref": "paper", "x": .8, "y": 1.08, "showarrow": False}]},
}

# 07 - exercise gradient.
exercise_band = pd.cut(df.exercise_minutes_per_day, [-.1, 20, 45, 70, np.inf], labels=["0-20", "21-45", "46-70", "71+"])
exercise = df.assign(exercise_band=exercise_band).groupby("exercise_band", observed=True).agg(
    good=("sleep_quality_category", lambda x: 100 * x.eq("Good").mean()), fatigue=("daytime_fatigue_score", "mean")
).reset_index()
charts["07_exercise_gradient.png"] = {
    "data": [
        {"type": "bar", "name": "Good sleep %", "x": exercise.exercise_band.astype(str).tolist(), "y": exercise.good.round(2).tolist(), "marker": {"color": COLORS["mint"]}},
        {"type": "scatter", "mode": "lines+markers", "name": "Fatigue", "x": exercise.exercise_band.astype(str).tolist(), "y": exercise.fatigue.round(2).tolist(), "yaxis": "y2", "line": {"color": COLORS["violet"], "width": 3}},
    ],
    "layout": {"height": 450, "margin": {"l": 60, "r": 65, "t": 35, "b": 60}, "xaxis": {"title": "Exercise minutes per day"}, "yaxis": {"title": "Good sleep (%)"}, "yaxis2": {"title": "Fatigue (1-10)", "overlaying": "y", "side": "right"}, "legend": {"orientation": "h", "y": 1.12}},
}

# 08 - demographics heatmap + country bars.
demo = df.groupby(["occupation_status", "age_bucket"], observed=True).doomscroller.apply(lambda x: 100 * x.eq("Yes").mean()).unstack()
country = df.groupby("country_region").agg(doom=("doomscroller", lambda x: 100 * x.eq("Yes").mean()), poor=("sleep_quality_category", lambda x: 100 * x.eq("Poor").mean())).sort_values("doom")
charts["08_demographics.png"] = {
    "data": [
        {"type": "heatmap", "x": demo.columns.astype(str).tolist(), "y": demo.index.astype(str).tolist(), "z": demo.round(2).values.tolist(), "colorscale": [[0, "#101F36"], [1, COLORS["violet"]]], "showscale": False, "hovertemplate": "%{y}<br>%{x}<br>%{z:.1f}% doomscrollers<extra></extra>", "xaxis": "x", "yaxis": "y"},
        {"type": "bar", "orientation": "h", "name": "Doomscrolling", "x": country.doom.round(2).tolist(), "y": country.index.tolist(), "marker": {"color": COLORS["blue"]}, "xaxis": "x2", "yaxis": "y2"},
        {"type": "bar", "orientation": "h", "name": "Poor sleep", "x": country.poor.round(2).tolist(), "y": country.index.tolist(), "marker": {"color": COLORS["pink"]}, "xaxis": "x2", "yaxis": "y2"},
    ],
    "layout": {"grid": {"rows": 1, "columns": 2, "pattern": "independent", "xgap": .2}, "barmode": "group", "height": 540,
               "margin": {"l": 130, "r": 30, "t": 50, "b": 60}, "legend": {"orientation": "h", "y": 1.13},
               "annotations": [{"text": "Age x occupation", "xref": "paper", "yref": "paper", "x": .2, "y": 1.08, "showarrow": False}, {"text": "Country rates", "xref": "paper", "yref": "paper", "x": .8, "y": 1.08, "showarrow": False}]},
}

# 09 - exceptions.
heavy_cut = df.bedtime_screen_time_minutes.quantile(.75)
heavy = df[df.doomscroller.eq("Yes") & df.bedtime_screen_time_minutes.ge(heavy_cut)].copy()
heavy["Exception"] = np.where(heavy.sleep_quality_category.eq("Good"), "Good-sleep exception", "Other heavy scrollers")
exc = heavy.groupby("Exception").agg(
    exercise=("exercise_minutes_per_day", "mean"), sleep=("sleep_hours_per_night", "mean"),
    debt=("weekly_sleep_debt_hours", "mean"), latency=("sleep_latency_minutes", "mean"),
    phone_out=("keeps_phone_in_bedroom", lambda x: 100 * x.eq("No").mean()),
    routine=("bedtime_routine_type", lambda x: 100 * x.isin(["Reading", "Meditation/Journaling"]).mean()),
)
z = (exc - exc.mean()) / exc.std(ddof=0)
z[["debt", "latency"]] *= -1
metric_names = ["Exercise", "Sleep hours", "Low debt", "Short latency", "Phone outside", "Restorative routine"]
charts["10_exceptions.png"] = {"data": [
    {"type": "bar", "name": idx, "x": metric_names, "y": row.round(3).tolist(), "marker": {"color": COLORS["mint"] if "Good" in idx else COLORS["pink"]}}
    for idx, row in z.iterrows()
], "layout": {"barmode": "group", "height": 470, "margin": {"l": 55, "r": 25, "t": 40, "b": 100}, "yaxis": {"title": "Standardized advantage"}, "legend": {"orientation": "h", "y": 1.14}}}

# 10 - persona heatmap.
q75 = df.bedtime_screen_time_minutes.quantile(.75)
median_screen = df.bedtime_screen_time_minutes.median()
conditions = [
    df.doomscroller.eq("Yes") & df.bedtime_screen_time_minutes.ge(q75),
    df.consumes_negative_news_content.eq("Yes") & df.anxiety_score.ge(7) & df.stress_score.ge(7),
    df.bedtime_screen_time_minutes.le(median_screen) & df.bedtime_routine_type.isin(["Reading", "Meditation/Journaling"]),
]
df["persona"] = np.select(conditions, ["The Night Scroller", "The Anxious News Seeker", "The Disciplined Sleeper"], default="The Balanced Middle")
persona = df[df.persona.ne("The Balanced Middle")].groupby("persona").agg(
    screen=("bedtime_screen_time_minutes", "mean"), latency=("sleep_latency_minutes", "mean"),
    anxiety=("anxiety_score", "mean"), fatigue=("daytime_fatigue_score", "mean"),
    good=("sleep_quality_category", lambda x: 100 * x.eq("Good").mean()), exercise=("exercise_minutes_per_day", "mean"),
)
normalized = (persona - persona.min()) / (persona.max() - persona.min()).replace(0, 1)
charts["11_personas.png"] = {"data": [{"type": "heatmap", "z": normalized.round(3).values.tolist(),
    "x": ["Bedtime screen", "Latency", "Anxiety", "Fatigue", "Good sleep %", "Exercise"], "y": persona.index.tolist(),
    "text": persona.round(1).astype(str).values.tolist(), "texttemplate": "%{text}", "colorscale": [[0, "#101F36"], [1, COLORS["cyan"]]], "showscale": False,
    "hovertemplate": "%{y}<br>%{x}: %{text}<extra></extra>"}], "layout": {"height": 420, "margin": {"l": 175, "r": 30, "t": 25, "b": 80}}}

# 11 - selected correlation heatmap.
corr_cols = ["bedtime_screen_time_minutes", "doomscroll_sessions_per_night", "sleep_latency_minutes", "number_of_night_wakeups", "sleep_hours_per_night", "weekly_sleep_debt_hours", "anxiety_score", "stress_score", "daytime_fatigue_score", "exercise_minutes_per_day"]
corr_labels = ["Bedtime screen", "Doom sessions", "Latency", "Wakeups", "Sleep hours", "Sleep debt", "Anxiety", "Stress", "Fatigue", "Exercise"]
corr = df[corr_cols].corr()
charts["12_correlation_heatmap.png"] = {"data": [{"type": "heatmap", "x": corr_labels, "y": corr_labels, "z": corr.round(3).values.tolist(),
    "zmin": -1, "zmax": 1, "colorscale": [[0, COLORS["blue"]], [.5, "#101F36"], [1, COLORS["pink"]]],
    "texttemplate": "%{z:.2f}", "hovertemplate": "%{y} x %{x}<br>r=%{z:.3f}<extra></extra>"}],
    "layout": {"height": 610, "margin": {"l": 120, "r": 40, "t": 25, "b": 120}}}

# 12 - feature importance.
importance = pd.read_csv(ROOT / "feature_importance.csv").head(12).sort_values("importance")
charts["13_feature_importance.png"] = {"data": [{"type": "bar", "orientation": "h",
    "x": importance.importance.round(5).tolist(), "y": importance.feature.str.replace("_", " ").str.title().tolist(),
    "error_x": {"type": "data", "array": importance.sd.round(5).tolist(), "visible": True, "color": COLORS["muted"]},
    "marker": {"color": [COLORS["cyan"] if x > 0 else COLORS["muted"] for x in importance.importance]},
    "hovertemplate": "%{y}<br>Importance: %{x:.4f}<extra></extra>"}],
    "layout": {"height": 520, "margin": {"l": 205, "r": 35, "t": 25, "b": 65}, "xaxis": {"title": "Drop in balanced accuracy when shuffled"}}}

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps(charts, separators=(",", ":")), encoding="utf-8")
print(f"Wrote {len(charts)} Plotly chart specifications to {OUTPUT}")
