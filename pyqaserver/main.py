"""The main module. It is called by __main__.py when run as a package."""

import argparse
import datetime
import re
import sys
from pathlib import Path

from flask import redirect, send_from_directory, session
from gevent.pywsgi import WSGIServer

from pyqaserver import app, db, loginmanager_app
from pyqaserver.blueprints.base.routes import AnonymousUser, login_bp
from pyqaserver.models import db_general

MAIN_PATH = Path(__file__).parent.resolve()


def is_ip_valid(address):
    """Check if the input IP address is valid."""
    regex = r"""^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?):[0-9]+$"""
    return re.search(regex, address)


def initialize_tables():
    """Build SQL tables for settings.

    If sqlite database does not exist, create it. If it does, use it.
    """
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"sqlite:///{app.config['GENERAL_DATABASE']}"
    )
    with app.app_context():
        if Path(app.config["GENERAL_DATABASE"]).exists():
            db.init_app(app)
        else:
            db.init_app(app)
            db.create_all()
            db_general.add_starting_data()


def collect_and_mount_blueprints():
    """Collect non-default blueprints and mount them to app."""
    from pyqaserver.blueprints.admin.admin import register_admin
    from pyqaserver.blueprints.js_fetcher.routes import js_fetcher_bp
    from pyqaserver.blueprints.orthanc.routes import orthanc_bp
    from pyqaserver.blueprints.winstonlutz.routes import wl_bp
    # Register blueprints. Each blueprint corresponds to a module.

    app.register_blueprint(login_bp)
    app.register_blueprint(orthanc_bp)
    app.register_blueprint(wl_bp)

    # Register admin pages
    register_admin()

    # register last
    app.register_blueprint(js_fetcher_bp)


def main():
    """The function is run from __main__.py which is the entry point for the script.

    The user defines: IP_address:PORT, path to database, and optional param
    --dev in order to use the development server
    """
    parser = argparse.ArgumentParser(
        description=(
            "To run pyqaserver you must supply the IP address and PORT for "
            "the server and the absolute path to the database folder. "
            "If you add the option '--dev' at the end, you will run "
            "the server in development mode (flask wsgi). Do not use "
            "this mode for regular use! "
            "An example of regular use:\n\n"
            "python pyqaserver.py 127.0.0.1:8080 C:\\database\n"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "ip_port",
        type=str,
        help="Set the IP address and PORT. For example: 127.0.0.1:8080",
    )
    parser.add_argument(
        "database_path",
        type=str,
        help="Set the path to the internal pyqaserver database folder. "
        r"For example: C:\database",
    )
    parser.add_argument(
        "--dev", action="store_true", help="Run pyqserver in debug mode (flask WSGI)."
    )

    args = parser.parse_args()
    ip_port = args.ip_port
    db_path = args.database_path

    if not is_ip_valid(ip_port):
        print(
            "\nInvalid ip:port. Follow this example: \n\n"
            r"pyqaserver 127.0.0.1:8080 \path_to_database"
            "\n"
        )
        sys.exit()

    if not Path(db_path).exists():
        print("Database directory does not exist.")
        sys.exit()

    app.config["DATABASE_DIRECTORY"] = db_path
    app.config["GENERAL_DATABASE"] = Path(db_path) / app.config["GENERAL_DATABASE_NAME"]

    ip_address, port = args.ip_port.split(":")

    # If run in dev mode, disable login
    if args.dev:
        app.config["LOGIN_DISABLED"] = True
        loginmanager_app.anonymous_user = AnonymousUser

    loginmanager_app.init_app(app)

    # Make session expire after some time
    @app.before_request
    def make_session_permanent():
        session.permanent = True
        app.permanent_session_lifetime = datetime.timedelta(days=1)

    @loginmanager_app.user_loader
    def load_user(user_id):
        # For some reason db.session ... doesn't work.
        return db_general.User.query.get(user_id)

    initialize_tables()

    # Add old routes so that users can use saved urls from their browsers.
    @app.route("/")
    @app.route("/qaserver/")
    @app.route("/qaserver/login/")
    def legacy_route():
        return redirect("/login/")

    # Add favicon
    @app.route("/favicon.ico")
    def favicon():
        return send_from_directory(
            MAIN_PATH / "blueprints" / "base" / "static" / "images",
            "favicon.ico",
            mimetype="image/vnd.microsoft.icon",
        )

    collect_and_mount_blueprints()

    # Register listener that hashes input passwords when users are created
    db_general.add_psswd_hasher()

    if args.dev:
        # print(app.url_map)
        app.config["EXPLAIN_TEMPLATE_LOADING"] = True
        app.run(host=ip_address, port=int(port), debug=True)
    else:
        cert_key = MAIN_PATH / "cert" / "server.key"
        cert_crt = MAIN_PATH / "cert" / "server.crt"

        if Path(cert_key).exists() and Path(cert_crt).exists():
            app.config["SESSION_COOKIE_SECURE"] = True
            http_server = WSGIServer(
                (ip_address, int(port)), app, keyfile=cert_key, certfile=cert_crt
            )
            print("Running encrypted with a self-signed certificate.")
        else:
            http_server = WSGIServer((ip_address, int(port)), app)
            print("Running unencrypted.")

        http_server.spawn = 4

        http_server.serve_forever()
        # serve(app, host=ip_address, port=port)
