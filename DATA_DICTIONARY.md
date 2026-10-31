# Primary file data dictionary and timing limits

Source: [public Kaggle dataset](https://www.kaggle.com/datasets/harpartapsingh13/sleep-and-doomscrolling-habits-dataset), described by its uploader as synthetic. The CSV supplies column names and values, but no original questionnaire, item wording, collection time, recall period, or generator specification. The descriptions below are interpretations of names and observed value ranges, **not verified survey definitions**.

| Fields | Apparent unit or coding | Timing evidence |
| --- | --- | --- |
| `respondent_id` | Record identifier | Unknown; exclude from models |
| `age`, `gender`, `occupation_status`, `country_region` | Years; categories | Static/context; unverified |
| `primary_device` | Category | Unknown |
| `total_daily_screen_time_hours` | Hours/day, by name | Recall period unknown |
| `bedtime_screen_time_minutes`, `doomscroll_sessions_per_night`, `avg_doomscroll_session_minutes`, `phone_checks_per_night` | Minutes, counts, minutes, counts | No timestamp; phone checks may occur after sleep onset |
| `doomscroller`, `consumes_negative_news_content`, `uses_night_mode`, `keeps_phone_in_bedroom`, `uses_sleep_tracking_app` | Yes/No labels | No observation timestamp; self-label may encode target rule |
| `number_of_news_apps_used`, `days_since_last_digital_detox` | Count; days | Unknown |
| `bedtime_routine_type` | Category | Unknown |
| `exercise_minutes_per_day` | Minutes/day, by name | Unknown recall period |
| `anxiety_score`, `stress_score` | Unspecified numeric score | Scale wording and timing unknown |
| `sleep_hours_per_night`, `sleep_latency_minutes`, `number_of_night_wakeups`, `weekly_sleep_debt_hours`, `daytime_fatigue_score`, `sleep_quality_score` | Hours, minutes, count, hours/week, unspecified score, 1–5 score | Sleep outcomes or possible downstream measures; excluded from production predictors |
| `sleep_quality_category` | Good/Fair/Poor | Target label; derivation undocumented |

Run `python scripts/audit_research_claims.py` to inspect the category/score disagreement. Missing item wording means no predictor can be asserted to be available at an actual bedtime decision point. `phone_checks_per_night` and the `doomscroller` self-label warrant ablation before any prospective interpretation.

Derived `habit_indicator_count` is a count of coded routine indicators, not a validated protective score. The original file provides neither the source questionnaire nor a label-generation algorithm, so those definitions cannot be reconstructed from these values.
