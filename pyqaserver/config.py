# Certain constants/global variables are defined here.
import os
import base64

QASERVER_VERSION = ""
INSTITUTION = "" # Define temporarily

D3_URL = "/js/d3.v3.min.js"
MPLD3_URL = "/js/mpld3.v0.3.min.js"

BOKEH_FILE_CSS = "/bokeh/css/bokeh-2.2.1.min.css"
BOKEH_FILE_JS = "/bokeh/js/bokeh-2.2.1.min.js"
BOKEH_WIDGETS_CSS = "/bokeh/css/bokeh-widgets-2.2.1.min.css"
BOKEH_WIDGETS_JS = "/bokeh/js/bokeh-widgets-2.2.1.min.js"
BOKEH_TABLES_CSS = "/bokeh/css/bokeh-tables-2.2.1.min.css"
BOKEH_TABLES_JS = "/bokeh/js/bokeh-tables-2.2.1.min.js"

# Generate secret key for cookies:
SECRET_KEY = base64.b64encode(os.urandom(12).hex().encode())

# A stupid variable I invented, now it must be empty :(
PLWEB_FOLDER = ""

# Name of the folder with reference images
REFERENCE_IMAGES_FOLDER = "reference_images"

# Database directory (passed in by user!):
WORKING_DIRECTORY = ""

# Database names:
GENERAL_DATABASE_NAME = "general_settings_database.db"
TRENDS_DATABASE_NAME = "trends_database.db"

# Define temporarily
GENERAL_DATABASE = ""
TRENDS_DATABASE = ""

USERNAME_ORTHANC = ""
PASSWORD_ORTHANC = ""
ORTHANC_IP = ""
ORTHANC_PORT = ""
ORTHANC_URL = "" 

PLANARIMAGING_PHANTOMS = ["QC3", "LeedsTOR", "Las Vegas", "DoselabMC2MV", "DoselabMC2kV"]
CATPHAN_PHANTOMS = ["Catphan 503", "Catphan 504", "Catphan 600", "Catphan 604"]
FIELDSIZE_FIELDS = ["Small", "Medium", "Large"]

# Dynalog archive folder:
DYNALOG_DATABASE_NAME = "dynalog_database.db"
DYNALOG_FOLDER_NAME = "dynalog_database"
DYNALOG_FOLDER = ""
DYNALOG_DATABASE = ""
DYNALOG_ARCHIVE_FOLDER_NAME = "ARCHIVE"
DYNALOG_ARCHIVE = ""
DYNALOG_FAILED_FOLDER_NAME = "dynalogs_with_errors"
DYNALOG_FAILED  = ""
DYNALOG_CONFIG_NAME = "dynalog_config.ini"
DYNALOG_CONFIG = ""
DYNALOG_SEND_POST_NAME = "dynalog_send_post_request.py"
DYNALOG_SEND_POST = ""
DYNALOG_ANALYSIS_IN_PROGRESS = False
DYNALOG_CURRENT_FOLDER_ANALYSIS = 0
DYNALOG_CURRENT_PROGRESS = 0

# Temp directories
TEMP_DCM_FOLDER_NAME = "temp_dcm_archive"
TEMP_DCM_FOLDER = ""
TEMP_NONDCM_FOLDER_NAME = "temp_nondicom_archive"
TEMP_NONDCM_FOLDER = ""
PDF_REPORT_FOLDER_NAME = "temp_pdf_reports"
PDF_REPORT_FOLDER = ""
TEMP_DYNALOG_FOLDER_NAME = "temp_dynalog_folder"
TEMP_DYNALOG_FOLDER = ""
TEMP_DIRECTORY_NAME = "temp_files"
TEMP_DIRECTORY = ""
