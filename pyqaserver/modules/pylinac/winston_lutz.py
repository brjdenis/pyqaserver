import os

from flask import Blueprint, render_template
from flask_login import login_required

from pyqaserver import site_config

cur_dir = site_config.FILE_DIR

wl_bp = Blueprint(
    "winston_lutz",
    __name__,
    template_folder=os.path.join(cur_dir, "templates", "modules", "winston_lutz"),
    static_folder=os.path.join(cur_dir, "static", "base"),
    url_prefix="/winston_lutz",
)


@wl_bp.route("/", methods=["GET", "POST"])
@login_required
def winston_lutz():
    return render_template("winston_lutz.html")
