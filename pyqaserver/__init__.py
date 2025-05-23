"""Here certain global variables and object are initialized."""

import base64
import datetime
import os
from pathlib import Path

from flask import Flask, make_response
from flask import abort as abort_flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from pyqaserver import site_config
from pyqaserver._version import __version__

app = Flask(__name__)
app.secret_key = base64.b64encode(os.urandom(12).hex().encode())

app.config.from_object(site_config)
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["REMEMBER_COOKIE_DURATION"] = datetime.timedelta(days=1)
app.config["LOGIN_DISABLED"] = False

loginmanager_app = LoginManager(app)
loginmanager_app.session_protection = "strong"
# Redirect to login at non-auth request
loginmanager_app.login_view = "/login"

db = SQLAlchemy()

# Set version in the site_config module
app.config["QASERVER_VERSION"] = __version__

# Set the path to the folder where server is running
MAIN_PATH = Path(__file__).parent.resolve()
app.config["MAIN_PATH"] = MAIN_PATH


def abort_text(status_code, description):
    response = make_response(
        f"Status code: {status_code}.\n\nDescription: {description}"
    )
    response.status_code = status_code
    abort_flask(response)
