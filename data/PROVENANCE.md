# Primary dataset provenance

The primary file is `sleep_doomscrolling_habits.csv`, a 1,000-row self-reported sleep and doomscrolling survey identified in the project synopsis as a Kaggle dataset attributed to Harpartap Singh.

The repository does not currently contain a stable Kaggle URL, dataset revision, license capture, acquisition timestamp, or source checksum from the original download. The file must therefore be treated as provenance-unresolved and should not be described as a verified survey conducted by this project. It is not labeled synthetic in the application because the source has not established that claim.

The canonical local checksum should be regenerated whenever the source file is replaced:

```powershell
Get-FileHash data/sleep_doomscrolling_habits.csv -Algorithm SHA256
```

Current checkout SHA-256: `e441b468e480f913e99a0666e0efe472fe8c1b6660ee96f3cf59982c5773c007`.

All model and descriptive results are conditional on this exact local file. External NHANES and PhysioNet data are downloaded by their respective scripts into the ignored `external/` directory and are analyzed independently.
