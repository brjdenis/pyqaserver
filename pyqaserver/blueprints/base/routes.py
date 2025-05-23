"""Blueprint for the login page."""

from pathlib import Path

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import (
    AnonymousUserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from pyqaserver.models import db_general

BLUEPRINT_PATH = Path(__file__).parent.resolve()

login_bp = Blueprint(
    "base",
    "base",
    template_folder=BLUEPRINT_PATH / "templates",
    static_folder=BLUEPRINT_PATH / "static",
    url_prefix="/login",
)


@login_bp.route("/", methods=["GET", "POST"])
def login():
    """Login form."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = db_general.User.get_user(username)
        if user is None:
            flash("User not recognized. Try again.", "danger")
        elif user.check_pass(password):
            login_user(user, remember=True)
            return redirect(url_for("base.menu"))
        else:
            flash("The password you entered is incorrect.", "danger")
    return render_template("login.html")


@login_bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    """Logging out a user."""
    logout_user()
    return render_template("login.html")


@login_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Goes to user profile. Used for changing password and other settings."""
    return render_template("profile.html")


@login_bp.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change the user password."""
    if request.method == "POST":
        username = current_user.username
        password = request.form["password"]
        db_general.User.change_pass(username, password)
    logout_user()
    return render_template("login.html")


@login_bp.route("/menu", methods=["GET", "POST"])
@login_required
def menu():
    """Opens the menu page."""
    return render_template("menu_page.html")


class AnonymousUser(AnonymousUserMixin):
    """Used for anon login in development mode."""

    def __init__(self):  # noqa: D107
        self.username = "admin"
        self.display_name = "admin"
