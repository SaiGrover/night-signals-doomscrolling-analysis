# Primary dataset provenance

The primary file is `sleep_doomscrolling_habits.csv`, a 1,000-row public Kaggle dataset attributed to Harpartap Singh. The uploader describes the records as synthetic. This project did not design or conduct a survey or recruit respondents. Rows describe simulated records; estimates cannot be generalized to people.

Source: <https://www.kaggle.com/datasets/harpartapsingh13/sleep-and-doomscrolling-habits-dataset> (uploader: Harpartap Singh). The public Kaggle metadata describes 1,000 synthetic records and says the three sleep-category labels were made roughly balanced. Its public metadata lists version 1, last updated 30 July 2026, and CC0. On 31 October 2026, `python scripts/verify_primary_source.py` downloaded Kaggle version 1 and confirmed its CSV is byte-identical to this checkout (`e441b468e480f913e99a0666e0efe472fe8c1b6660ee96f3cf59982c5773c007`). See `outputs/tables/primary_source_verification.json`. The source still does not disclose the label-generation rule, questionnaire wording, or within-night observation times.

The source file is now tied to Kaggle version 1 by checksum. Its public metadata lists CC0; no questionnaire wording, observation window, or within-night timestamps are supplied. Bedtime availability of predictors cannot be established. See `DATA_DICTIONARY.md`.

The canonical local checksum should be regenerated whenever the source file is replaced:

```powershell
Get-FileHash data/sleep_doomscrolling_habits.csv -Algorithm SHA256
```

Current checkout SHA-256: `e441b468e480f913e99a0666e0efe472fe8c1b6660ee96f3cf59982c5773c007`.

All model and descriptive results are conditional on this exact local file. External NHANES and PhysioNet data are downloaded by their respective scripts into the ignored `external/` directory and are analyzed independently.
