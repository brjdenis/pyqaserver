import argparse
import datetime
import os
import re
import sys

from flask import redirect, send_from_directory, session
from gevent.pywsgi import WSGIServer
from waitress import serve

from pyqaserver import __version__, app, db, login_app
from pyqaserver.models import db_general
from pyqaserver.modules.pylinac.winston_lutz import wl_bp
from pyqaserver.modules.server.admin import register_admin
from pyqaserver.modules.server.login import AnonymousUser, login_bp
from pyqaserver.modules.server.orthanc import orthanc_bp

# Set version in the site_config module
app.config["QASERVER_VERSION"] = __version__


def check_ip(address):
    # Check that the ip address has the right shape
    regex = r"""^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?):[0-9]+$"""
    if re.search(regex, address):
        return True
    else:
        return False


def initialize_tables():
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"sqlite:///{app.config['GENERAL_DATABASE']}"
    )
    with app.app_context():
        if os.path.exists(app.config["GENERAL_DATABASE"]):
            db.init_app(app)
        else:
            db.init_app(app)
            db.create_all()
            db_general.add_starting_data()


def main():
    # The user defines: IP_address:PORT, path to database, and optional param
    # --dev in order to use the development server
    parser = argparse.ArgumentParser(
        description=(
            "To run pyqaserver you must supply IP address and PORT for "
            "the server and the absolute path to the database folder. "
            "If you add the option '--dev' at the end, you will run "
            "the server in development mode (flask wsgi) . Do not use "
            "this mode for regular use. "
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

    if not check_ip(ip_port):
        print(
            r"Invalid ip:port. Follow this example: \n"
            + r"pyqaserver 127.0.0.1:8080 \path_to_database"
        )
        sys.exit()

    if not os.path.exists(db_path):
        print("Database directory does not exist.")
        sys.exit()

    app.config["DATABASE_DIRECTORY"] = db_path
    app.config["GENERAL_DATABASE"] = os.path.join(
        db_path, app.config["GENERAL_DATABASE_NAME"]
    )

    ip_address, port = args.ip_port.split(":")

    # If run in dev mode, disable loginn
    if args.dev:
        app.config["LOGIN_DISABLED"] = True
        login_app.anonymous_user = AnonymousUser

    login_app.init_app(app)

    # Make session expire after some time
    @app.before_request
    def make_session_permanent():
        session.permanent = True
        app.permanent_session_lifetime = datetime.timedelta(days=1)

    @login_app.user_loader
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
            os.path.join(app.config["FILE_DIR"], "static", "base", "images"),
            "favicon.ico",
            mimetype="image/vnd.microsoft.icon",
        )

    # Register blueprints. Each blueprint corresponds to a module.
    app.register_blueprint(login_bp)
    app.register_blueprint(orthanc_bp)
    app.register_blueprint(wl_bp)

    # Register admin pages
    register_admin()

    # Register listener that hashes input passwords when users are created
    db_general.add_psswd_hasher()

    if args.dev:
        # print(app.url_map)
        app.run(host=ip_address, port=port, debug=True)
    else:
        cert_key = os.path.join(app.config["FILE_DIR"], "cert", "server.key")
        cert_crt = os.path.join(app.config["FILE_DIR"], "cert", "server.crt")

        if os.path.exists(cert_key) and os.path.exists(cert_crt):
            http_server = WSGIServer(
                ("127.0.0.1", 8080), app, keyfile=cert_key, certfile=cert_crt
            )
            print("Running encrypted with a self-signed certificate.")
        else:
            http_server = WSGIServer(("127.0.0.1", 8080), app)
            print("Running unencrypted.")

        http_server.spawn = 4

        http_server.serve_forever()
        # serve(app, host=ip_address, port=port)
