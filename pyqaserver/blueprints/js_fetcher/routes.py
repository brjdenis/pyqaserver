"""Blueprint that serves as a fetcher of variables to js scripts."""

from pathlib import Path

from flask import Blueprint, url_for
from flask_login import login_required

BLUEPRINT_PATH = Path(__file__).parent.resolve()

js_fetcher_bp = Blueprint(
    "js_fetcher",
    "js_fetcher",
    template_folder=BLUEPRINT_PATH / "templates",
    static_folder=BLUEPRINT_PATH / "static",
    url_prefix="/js_fetcher",
)


@js_fetcher_bp.route("/fetch_base_variables", methods=["GET", "POST"])
@login_required
def fetch_base_variables():
    pass
