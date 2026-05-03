"""Pylinac winston_lutz module."""

from pathlib import Path

from flask import Blueprint, render_template
from flask_login import login_required
import time

BLUEPRINT_PATH = Path(__file__).parent.resolve()

wl_bp = Blueprint(
    "winston_lutz",
    __name__,
    template_folder=BLUEPRINT_PATH / "templates",
    static_folder=BLUEPRINT_PATH / "static",
    url_prefix="/winston_lutz",
)


@wl_bp.route("/", methods=["GET", "POST"])
@login_required
def winston_lutz():
    
    return render_template("winston_lutz.html")
