"""Mark the historical analysis notebook and retract its unsupported habit claims."""
from pathlib import Path
import nbformat

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "notebooks/sleep_doomscrolling_analysis.ipynb"
WARNING = (
    "# Historical analysis - superseded claims\n\n"
    "This notebook documents an earlier exploratory workflow on a public Kaggle file "
    "described by its uploader as synthetic. It is not a survey conducted by this project. "
    "Its three-class model uses sleep outcomes and is not the current binary model. "
    "The routine and night-mode protective conclusions in earlier versions were contradicted "
    "by the saved table and are retracted. See RESEARCH_INTEGRITY.md and the regenerated PDF "
    "for current interpretation. Historical cell outputs are retained as an audit trail."
)


def main() -> None:
    notebook = nbformat.read(PATH, as_version=4)
    if notebook.cells and notebook.cells[0].cell_type == "markdown" and notebook.cells[0].source.startswith("# Historical analysis - superseded claims"):
        notebook.cells[0].source = WARNING
    else:
        notebook.cells.insert(0, nbformat.v4.new_markdown_cell(WARNING))
    for cell in notebook.cells[1:]:
        if cell.cell_type != "markdown":
            continue
        cell.source = cell.source.replace(
            "Reading and meditation/journaling routines stand out more consistently than night mode alone",
            "Reading and meditation/journaling do not establish a protective effect; the unadjusted table contradicts the earlier interpretation",
        ).replace(
            "Reading, meditation/journaling, keeping the phone outside the bedroom, and exercise align with better sleep; night mode alone is comparatively weak.",
            "The earlier protective interpretation is retracted. Routine groups are confounded, and no prospective protective effect is established.",
        )
    nbformat.write(notebook, PATH)
    print(PATH)


if __name__ == "__main__":
    main()
