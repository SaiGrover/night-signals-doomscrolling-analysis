"""Reword 'synthetic dataset' framing to the self-reported-survey framing the
synopsis mandates, across every copy of the exploratory-analysis notebook.

Leaves legitimate ML uses of 'synthetic' (SMOTE synthetic minority samples)
untouched. Idempotent: re-running makes no further changes once applied.
"""
import json
from pathlib import Path

REPLACEMENTS = [
    ("This is observational and apparently synthetic survey data.",
     "This is an observational, self-reported survey with only partially documented provenance."),
    ("## 3. Synthetic-data sanity check",
     "## 3. Data-provenance sanity check"),
    ("These checks do not prove a dataset is synthetic, but they reveal when conventional inferential language would overstate realism.",
     "These checks do not establish how the file was produced, but they reveal when conventional inferential language would overstate realism."),
    ("**Synthetic-data finding.**", "**Data-provenance finding.**"),
    ("but the balanced target classes and strong engineered structure are consistent with synthetic or simulation-assisted generation;",
     "but the balanced target classes and strong internal structure mean the provenance and sampling cannot be verified from the source;"),
    ("reinforces the synthetic-data warning:", "reinforces the provenance caveat:"),
    ("appear jointly engineered around a common disruption pattern.",
     "appear strongly correlated around a common disruption pattern."),
    ("6. **Synthetic structure limits inference.** Strong engineered correlations,",
     "6. **Provenance limits inference.** Strong correlations,"),
]

TARGETS = [
    Path("notebooks/sleep_doomscrolling_analysis.ipynb"),
    Path("public/methodology/sleep_doomscrolling_analysis.ipynb"),
    Path("../sleep_doomscrolling_analysis.ipynb"),  # root repo copy (best-effort)
]


def apply(path: Path) -> int:
    if not path.exists():
        print(f"skip (missing): {path}")
        return 0
    nb = json.loads(path.read_text(encoding="utf-8"))
    changed = 0
    for cell in nb.get("cells", []):
        src = cell.get("source", [])
        joined = "".join(src) if isinstance(src, list) else src
        new = joined
        for old, repl in REPLACEMENTS:
            if old in new:
                new = new.replace(old, repl)
        if new != joined:
            changed += 1
            # preserve the list-of-lines-with-trailing-newlines shape
            lines = new.splitlines(keepends=True)
            cell["source"] = lines
    if changed:
        path.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{path}: {changed} cell(s) reworded")
    return changed


if __name__ == "__main__":
    for t in TARGETS:
        apply(t)
