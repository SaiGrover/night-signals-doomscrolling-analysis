# Primary dataset provenance

The primary file is `sleep_doomscrolling_habits.csv`, a 1,000-row public Kaggle dataset attributed to Harpartap Singh. The uploader describes the records as synthetic. This project did not design or conduct a survey or recruit respondents. Rows describe simulated records; estimates cannot be generalized to people.

Source: <https://www.kaggle.com/datasets/harpartapsingh13/sleep-and-doomscrolling-habits-dataset> (uploader: Harpartap Singh). The source description calls this 1,000 synthetic records. The exact source revision and item-generation mechanism are not recorded in the CSV.

The original Kaggle revision is not captured in the downloaded file. Recheck the source license before redistribution. No questionnaire wording, observation window, or within-night timestamps are supplied; bedtime availability of predictors cannot be established. See `DATA_DICTIONARY.md`.

The canonical local checksum should be regenerated whenever the source file is replaced:

```powershell
Get-FileHash data/sleep_doomscrolling_habits.csv -Algorithm SHA256
```

Current checkout SHA-256: `e441b468e480f913e99a0666e0efe472fe8c1b6660ee96f3cf59982c5773c007`.

All model and descriptive results are conditional on this exact local file. External NHANES and PhysioNet data are downloaded by their respective scripts into the ignored `external/` directory and are analyzed independently.
