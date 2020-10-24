import sys
import os
import numpy as np
from multiprocessing import Pool
import tempfile
import matplotlib.style
import matplotlib
matplotlib.use('Agg')
from matplotlib.figure import Figure

# To revert back to matplotlib 1.0 style
matplotlib.style.use('classic')

from pylinac import DRGS, DRMLC

parent_module = sys.modules['.'.join(__name__.split('.')[:-1]) or '__main__']
if __name__ == '__main__' or parent_module.__name__ == '__main__':
    #sys.path.append(os.path.abspath(os.path.realpath("python_packages")))
    import config
    from python_packages.bottlepy.bottle import Bottle, request, TEMPLATE_PATH, template, redirect, response
    import general_functions
    import RestToolbox_modified as RestToolbox
    from python_packages import mpld3
else:
    from . import config
    from .python_packages.bottlepy.bottle import Bottle, request, TEMPLATE_PATH, template, redirect, response
    from . import general_functions
    from . import RestToolbox_modified as RestToolbox
    from .python_packages import mpld3

CUR_DIR = os.path.realpath(os.path.dirname(__file__))

# Path to Bottle templates
TEMPLATE_PATH.insert(0, os.path.join(CUR_DIR, 'views'))

# Url to some mpld3 library
D3_URL = config.D3_URL
MPLD3_URL = config.MPLD3_URL

PI = np.pi

# MLC type for PicketFence analysis:
LEAF_TYPE = ["Varian_120", "Varian_120HD", "Varian_80", "Elekta_80", "Elekta_160"]

# Here starts the bottle server
vmat_app = Bottle()

@vmat_app.route('/vvmat', method="POST")
def vvmat():
    displayname = request.forms.hidden_displayname
    username = request.get_cookie("account", secret=config.SECRET_KEY)
    if not username:
        redirect("/login")
    try:
        variables = general_functions.Read_from_dcm_database()
        variables["displayname"] = displayname
        response.set_cookie("account", username, secret=config.SECRET_KEY, samesite="lax")
    except ConnectionError:
        return template("error_template", {"error_message": "Orthanc is refusing connection."})
    return template("vvmat", variables)


def vmat_helperf_catch_error(args):
    try:
        return vmat_helperf(args)
    except Exception as e:
        return template("error_template", {"error_message": str(e)})


def vmat_helperf(args):
    testtype = args["testtype"]
    w1 = args["w1"]
    w2 = args["w2"]
    imgdescription = args["imgdescription"]
    station = args["station"]
    displayname = args["displayname"]
    acquisition_datetime = args["acquisition_datetime"]
    general_functions.set_configuration(args["config"])
    
    # Collect data for "save results"
    dicomenergy = general_functions.get_energy_from_imgdescription(imgdescription)
    user_machine, user_energy = general_functions.get_user_machine_and_energy(station, dicomenergy)
    machines_and_energies = general_functions.get_machines_and_energies(general_functions.get_treatmentunits_vmat())
    tolerances = general_functions.get_tolerance_user_machine_vmat(user_machine)  # If user_machne has specific tolerance

    if not tolerances:
        tolerance, pdf_report_enable = general_functions.get_settings_vmat()
    else:
        tolerance, pdf_report_enable = tolerances[0]
    
    tolerance = float(tolerance)
    
    save_results = {
                    "user_machine": user_machine,
                    "user_energy": user_energy,
                    "machines_and_energies": machines_and_energies,
                    "testtype": [testtype],
                    "displayname": displayname
                    }

    if w1==w2:
        return template("error_template", {"error_message": "Selected images must not be equal. One image should be an open field,"\
                                           " the other DRGS or DRMLC."})
    try:
        temp_folder1, file_path1 = RestToolbox.GetSingleDcm(config.ORTHANC_URL, w1)
        temp_folder2, file_path2 = RestToolbox.GetSingleDcm(config.ORTHANC_URL, w2)
    except:
        return template("error_template", {"error_message": "Cannot read images."})

    try:
        if testtype == "DRGS":
            myvmat = DRGS(image_paths=(file_path1, file_path2))
        else:
            myvmat = DRMLC(image_paths=(file_path1, file_path2))
        myvmat.analyze(tolerance=tolerance)
    except Exception as e:
        return template("error_template", {"error_message": "Cannot analyze images. "+str(e)})

    fig1 = Figure(figsize=(10.5, 5), tight_layout={"w_pad":3,  "pad": 3})
    ax1 = fig1.add_subplot(1,2,1)
    ax2 = fig1.add_subplot(1,2,2)

    ax1.imshow(myvmat.open_image.array, cmap=matplotlib.cm.gray, interpolation="none", aspect="equal", origin='upper')
    ax1.set_title('Open')
    ax1.axis('off')
    myvmat._draw_segments(ax1)
    ax2.imshow(myvmat.dmlc_image, cmap=matplotlib.cm.gray, interpolation="none", aspect="equal", origin='upper')
    ax2.set_title('DMLC')
    ax2.axis('off')
    myvmat._draw_segments(ax2)
    
    mpld3.plugins.connect(fig1, mpld3.plugins.MousePosition(fontsize=14, fmt=".2f"))
    script1 = mpld3.fig_to_html(fig1, d3_url=D3_URL, mpld3_url=MPLD3_URL)

    fig2 = Figure(figsize=(10.5, 5), tight_layout={"w_pad":1, "pad": 1})
    ax3 = fig2.add_subplot(1,1,1)
    dmlc_prof, open_prof = myvmat._median_profiles((myvmat.dmlc_image, myvmat.open_image))
    
    # Taken from pylinac:
    ax3.plot(dmlc_prof.values, label='DMLC')
    ax3.plot(open_prof.values, label='Open')
    ax3.autoscale(axis='x', tight=True)
    ax3.legend(loc=8, fontsize='large')
    ax3.grid()
    ax3.set_title("Median profiles")
    ax3.margins(0.05)
    
    mpld3.plugins.connect(fig2, mpld3.plugins.MousePosition(fontsize=14, fmt=".2f"))
    script2 = mpld3.fig_to_html(fig2, d3_url=D3_URL, mpld3_url=MPLD3_URL)
    
    # Collect data
    Rcorr = [roi.r_corr for roi in myvmat.segments]
    diff_corr = myvmat.r_devs
    diff_avg_abs = round(myvmat.avg_abs_r_deviation, 2)
    max_diff_abs = round(myvmat.max_r_deviation, 2)
    segment_passed = [roi.passed for roi in myvmat.segments]
    test_passed = myvmat.passed
    
    variables = {
                "script1": script1,
                "script2": script2,
                "Rcorr": Rcorr,
                "diff_corr": diff_corr,
                "diff_avg_abs": diff_avg_abs,
                "max_diff_abs": max_diff_abs,
                "segment_passed": segment_passed,
                "test_passed": test_passed,
                "save_results": save_results,
                "pdf_report_enable": pdf_report_enable,
                "acquisition_datetime": acquisition_datetime
                }
    # Generate pylinac report:
    if pdf_report_enable == "True":
        pdf_file = tempfile.NamedTemporaryFile(delete=False, prefix="VMAT", suffix=".pdf", dir=config.PDF_REPORT_FOLDER)
        myvmat.publish_pdf(pdf_file)
        variables["pdf_report_filename"] = os.path.basename(pdf_file.name)

    general_functions.delete_files_in_subfolders([temp_folder1, temp_folder2]) # Delete image
    return template("vmat_results", variables)

@vmat_app.route('/vvmat/<w1>/<w2>/<testtype>', method="POST")
def vvmat_calculate(w1, w2, testtype):
    imgdescription = request.forms.hidden_imgdescription
    station = request.forms.hidden_station
    displayname = request.forms.hidden_displayname
    acquisition_datetime = request.forms.hidden_datetime
    
    args = {"w1": w1, "w2": w2, "testtype": testtype, "imgdescription": imgdescription,
            "station": station, "displayname": displayname, "acquisition_datetime": acquisition_datetime,
            "config": general_functions.get_configuration()}
    p = Pool(1)
    data = p.map(vmat_helperf_catch_error, [args])
    p.close()
    p.join()
    return data