import sys
import os
import sqlite3 as sql
import json
import tempfile
import zipfile
from scipy.signal import savgol_filter
import gc
import datetime
import numpy as np
import configparser
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.layouts import gridplot, row, layout, Column 
from bokeh.models import CustomJS, ColumnDataSource, Slider, Legend
from bokeh.core.properties import value as bokeh_value
import matplotlib.style
import matplotlib
matplotlib.use('Agg')
from matplotlib.figure import Figure
from matplotlib import patches

# To revert back to matplotlib 1.0 style
matplotlib.style.use('classic')

parent_module = sys.modules['.'.join(__name__.split('.')[:-1]) or '__main__']
if __name__ == '__main__' or parent_module.__name__ == '__main__':
    #sys.path.append(os.path.abspath(os.path.realpath("python_packages")))
    import config
    from python_packages.bottlepy.bottle import Bottle, request, TEMPLATE_PATH, template, redirect, response
    import general_functions
    from python_packages import mpld3
else:
    from . import config
    from .python_packages.bottlepy.bottle import Bottle, request, TEMPLATE_PATH, template, redirect, response
    from . import general_functions
    from .python_packages import mpld3

CUR_DIR = os.path.realpath(os.path.dirname(__file__))

# Path to Bottle templates
TEMPLATE_PATH.insert(0, os.path.join(CUR_DIR, 'views'))

# Set string for the header of HTML pages:
INSTITUTION = config.INSTITUTION

# Url to some mpld3 library
D3_URL = config.D3_URL
MPLD3_URL = config.MPLD3_URL

# Working directory
PLWEB_FOLDER = config.PLWEB_FOLDER

PI = np.pi

#  Global filepaths for bokeh import
BOKEH_FILE_CSS = config.BOKEH_FILE_CSS
BOKEH_FILE_JS = config.BOKEH_FILE_JS
BOKEH_WIDGETS_CSS = config.BOKEH_WIDGETS_CSS
BOKEH_WIDGETS_JS = config.BOKEH_WIDGETS_JS
BOKEH_TABLES_CSS = config.BOKEH_TABLES_CSS
BOKEH_TABLES_JS = config.BOKEH_TABLES_JS

# Leaf borders for Dynalog files (in mm):
MLC_DYNALOG = {"Varian_120": [-200.0, -190.0, -180.0, -170.0, -160.0, -150.0, -140.0, -130.0, -120.0, -110.0, -100.0, -95.0, -90.0, -85.0, -80.0, -75.0, -70.0, -65.0, -60.0, -55.0, -50.0, -45.0, -40.0, -35.0, -30.0, -25.0, -20.0, -15.0, -10.0, -5.0, 0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0, 55.0, 60.0, 65.0, 70.0, 75.0, 80.0, 85.0, 90.0, 95.0, 100.0, 110.0, 120.0, 130.0, 140.0, 150.0, 160.0, 170.0, 180.0, 190.0, 200.0],
              "Varian_120HD": [-110, -105, -100, -95, -90, -85, -80, -75, -70, -65, -60, -55, -50, -45, -40, -37.5, -35, -32.5, -30, -27.5, -25, -22.5, -20, -17.5, -15, -12.5, -10, -7.5, -5, -2.5, 0.0, 2.5, 5, 7.5, 10, 12.5, 15, 17.5, 20, 22.5, 25, 27.5, 30, 32.5, 35, 37.5, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110],
              "Varian_80": [-200.0, -190.0, -180.0, -170.0, -160.0, -150.0, -140.0, -130.0, -120.0, -110.0, -100.0, -90.0, -80.0, -70.0, -60.0, -50.0, -40.0, -30.0, -20.0, -10.0, 0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0, 110.0, 120.0, 130.0, 140.0, 150.0, 160.0, 170.0, 180.0, 190.0, 200.0],
              }


# Here starts the bottle server
dyn_app = Bottle()

@dyn_app.route(PLWEB_FOLDER + '/dynalog', method="POST")
def dynalog():
    displayname = request.forms.hidden_displayname
    username = request.get_cookie("account", secret=config.SECRET_KEY)
    if not username:
        redirect(PLWEB_FOLDER + "/login")
    
    config_ini = configparser.ConfigParser()
    config_ini.read(config.DYNALOG_CONFIG)
    DTA = float(config_ini["Dynalog"]["TOLERANCE_DTA"])
    DD = float(config_ini["Dynalog"]["TOLERANCE_DD"])
    resolution = float(config_ini["Dynalog"]["RESOLUTION"])
    threshold = float(config_ini["Dynalog"]["THRESHOLD"])
    labels = [k.strip() for k in config_ini["Dynalog"]["REPOSITORIES_LABELS"].split(",")]
    response.set_cookie("account", username, secret=config.SECRET_KEY, samesite="lax")
    variables = {
                 "institution": INSTITUTION,
                 "plweb_folder": PLWEB_FOLDER,
                 "DTA": DTA,
                 "DD": DD,
                 "resolution": resolution,
                 "threshold": threshold,
                 "labels": ["All"]+labels,
                 "displayname": displayname
                 }
    return template("dynalog", variables)
 
@dyn_app.route(PLWEB_FOLDER + '/dynalogPatients/<s>', method="POST")
def dynalogPatients(s):
    # Function that sends patients for a parcticular date
    conn = sql.connect(config.DYNALOG_DATABASE)
    curs = conn.cursor()
    
    if s == "getall":
        curs.execute("SELECT DISTINCT PatientID FROM VarianDynalog "\
                     " ORDER BY PatientID")
    elif s == "getfiltered":
        filt = request.forms.filter
        label = request.forms.label
        if label == "All":
            curs.execute("SELECT DISTINCT PatientID FROM VarianDynalog "\
                         " WHERE PatientID LIKE '%" + filt + "%' ORDER BY PatientID")
        else:
            curs.execute("SELECT DISTINCT PatientID FROM VarianDynalog "\
                         " WHERE (Repository = '"+label+"') AND (PatientID LIKE '%" + filt + "%') ORDER BY PatientID")
        
    else:
        
        folder = request.forms.folder
        if folder == "All":
            curs.execute("SELECT DISTINCT PatientID FROM VarianDynalog "\
                         "WHERE Date = '" + s + "' ORDER BY PatientLastName")
        else:
            curs.execute("SELECT DISTINCT PatientID FROM VarianDynalog "\
                         "WHERE Date = '" + s + "' AND Repository = '"+folder+"' ORDER BY PatientID")
    data = curs.fetchall()
    curs.close()
    conn.close()
    data_values = ["-----------"] + [f[0] for f in data]
    data_label = ["-----------"] + [f[0] for f in data]
    return json.dumps((data_label, data_values))


@dyn_app.route(PLWEB_FOLDER + '/dynalogRecords', method="POST")
def dynalogRecords():
    # Function for sending records for dynalog module
    patient = request.forms.patient
    if patient != "-----------":
        patientID = patient
    else:
        patientID = ""
    conn = sql.connect(config.DYNALOG_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT DISTINCT Date FROM VarianDynalog "\
                 "WHERE PatientID = '" + patientID + "' ORDER BY Date")
    data = curs.fetchall()
    curs.close()
    conn.close()
    data = ["-----------"] + [f[0] for f in data]
    return json.dumps((data))


@dyn_app.route(PLWEB_FOLDER + '/dynalogRecordData', method="POST")
def dynalogRecordData():
    patient = request.forms.patient
    record = request.forms.record
    if patient != "-----------":
        patientID = patient
    else:
        patientID = ""
    conn = sql.connect(config.DYNALOG_DATABASE)
    curs = conn.cursor()

    curs.execute("SELECT BeamID, Gantry, Time, Snapshots, Beamholds, RMSmax, RMSmax2, "\
                 "DIFFmax, DIFFmax2, RMSAvg, GammaAvg, GammaIndex, FileName, ZipArchive, GammaTol, Repository "\
                 "FROM VarianDynalog WHERE PatientID = '"+patientID+"' AND Date = '" + record + "' ORDER BY PatientID, BeamID, Date, Time")
    data = curs.fetchall()
    curs.close()
    conn.close()
    data = np.asarray(data)

    for k in data:
        k[1] = round(float(k[1]), 1)
        k[5] = round(float(k[5])*10, 2)
        k[6] = round(float(k[6])*10, 2)
        k[7] = round(float(k[7])*10, 2)
        k[8] = round(float(k[8])*10, 2)
        k[9] = round(float(k[9])*10, 2)
        k[10] = round(float(k[10]), 2)
        k[11] = round(float(k[11]), 1)
    return json.dumps((data.tolist()))

@dyn_app.route(PLWEB_FOLDER + '/dynalogGetReportDate', method="POST")
def dynalogGetReportDate():
    date = request.forms.hidden_date
    date2 = request.forms.hidden_date2
    folder = request.forms.hidden_folder
    search_by_folder = " AND Repository = '"+folder+"' " if folder!="All" else " "
    conn = sql.connect(config.DYNALOG_DATABASE)
    curs = conn.cursor()

    if date == "":
        curs.execute("SELECT MAX(ROWID) FROM VarianDynalog")
        last_row = str(curs.fetchone()[0])
        curs.execute("SELECT DateEntered FROM VarianDynalog WHERE ROWID = '"+last_row+"' ")
        date = curs.fetchone()[0]
        curs.execute("SELECT PatientID, Repository, BeamID, Gantry, Date, Time, Snapshots, Beamholds, RMSmax2, "\
                 "DIFFmax2, GammaAvg, GammaIndex "\
                 "FROM VarianDynalog WHERE DateEntered = '"+date+"'"+search_by_folder+" ORDER BY Repository, PatientID, Date, Time")
    else:
        curs.execute("SELECT PatientID, Repository, BeamID, Gantry, Date, Time, Snapshots, Beamholds, RMSmax2, "\
                     "DIFFmax2, GammaAvg, GammaIndex "\
                     "FROM VarianDynalog WHERE Date BETWEEN '"+date+"' AND '"+date2+"' "+search_by_folder+" ORDER BY Repository, PatientID, Date, Time")
    data = curs.fetchall()
    curs.close()
    conn.close()

    variables = {
                "data": data,
                "date": date,
                "date2": date2
                }
    return template("dynalog_report", variables)

@dyn_app.route(PLWEB_FOLDER + '/dynalogGetBigError/<diff>', method="POST")
def dynalogGetBigError(diff):
    diff = str(float(diff)/10.0)  # Convert to cm
    date = request.forms.hidden_date
    date2 = request.forms.hidden_date2
    folder = request.forms.hidden_folder
    search_by_folder = "AND Repository = '"+folder+"' " if folder!="All" else " "

    conn = sql.connect(config.DYNALOG_DATABASE)
    curs = conn.cursor()
    if date == "" and date2 == "":
        curs.execute("SELECT PatientID, Repository, BeamID, Gantry, Date, Time, Snapshots, Beamholds, RMSmax2, "\
                 "DIFFmax2, GammaAvg, GammaIndex "\
                 "FROM VarianDynalog WHERE DIFFmax2 >= '"+diff+"' "+ search_by_folder +" ORDER BY Repository, PatientID, Date, Time")
    else:
        curs.execute("SELECT PatientID, Repository, BeamID, Gantry, Date, Time, Snapshots, Beamholds, RMSmax2, "\
                     "DIFFmax2, GammaAvg, GammaIndex "\
                     "FROM VarianDynalog WHERE Date BETWEEN '"+date+"' AND '"+date2+"' "+search_by_folder+" AND DIFFmax2 >= '"+diff+"' ORDER BY Repository, PatientID, Date, Time")
    data = curs.fetchall()
    curs.close()
    conn.close()

    variables = {
                "data": data,
                "date": date,
                "date2": date2
                }
    return template("dynalog_report", variables)


@dyn_app.route(PLWEB_FOLDER + '/dynalogGetReportPatient', method="POST")
def dynalogGetReportPatient():
    patient = request.forms.hidden_patient
    if patient != "-----------":
        patientID = patient
    else:
        return template("error_template", {"error_message": "Patient ID not valid.",
                                           "plweb_folder": PLWEB_FOLDER})

    conn = sql.connect(config.DYNALOG_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT BeamID, Gantry, Date, Time, Snapshots, Beamholds, RMSmax, RMSmax2, "\
                 "DIFFmax, DIFFmax2, GammaAvg, GammaIndex, RMSAvg "\
                 "FROM VarianDynalog WHERE PatientID = '"+patientID+"' ORDER by Date")
    data1 = np.asarray(curs.fetchall())
    curs.close()
    conn.close()

    beamID = data1[:, 0]
    date = data1[:, 2]

    unique_beamid, counts_beamid = np.unique(beamID, return_counts=True)
    unique_date, inv_date, counts_date = np.unique(date, return_inverse=True, return_counts=True)

    kelly_colors = ['#222222', '#F3C300', '#875692', '#F38400']
    
    TOOLTIPS = [
        ("date", "@dates"),
        ("time", "@time"),
        ("gantry", "@gantry")
    ]

    x = []
    rms_max2 = []
    diff_max2 = []
    gammaind = []
    gammaavg = []
    rms_avg = []
    repetitions = []
    gantry = []
    time = []
    for p in range(0, len(unique_date), 1):
        x.append(p)
        temp = list(data1[data1[:,2]==unique_date[p], 7])  # keep one to count repetitions
        repetitions.append(len(temp))
        rms_max2 += [float(a) for a in temp]
        diff_max2 += [float(a) for a in list(data1[data1[:,2]==unique_date[p], 9])]
        gammaavg += [float(a) for a in list(data1[data1[:,2]==unique_date[p], 10])]
        gammaind += [float(a) for a in list(data1[data1[:,2]==unique_date[p], 11])]
        rms_avg += [float(a) for a in list(data1[data1[:,2]==unique_date[p], 12])]
        gantry += [float(a) for a in list(data1[data1[:,2]==unique_date[p], 1])]
        time += list(data1[data1[:,2]==unique_date[p], 3])

    x = list(np.repeat(np.arange(0, len(unique_date), 1), repetitions))
    dates = list(np.repeat(unique_date, repetitions))
    source = ColumnDataSource(data=dict(
        rms_max2=rms_max2,
        diff_max2=diff_max2,
        rms_avg=rms_avg,
        dates=dates,
        gantry=gantry,
        time=time,
        x=x
    ))
    
    fig1 = figure(plot_width=900, plot_height=450, tooltips=TOOLTIPS, toolbar_location="above")
    f1 = fig1.circle("x", "rms_max2", size = 10, color=kelly_colors[1], alpha=0.5, source=source)
    f2 = fig1.circle("x", "diff_max2", size = 10, color=kelly_colors[3], alpha=0.5,  source=source)
    f3 = fig1.circle("x", "rms_avg", size = 10, color=kelly_colors[2], alpha=0.5,  source=source)
    
    legend = Legend(items=[
            ("RMS MAX2"   , [f1]),
            ("DIFF MAX2" , [f2]),
            ("RMS AVG2" , [f3]),
        ], location="center", click_policy="hide")

    fig1.xaxis.axis_label = 'Fraction'
    fig1.yaxis.axis_label = '[cm]'
    fig1.add_layout(legend, 'right')
    
    TOOLTIPS2 = [
            ("date", "@dates"),
            ("time", "@time"),
            ("gamma index", "@gammaind")
        ]
    
    source2 = ColumnDataSource(data=dict(
        gammaind=gammaind,
        dates=dates,
        gantry=gantry,
        time=time,
        x=x
    ))
    
    fig2 = figure(plot_width=900, plot_height=200, tooltips=TOOLTIPS2, toolbar_location="above")
    f21 = fig2.circle("x", "gammaind", size = 10, color=kelly_colors[2], alpha=0.5, source=source2)
    legend2 = Legend(items=[
            ("Gamma index" , [f21])
        ], location="center", click_policy="hide")

    fig2.xaxis.axis_label = 'Fraction'
    fig2.yaxis.axis_label = '[]'
    fig2.add_layout(legend2, 'right')
    
    TOOLTIPS3 = [
            ("date", "@dates"),
            ("time", "@time"),
            ("gamma avg", "@gammaavg")
        ]
    
    source3 = ColumnDataSource(data=dict(
        gammaavg=gammaavg,
        dates=dates,
        gantry=gantry,
        time=time,
        x=x
    ))
    
    fig3 = figure(plot_width=900, plot_height=200, tooltips=TOOLTIPS3, toolbar_location="above")
    f31 = fig3.circle("x", "gammaavg", size = 10, color=kelly_colors[2], alpha=0.5, source=source3)
    legend3 = Legend(items=[
            ("Gamma avg.", [f31])
        ], location="center", click_policy="hide")

    fig3.xaxis.axis_label = 'Fraction'
    fig3.yaxis.axis_label = '[]'
    fig3.add_layout(legend3, 'right')
    
    script1, div1 = components(fig1)
    script2, div2 = components(fig2)
    script3, div3 = components(fig3)
    
    variables = {
                "bokeh_file_css": BOKEH_FILE_CSS,
                "bokeh_file_js": BOKEH_FILE_JS,
                "script1": script1,
                "div1": div1,
                "script2": script2,
                "div2": div2,
                "script3": script3,
                "div3": div3
                }
    return template("dynalog_report_patient", variables)

@dyn_app.route(PLWEB_FOLDER + '/dynalogGetReportUploads', method="POST")
def dynalogGetReportUploads():
    conn = sql.connect(config.DYNALOG_DATABASE)
    curs = conn.cursor()
    curs.execute("SELECT DISTINCT DateEntered FROM VarianDynalog")
    data = curs.fetchall()
    curs.close()
    conn.close()
    variables = {
                "data": data
                }
    return template("dynalog_report_uploads", variables)
    
    
@dyn_app.route(PLWEB_FOLDER + '/dynalog_analyze', method="POST")
def dynalog_analyze():
    if request.forms.filename_calc=="":
        return template("error_template", {"error_message": "Empty string.",
                                           "plweb_folder": PLWEB_FOLDER})
    ziparchive, filename = request.forms.filename_calc.split(",,,")
    mlc = request.forms.mlc

    temp_folder = tempfile.mkdtemp(prefix="Temp_dynalog_", dir=config.TEMP_DYNALOG_FOLDER)
    try:
        with zipfile.ZipFile(os.path.join(config.DYNALOG_ARCHIVE, ziparchive), 'r') as z:
            z.extract("A" + filename + ".dlg", path=temp_folder)
            z.extract("B" + filename + ".dlg", path=temp_folder)
    except:
        return template("error_template", {"error_message": "Cannot extract dynalogs from zip archive.",
                                           "plweb_folder": PLWEB_FOLDER})
    config_ini = configparser.ConfigParser()
    config_ini.read(config.DYNALOG_CONFIG)
    exclude_beam_off = True if config_ini["Dynalog"]["EXCLUDE_BEAM_OFF"]=="True" else False

    try:
        log = general_functions.VarianDynalog(general_functions.get_dataset_from_dlg(os.path.join(temp_folder, "A" + filename + ".dlg"), exclude_beam_off=exclude_beam_off))
    except:
        return template("error_template", {"error_message": "Cannot analyze dynalogs.",
                                           "plweb_folder": PLWEB_FOLDER})

    time = os.path.basename(filename).split("_")[0]
    record = datetime.datetime.strptime(str(time), '%Y%m%d%H%M%S')
    
    # Plot MLC positions:
    MLC_nr = log.MLC_number
    num_snapshots = log.number_of_snapshots
    snap = 0 # start with first snapshot
    dt = 0.05 # seconds

    # Actual positions of leaves
    positionsA = np.asarray(log.bankA_actual).reshape(int(MLC_nr/2), num_snapshots)
    positionsB = np.asarray(log.bankB_actual).reshape(int(MLC_nr/2), num_snapshots)

    # Planned positions of leaves
    positionsA_plan = np.asarray(log.bankA_expected).reshape(int(MLC_nr/2), num_snapshots)
    positionsB_plan = np.asarray(log.bankB_expected).reshape(int(MLC_nr/2), num_snapshots)

    diffA = positionsA - positionsA_plan
    diffB = positionsB - positionsB_plan
    carriageA = log.carriageA_actual
    carriageB = log.carriageB_actual
    
    speedA_actual = np.diff(positionsA, axis = 1)/dt
    speedB_actual = np.diff(positionsB, axis = 1)/dt

    # Suppose speed is zero at t=0
    speedA_actual = np.hstack((np.zeros((speedA_actual.shape[0], 1)), speedA_actual))
    speedB_actual = np.hstack((np.zeros((speedB_actual.shape[0], 1)), speedB_actual))

    beam_on = log.beam_on
    beam_hold = log.beam_hold

    rmsA_on = np.sqrt(np.mean(np.square(diffA[:, beam_on==1]), axis=1))
    rmsB_on = np.sqrt(np.mean(np.square(diffB[:, beam_on==1]), axis=1))
    rmsA_hold = np.sqrt(np.mean(np.square(diffA[:, (beam_on==1)&(beam_hold==0)]), axis=1))
    rmsB_hold = np.sqrt(np.mean(np.square(diffB[:, (beam_on==1)&(beam_hold==0)]), axis=1))

    diffA_max_on = np.max(np.abs(diffA[:, beam_on==1]))
    diffB_max_on = np.max(np.abs(diffB[:, beam_on==1]))
    diffA_max_hold = np.max(np.abs(diffA[:, (beam_on==1)&(beam_hold==0)]))
    diffB_max_hold = np.max(np.abs(diffB[:, (beam_on==1)&(beam_hold==0)]))

    jaw_x1 = np.asarray((log.x1))
    jaw_x2 = np.asarray((log.x2))
    jaw_y1 = np.asarray((log.y1))
    jaw_y2 = np.asarray((log.y2))

    if mlc == "Varian_120":
        MLC_width = MLC_DYNALOG["Varian_120"]
    elif mlc == "Varian_80":
        MLC_width = MLC_DYNALOG["Varian_80"]
    elif mlc == "Varian_120HD":
        MLC_width = MLC_DYNALOG["Varian_120HD"]
    else:
        return template("error_template", {"error_message": "Cannot recognize MLC type.",
                                           "plweb_folder": PLWEB_FOLDER})

    MLC_width = np.asarray(MLC_width).reshape(-1, 1)/10.0  # DIvide by 10 because it is in mm.

    if 2*(MLC_width.shape[0]-1) != MLC_nr:
        return template("error_template", {"error_message": "Inconsistent number of MLC leaves.",
                                           "plweb_folder": PLWEB_FOLDER})

    mlc_points = []
    mlc_points_plan = []
    x1 = []
    y1 = []
    x2 = []
    y2 = []
    x1_plan = []
    y1_plan = []
    x2_plan = []
    y2_plan = []
    jawX = []
    jawY = []
    p1x = []
    p1y = []
    p2x = []
    p2y = []
    p3x = []
    p3y = []
    p4x = []
    p4y = []

    for s in np.arange(0, num_snapshots, 1):

        mlc_points = general_functions.MLCpositions_to_points(positionsA[:, s].reshape(-1, 1), positionsB[:, s].reshape(-1, 1), MLC_width)
        # Planned positions:
        mlc_points_plan = general_functions.MLCpositions_to_points(positionsA_plan[:, s].reshape(-1, 1), positionsB_plan[:, s].reshape(-1, 1), MLC_width)

        x1.append(list(mlc_points[0][:, 0]))# These are points for both banks
        y1.append(list(mlc_points[0][:, 1]))
        x2.append(list(mlc_points[1][:, 0]))
        y2.append(list(mlc_points[1][:, 1]))

        x1_plan.append(list(mlc_points_plan[0][:, 0]))  # These are original points for banks
        y1_plan.append(list(mlc_points_plan[0][:, 1]))
        x2_plan.append(list(mlc_points_plan[1][:, 0]))
        y2_plan.append(list(mlc_points_plan[1][:, 1]))

        # Text coordinates:
        x1j = jaw_x1[s]
        x2j = jaw_x2[s]
        y1j = jaw_y1[s]
        y2j = jaw_y2[s]
        p1x.append([(x1j+x2j)/2])
        p1y.append([(y1j+y1j)/2])
        p2x.append([(x2j+x2j)/2])
        p2y.append([(y1j+y2j)/2])
        p3x.append([(x1j+x2j)/2])
        p3y.append([(y2j+y2j)/2])
        p4x.append([(x1j+x1j)/2])
        p4y.append([(y1j+y2j)/2])

        #  Jaws:
        jawX.append([x2j, x1j, x1j, x2j, x2j])
        jawY.append([y2j, y2j, y1j, y1j, y2j])
        
    CAX1x = [21, -21]
    CAX1y = [0, 0]
    CAX2x = [0, 0]
    CAX2y = [-21, 21]
    
    # Here we start drawing:
    fig = figure(x_range=[-21, 21], y_range=[-21, 21],
                 plot_width=500, plot_height=500, title="", match_aspect=True,
                 toolbar_location="right",
                 tools=["pan, wheel_zoom, box_zoom, reset, save"])

    fig.xgrid.grid_line_color = None
    fig.ygrid.grid_line_color = None

    if snap >= num_snapshots:
        snap = num_snapshots-1

    x1e = x1[snap]
    y1e = y1[snap]
    x2e = x2[snap]
    y2e = y2[snap]
    x1_plane = x1_plan[snap]
    y1_plane = y1_plan[snap]
    x2_plane = x2_plan[snap]
    y2_plane = y2_plan[snap]
    jawXe = jawX[snap]
    jawYe = jawY[snap]
    p1xe = p1x[snap]
    p1ye = p1y[snap]
    p2xe = p2x[snap]
    p2ye = p2y[snap]
    p3xe = p3x[snap]
    p3ye = p3y[snap]
    p4xe = p4x[snap]
    p4ye = p4y[snap]
    text_x1 = ["X1"]*num_snapshots
    text_x2 = ["X2"]*num_snapshots
    text_y1 = ["Y1"]*num_snapshots
    text_y2 = ["Y2"]*num_snapshots
    text_x1e = ["X1"]
    text_x2e = ["X2"]
    text_y1e = ["Y1"]
    text_y2e = ["Y2"]

    source_full = ColumnDataSource(data=dict(x1=x1, x2=x2, y1=y1, y2=y2,
                                        x1_plan=x1_plan, x2_plan=x2_plan,
                                        y1_plan=y1_plan, y2_plan=y2_plan
                                        ))

    source_current = ColumnDataSource(data=dict(x1e=x1e, x2e=x2e, y1e=y1e, y2e=y2e,
                                        x1_plane=x1_plane, x2_plane=x2_plane,
                                        y1_plane=y1_plane, y2_plane=y2_plane,
                                        ))

    source_jaw = ColumnDataSource(data=dict(jawX=jawX, jawY=jawY))
    source_current_jaw = ColumnDataSource(data=dict(jawXe=jawXe, jawYe=jawYe))


    source_tags_full = ColumnDataSource(data=dict(p1x=p1x, p1y=p1y, p2x=p2x,
                                                  p2y=p2y, p3x=p3x, p3y=p3y,
                                                  p4x=p4x, p4y=p4y,
                                                  text_x1=text_x1, text_x2=text_x2,
                                                  text_y1=text_y1, text_y2=text_y2))

    source_tags_current = ColumnDataSource(data=dict(p1xe=p1xe, p1ye=p1ye, p2xe=p2xe,
                                                  p2ye=p2ye, p3xe=p3xe, p3ye=p3ye,
                                                  p4xe=p4xe, p4ye=p4ye,
                                                  text_x1e=text_x1e, text_x2e=text_x2e,
                                                  text_y1e=text_y1e, text_y2e=text_y2e))

    fig.line("x1e", "y1e", line_color="blue", line_width=1, legend_label="Actual MLC", source=source_current)
    fig.line("x2e", "y2e", line_color="blue", line_width=1, source=source_current)

    # Plot planned MLC
    fig.line("x1_plane", "y1_plane", line_color="red", line_width=1, legend_label="Planned MLC", source=source_current)
    fig.line("x2_plane", "y2_plane", line_color="red", line_width=1, source=source_current)

    # Plot jaws (actual)
    fig.line("jawXe", "jawYe", source=source_current_jaw, line_color="green", line_width=2,
             legend_label="Actual Jaws")

    # Plot CAX
    fig.line(CAX1x, CAX1y, line_color="black", line_width=2)
    fig.line(CAX2x, CAX2y,  line_color="black", line_width=2)

    # Plot text (jaws):

    fig.text("p1xe", "p1ye",  text="text_y1e", source=source_tags_current,
             text_align='center', text_baseline='top',
             text_font_size=bokeh_value("12pt"))
    fig.text("p2xe", "p2ye", text="text_x2e", source=source_tags_current,
             text_align='left', text_baseline='middle',
             text_font_size=bokeh_value("12pt"))
    fig.text("p3xe", "p3ye", text="text_y2e", source=source_tags_current,
             text_align='center', text_baseline='bottom',
             text_font_size=bokeh_value("12pt"))
    fig.text("p4xe", "p4ye", text="text_x1e", source=source_tags_current,
             text_align='right', text_baseline='middle',
             text_font_size=bokeh_value("12pt"))

    fig.xaxis.axis_label_text_font_size = "12pt"
    fig.yaxis.axis_label_text_font_size = "12pt"
    fig.yaxis.axis_label_text_font_style = "normal"
    fig.xaxis.axis_label_text_font_style = "normal"
    fig.min_border = 0

    # Plot Bokeh plots of motion
    x = list(np.arange(0.5, int(MLC_nr/2)+0.5, 1))
    z1 = [list(i) for i in diffA.T]
    y1_new = z1[0]
    z2 = [list(i) for i in diffB.T]
    y2_new = z2[0]

    colorg = ["blue"]*int(MLC_nr/2)
    colorr = ["red"]*int(MLC_nr/2)

    A = [list(i) for i in speedA_actual.T]
    A1 = A[0]
    B = [list(i) for i in speedB_actual.T]
    B1 = B[0]

    left = np.arange(0, int(MLC_nr/2), 1)+0.5
    right = np.arange(1, int(MLC_nr/2)+1, 1)+0.5

    source_full_new = ColumnDataSource(data=dict(z1=z1, z2=z2,
                                                 A=A,  B=B))
    source_current_new = ColumnDataSource(data=dict(x=x, y1_new=y1_new, y2_new=y2_new,
                                          A1=A1, B1=B1, left=left,
                                          right=right,
                                          colorg=colorg, colorr=colorr, beam_on=[beam_on]*len(x)))

    y_max2 = np.max([np.abs(speedA_actual), np.abs(speedB_actual)])
    y_max = np.max([np.abs(diffA), np.abs(diffB)])

    fig_bokeh = figure(x_range=[0, int(MLC_nr/2)+1], plot_width=400,
                       y_range= [-y_max, y_max], title="X(actual) - X(expected) [cm]",
                       plot_height=250, toolbar_location="right",
                       tools = ["pan, wheel_zoom, box_zoom, reset, save"])

    fig_bokeh.quad(top="y1_new", bottom=0, left="left", right="right", source=source_current_new, fill_color="colorg",
                   line_color="blue", fill_alpha=0.5, line_alpha=0.5)

    fig_bokeh.quad(top="y2_new", bottom=0, left="left", right="right", source=source_current_new, fill_color="colorr",
                   line_color="red", fill_alpha=0.5, line_alpha=0.5)

    fig_bokeh.title.align = "center"

    # Second plot:
    fig_bokeh2 = figure(x_range=[0, int(MLC_nr/2)+1], plot_width=400,
                       y_range= [-y_max2, y_max2], title="Actual speed at isocenter [cm/s]",
                       plot_height=250, toolbar_location="right",
                      tools = ["pan, wheel_zoom, box_zoom, reset, save"])

    fig_bokeh2.quad(top="A1", bottom=0, left="left", right="right", source=source_current_new, fill_color="colorg",
                   line_color="blue", fill_alpha=0.5, line_alpha=0.5)

    fig_bokeh2.quad(top="B1", bottom=0, left="left", right="right", source=source_current_new, fill_color="colorr",
                   line_color="red", fill_alpha=0.5, line_alpha=0.5)

    fig_bokeh2.title.align = "center"

    slider = Slider(start=0, end=int(num_snapshots)-1, value=int(snap), step=1, title="Snapshot")

    callback = CustomJS(args=dict(source_current=source_current,
                                  source_full=source_full,
                                  source_jaw=source_jaw,
                                  source_current_jaw=source_current_jaw,
                                  source_tags_current=source_tags_current,
                                  source_tags_full=source_tags_full,
                                  source_current_new=source_current_new,
                                  source_full_new=source_full_new), code="""

                var data = source_current.data;
                var f = cb_obj.value;
                var data_full = source_full.data;
                var data_full_new = source_full_new.data;
                var data_current_new = source_current_new.data;
                var data_jaws_full = source_jaw.data;
                var data_jaws = source_current_jaw.data;
                var data_tags_full = source_tags_full.data;
                var data_tags_current = source_tags_current.data;

                var x1 = data_full['x1'];
                var x2 = data_full['x2'];
                var y1 = data_full['y1'];
                var y2 = data_full['y2'];
                var x1_plan = data_full['x1_plan'];
                var x2_plan = data_full['x2_plan'];
                var y1_plan = data_full['y1_plan'];
                var y2_plan = data_full['y2_plan'];
                var jawX = data_jaws_full['jawX'];
                var jawY = data_jaws_full['jawY'];
                var p1x = data_tags_full['p1x'];
                var p1y = data_tags_full['p1y'];
                var p2x = data_tags_full['p2x'];
                var p2y = data_tags_full['p2y'];
                var p3x = data_tags_full['p3x'];
                var p3y = data_tags_full['p3y'];
                var p4x = data_tags_full['p4x'];
                var p4y = data_tags_full['p4y'];
                var text_x1 = data_tags_full['text_x1'];
                var text_x2 = data_tags_full['text_x2'];
                var text_y1 = data_tags_full['text_y1'];
                var text_y2 = data_tags_full['text_y2'];

                for (var i = 0; i < x1[0].length; i++) {
                    data['x1e'][i] = parseFloat(x1[parseInt(f)][i]);
                    data['y1e'][i] = parseFloat(y1[parseInt(f)][i]);
                    data['x2e'][i] = parseFloat(x2[parseInt(f)][i]);
                    data['y2e'][i] = parseFloat(y2[parseInt(f)][i]);
                    data['x1_plane'][i] = parseFloat(x1_plan[parseInt(f)][i]);
                    data['y1_plane'][i] = parseFloat(y1_plan[parseInt(f)][i]);
                    data['x2_plane'][i] = parseFloat(x2_plan[parseInt(f)][i]);
                    data['y2_plane'][i] = parseFloat(y2_plan[parseInt(f)][i]);
                }
                for (var j = 0; j < jawX[0].length; j++){
                    data_jaws['jawXe'][j] = jawX[parseInt(f)][j];
                    data_jaws['jawYe'][j] = jawY[parseInt(f)][j];
                }
                
                data_tags_current['p1xe'] = p1x[parseInt(f)];
                data_tags_current['p1ye'] = p1y[parseInt(f)];
                data_tags_current['p2xe'] = p2x[parseInt(f)];
                data_tags_current['p2ye'] = p2y[parseInt(f)];
                data_tags_current['p3xe'] = p3x[parseInt(f)];
                data_tags_current['p3ye'] = p3y[parseInt(f)];
                data_tags_current['p4xe'] = p4x[parseInt(f)];
                data_tags_current['p4ye'] = p4y[parseInt(f)];

                data_tags_current['text_x1e'] = text_x1[parseInt(f)];
                data_tags_current['text_x2e'] = text_x2[parseInt(f)];
                data_tags_current['text_y1e'] = text_y1[parseInt(f)];
                data_tags_current['text_y2e'] = text_y2[parseInt(f)];

                var x = data_current_new['x'];
                var beam_on = data_current_new['beam_on'][0];
    
                for (var i = 0; i < x.length; i++) {
                    data_current_new['y1_new'][i] = data_full_new['z1'][f][i];
                    data_current_new['y2_new'][i] = data_full_new['z2'][f][i];
                    data_current_new['A1'][i] = data_full_new['A'][f][i];
                    data_current_new['B1'][i] = data_full_new['B'][f][i];
                    if (parseInt(beam_on[f]) == 1){
                        data_current_new['colorr'][i]='red';
                        data_current_new['colorg'][i]='blue';
                        }
                    else{
                        data_current_new['colorr'][i]='white';
                        data_current_new['colorg'][i]='white';
                    }
                }
                parent.beamOnOff(parseInt(f));
                source_current.change.emit();
                source_current_new.change.emit();

        """)
    slider.js_on_change('value', callback)

    size = "12pt"
    fig_bokeh.yaxis.axis_label_text_font_style = "normal"
    fig_bokeh.yaxis.axis_label_text_font_size = size
    fig_bokeh.title.text_font_size = size
    fig_bokeh.xgrid.grid_line_color = None
    fig_bokeh.ygrid.grid_line_color = None

    size = "12pt"
    fig_bokeh2.yaxis.axis_label_text_font_style = "normal"
    fig_bokeh2.yaxis.axis_label_text_font_size = size
    fig_bokeh2.title.text_font_size = size
    fig_bokeh2.xgrid.grid_line_color = None
    fig_bokeh2.ygrid.grid_line_color = None

    layout_bokeh = layout([
                        [Column(slider, width=550)],
                        [fig, [fig_bokeh, fig_bokeh2]]
                        ]
                        )

    script1, div1 = components(layout_bokeh)

    # Plot fluences
    DTA = float(request.forms.gamma_DTA)
    DD = float(request.forms.gamma_DD)
    resolution = float(request.forms.gamma_res)
    threshold = float(request.forms.gamma_thres)
    gamma_tol_str = str(DD)+" / "+str(DTA)+" / "+str(threshold)+" / "+str(resolution)

    dose_ref = log.log.fluence.actual.calc_map(resolution=resolution)
    dose_eval = log.log.fluence.expected.calc_map(resolution=resolution)

    gamma_map = log.log.fluence.gamma.calc_map(doseTA=DD, distTA=DTA, threshold=threshold, resolution=resolution)

    size_x = 9
    size_y = 9
    
    fig1 = Figure(figsize=(size_x, size_y), tight_layout={"w_pad":1})
    ax1 = fig1.add_subplot(2, 2, 1)
    ax2 = fig1.add_subplot(2, 2, 2)
    ax3 = fig1.add_subplot(2, 2, 3)
    ax4 = fig1.add_subplot(2, 2, 4)

    cmap = matplotlib.cm.jet
    cmap_gamma = matplotlib.cm.inferno_r

    ax1.imshow(dose_ref.astype(np.float32, copy=False), cmap=cmap, interpolation='nearest',
               aspect="auto", vmin=0, origin="lower", vmax=np.max(dose_eval))
    ax1.autoscale(False)
    ax1.set_title("Actual Fluence")

    ax2.imshow(dose_eval.astype(np.float32, copy=False), cmap=cmap, interpolation='nearest',
               aspect="auto", vmin=0, origin="lower", vmax=np.max(dose_eval))
    ax2.autoscale(False)
    ax2.set_title("Expected Fluence")
    
    gam = ax3.imshow(gamma_map.astype(np.float32, copy=False), cmap=cmap_gamma, interpolation='nearest',
               aspect="auto", origin="lower", vmin=0, vmax=1)
    ax3.autoscale(False)
    ax3.set_title("Gamma map")
    cax0 = fig1.add_axes([ax3.get_position().x1-0.08, ax3.get_position().y0-0.02, 0.02, ax3.get_position().height])
    cb0 = fig1.colorbar(gam, ax=ax3, cax=cax0)
    cb0.outline.set_edgecolor('white')

    # Calculate threshold line to show it on gamma map:
    #level = np.max(dose_ref)*threshold
    #ax1.contour(np.flipud(dose_ref), levels=[level], colors = ["blue"])  # threshold
    #ax2.contour(np.flipud(dose_ref), levels=[level], colors = ["blue"])  # threshold
    #ax3.contour(np.flipud(dose_ref), levels=[level], colors = ["blue"])  # threshold
    #ax4.contour(np.flipud(dose_ref), levels=[level], colors = ["blue"])  # threshold

    dose_ref[dose_ref < np.max(dose_ref)*threshold] = np.nan
    dose_eval[dose_eval < np.max(dose_ref)*threshold] = np.nan

    fluence_difference = 100*(dose_ref-dose_eval)/dose_eval

    diff = ax4.imshow(fluence_difference.astype(np.float32, copy=False), cmap=cmap, interpolation="nearest",
                      aspect="auto", origin="lower", vmin=-5, vmax=5)
    ax4.autoscale(False)
    ax4.set_title("100 x (Actual-Expected)/Expected [%]")
    cax1 = fig1.add_axes([ax4.get_position().x1-0.01, ax4.get_position().y0-0.02, 0.02, ax4.get_position().height])
    fig1.colorbar(diff, ax=ax4, cax=cax1)
 
    #fig1.tight_layout()
    script2 = mpld3.fig_to_html(fig1, d3_url=D3_URL, mpld3_url=MPLD3_URL)
    general_functions.delete_figure([fig1])

    # Gamma histogram:
    gamma_avg = log.log.fluence.gamma.avg_gamma
    gamma_prcnt = log.log.fluence.gamma.pass_prcnt
    gamma_avg = round(gamma_avg, 2) if np.isfinite(gamma_avg) else "NA"
    gamma_prcnt = round(gamma_prcnt, 1) if np.isfinite(gamma_prcnt) else "NA"
    upper_bound = 1
    upper_outliers = np.sum(gamma_map.flatten()>upper_bound)

    fig2 = figure(x_range=[0, 1.1], y_range=[0.5, np.sum(gamma_map >= 0)], y_axis_type="log",
                 plot_width=340, plot_height=250, title="Gamma histogram",
                 toolbar_location="right",
                 tools=["pan, wheel_zoom, box_zoom, reset, save"])
    fig2.xgrid.grid_line_color = None
    fig2.ygrid.grid_line_color = None
    fig2.xaxis.axis_label = 'Gamma'
    fig2.yaxis.axis_label = 'Counts'
    hist2, edges2 = np.histogram(gamma_map.flatten(), density=False, bins=10, range=(0, 1))
    fig2.quad(top=hist2, bottom=0.001, left=edges2[:-1], right=edges2[1:], line_color='black')
    fig2.quad(top=upper_outliers, bottom=0.001, left=1, right=1.1, line_color='red', color='red')

    # Plot dose difference histogram:
    fluence_difference = fluence_difference[~np.isinf(fluence_difference)]
    fluence_difference = fluence_difference[~np.isnan(fluence_difference)]

    upper_bound2 = 10
    lower_bound2 = -10
    upper_outliers2 = np.sum(fluence_difference>upper_bound2)
    lower_outliers2 = np.sum(fluence_difference<lower_bound2)

    fig3 = figure(x_range=[-12, 12], y_range=[0.5, fluence_difference.size], y_axis_type="log",
                 plot_width=340, plot_height=250, title="Dose difference histogram, avg. = " + str(round(np.average(fluence_difference), 1)),
                 toolbar_location="right",
                 tools=["pan, wheel_zoom, box_zoom, reset, save"])
    fig3.xgrid.grid_line_color = None
    fig3.ygrid.grid_line_color = None
    fig3.xaxis.axis_label = 'Dose difference [%]'
    fig3.yaxis.axis_label = 'Counts'
    
    hist3, edges3 = np.histogram(fluence_difference, density=False, bins=20, range=(lower_bound2, upper_bound2))
    fig3.quad(top=hist3, bottom=0.001, left=edges3[:-1], right=edges3[1:], line_color='black')
    fig3.quad(top=upper_outliers2, bottom=0.001, left=10, right=11, line_color='red', color='red')
    fig3.quad(top=lower_outliers2, bottom=0.001, left=-11, right=-10, line_color='red', color='red')
    
    script3, div3 = components(row(fig2, fig3))

    # plot rms histograms
    fig4 = Figure(figsize=(10, 8), tight_layout={"w_pad":1})
    ax5 = fig4.add_subplot(2, 2, 1)
    ax55 = fig4.add_subplot(2, 2, 2)
    ax6 = fig4.add_subplot(2, 2, 3)
    ax66 = fig4.add_subplot(2, 2, 4)

    ax5.bar(np.arange(0.5, int(MLC_nr/2)+0.5, 1), rmsA_on, width=1, color="blue", edgecolor="None", alpha=0.5)
    ax5.bar(np.arange(0.5, int(MLC_nr/2)+0.5, 1), rmsB_on, width=1, color="None", edgecolor="red", alpha=1)
    ax55.bar(np.arange(0.5, int(MLC_nr/2)+0.5, 1), rmsA_hold, width=1, color="blue", edgecolor="None", alpha=0.5)
    ax55.bar(np.arange(0.5, int(MLC_nr/2)+0.5, 1), rmsB_hold, width=1, color="None", edgecolor="red", alpha=1)

    top = ax5.get_ylim()[1]
    max_patch = np.max([np.max(rmsA_on), np.max(rmsB_on)])
    ax5.add_patch(patches.Rectangle((0.44*MLC_nr, 0.95*top), 3, max_patch/25, alpha=0.5, edgecolor="none", facecolor="red"))
    ax5.annotate("A", (0.44*MLC_nr+4, 0.95*top), color='black', fontsize=10, ha='left', va='bottom')

    ax5.add_patch(patches.Rectangle((0.44*MLC_nr, 0.90*top), 3, max_patch/25, alpha=0.5, edgecolor="blue", facecolor="None"))
    ax5.annotate("B", (0.44*MLC_nr+4, 0.90*top), color='black', fontsize=10, ha='left', va='bottom')

    ax6.bar(np.arange(0.5, int(MLC_nr/2)+0.5, 1), np.max(np.abs(diffA[:, beam_on==1]), axis=1), width=1, color="blue",edgecolor="None", alpha=0.5)
    ax6.bar(np.arange(0.5, int(MLC_nr/2)+0.5, 1), np.max(np.abs(diffB[:, beam_on==1]), axis=1), width=1, color="None", edgecolor="red", alpha=1)
    ax66.bar(np.arange(0.5, int(MLC_nr/2)+0.5, 1), np.max(np.abs(diffA[:, (beam_on==1)&(beam_hold==0)]), axis=1), width=1, color="blue", edgecolor="None", alpha=0.5)
    ax66.bar(np.arange(0.5, int(MLC_nr/2)+0.5, 1), np.max(np.abs(diffB[:, (beam_on==1)&(beam_hold==0)]), axis=1), width=1, color="None", edgecolor="red", alpha=1)

    ax5.set_title("RMS - beam ON")
    ax55.set_title("RMS - beam ON and no holdoffs")
    ax5.set_ylabel('[cm]')
    ax55.set_ylim(ax5.get_ylim())

    ax66.set_title("MAX(ABS) - beam ON and no holdoffs")
    ax6.set_title("MAX(ABS(Act.-Exp.)) - beam ON")
    ax6.set_ylabel('[cm]')
    ax66.set_ylim(ax6.get_ylim())

    #fig4.tight_layout()
    script_MLC_rms = mpld3.fig_to_html(fig4, d3_url=D3_URL, mpld3_url=MPLD3_URL)
    general_functions.delete_figure([fig4])

    # Dose rate and gantry plot

    # Calculate gantry speed
    def f(a1, a2):
        # Calculate angle increment
        return 180 - abs(abs(a1 - a2) - 180)

    gantry = log.gantry
    muu = log.mu
    MU = list(muu/muu[-1])
    DR = list(np.diff(np.hstack((0, muu/muu[-1])))/dt)
    
    gantry_sum = 0
    gantry_sum_full = []
    for g in np.arange(0, gantry.shape[0]-1, 1):
        gantry_sum += f(gantry[g+1], gantry[g])
        gantry_sum_full.append(gantry_sum)

    # Do not pick every element:
    M = 2  #every M-th element
    MM = 3
    smooth_window = 7
    polyorder = 1
    
    gantry_sum_full_smooth = savgol_filter(gantry_sum_full[0:-1:M], window_length=smooth_window, polyorder=polyorder)
    gantry_speed = np.hstack((np.array([0]), np.diff(gantry_sum_full_smooth[0:-1:MM])/(M*MM*dt)))
    gantry_speed2 = np.hstack((np.array([0]), np.diff(gantry_sum_full)/dt))
    
    MU_smooth = savgol_filter(MU[0:-1:M], window_length=smooth_window, polyorder=polyorder)
    dose_rate_actual_full = np.hstack((np.array([0]), 60.0*np.diff(MU_smooth[0:-1:MM])/(M*MM*dt)))
    dose_rate_actual_full2 = np.hstack((np.array([0]), 60.0*np.diff(MU)/dt))
    
    fig5 = Figure(figsize=(10, 8), tight_layout={"w_pad":1})
    ax7 = fig5.add_subplot(2, 2, 3)
    ax8 = fig5.add_subplot(2, 2, 1)
    ax9 = fig5.add_subplot(2, 2, 4)
    ax10 = fig5.add_subplot(2, 2, 2)
    
    ax7.plot(np.arange(0, len(dose_rate_actual_full), 1)*dt*MM*M, dose_rate_actual_full, color="blue", drawstyle='steps')
    ax7.plot(np.arange(0, len(dose_rate_actual_full2), 1)*dt, dose_rate_actual_full2, color="blue", drawstyle='steps',  alpha=0.1)
    ax7.set_title("Actual dose rate")
    ax7.set_ylabel('[1/min] x Monitor Units')
    ax7.set_xlabel("Time [s]")
    ax7.set_ylim([0, np.max(dose_rate_actual_full2)*1.05])

    ax8.step(np.arange(0, len(beam_on), 1)*dt, beam_on, color="blue", where='post', alpha=0.8)
    ax8.plot(np.arange(0, len(MU), 1)*dt, MU, color="green")
    
    ax8.set_ylim([0, 1.5])
    top2 = ax8.get_ylim()[1]
    right2 = ax8.get_xlim()[1]
    ax8.add_patch(patches.Rectangle((right2*0.75, 0.90*top2), right2/25, 1/25, alpha=0.5, edgecolor="none", facecolor="blue"))
    ax8.annotate("Beam on", (right2*0.8, 0.90*top2), color='black', fontsize=10, ha='left', va='bottom')

    ax8.add_patch(patches.Rectangle((right2*0.75, 0.95*top2), right2/25, 1/25, alpha=0.5, edgecolor="none", facecolor="green"))
    ax8.annotate("MU", (right2*0.8, 0.95*top2), color='black', fontsize=10, ha='left', va='bottom')

    ax8.set_title("Beam on, MU vs time")
    ax8.set_xlabel("Time [s]")
    ax8.set_ylabel("ON = 1, OFF = 0")

    ax9.plot(np.arange(0, len(gantry), 1)*dt, gantry, color="blue", drawstyle='steps')
    ax9.set_title("Gantry (actual)")
    ax9.set_ylabel('[degree]')
    ax9.set_xlabel("Time [s]")

    ax10.plot(np.arange(0, len(gantry_speed), 1)*dt*M*MM, gantry_speed, color="blue", drawstyle='steps')
    ax10.plot(np.arange(0, len(gantry_speed2), 1)*dt, gantry_speed2, color="blue", drawstyle='steps', alpha=0.1)
    ax10.set_title("Gantry speed (actual), avg. = "+str(round(np.average(gantry_speed), 1)))
    ax10.set_ylabel('[degree/s]')
    ax10.set_xlabel("Time [s]")
    ax10.set_ylim([0, np.max(gantry_speed2)*1.05])

    #fig5.tight_layout()
    script_dose_rate = mpld3.fig_to_html(fig5, d3_url=D3_URL, mpld3_url=MPLD3_URL)
    general_functions.delete_figure([fig5])
    
    # Plot Carriage and motions
    fig6 = Figure(figsize=(10, 4), tight_layout={"w_pad":1})
    ax11 = fig6.add_subplot(1, 2, 1)
    ax12 = fig6.add_subplot(1, 2, 2)

    ax11.plot(np.arange(0, num_snapshots, 1), carriageA, color="red")
    ax11.set_title("Carriage A position (actual)")
    ax11.set_ylabel('[cm]')
    ax11.set_xlabel("Snapshots")

    ax12.plot(np.arange(0, num_snapshots, 1), carriageB, color="green")
    ax12.set_title("Carriage B position (actual)")
    ax12.set_ylabel('[cm]')
    ax12.set_xlabel("Snapshots")

    #fig6.tight_layout()
    script_carriage = mpld3.fig_to_html(fig6, d3_url=D3_URL, mpld3_url=MPLD3_URL)
    general_functions.delete_figure([fig6])

    std_threshold = 0.01
    std_A = np.std(positionsA, axis=1)
    std_B = np.std(positionsB, axis=1)
    
    rmsA_on[std_A <= std_threshold] = np.nan
    rmsB_on[std_B <= std_threshold] = np.nan
    rmsA_hold[std_A <= std_threshold] = np.nan
    rmsB_hold[std_B <= std_threshold] = np.nan

    variables = {
                "record": record,
                "patient_name": log.patient_name[2],
                "beam_id": log.beam_id,
                "num_snapshots": num_snapshots,
                "num_beamholds": log.log.num_beamholds,
                "tolerance": log.tolerance,
                "beam_on": list(log.beam_on),
                "beam_hold": list(log.beam_hold),
                "gantry": list(gantry),
                "time": log.time_line,
                "collimator": list(log.collimator),
                "x1": list(log.x1),
                "x2": list(log.x2),
                "y1": list(log.y1),
                "y2": list(log.y2),
                "MU": MU,
                "DR": DR,
                "gamma_avg": gamma_avg,
                "gamma_prcnt": gamma_prcnt,
                "gamma_tol_str": gamma_tol_str,
                "rmsA_max_on": round(np.nanmax(rmsA_on)*10, 2),
                "rmsB_max_on": round(np.nanmax(rmsB_on)*10, 2),
                "rmsA_max_hold": round(np.nanmax(rmsA_hold)*10, 2),
                "rmsB_max_hold": round(np.nanmax(rmsB_hold)*10, 2),
                "diffA_max_on": round(diffA_max_on*10, 2),
                "diffB_max_on": round(diffB_max_on*10, 2),
                "diffA_max_hold": round(diffA_max_hold*10, 2),
                "diffB_max_hold": round(diffB_max_hold*10, 2),
                "rmsA_on": np.round(10*np.nan_to_num(rmsA_on, copy=True), 2),
                "rmsB_on": np.round(10*np.nan_to_num(rmsB_on, copy=True), 2),
                "rmsA_hold": np.round(10*np.nan_to_num(rmsA_hold, copy=True), 2),
                "rmsB_hold": np.round(10*np.nan_to_num(rmsB_hold, copy=True), 2),
                "rmsA_on_avg": round(10*np.nanmean(rmsA_on), 2),
                "rmsB_on_avg": round(10*np.nanmean(rmsB_on), 2),
                "rmsA_hold_avg": round(10*np.nanmean(rmsA_hold), 2),
                "rmsB_hold_avg": round(10*np.nanmean(rmsB_hold), 2),
                "npnan": np.nan,
                "bokeh_file_css": BOKEH_FILE_CSS,
                "bokeh_file_js": BOKEH_FILE_JS,
                "bokeh_widgets_css": BOKEH_WIDGETS_CSS,
                "bokeh_widgets_js": BOKEH_WIDGETS_JS,
                "script1": script1,
                "div1": div1,
                "script2": script2,
                "script3": script3,
                "div3": div3,
                "script_MLC_rms": script_MLC_rms,
                "script_dose_rate": script_dose_rate,
                "script_carriage": script_carriage
            }
    general_functions.delete_files_in_subfolders([temp_folder]) # Delete image
    gc.collect()
    return template("dynalog_analysis", variables)


@dyn_app.route(PLWEB_FOLDER + '/dynalogHistograms', method="POST")
def dynalogHistograms():
    # Function that calculates histograms from a particular date onwards till date2.
    date = request.forms.hidden_date
    date2 = request.forms.hidden_date2
    density = True if request.forms.hidden_histdensity=="true" else False
    log = True if request.forms.hidden_histlog=="true" else False

    # Define function for drawing histograms
    def plot_histogram(fig, data, x_lower, x_upper, x_label, y_label, legend_label,
                       bins, log_style, density):
        upper_outliers = np.sum(data > x_upper)
        if fig == None:
            fig = figure(x_range=[x_lower, x_upper+(x_upper-x_lower)/bins], 
                         y_axis_type="log"if log_style==True else "linear", title=y_label,
                         toolbar_location="above",  tools=["pan, wheel_zoom, box_zoom, reset, save"])
            fig.xgrid.grid_line_color = None
            fig.ygrid.grid_line_color = None
            fig.xaxis.axis_label = x_label
            fig.yaxis.axis_label = y_label
            fig.y_range.start = 0.1 if log_style==True else 0

        hist, edges = np.histogram(data, density=False, bins=bins, range=(x_lower, x_upper))
        bin_width = (x_upper-x_lower)/bins
        
        if density:
            normalization = 1.0/((np.sum(hist)+upper_outliers)*bin_width)
            hist = hist*normalization
            upper_outliers = upper_outliers*normalization

        f = fig.quad(top=hist, bottom=0.0001 if log_style==True else 0, left=edges[:-1], right=edges[1:],
                     fill_alpha=0.5, line_color='black')
        f_outlier = fig.quad(top=upper_outliers, bottom=0.0001 if log_style==True else 0, left=x_upper,
                             right=x_upper+bin_width, line_color='red', color='red',
                             fill_alpha=0.5)
        return [fig, [f_outlier, f]]

    conn = sql.connect(config.DYNALOG_DATABASE)
    curs = conn.cursor()

    # Get folder (machine) list
    curs.execute("SELECT DISTINCT Repository FROM VarianDynalog")
    folders = [ca[0] for ca in curs.fetchall()]

    list_plots_maxdiff2 = []
    fig_maxdiff2 = None
    list_plots_maxdiff = []
    fig_maxdiff = None
    list_plots_rmsmax2 = []
    fig_rmsmax2 = None
    list_plots_rmsmax = []
    fig_rmsmax = None
    list_plots_gammaavg = []
    fig_gammaavg = None
    list_plots_gammaind = []
    fig_gammaind = None
    for folder in folders:
        if date == "" and date2 == "":
            curs.execute("SELECT Snapshots, Beamholds, RMSmax, RMSmax2, DIFFmax, DIFFmax2, GammaAvg, GammaIndex "\
                         "FROM VarianDynalog WHERE Repository = '"+folder+"'")
        elif date != "" and date2 == "":
            curs.execute("SELECT Snapshots, Beamholds, RMSmax, RMSmax2, DIFFmax, DIFFmax2, GammaAvg, GammaIndex "\
                         "FROM VarianDynalog WHERE Date >= '"+date+"' AND Repository = '"+folder+"'")
        elif date == "" and date2 !="":
            curs.execute("SELECT Snapshots, Beamholds, RMSmax, RMSmax2, DIFFmax, DIFFmax2, GammaAvg, GammaIndex "\
                         "FROM VarianDynalog WHERE Date <= '"+date2+"' AND Repository = '"+folder+"'")
        else:
            curs.execute("SELECT Snapshots, Beamholds, RMSmax, RMSmax2, DIFFmax, DIFFmax2, GammaAvg, GammaIndex "\
                         "FROM VarianDynalog WHERE Date BETWEEN '"+date+"' AND '"+date2+"' AND Repository = '"+folder+"'")

        data = np.asarray(curs.fetchall())

        [fig_maxdiff2, [f_outlier_maxdiff2, f_maxdiff2]] = plot_histogram(fig_maxdiff2, data[:, 5], 0, 0.5, "MAX DIFF2 [cm]",
                                                        "Probability density" if density else "Counts", folder, 25, log_style=log, density=density)
        list_plots_maxdiff2.append((folder, [f_outlier_maxdiff2, f_maxdiff2]))

        [fig_maxdiff, [f_outlier_maxdiff, f_maxdiff]] = plot_histogram(fig_maxdiff, data[:, 4], 0, 0.5, "MAX DIFF [cm]",
                                                        "Probability density" if density else "Counts", folder, 25, log_style=log, density=density)
        list_plots_maxdiff.append((folder, [f_outlier_maxdiff, f_maxdiff]))
        
        [fig_rmsmax2, [f_outlier_rmsmax2, f_rmsmax2]] = plot_histogram(fig_rmsmax2, data[:, 3], 0, 0.5, "MAX RMS2 [cm]",
                                                        "Probability density" if density else "Counts", folder, 25, log_style=log, density=density)
        list_plots_rmsmax2.append((folder, [f_outlier_rmsmax2, f_rmsmax2]))
        
        [fig_rmsmax, [f_outlier_rmsmax, f_rmsmax]] = plot_histogram(fig_rmsmax, data[:, 2], 0, 0.5, "MAX RMS [cm]",
                                                        "Probability density" if density else "Counts", folder, 25, log_style=log, density=density)
        list_plots_rmsmax.append((folder, [f_outlier_rmsmax, f_rmsmax]))
        
        [fig_gammaavg, [f_outlier_gammaavg, f_gammaavg]] = plot_histogram(fig_gammaavg, data[:, 6], 0, 1, "Gamma avg",
                                                        "Probability density" if density else "Counts", folder, 25, log_style=log, density=density)
        list_plots_gammaavg.append((folder, [f_outlier_gammaavg, f_gammaavg]))
        
        [fig_gammaind, [f_outlier_gammaind, f_gammaind]] = plot_histogram(fig_gammaind, data[:, 7], 0, 100, "Gamma index [%]",
                                                        "Probability density" if density else "Counts", folder, 25, log_style=log, density=density)
        list_plots_gammaind.append((folder, [f_outlier_gammaind, f_gammaind]))

    curs.close()
    conn.close()

    legend_maxdiff2 = Legend(items=list_plots_maxdiff2, location="center", click_policy="hide")
    fig_maxdiff2.add_layout(legend_maxdiff2, 'right')
    
    legend_maxdiff = Legend(items=list_plots_maxdiff, location="center", click_policy="hide")
    fig_maxdiff.add_layout(legend_maxdiff, 'right')
    
    legend_rmsmax2 = Legend(items=list_plots_rmsmax2, location="center", click_policy="hide")
    fig_rmsmax2.add_layout(legend_rmsmax2, 'right')
    
    legend_rmsmax = Legend(items=list_plots_rmsmax, location="center", click_policy="hide")
    fig_rmsmax.add_layout(legend_rmsmax, 'right')
    
    legend_gammaavg = Legend(items=list_plots_gammaavg, location="center", click_policy="hide")
    fig_gammaavg.add_layout(legend_gammaavg, 'right')
    
    legend_gammaind = Legend(items=list_plots_gammaind, location="center", click_policy="hide")
    fig_gammaind.add_layout(legend_gammaind, 'right')
    
    script, div = components(gridplot([[fig_maxdiff2, fig_maxdiff], [fig_rmsmax2, fig_rmsmax], [fig_gammaavg, fig_gammaind]], plot_width=650, plot_height=300))

    variables = {
                "bokeh_file_css": BOKEH_FILE_CSS,
                "bokeh_file_js": BOKEH_FILE_JS,
                "bokeh_widgets_css": BOKEH_WIDGETS_CSS,
                "bokeh_widgets_js": BOKEH_WIDGETS_JS,
                "script": script,
                "div": div,
                "date": date,
                "date2": date2
            }

    return template("dynalog_histograms", variables)

