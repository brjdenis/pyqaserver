import sys
import os
import re
import sqlite3 as sql
import random
import configparser

parent_module = sys.modules['.'.join(__name__.split('.')[:-1]) or '__main__']
if __name__ == '__main__' or parent_module.__name__ == '__main__':
    #sys.path.append(os.path.abspath(os.path.realpath("python_packages")))
    import config
    import RestToolbox_modified as RestToolbox
    import general_settings_database
    import trends_database
    import general_functions
    import create_dynalog_database
    from python_packages.bottlepy.bottle import Bottle, redirect, TEMPLATE_PATH, template, response, request
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

else:
    from . import config
    from . import RestToolbox_modified as RestToolbox
    from . import general_settings_database
    from . import trends_database
    from . import general_functions
    from . import create_dynalog_database
    from .python_packages.bottlepy.bottle import Bottle, redirect, TEMPLATE_PATH, template, response, request
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

# Set version in the config module
config.QASERVER_VERSION = __version__

CUR_DIR = os.path.realpath(os.path.dirname(__file__))

PLWEB_FOLDER = config.PLWEB_FOLDER

# Path to Bottle templates
TEMPLATE_PATH.insert(0, os.path.join(CUR_DIR, 'views'))

def check_ip(ip):  
    # pass the regular expression 
    # and the string in search() method 
    regex = '''^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?):[0-9]+$'''
    if(re.search(regex, ip)):  
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
        the_file.write("import requests\n"
                       "r = requests.post('http://localhost/dynalog_start_batch_analysis', timeout=1)\n"
                       "print(r.text)\n")

def main():
    # This function exists to act as a console script entry-point.
    # Get IP address and port:
    if len(sys.argv) != 3:
        print("Missing IP and path to database folder. To define them follow this example:\n python start.py 127.0.0.1:80")
        sys.exit()
    # If IP/port not valid strings
    if not check_ip(sys.argv[1]):
        print("IP address and port not valid. To define them follow this example:\n python start.py 127.0.0.1:80")
        sys.exit()
    # If directory does not exist:
    if not check_database(sys.argv[2]):
        print("Path to database does not exist. To define the path follow this example:\n"
              " python start.py 127.0.0.1:80 C:\database_folder")
        sys.exit()
    
    # Define ip and port in config.py
    ip, port = sys.argv[1].split(":")
    
    # Redefine folder path in config.py
    path = sys.argv[2]
    config.WORKING_DIRECTORY = path
    
    def get_orthanc_settings(general_database):
        conn = sql.connect(general_database)
        curs = conn.cursor()
        curs.execute("SELECT IP, Port, User, Password FROM Orthanc WHERE ROWID=1")
        data = curs.fetchone()
        curs.close()
        conn.close()
        return data
    
    def get_institution_settings(general_database):
        conn = sql.connect(general_database)
        curs = conn.cursor()
        curs.execute("SELECT Name FROM Institution WHERE ROWID=1")
        data = curs.fetchone()
        curs.close()
        conn.close()
        return data
    
    # Check if database exists in the passed in folder. Otherwise create new db.
    if os.path.exists(path):
        config.GENERAL_DATABASE = os.path.join(path, config.GENERAL_DATABASE_NAME)
        if not os.path.exists(config.GENERAL_DATABASE):
            general_settings_database.create_general_settings_database(config.GENERAL_DATABASE)
            print("Created {}".format(config.GENERAL_DATABASE))
        else:
            print("Using {}".format(config.GENERAL_DATABASE))
        
        config.TRENDS_DATABASE = os.path.join(path, config.TRENDS_DATABASE_NAME)
        if not os.path.exists(config.TRENDS_DATABASE):
            trends_database.create_trends_database(config.TRENDS_DATABASE)
            print("Created {}".format(config.TRENDS_DATABASE))
        else:
            print("Using {}".format(config.TRENDS_DATABASE))

        # If database_folder_path exists redefine variables:
        config.ORTHANC_IP, config.ORTHANC_PORT, config.USERNAME_ORTHANC, config.PASSWORD_ORTHANC = get_orthanc_settings(config.GENERAL_DATABASE)
        config.ORTHANC_URL = "http://"+str(config.ORTHANC_IP) + ":" + str(config.ORTHANC_PORT)
        RestToolbox.SetCredentials(config.USERNAME_ORTHANC, config.PASSWORD_ORTHANC)
        
        # Set string for the header of HTML pages:
        config.INSTITUTION = get_institution_settings(config.GENERAL_DATABASE)[0]
        
        #####################################################################
        # Check if reference image folder exists. Otherwise create one
        if os.path.isdir(os.path.join(path, config.REFERENCE_IMAGES_FOLDER)):
            print("Using {}".format(os.path.join(path, config.REFERENCE_IMAGES_FOLDER)))
            image_list = general_functions.get_referenceimages_planarimaging()  # Referenced images in sql
            image_list += general_functions.get_referenceimages_catphan()  # Referenced images in sql
            image_list = [i[4] for i in image_list]
            for i in image_list:
                if not os.path.exists(os.path.join(config.WORKING_DIRECTORY, config.REFERENCE_IMAGES_FOLDER, i)):
                    print("Warning: not all images referenced by the sql database "
                          "are contained in the reference image folder.")
                    break
        else:
            # Now create the folder
            try:
                os.makedirs(os.path.join(path, config.REFERENCE_IMAGES_FOLDER))
                print("Created {}".format(os.path.join(path, config.REFERENCE_IMAGES_FOLDER)))
            except:
                print("Could not create the reference_images directory!\n")
        
        ############################################################################
        # Check if dynalog folder and config file exist. If not, create them.
        config.DYNALOG_FOLDER = os.path.join(path, config.DYNALOG_FOLDER_NAME)
        config.DYNALOG_DATABASE = os.path.join(path, config.DYNALOG_FOLDER_NAME, config.DYNALOG_DATABASE_NAME)
        config.DYNALOG_CONFIG = os.path.join(path, config.DYNALOG_FOLDER_NAME, config.DYNALOG_CONFIG_NAME)
        config.DYNALOG_ARCHIVE = os.path.join(path, config.DYNALOG_FOLDER_NAME, config.DYNALOG_ARCHIVE_FOLDER_NAME)
        config.DYNALOG_FAILED = os.path.join(path, config.DYNALOG_FOLDER_NAME, config.DYNALOG_FAILED_FOLDER_NAME)
        config.DYNALOG_SEND_POST = os.path.join(path, config.DYNALOG_FOLDER_NAME, config.DYNALOG_SEND_POST_NAME)

        if os.path.isdir(os.path.join(path, config.DYNALOG_FOLDER_NAME)):
            print("Using {}".format(os.path.join(path, config.DYNALOG_FOLDER_NAME)))
            # Check for config.ini
            if not os.path.exists(config.DYNALOG_CONFIG):
                create_dynalog_config_ini(config.DYNALOG_CONFIG)
                print("Created {}".format(config.DYNALOG_CONFIG))
            else:
                print("Using {}".format(config.DYNALOG_CONFIG))
            
            # Check for dynalog_send_post_request.py
            if not os.path.exists(config.DYNALOG_SEND_POST):
                create_dynalog_send_post_request_file(config.DYNALOG_SEND_POST)
                print("Created {}".format(config.DYNALOG_SEND_POST))
            else:
                print("Using {}".format(config.DYNALOG_SEND_POST))
            
            # Check for database.db
            if not os.path.exists(config.DYNALOG_DATABASE):
                create_dynalog_database.create_dynalog_database(config.DYNALOG_DATABASE)
                print("Created {}".format(config.DYNALOG_DATABASE))
            else:
                print("Using {}".format(config.DYNALOG_DATABASE))
            
            # Check if ARCHIVE directory exists
            if not os.path.isdir(config.DYNALOG_ARCHIVE):
                try:
                    os.makedirs(config.DYNALOG_ARCHIVE) 
                    print("Created {}".format(config.DYNALOG_ARCHIVE))
                except:
                    print("Could not create the archive zip directory!\n")
            else:
                print("Using {}".format(config.DYNALOG_ARCHIVE))
            
            # Check if dynalog_failed directory exists
            if not os.path.isdir(config.DYNALOG_FAILED):
                try:
                    os.makedirs(config.DYNALOG_FAILED) 
                    print("Created {}".format(config.DYNALOG_FAILED))
                except:
                    print("Could not create dynalogs_with_errors directory!\n")
            else:
                print("Using {}".format(config.DYNALOG_FAILED))
        else:
            try:
                os.makedirs(os.path.join(path, config.DYNALOG_FOLDER_NAME)) 
                os.makedirs(config.DYNALOG_ARCHIVE) 
                os.makedirs(config.DYNALOG_FAILED) 
                create_dynalog_config_ini(config.DYNALOG_CONFIG)
                create_dynalog_send_post_request_file(config.DYNALOG_SEND_POST)
                create_dynalog_database.create_dynalog_database(config.DYNALOG_DATABASE)
                print("Created {}".format(os.path.join(path, config.DYNALOG_FOLDER_NAME)))
                print("Created {}".format(config.DYNALOG_CONFIG))
                print("Created {}".format(config.DYNALOG_SEND_POST))
                print("Created {}".format(config.DYNALOG_DATABASE))
                print("Created {}".format(config.DYNALOG_ARCHIVE))
                print("Created {}".format(config.DYNALOG_FAILED))
            except:
                print("Could not create the dynalog directory!\n")
        
        # Create the temp directory
        config.TEMP_DIRECTORY = os.path.join(path, config.TEMP_DIRECTORY_NAME)
        config.TEMP_DCM_FOLDER = os.path.join(path, config.TEMP_DIRECTORY_NAME, config.TEMP_DCM_FOLDER_NAME)
        config.TEMP_NONDCM_FOLDER = os.path.join(path, config.TEMP_DIRECTORY_NAME, config.TEMP_NONDCM_FOLDER_NAME)
        config.TEMP_DYNALOG_FOLDER = os.path.join(path, config.TEMP_DIRECTORY_NAME, config.TEMP_DYNALOG_FOLDER_NAME)
        config.PDF_REPORT_FOLDER = os.path.join(path, config.TEMP_DIRECTORY_NAME, config.PDF_REPORT_FOLDER_NAME)
        
        if os.path.isdir(os.path.join(path, config.TEMP_DIRECTORY_NAME)):
            if not os.path.isdir(config.TEMP_DCM_FOLDER):
                try:
                    os.makedirs(config.TEMP_DCM_FOLDER) 
                    print("Created {}".format(config.TEMP_DCM_FOLDER))
                except:
                    print("Could not create the dcm temp directory!\n")
            else:
                print("Using {}".format(config.TEMP_DCM_FOLDER))
            
            if not os.path.isdir(config.TEMP_NONDCM_FOLDER):
                try:
                    os.makedirs(config.TEMP_NONDCM_FOLDER) 
                    print("Created {}".format(config.TEMP_NONDCM_FOLDER))
                except:
                    print("Could not create the non-dcm temp directory!\n")
            else:
                print("Using {}".format(config.TEMP_NONDCM_FOLDER))
            
            if not os.path.isdir(config.PDF_REPORT_FOLDER):
                try:
                    os.makedirs(config.PDF_REPORT_FOLDER)
                    print("Created {}".format(config.PDF_REPORT_FOLDER))
                except:
                    print("Could not create the pdf temp directory!\n")
            else:
                print("Using {}".format(config.PDF_REPORT_FOLDER))
            
            if not os.path.isdir(config.TEMP_DYNALOG_FOLDER):
                try:
                    os.makedirs(config.TEMP_DYNALOG_FOLDER) 
                    print("Created {}".format(config.TEMP_DYNALOG_FOLDER))
                except:
                    print("Could not create the dynalog temp directory!\n")
            else:
                print("Using {}".format(config.TEMP_DYNALOG_FOLDER))
        else:
            try:
                os.makedirs(config.TEMP_DCM_FOLDER) 
                os.makedirs(config.TEMP_NONDCM_FOLDER) 
                os.makedirs(config.TEMP_DYNALOG_FOLDER) 
                os.makedirs(config.PDF_REPORT_FOLDER) 
                print("Created {}".format(config.TEMP_DCM_FOLDER))
                print("Created {}".format(config.TEMP_NONDCM_FOLDER))
                print("Created {}".format(config.TEMP_DYNALOG_FOLDER))
                print("Created {}".format(config.PDF_REPORT_FOLDER))
            except:
                print("Could not create the temp directory!\n")
    print("\n")

    # Here starts the bottle server
    app = Bottle()
    
    @app.error(500)
    def custom500(error):
        return template("error_template", {"error_message": "Cause unknown.",
                                          "plweb_folder": PLWEB_FOLDER })
    
    @app.route('/')
    @app.route('/qaserver')  # legacy
    @app.route('/qaserver/')  # legacy
    @app.route('/qaserver/login')  # legacy
    def redirect_to_login():
        redirect(PLWEB_FOLDER + "/login")
    
    @app.route(PLWEB_FOLDER)
    def redirect_to_login2():
        redirect(PLWEB_FOLDER + "/login")

    @app.route(PLWEB_FOLDER + "/login")
    def login_form():
        try:
            images = [os.path.join("images", f) for f in os.listdir(os.path.join(CUR_DIR, "static", "images")) if f.endswith('.png')]
        except:
            images = []

        if len(images) != 0:
            image = random.choice(images)
        else:
            image="blank"

        return template("login", {"plweb_folder": PLWEB_FOLDER,
                                  "institution": config.INSTITUTION,
                                  "image": image
                                  })
    
    @app.route(PLWEB_FOLDER + '/login_check_credentials', method='POST')
    def login_check_credentials():
        # Get form data from login page
        username = request.forms.username
        password = request.forms.password
        user_list = general_functions.get_one_user(username)
        if user_list is None:
            return "User not recognized!"
        else:
            if not general_functions.check_encrypted_password(password, user_list[-3]):
                return "Wrong password!"
            else:
                return "Success!"
    
    @app.route(PLWEB_FOLDER + '/login', method='POST')
    def login_submit():
        # Get form data from login page
        username = request.forms.username
        password = request.forms.password
        user_list = general_functions.get_one_user(username)
        if user_list is None:
            return template("error_template", {"error_message": "User not recognized.",
                                               "plweb_folder": PLWEB_FOLDER })
        else:
            if not general_functions.check_encrypted_password(password, user_list[-3]):
                return template("error_template", {"error_message": "Wrong password.",
                                                   "plweb_folder": PLWEB_FOLDER })
            else:
                response.set_cookie("account", username, secret=config.SECRET_KEY, samesite="lax")
                return template("menu_page", {"institution": config.INSTITUTION, "orthanc_url": config.ORTHANC_URL,
                                "plweb_folder": PLWEB_FOLDER, "qaserver_version": config.QASERVER_VERSION,
                                "displayname": user_list[-1], "is_admin": general_functions.check_is_admin(username)})
    
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

    bottle_run(app=app, server="waitress", host=ip, port=port, reloader=False, debug=False)

if __name__ == '__main__':
    main()
