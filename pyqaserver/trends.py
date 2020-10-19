import sys
import os
import sqlite3 as sql
import json
from datetime import datetime
import tempfile
import csv

parent_module = sys.modules['.'.join(__name__.split('.')[:-1]) or '__main__']
if __name__ == '__main__' or parent_module.__name__ == '__main__':
    #sys.path.append(os.path.abspath(os.path.realpath("python_packages")))
    import config
    import general_functions
    from python_packages.bottlepy.bottle import Bottle, request, TEMPLATE_PATH, template, static_file, redirect, response
else:
    from . import config
    from . import general_functions
    from .python_packages.bottlepy.bottle import Bottle, request, TEMPLATE_PATH, template, static_file, redirect, response

CUR_DIR = os.path.realpath(os.path.dirname(__file__))

# Path to Bottle templates
TEMPLATE_PATH.insert(0, os.path.join(CUR_DIR, 'views'))

# Working directory
PLWEB_FOLDER = config.PLWEB_FOLDER

WINSTON_LUTZ_PARAMETERS = {"Default": ["BBshiftX", "BBshiftY", "BBshiftZ", "BeamDeviation", "CollAsymX", "CollAsymY",
                                       "WobbleColl", "WobbleGnt", "EpidDevX", "EpidDevY", "RadiusMax"],
                          
                           "Gnt/coll + couch rotation": ["BBshiftX", "BBshiftY", "BBshiftZ", "BeamDeviation", "CollAsymX",
                                                        "CollAsymY", "WobbleColl", "WobbleGnt", "WobbleCouch", "EpidDevX", "EpidDevY",
                                                        "RadiusMax", "CouchAxisLAT", "CouchAxisLONG", "CouchAxisDIST"],

                           "Couch only": ["RadiusMax", "WobbleCouch"],
                          
                           "Collimator only": ["RadiusMax", "WobbleColl"],
                           
                           "Pylinac Gantry only": ["Max2DbbCAX", "Median2DbbCAX", "BBshiftX", "BBshiftY", "BBshiftZ",
                                                   "GntIsoSize", "MaxGntRMS", "MaxEpidRMS", "GntColl3DisoSize", "Coll2DisoSize",
                                                   "MaxCollRMS", "Couch2DisoDia", "MaxCouchRMS", "RadiusMax"],
                           
                           "Pylinac Collimator only": ["Max2DbbCAX", "Median2DbbCAX", "BBshiftX", "BBshiftY", "BBshiftZ",
                                                       "GntIsoSize", "MaxGntRMS", "MaxEpidRMS", "GntColl3DisoSize", "Coll2DisoSize",
                                                       "MaxCollRMS", "Couch2DisoDia", "MaxCouchRMS", "RadiusMax"],
                           
                           "Pylinac Couch only": ["Max2DbbCAX", "Median2DbbCAX", "BBshiftX", "BBshiftY", "BBshiftZ",
                                                  "GntIsoSize", "MaxGntRMS", "MaxEpidRMS", "GntColl3DisoSize", "Coll2DisoSize",
                                                  "MaxCollRMS", "Couch2DisoDia", "MaxCouchRMS", "RadiusMax"],
                           
                           "Pylinac Mixed": ["Max2DbbCAX", "Median2DbbCAX", "BBshiftX", "BBshiftY", "BBshiftZ",
                                             "GntIsoSize", "MaxGntRMS", "MaxEpidRMS", "GntColl3DisoSize", "Coll2DisoSize",
                                             "MaxCollRMS", "Couch2DisoDia", "MaxCouchRMS", "RadiusMax"]
                          }

STARSHOT_PARAMETERS = {"Collimator": ["Radius"],
                       "Couch": ["Radius"],
                       "Gantry": ["Radius"]
                       }

PICKETFENCE_PARAMETERS = {"Default": ["PassPrcnt", "MaxError", "MaxErrorPckt", "MaxErrorLeaf",
                                      "MedianError", "MeanPicketSpacing", "MeanFWHM"]
                       }

PLANARIMAGING_PARAMETERS = {"Default": ["f30", "f40", "f50", "f80",
                                        "MedianContrast", "MedianCNR"]
                           }

CATPHAN_PARAMETERS = {"Default": ["MTF30", "MTF50", "MTF80", "LCV", "SliceThickness",
                                  "Scaling", "PhantomRoll", "PhantomCenterX", "PhantomCenterY",
                                  "OriginSlice", "mm_per_pixel", "UniformityIndex", 
                                  "UniformityAbsoluteValue", "LowContrastROIsSeen",
                                  "LowContrastCNR", "Air_HU", "PMP_HU", "LDPE_HU",
                                  "Poly_HU", "Acrylic_HU",  "Delrin_HU",
                                  "Teflon_HU", "Bone20_HU", "Bone50_HU",
                                  "Air_CNR", "PMP_CNR", "LDPE_CNR", "Poly_CNR",
                                  "Acrylic_CNR", "Delrin_CNR", "Teflon_CNR",
                                  "Bone20_CNR", "Bone50_CNR"]}

FLATSYM_PARAMETERS = {"Elekta": ["Symmetry_hor", "Symmetry_vrt", "Flatness_hor",
                                  "Flatness_vrt", "Horizontal_width", "Vertical_width",
                                  "Horizontal_penumbra_width", "Vertical_penumbra_width"],
                      "Varian": ["Symmetry_hor", "Symmetry_vrt", "Flatness_hor",
                                  "Flatness_vrt", "Horizontal_width", "Vertical_width",
                                  "Horizontal_penumbra_width", "Vertical_penumbra_width"]}

VMAT_PARAMETERS = {"DRGS": ["Max_diff", "Mean_diff"],
                   "DRMLC": ["Max_diff", "Mean_diff"]}

FIELDSIZE_PARAMETERS = {"MLC and Jaws": ["LeafSide1", "LeafSide2", "JawSide1", "JawSide2", "LeafWidth",
                                         "JawWidth", "IsoOffsetX", "IsoOffsetY", "FieldRot", "IsoMethod"],
                        "Jaws only": ["LeafSide1", "LeafSide2", "JawSide1", "JawSide2", "LeafWidth",
                                      "JawWidth", "IsoOffsetX", "IsoOffsetY", "FieldRot", "IsoMethod"],
                        "MLC only": ["LeafSide1", "LeafSide2", "JawSide1", "JawSide2", "LeafWidth",
                                     "JawWidth", "IsoOffsetX", "IsoOffsetY", "FieldRot", "IsoMethod"]}

FIELDROTATION_PARAMETERS = {"Collimator absolute": ["Angle"],
                            "Collimator relative": ["Angle"],
                            "Couch relative": ["Angle"]}

# Here starts the bottle server
trends_app = Bottle()

def get_unique_names(table):
    # Collect machines, beams and phantoms from table
    conn = sql.connect(config.TRENDS_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT Machine, Beam, Phantom FROM " + table)
    data = curs.fetchall()
    curs.close()
    conn.close()
    machines = list(set([i[0] for i in data]))
    machines.sort()
    beams = {}
    phantoms = {}
    for m in machines:
        temp = []
        temp2 = []
        for k in data:
            if k[0]==m:
                temp.append(k[1])
                temp2.append(k[2])
        temp = list(set(temp))
        temp2 = list(set(temp2))
        temp.sort()
        temp2.sort()
        beams[m]=temp
        phantoms[m]=temp2
    return [machines, beams, phantoms]

def get_trend_data(Module, TestType, Parameters, Machine, Beam, Phantom, Date1, Date2):
    conn = sql.connect(config.TRENDS_DATABASE)
    curs = conn.cursor()
    select_declaration = "rowid, Datetime, User, Comment, {}".format(", ". join(Parameters))
    if Module == "Winston Lutz":
        curs.execute("SELECT {} FROM Winstonlutz WHERE TestType=? AND Machine=? AND Beam=? AND Phantom=? AND (Datetime BETWEEN ? AND ?) ORDER BY Datetime".format(select_declaration),
                    (TestType, Machine, Beam, Phantom, Date1, Date2))
    elif Module == "Starshot":
        curs.execute("SELECT {} FROM Starshot WHERE TestType=? AND Machine=? AND Beam=? AND (Datetime BETWEEN ? AND ?) ORDER BY Datetime".format(select_declaration),
                    (TestType, Machine, Beam, Date1, Date2))
    elif Module == "Picketfence":
        curs.execute("SELECT {} FROM Picketfence WHERE Machine=? AND Beam=? AND (Datetime BETWEEN ? AND ?) ORDER BY Datetime".format(select_declaration),
                    (Machine, Beam, Date1, Date2))
    elif Module == "PlanarImaging":
        curs.execute("SELECT {} FROM PlanarImaging WHERE Machine=? AND Beam=? AND Phantom=? AND (Datetime BETWEEN ? AND ?) ORDER BY Datetime".format(select_declaration),
                    (Machine, Beam, Phantom, Date1, Date2))
    elif Module == "Catphan":
        curs.execute("SELECT {} FROM Catphan WHERE Machine=? AND Beam=? AND Phantom=? AND (Datetime BETWEEN ? AND ?) ORDER BY Datetime".format(select_declaration),
                    (Machine, Beam, Phantom, Date1, Date2))
    elif Module == "Flatness/Symmetry":
        curs.execute("SELECT {} FROM FlatSym WHERE Machine=? AND Beam=? AND TestType=? AND (Datetime BETWEEN ? AND ?) ORDER BY Datetime".format(select_declaration),
                    (Machine, Beam, TestType, Date1, Date2))
    elif Module == "Vmat":
        curs.execute("SELECT {} FROM Vmat WHERE TestType=? AND Machine=? AND Beam=? AND (Datetime BETWEEN ? AND ?) ORDER BY Datetime".format(select_declaration),
                    (TestType, Machine, Beam, Date1, Date2))
    elif Module == "Fieldsize":
        curs.execute("SELECT {} FROM FieldSize WHERE TestType=? AND Machine=? AND Beam=? AND Phantom=? AND (Datetime BETWEEN ? AND ?) ORDER BY Datetime".format(select_declaration),
                    (TestType, Machine, Beam, Phantom, Date1, Date2))
    elif Module == "Fieldrot":
        curs.execute("SELECT {} FROM FieldRotation WHERE TestType=? AND Machine=? AND Beam=? AND Phantom=? AND (Datetime BETWEEN ? AND ?) ORDER BY Datetime".format(select_declaration),
                    (TestType, Machine, Beam, Phantom, Date1, Date2))
    data = curs.fetchall()
    curs.close()
    conn.close()
    return data

@trends_app.route(PLWEB_FOLDER + '/save_winstonlutz', method="POST")
def save_winstonlutz():
    json_data = json.loads(request.forms.json_data)
    if json_data=={}:
        return "Failed! Only results from 4 or 8 images can be saved."
    columns = []
    data = []
    machine = json_data["Machine"] if json_data["Machine"] is not None else ""
    beam = json_data["Beam"] if json_data["Beam"] is not None else ""
    phantom = json_data["Phantom"] if json_data["Phantom"] is not None else ""
    if machine == "" or beam == "" or phantom == "":
        return "Cannot save unknown machine/beam/phantom."
    
    for key, val in json_data.items():
        columns.append(key if key is not None else "")
        data.append(val if val is not None else "")
    columns_declaration = ', '.join(c for c in columns)
    data_declaration = ", ".join(["?"]*len(data))
    try:
        conn = sql.connect(config.TRENDS_DATABASE)
        curs = conn.cursor()
        curs.execute("INSERT INTO Winstonlutz ({}) VALUES ({})".format(columns_declaration, data_declaration), data)
        curs.execute("INSERT OR IGNORE INTO WinstonlutzUniqueNames (Machine, Beam, Phantom) VALUES (?, ?, ?)",
                     (machine, beam, phantom))
        conn.commit()
        curs.close()
        conn.close()
        return "Done!"
    except sql.IntegrityError as e:
        return "Failed! "+str(e)
    except sql.OperationalError as e:
        return "Failed! "+str(e)
    else:
        return "Failed"

@trends_app.route(PLWEB_FOLDER + '/save_starshot', method="POST")
def save_starshot():
    json_data = json.loads(request.forms.json_data)
    machine = json_data["Machine"] if json_data["Machine"] is not None else ""
    beam = json_data["Beam"] if json_data["Beam"] is not None else ""

    if json_data == {}:
        return "No data to save."
    if machine == "" or beam == "":
        return "Cannot save unknown machine/beam."
    columns = []
    data = []
    for key, val in json_data.items():
        columns.append(key if key is not None else "")
        data.append(val if val is not None else "")
    columns_declaration = ', '.join(c for c in columns)
    data_declaration = ", ".join(["?"]*len(data))
    try:
        conn = sql.connect(config.TRENDS_DATABASE)
        curs = conn.cursor()
        curs.execute("INSERT INTO Starshot ({}) VALUES ({})".format(columns_declaration, data_declaration), data)
        curs.execute("INSERT OR IGNORE INTO StarshotUniqueNames (Machine, Beam) VALUES (?, ?)",
                     (machine, beam))
        conn.commit()
        curs.close()
        conn.close()
        return "Done!"
    except sql.IntegrityError as e:
        return "Failed! "+str(e)
    except sql.OperationalError as e:
        return "Failed! "+str(e)
    else:
        return "Failed"

@trends_app.route(PLWEB_FOLDER + '/save_picketfence', method="POST")
def save_picketfence():
    json_data = json.loads(request.forms.json_data)
    machine = json_data["Machine"] if json_data["Machine"] is not None else ""
    beam = json_data["Beam"] if json_data["Beam"] is not None else ""

    if json_data == {}:
        return "No data to save."
    if machine == "" or beam == "":
        return "Cannot save unknown machine/beam."
    columns = []
    data = []
    for key, val in json_data.items():
        columns.append(key if key is not None else "")
        data.append(val if val is not None else "")
    columns_declaration = ', '.join(c for c in columns)
    data_declaration = ", ".join(["?"]*len(data))
    try:
        conn = sql.connect(config.TRENDS_DATABASE)
        curs = conn.cursor()
        curs.execute("INSERT INTO Picketfence ({}) VALUES ({})".format(columns_declaration, data_declaration), data)
        curs.execute("INSERT OR IGNORE INTO PicketfenceUniqueNames (Machine, Beam) VALUES (?, ?)",
                     (machine, beam))
        conn.commit()
        curs.close()
        conn.close()
        return "Done!"
    except sql.IntegrityError as e:
        return "Failed! "+str(e)
    except sql.OperationalError as e:
        return "Failed! "+str(e)
    else:
        return "Failed"

@trends_app.route(PLWEB_FOLDER + '/save_planarimaging', method="POST")
def save_planarimaging():
    json_data = json.loads(request.forms.json_data)
    machine = json_data["Machine"] if json_data["Machine"] is not None else ""
    beam = json_data["Beam"] if json_data["Beam"] is not None else ""
    phantom = json_data["Phantom"] if json_data["Phantom"] is not None else ""

    if json_data == {}:
        return "No data to save."
    if machine == "" or beam == "":
        return "Cannot save unknown machine/beam."
    
    columns = []
    data = []
    for key, val in json_data.items():
        columns.append(key if key is not None else "")
        data.append(val if val is not None else "")
    columns_declaration = ', '.join(c for c in columns)
    data_declaration = ", ".join(["?"]*len(data))
    try:
        conn = sql.connect(config.TRENDS_DATABASE)
        curs = conn.cursor()
        curs.execute("INSERT INTO PlanarImaging ({}) VALUES ({})".format(columns_declaration, data_declaration), data)
        curs.execute("INSERT OR IGNORE INTO PlanarImagingUniqueNames (Machine, Beam, Phantom) VALUES (?, ?, ?)",
                     (machine, beam, phantom))
        conn.commit()
        curs.close()
        conn.close()
        return "Done!"
    except sql.IntegrityError as e:
        return "Failed! "+str(e)
    except sql.OperationalError as e:
        return "Failed! "+str(e)
    else:
        return "Failed"

@trends_app.route(PLWEB_FOLDER + '/save_catphan', method="POST")
def save_catphan():
    json_data = json.loads(request.forms.json_data)
    machine = json_data["Machine"] if json_data["Machine"] is not None else ""
    beam = json_data["Beam"] if json_data["Beam"] is not None else ""
    phantom = json_data["Phantom"] if json_data["Phantom"] is not None else ""

    if json_data == {}:
        return "No data to save."
    if machine == "" or beam == "":
        return "Cannot save unknown machine/beam."
    
    columns = []
    data = []
    for key, val in json_data.items():
        columns.append(key if key is not None else "")
        data.append(val if val is not None else "")
    columns_declaration = ', '.join(c for c in columns)
    data_declaration = ", ".join(["?"]*len(data))
    try:
        conn = sql.connect(config.TRENDS_DATABASE)
        curs = conn.cursor()
        curs.execute("INSERT INTO Catphan ({}) VALUES ({})".format(columns_declaration, data_declaration), data)
        curs.execute("INSERT OR IGNORE INTO CatphanUniqueNames (Machine, Beam, Phantom) VALUES (?, ?, ?)",
                     (machine, beam, phantom))
        conn.commit()
        curs.close()
        conn.close()
        return "Done!"
    except sql.IntegrityError as e:
        return "Failed! "+str(e)
    except sql.OperationalError as e:
        return "Failed! "+str(e)
    else:
        return "Failed"


@trends_app.route(PLWEB_FOLDER + '/save_flatsym', method="POST")
def save_flatsym():
    json_data = json.loads(request.forms.json_data)
    machine = json_data["Machine"] if json_data["Machine"] is not None else ""
    beam = json_data["Beam"] if json_data["Beam"] is not None else ""

    if json_data == {}:
        return "No data to save."
    if machine == "" or beam == "":
        return "Cannot save unknown machine/beam."
    columns = []
    data = []
    for key, val in json_data.items():
        columns.append(key if key is not None else "")
        data.append(val if val is not None else "")
    columns_declaration = ', '.join(c for c in columns)
    data_declaration = ", ".join(["?"]*len(data))
    try:
        conn = sql.connect(config.TRENDS_DATABASE)
        curs = conn.cursor()
        curs.execute("INSERT INTO FlatSym ({}) VALUES ({})".format(columns_declaration, data_declaration), data)
        curs.execute("INSERT OR IGNORE INTO FlatSymUniqueNames (Machine, Beam) VALUES (?, ?)",
                     (machine, beam))
        conn.commit()
        curs.close()
        conn.close()
        return "Done!"
    except sql.IntegrityError as e:
        return "Failed! "+str(e)
    except sql.OperationalError as e:
        return "Failed! "+str(e)
    else:
        return "Failed"

@trends_app.route(PLWEB_FOLDER + '/save_vmat', method="POST")
def save_vmat():
    json_data = json.loads(request.forms.json_data)
    machine = json_data["Machine"] if json_data["Machine"] is not None else ""
    beam = json_data["Beam"] if json_data["Beam"] is not None else ""

    if json_data == {}:
        return "No data to save."
    if machine == "" or beam == "":
        return "Cannot save unknown machine/beam."
    columns = []
    data = []
    for key, val in json_data.items():
        columns.append(key if key is not None else "")
        data.append(val if val is not None else "")
    columns_declaration = ', '.join(c for c in columns)
    data_declaration = ", ".join(["?"]*len(data))
    try:
        conn = sql.connect(config.TRENDS_DATABASE)
        curs = conn.cursor()
        curs.execute("INSERT INTO Vmat ({}) VALUES ({})".format(columns_declaration, data_declaration), data)
        curs.execute("INSERT OR IGNORE INTO VmatUniqueNames (Machine, Beam) VALUES (?, ?)",
                     (machine, beam))
        conn.commit()
        curs.close()
        conn.close()
        return "Done!"
    except sql.IntegrityError as e:
        return "Failed! "+str(e)
    except sql.OperationalError as e:
        return "Failed! "+str(e)
    else:
        return "Failed"

@trends_app.route(PLWEB_FOLDER + '/save_fieldsize', method="POST")
def save_fieldsize():
    json_data = json.loads(request.forms.json_data)
    machine = json_data["Machine"] if json_data["Machine"] is not None else ""
    beam = json_data["Beam"] if json_data["Beam"] is not None else ""
    phantom = json_data["Phantom"] if json_data["Phantom"] is not None else ""

    if json_data == {}:
        return "No data to save."
    if machine == "" or beam == "" or phantom == "":
        return "Cannot save unknown machine/beam."
    
    columns = []
    data = []
    for key, val in json_data.items():
        columns.append(key if key is not None else "")
        data.append(val if val is not None else "")
    columns_declaration = ', '.join(c for c in columns)
    data_declaration = ", ".join(["?"]*len(data))
    try:
        conn = sql.connect(config.TRENDS_DATABASE)
        curs = conn.cursor()
        curs.execute("INSERT INTO FieldSize ({}) VALUES ({})".format(columns_declaration, data_declaration), data)
        curs.execute("INSERT OR IGNORE INTO FieldSizeUniqueNames (Machine, Beam, Phantom) VALUES (?, ?, ?)",
                     (machine, beam, phantom))
        conn.commit()
        curs.close()
        conn.close()
        return "Done!"
    except sql.IntegrityError as e:
        return "Failed! "+str(e)
    except sql.OperationalError as e:
        return "Failed! "+str(e)
    else:
        return "Failed"

@trends_app.route(PLWEB_FOLDER + '/save_fieldrotation', method="POST")
def save_fieldrotation():
    json_data = json.loads(request.forms.json_data)
    machine = json_data["Machine"] if json_data["Machine"] is not None else ""
    beam = json_data["Beam"] if json_data["Beam"] is not None else ""
    phantom = json_data["Phantom"] if json_data["Phantom"] is not None else ""

    if json_data == {}:
        return "No data to save."
    if machine == "" or beam == "" or phantom == "":
        return "Cannot save unknown machine/beam."
    try:
        float(json_data["Angle"])
    except:
        return "Failed. Cannot convert measured angle to valid float."
    
    columns = []
    data = []
    for key, val in json_data.items():
        columns.append(key if key is not None else "")
        data.append(val if val is not None else "")
    columns_declaration = ', '.join(c for c in columns)
    data_declaration = ", ".join(["?"]*len(data))
    try:
        conn = sql.connect(config.TRENDS_DATABASE)
        curs = conn.cursor()
        curs.execute("INSERT INTO FieldRotation ({}) VALUES ({})".format(columns_declaration, data_declaration), data)
        curs.execute("INSERT OR IGNORE INTO FieldRotationUniqueNames (Machine, Beam, Phantom) VALUES (?, ?, ?)",
                     (machine, beam, phantom))
        conn.commit()
        curs.close()
        conn.close()
        return "Done!"
    except sql.IntegrityError as e:
        return "Failed! "+str(e)
    except sql.OperationalError as e:
        return "Failed! "+str(e)
    else:
        return "Failed"


@trends_app.route(PLWEB_FOLDER + '/remove_measurement', method="POST")
def remove_measurement():
    rowid = request.forms.rowid
    module = request.forms.module
    if module == "Winston Lutz":
        module_name = "Winstonlutz"
    elif module == "Starshot":
        module_name = "Starshot"
    elif module == "Picketfence":
        module_name = "Picketfence"
    elif module == "PlanarImaging":
        module_name = "PlanarImaging"
    elif module == "Catphan":
        module_name = "Catphan"
    elif module == "Flatness/Symmetry":
        module_name = "FlatSym"
    elif module == "Vmat":
        module_name = "Vmat"
    elif module == "Fieldsize":
        module_name = "FieldSize"
    elif module == "Fieldrot":
        module_name = "FieldRotation"
    try:
        conn = sql.connect(config.TRENDS_DATABASE)
        curs = conn.cursor()
        curs.execute("DELETE FROM {} WHERE rowid = ?".format(module_name), (rowid, ))
        conn.commit()
        curs.close()
        conn.close()
        return "Done!"
    except sql.IntegrityError as e:
        return "Failed! "+str(e)
    except sql.OperationalError as e:
        return "Failed! "+str(e)
    else:
        return "Failed"

@trends_app.route(PLWEB_FOLDER + '/review_trends', method="POST")
def review_trends():
    displayname = request.forms.hidden_displayname
    username = request.get_cookie("account", secret=config.SECRET_KEY)
    if not username:
        redirect(PLWEB_FOLDER + "/login")
    
    tables = {"Winston Lutz": WINSTON_LUTZ_PARAMETERS,
              "Starshot": STARSHOT_PARAMETERS,
              "Picketfence": PICKETFENCE_PARAMETERS,
              "PlanarImaging": PLANARIMAGING_PARAMETERS,
              "Catphan": CATPHAN_PARAMETERS,
              "Flatness/Symmetry": FLATSYM_PARAMETERS,
              "Vmat": VMAT_PARAMETERS,
              "Fieldsize": FIELDSIZE_PARAMETERS,
              "Fieldrot": FIELDROTATION_PARAMETERS
              }
    unique_names = {
                    "Winston Lutz": get_unique_names("WinstonlutzUniqueNames"),
                    "Starshot": get_unique_names("StarshotUniqueNames"),
                    "Picketfence": get_unique_names("PicketfenceUniqueNames"),
                    "PlanarImaging": get_unique_names("PlanarImagingUniqueNames"),
                    "Catphan": get_unique_names("CatphanUniqueNames"),
                    "Flatness/Symmetry": get_unique_names("FlatSymUniqueNames"),
                    "Vmat": get_unique_names("VmatUniqueNames"),
                    "Fieldsize": get_unique_names("FieldSizeUniqueNames"),
                    "Fieldrot": get_unique_names("FieldRotationUniqueNames")
                    }
    variables = {
                "tables": json.dumps(tables),
                "unique_names": json.dumps(unique_names),
                "plweb_folder": PLWEB_FOLDER,
                "displayname": displayname,
                "is_admin": general_functions.check_is_admin(username)
                }
    response.set_cookie("account", username, secret=config.SECRET_KEY, samesite="lax")
    return template("trends", variables)


@trends_app.route(PLWEB_FOLDER + '/fetch_trends', method="POST")
def fetch_trends():
    Module = request.forms.Module
    TestType = request.forms.TestType
    Parameters = json.loads(request.forms.Parameters)
    Machine = request.forms.Machine
    Beam = request.forms.Beam
    Phantom = request.forms.Phantom
    Date1 = request.forms.Date1
    Date2 = request.forms.Date2

    if Date1=="" and Date2=="":
        Date1 = datetime.min.strftime('%Y-%m-%d')
        Date2 = datetime.today().strftime('%Y-%m-%d')
    elif Date1!="" and Date2=="":
        Date2 = datetime.today().strftime('%Y-%m-%d')
    return json.dumps(get_trend_data(Module, TestType, Parameters, Machine, Beam, Phantom, Date1, Date2))


@trends_app.route(PLWEB_FOLDER + '/download_csv', method="POST")
def download_csv():
    Module = request.forms.hidden_module
    TestType = request.forms.hidden_testtype
    Parameters = json.loads(request.forms.hidden_parameters)
    Machine = request.forms.hidden_machine
    Beam = request.forms.hidden_beam
    Phantom = request.forms.hidden_phantom
    Date1 = request.forms.hidden_date1
    Date2 = request.forms.hidden_date2
    
    if Date1=="" and Date2=="":
        Date1 = datetime.min.strftime('%Y-%m-%d')
        Date2 = datetime.today().strftime('%Y-%m-%d')
    elif Date1!="" and Date2=="":
        Date2 = datetime.today().strftime('%Y-%m-%d')
    
    file = tempfile.NamedTemporaryFile(delete=False, prefix="download_csv_", suffix=".csv", dir=config.TEMP_NONDCM_FOLDER)
    data = get_trend_data(Module, TestType, Parameters, Machine, Beam, Phantom, Date1, Date2)
    with open(file.name, 'w', newline='') as csvfile:  
        csvwriter = csv.writer(csvfile, delimiter=';') 
        csvwriter.writerow(["rowid", "Datetime", "User", "Comment"]+Parameters)
        csvwriter.writerows(data) 
    return static_file(file.name, root=config.TEMP_NONDCM_FOLDER, download=file.name)
    