from pathlib import Path

from streamlit.testing.v1 import AppTest

ENTRYPOINT = Path(__file__).resolve().parents[1] / "streamlit_app.py"


def test_entrypoint_renders_without_exception():
    app = AppTest.from_file(ENTRYPOINT, default_timeout=30).run()
    assert not app.exception
    assert app.html
    assert any("Night" in item.value and "Signals" in item.value for item in app.html)


def test_all_registered_pages_render_without_exception():
    pages = [
        "app_pages/landing.py",
        "app_pages/overview.py",
        "app_pages/data_audit.py",
        "app_pages/associations.py",
        "app_pages/resilience.py",
        "app_pages/modeling.py",
        "app_pages/nhanes.py",
        "app_pages/physionet.py",
        "app_pages/workflow.py",
        "app_pages/notebooks.py",
        "app_pages/downloads.py",
    ]
    for page in pages:
        app = AppTest.from_file(ENTRYPOINT, default_timeout=30).run()
        app.switch_page(page).run()
        assert not app.exception, page


def test_modeling_form_produces_a_probability():
    app = AppTest.from_file(ENTRYPOINT, default_timeout=30).run()
    app.switch_page("app_pages/modeling.py").run()
    app.form_submit_button[0].click().run()
    assert not app.exception
    assert any("Estimated Poor-label probability" in metric.label for metric in app.metric)
