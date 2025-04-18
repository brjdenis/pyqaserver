"""Here certain global variables and object are initialized."""

import base64
import datetime
import os

from flask import Flask, make_response
from flask import abort as abort_flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from pyqaserver import site_config
from pyqaserver.version import __version__

cur_dir = os.path.realpath(os.path.dirname(__file__))
site_config.FILE_DIR = cur_dir

app = Flask(__name__)
app.secret_key = base64.b64encode(os.urandom(12).hex().encode())
app.config.from_object(site_config)
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
# app.config['SESSION_COOKIE_SECURE'] = True
app.config["REMEMBER_COOKIE_DURATION"] = datetime.timedelta(days=1)
app.config["LOGIN_DISABLED"] = False

login_app = LoginManager(app)
login_app.session_protection = "strong"
login_app.login_view = "/login"  # Redirect to login at non-auth requst # type: ignore

db = SQLAlchemy()


def abort_text(status_code, description):
    response = make_response(
        f"Status code: {status_code}.\n\nDescription: {description}"
    )
    response.status_code = status_code
    abort_flask(response)
