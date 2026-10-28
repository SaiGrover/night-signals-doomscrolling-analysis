# Primary dataset provenance

The primary file is `sleep_doomscrolling_habits.csv`, a 1,000-row self-reported sleep and doomscrolling survey identified in the project synopsis as the Kaggle dataset attributed to Harpartap Singh.

Source: <https://www.kaggle.com/datasets/harpartapsingh13/sleep-and-doomscrolling-habitsdataset> (Kaggle dataset author: Harpartap Singh). The project synopsis identifies it as a public Kaggle source for academic, non-commercial analysis with attribution. Access date for this checkout: 2026-10-28.

The original Kaggle revision and collection methodology are not captured in the downloaded file, and the dataset card/license should be rechecked before redistribution. The file must not be described as a survey conducted by this project. It is not labeled synthetic because the source does not establish that claim.

The canonical local checksum should be regenerated whenever the source file is replaced:

```powershell
Get-FileHash data/sleep_doomscrolling_habits.csv -Algorithm SHA256
```

Current checkout SHA-256: `e441b468e480f913e99a0666e0efe472fe8c1b6660ee96f3cf59982c5773c007`.

All model and descriptive results are conditional on this exact local file. External NHANES and PhysioNet data are downloaded by their respective scripts into the ignored `external/` directory and are analyzed independently.
