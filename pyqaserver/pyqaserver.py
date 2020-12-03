import sys
import os
import re
import sqlite3 as sql
import random
import configparser

parent_module = sys.modules['.'.join(__name__.split('.')[:-1]) or '__main__']
if __name__ == '__main__' or parent_module.__name__ == '__main__':
    # sys.path.append(os.path.abspath(os.path.realpath("python_packages")))
    import config
    import RestToolbox_modified as RestToolbox
    from general_settings_database import create_general_settings_database
    from trends_database import create_trends_database
    from general_functions import check_encrypted_password, get_one_user, \
        check_is_admin
    from create_dynalog_database import create_dynalog_database
    from python_packages.bottlepy.bottle import run as bottle_run
    from administration import admin_app
    from winstonlutz_module import wl_app
    from starshot_module import ss_app
    from picketfence_module import pf_app
    from planarimaging_module import plimg_app
    from catphan_module import ctp_app
    from dynalog_module import dyn_app
    from flatsym_module import flatsym_app
    from vmat_module import vmat_app
    from fieldsize_module import fieldsize_app
    from imagereview_module import imgreview_app
    from fieldrot_module import fieldrot_app
    from general_routes import app_general
    from trends import trends_app
    from version import __version__
    from python_packages.bottlepy.bottle import Bottle, redirect, \
        TEMPLATE_PATH, template, response, request
else:
    from . import config
    from . import RestToolbox_modified as RestToolbox
    from .general_settings_database import create_general_settings_database
    from .trends_database import create_trends_database
    from .general_functions import check_encrypted_password, get_one_user, \
        check_is_admin
    from .create_dynalog_database import create_dynalog_database
    from .python_packages.bottlepy.bottle import run as bottle_run
    from .administration import admin_app
    from .winstonlutz_module import wl_app
    from .starshot_module import ss_app
    from .picketfence_module import pf_app
    from .planarimaging_module import plimg_app
    from .catphan_module import ctp_app
    from .dynalog_module import dyn_app
    from .flatsym_module import flatsym_app
    from .vmat_module import vmat_app
    from .fieldsize_module import fieldsize_app
    from .imagereview_module import imgreview_app
    from .fieldrot_module import fieldrot_app
    from .general_routes import app_general
    from .trends import trends_app
    from .version import __version__
    from .python_packages.bottlepy.bottle import Bottle, redirect, \
        TEMPLATE_PATH, template, response, request

# Set version in the config module
config.QASERVER_VERSION = __version__

# Path to Bottle templates
CUR_DIR = os.path.realpath(os.path.dirname(__file__))
TEMPLATE_PATH.insert(0, os.path.join(CUR_DIR, 'views'))


def check_ip(ip):
    # pass the regular expression
    # and the string in search() method
    regex = '''^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?):[0-9]+$'''
    if re.search(regex, ip):
        return True
    else:
        return False


def check_database(path):
    return os.path.exists(path)


def create_dynalog_config_ini(path):
    config_object = configparser.ConfigParser()
    config_object.optionxform = str
    config_object["Dynalog"] = {
        "TOLERANCE_DTA": "1",
        "TOLERANCE_DD": "1",
        "THRESHOLD": "0.2",
        "RESOLUTION": "1",
        "EXCLUDE_BEAM_OFF": "True",
        "DYNALOG_REPOSITORIES": "",
        "REPOSITORIES_LABELS": "",
        "SEND_EMAIL": "False",
        "SMTP_SERVER": "",
        "SMTP_PORT": "",
        "SEND_FROM_USER": "",
        "SEND_FROM_PASSWORD": "",
        "SEND_TO": ""
    }
    with open(path, 'w') as conf:
        config_object.write(conf)


def create_dynalog_send_post_request_file(path):
    with open(path, 'w', newline='\n') as the_file:
        the_file.write(
            "import requests\n"
            "http = 'http://localhost/dynalog_start_batch_analysis'\n"
            "r = requests.post(http, timeout=1)\n"
            "print(r.text)\n"
        )


def get_orthanc_settings(general_database):
    conn = sql.connect(general_database)
    conn.row_factory = sql.Row
    curs = conn.cursor()
    curs.execute("SELECT IP, Port, User, Password FROM Orthanc WHERE ROWID=1")
    data = curs.fetchone()
    curs.close()
    conn.close()
    return data


def get_institution_settings(general_database):
    conn = sql.connect(general_database)
    conn.row_factory = sql.Row
    curs = conn.cursor()
    curs.execute("SELECT Name FROM Institution WHERE ROWID=1")
    data = curs.fetchone()
    curs.close()
    conn.close()
    return data


def main():
    # This function acts as a console script entry-point.

    if len(sys.argv) != 3 or not check_ip(sys.argv[1]):
        print(
            "Invalid ip:port. Follow this example: \n"
            "pyqaserver 127.0.0.1:8080 \path_to_database"
        )
        sys.exit()

    if not check_database(sys.argv[2]):
        print("Path to database directory does not exist.")
        sys.exit()

    # Redefine folder path in config.py
    path = sys.argv[2]
    config.WORKING_DIRECTORY = path

    # Create new general_settings database.
    config.GENERAL_DATABASE = os.path.join(path, config.GENERAL_DATABASE_NAME)
    if not os.path.exists(config.GENERAL_DATABASE):
        create_general_settings_database(config.GENERAL_DATABASE)
        print("Created {}".format(config.GENERAL_DATABASE))
    else:
        print("Using {}".format(config.GENERAL_DATABASE))

    # Create new trends database.
    config.TRENDS_DATABASE = os.path.join(path, config.TRENDS_DATABASE_NAME)
    if not os.path.exists(config.TRENDS_DATABASE):
        create_trends_database(config.TRENDS_DATABASE)
        print("Created {}".format(config.TRENDS_DATABASE))
    else:
        print("Using {}".format(config.TRENDS_DATABASE))

    # Set Orthanc ip address and credentials:
    orthanc_settings = get_orthanc_settings(config.GENERAL_DATABASE)
    config.ORTHANC_IP = orthanc_settings["IP"]
    config.ORTHANC_PORT = orthanc_settings["Port"]
    config.USERNAME_ORTHANC = orthanc_settings["User"]
    config.PASSWORD_ORTHANC = orthanc_settings["Password"]
    config.ORTHANC_URL = "http://{}:{}".format(
        str(config.ORTHANC_IP), str(config.ORTHANC_PORT)
    )
    RestToolbox.SetCredentials(config.USERNAME_ORTHANC, config.PASSWORD_ORTHANC)

    # Set institution name (not used a lot):
    institution_setttings = get_institution_settings(config.GENERAL_DATABASE)
    config.INSTITUTION = institution_setttings["Name"]

    ###########################################################################
    # Create new reference images folder
    config.REFERENCE_IMAGES_FOLDER = os.path.join(path, config.REFERENCE_IMAGES_FOLDER_NAME)
    if os.path.isdir(config.REFERENCE_IMAGES_FOLDER):
        print("Using {}".format(config.REFERENCE_IMAGES_FOLDER))
    else:
        os.makedirs(config.REFERENCE_IMAGES_FOLDER)
        print("Created {}".format(config.REFERENCE_IMAGES_FOLDER))

    ###########################################################################
    # Create dynalog folders and files
    dynpath = os.path.join(path, config.DYNALOG_FOLDER_NAME)
    config.DYNALOG_FOLDER = dynpath
    config.DYNALOG_DATABASE = os.path.join(dynpath, config.DYNALOG_DATABASE_NAME)
    config.DYNALOG_CONFIG = os.path.join(dynpath, config.DYNALOG_CONFIG_NAME)
    config.DYNALOG_ARCHIVE = os.path.join(dynpath, config.DYNALOG_ARCHIVE_FOLDER_NAME)
    config.DYNALOG_FAILED = os.path.join(dynpath, config.DYNALOG_FAILED_FOLDER_NAME)
    config.DYNALOG_SEND_POST = os.path.join(dynpath, config.DYNALOG_SEND_POST_NAME)

    if os.path.isdir(dynpath):
        print("Using {}".format(dynpath))

        # Create config.ini
        if not os.path.exists(config.DYNALOG_CONFIG):
            create_dynalog_config_ini(config.DYNALOG_CONFIG)
            print("Created {}".format(config.DYNALOG_CONFIG))
        else:
            print("Using {}".format(config.DYNALOG_CONFIG))

        # Create dynalog_send_post_request.py
        if not os.path.exists(config.DYNALOG_SEND_POST):
            create_dynalog_send_post_request_file(config.DYNALOG_SEND_POST)
            print("Created {}".format(config.DYNALOG_SEND_POST))
        else:
            print("Using {}".format(config.DYNALOG_SEND_POST))

        # Create database.db
        if not os.path.exists(config.DYNALOG_DATABASE):
            create_dynalog_database(config.DYNALOG_DATABASE)
            print("Created {}".format(config.DYNALOG_DATABASE))
        else:
            print("Using {}".format(config.DYNALOG_DATABASE))

        # Create ARCHIVE directory
        if not os.path.isdir(config.DYNALOG_ARCHIVE):
            os.makedirs(config.DYNALOG_ARCHIVE)
            print("Created {}".format(config.DYNALOG_ARCHIVE))
        else:
            print("Using {}".format(config.DYNALOG_ARCHIVE))

        # Create dynalog_failed directory
        if not os.path.isdir(config.DYNALOG_FAILED):
            os.makedirs(config.DYNALOG_FAILED)
            print("Created {}".format(config.DYNALOG_FAILED))
        else:
            print("Using {}".format(config.DYNALOG_FAILED))
    else:
        os.makedirs(dynpath)
        os.makedirs(config.DYNALOG_ARCHIVE)
        os.makedirs(config.DYNALOG_FAILED)
        create_dynalog_config_ini(config.DYNALOG_CONFIG)
        create_dynalog_send_post_request_file(config.DYNALOG_SEND_POST)
        create_dynalog_database(config.DYNALOG_DATABASE)
        print("Created {}".format(dynpath))
        print("Created {}".format(config.DYNALOG_CONFIG))
        print("Created {}".format(config.DYNALOG_SEND_POST))
        print("Created {}".format(config.DYNALOG_DATABASE))
        print("Created {}".format(config.DYNALOG_ARCHIVE))
        print("Created {}".format(config.DYNALOG_FAILED))

    ###########################################################################
    # Create temp directories
    temp_path = os.path.join(path, config.TEMP_DIRECTORY_NAME)
    config.TEMP_DIRECTORY = temp_path
    config.TEMP_DCM_FOLDER = os.path.join(temp_path, config.TEMP_DCM_FOLDER_NAME)
    config.TEMP_NONDCM_FOLDER = os.path.join(temp_path, config.TEMP_NONDCM_FOLDER_NAME)
    config.TEMP_DYNALOG_FOLDER = os.path.join(temp_path, config.TEMP_DYNALOG_FOLDER_NAME)
    config.PDF_REPORT_FOLDER = os.path.join(temp_path, config.PDF_REPORT_FOLDER_NAME)

    if os.path.isdir(temp_path):
        # Create DCM temp directory
        if not os.path.isdir(config.TEMP_DCM_FOLDER):
            os.makedirs(config.TEMP_DCM_FOLDER)
            print("Created {}".format(config.TEMP_DCM_FOLDER))
        else:
            print("Using {}".format(config.TEMP_DCM_FOLDER))

        # Create NONDCM temp directory
        if not os.path.isdir(config.TEMP_NONDCM_FOLDER):
            os.makedirs(config.TEMP_NONDCM_FOLDER)
            print("Created {}".format(config.TEMP_NONDCM_FOLDER))
        else:
            print("Using {}".format(config.TEMP_NONDCM_FOLDER))

        # Create PDF temp directory
        if not os.path.isdir(config.PDF_REPORT_FOLDER):
            os.makedirs(config.PDF_REPORT_FOLDER)
            print("Created {}".format(config.PDF_REPORT_FOLDER))
        else:
            print("Using {}".format(config.PDF_REPORT_FOLDER))

        # Create DYNALOG temp directory
        if not os.path.isdir(config.TEMP_DYNALOG_FOLDER):
            os.makedirs(config.TEMP_DYNALOG_FOLDER)
            print("Created {}".format(config.TEMP_DYNALOG_FOLDER))
        else:
            print("Using {}".format(config.TEMP_DYNALOG_FOLDER))
    else:
        os.makedirs(config.TEMP_DCM_FOLDER)
        os.makedirs(config.TEMP_NONDCM_FOLDER)
        os.makedirs(config.TEMP_DYNALOG_FOLDER)
        os.makedirs(config.PDF_REPORT_FOLDER)
        print("Created {}".format(config.TEMP_DCM_FOLDER))
        print("Created {}".format(config.TEMP_NONDCM_FOLDER))
        print("Created {}".format(config.TEMP_DYNALOG_FOLDER))
        print("Created {}".format(config.PDF_REPORT_FOLDER))

    print("\n")

    # Here starts the bottle app
    app = Bottle()

    @app.error(500)
    def custom500(error):
        return template(
            "error_template.tpl",
            error_message="Cause unknown."
        )

    @app.route('')
    @app.route('/')
    @app.route('/qaserver')  # legacy
    @app.route('/qaserver/')  # legacy
    @app.route('/qaserver/login')  # legacy
    def redirect_to_login():
        redirect("/login")

    @app.route("/login")
    def login_form():
        images = []
        for f in os.listdir(os.path.join(CUR_DIR, "static", "images")):
            if f.endswith('.png'):
                images.append(os.path.join("images", f))

        if images:
            image = random.choice(images)
        else:
            image = "blank"

        return template(
            "login.tpl",
            institution=config.INSTITUTION,
            image=image
        )

    @app.route('/login_check_credentials', method='POST')
    def login_check_credentials():
        username = request.forms.username
        password = request.forms.password
        user_list = get_one_user(username)
        if user_list is None:
            return "User not recognized!"
        else:
            if not check_encrypted_password(password, user_list["Password"]):
                return "Wrong password!"
            else:
                return "Success!"

    @app.route('/login', method='POST')
    def login_submit():
        username = request.forms.username
        password = request.forms.password
        user_list = get_one_user(username)
        if user_list is None:
            return template(
                "error_template.tpl",
                error_message="User not recognized."
            )
        else:
            if not check_encrypted_password(password, user_list["Password"]):
                return template(
                    "error_template.tpl",
                    error_message="Wrong password."
                )
            else:
                response.set_cookie(
                    "account", username,
                    secret=config.SECRET_KEY,
                    samesite="lax"
                )
                return template(
                    "menu_page.tpl",
                    institution=config.INSTITUTION,
                    orthanc_url=config.ORTHANC_URL,
                    qaserver_version=config.QASERVER_VERSION,
                    displayname=user_list["DisplayName"],
                    is_admin=check_is_admin(username)
                )

    # Merge apps
    app.merge(app_general)
    app.merge(wl_app)
    app.merge(ss_app)
    app.merge(pf_app)
    app.merge(plimg_app)
    app.merge(ctp_app)
    app.merge(dyn_app)
    app.merge(flatsym_app)
    app.merge(vmat_app)
    app.merge(fieldsize_app)
    app.merge(imgreview_app)
    app.merge(fieldrot_app)
    app.merge(admin_app)
    app.merge(trends_app)

    ip, port = sys.argv[1].split(":")

    bottle_run(
        app=app,
        server="waitress",
        host=ip,
        port=port,
        reloader=False,
        debug=False
    )


if __name__ == '__main__':
    main()
