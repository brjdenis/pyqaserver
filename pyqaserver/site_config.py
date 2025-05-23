"""Flask and general configuration."""

BOKEH_FILE_CSS = "/bokeh/css/bokeh-2.2.1.min.css"
BOKEH_FILE_JS = "/bokeh/js/bokeh-2.2.1.min.js"
BOKEH_WIDGETS_CSS = "/bokeh/css/bokeh-widgets-2.2.1.min.css"
BOKEH_WIDGETS_JS = "/bokeh/js/bokeh-widgets-2.2.1.min.js"
BOKEH_TABLES_CSS = "/bokeh/css/bokeh-tables-2.2.1.min.css"
BOKEH_TABLES_JS = "/bokeh/js/bokeh-tables-2.2.1.min.js"

# Name of the folder with reference images
REFERENCE_IMAGES_FOLDER_NAME = "reference_images"
REFERENCE_IMAGES_FOLDER = ""

# Database directory. Passed in by user, must be absolute:
DATABASE_DIRECTORY = ""

# Database names:
GENERAL_DATABASE_NAME = "general_settings_database.db"
TRENDS_DATABASE_NAME = "trends_database.db"

# Define temporarily
GENERAL_DATABASE = ""
TRENDS_DATABASE = ""

PLANARIMAGING_PHANTOMS = [
    "QC3",
    "LeedsTOR",
    "Las Vegas",
    "DoselabMC2MV",
    "DoselabMC2kV",
]
CATPHAN_PHANTOMS = ["Catphan 503", "Catphan 504", "Catphan 600", "Catphan 604"]
FIELDSIZE_FIELDS = ["Small", "Medium", "Large"]
