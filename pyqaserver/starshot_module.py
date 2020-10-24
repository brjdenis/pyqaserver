import sys
import os
import tempfile
from multiprocessing import Pool
import datetime
import numpy as np
import matplotlib.style
import matplotlib
matplotlib.use('Agg')
from matplotlib.figure import Figure

# To revert back to matplotlib 1.0 style
matplotlib.style.use('classic')

from pylinac import Starshot as Starshot

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

# Here starts the bottle server
ss_app = Bottle()

@ss_app.route('/starshot', method="POST")
def starshot_module():
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
    return template("starshot", variables)


def starshot_helperf_catch_error(args):
    try:
        return starshot_helperf(args)
    except Exception as e:
        return template("error_template", {"error_message": str(e)})


def starshot_helperf(args):
    imgtype = args["imgtype"]
    w = args["w"]
    clip_box = args["clip_box"]
    radius = args["radius"]
    min_peak_height = args["min_peak_height"]
    start_x = args["start_x"]
    start_y = args["start_y"]
    dpi = args["dpi"]
    sid = args["sid"]
    fwhm = args["fwhm"]
    recursive = args["recursive"]
    invert = args["invert"]
    temp_folder = args["temp_folder"]
    file_path = args["file_path"]
    imgdescription = args["imgdescription"]
    station = args["station"]
    displayname = args["displayname"]
    acquisition_datetime = args["acquisition_datetime"]
    general_functions.set_configuration(args["config"])

    # Collect data for "save results"
    dicomenergy = general_functions.get_energy_from_imgdescription(imgdescription)
    user_machine, user_energy = general_functions.get_user_machine_and_energy(station, dicomenergy)
    machines_and_energies = general_functions.get_machines_and_energies(general_functions.get_treatmentunits_starshot())
    tolerances = general_functions.get_tolerance_user_machine_starshot(user_machine)  # If user_machne has specific tolerance
    if not tolerances:
        tolerance, pdf_report_enable = general_functions.get_settings_starshot()
    else:
        tolerance, pdf_report_enable = tolerances[0]

    tolerance = float(tolerance)  # If more than this, the test is "borderline", but not "failed"
    
    save_results = {
                    "user_machine": user_machine,
                    "user_energy": user_energy,
                    "machines_and_energies": machines_and_energies,
                    "testtype": ["Collimator", "Couch", "Gantry"],
                    "displayname": displayname
                    }

    if start_x==0 or start_y==0:
        start_point=None
    else:
        start_point=(start_x, start_y)

    if sid==0.0 and dpi==0:
        try:
            star = Starshot(file_path)
        except Exception as e:
            return template("error_template", {"error_message": "The Starshot module cannot calculate. "+str(e)})
    elif sid==0.0 and dpi!=0:
        try:
            star = Starshot(file_path, dpi=dpi)
        except Exception as e:
            return template("error_template", {"error_message": "The Starshot module cannot calculate. "+str(e)})
    elif sid!=0.0 and dpi==0:
        try:
            star = Starshot(file_path, sid=sid)
        except Exception as e:
            return template("error_template", {"error_message": "The Starshot module cannot calculate. "+str(e)})
    else:
        try:
            star = Starshot(file_path, dpi=dpi, sid=sid)
        except Exception as e:
            return template("error_template", {"error_message": "The Starshot module cannot calculate. "+str(e)})
    
    # Here we force pixels to background outside of box:
    if clip_box != 0:
        try:
            star.image.check_inversion_by_histogram(percentiles=[4, 50, 96]) # Check inversion otherwise this might not work
            general_functions.clip_around_image(star.image, clip_box)
        except Exception as e:
            return template("error_template", {"error_message": "Unable to apply clipbox. "+str(e)})
    
    # If inversion is selected:
    if invert:
        star.image.invert()

    # Now we try to analyse
    try:
        star.analyze(radius=radius, min_peak_height=min_peak_height, tolerance=tolerance,
                     start_point=start_point, fwhm=fwhm, recursive=recursive)
    except Exception as e:
        return template("error_template", {"error_message": "Module Starshot cannot calculate. "+str(e)})

    fig_ss = Figure(figsize=(10, 6), tight_layout={"w_pad":4})
    img_ax = fig_ss.add_subplot(1,2,1)
    wobble_ax = fig_ss.add_subplot(1,2,2)

    img_ax.imshow(star.image.array, cmap=matplotlib.cm.gray, interpolation="none", aspect="equal", origin='upper')

    star.lines.plot(img_ax)
    star.wobble.plot2axes(img_ax, edgecolor='green')
    star.circle_profile.plot2axes(img_ax, edgecolor='green')
    img_ax.axis('off')
    img_ax.autoscale(tight=True)
    img_ax.set_aspect(1)
    img_ax.set_xticks([])
    img_ax.set_yticks([])

    star.lines.plot(wobble_ax)
    star.wobble.plot2axes(wobble_ax, edgecolor='green')
    star.circle_profile.plot2axes(wobble_ax, edgecolor='green')
    wobble_ax.axis('off')
    xlims = [star.wobble.center.x + star.wobble.diameter, star.wobble.center.x - star.wobble.diameter]
    ylims = [star.wobble.center.y + star.wobble.diameter, star.wobble.center.y - star.wobble.diameter]
    wobble_ax.set_xlim(xlims)
    wobble_ax.set_ylim(ylims)
    wobble_ax.axis('on')
    wobble_ax.set_aspect(1)

    script = mpld3.fig_to_html(fig_ss, d3_url=D3_URL, mpld3_url=MPLD3_URL)

    variables = {
                 "script": script,
                 "passed": star.passed,
                 "radius": star.wobble.radius_mm,
                 "tolerance": star.tolerance,
                 "circle_center": star.wobble.center,
                 "pdf_report_enable": pdf_report_enable,
                 "save_results": save_results,
                 "acquisition_datetime": acquisition_datetime
                 }
 
    # Generate pylinac report:
    if pdf_report_enable == "True":
        pdf_file = tempfile.NamedTemporaryFile(delete=False, prefix="Starshot_", suffix=".pdf", dir=config.PDF_REPORT_FOLDER)
        if imgtype == "dicom":
            metadata = RestToolbox.GetInstances(config.ORTHANC_URL, [w])
            try:
                patient = metadata[0]["PatientName"]
            except:
                patient = ""
            try:
                stationname = metadata[0]["StationName"]
            except:
                stationname = ""
            try:
                date_time = RestToolbox.get_datetime(metadata[0])
                date_var = datetime.datetime.strptime(date_time[0], "%Y%m%d").strftime("%d/%m/%Y")
            except:
                date_var = ""

            star.publish_pdf(pdf_file, notes=["Date = "+date_var, "Patient = "+patient, "Station = "+stationname])
        else:
            star.publish_pdf(pdf_file)
        variables["pdf_report_filename"] = os.path.basename(pdf_file.name)

    general_functions.delete_figure([fig_ss])
    general_functions.delete_files_in_subfolders([temp_folder]) # Delete image
    return template("starshot_results", variables)

@ss_app.route('/starshot_calculate/<imgtype>/<w>', method="POST")
def starshot_calculate(imgtype, w):
    # w is the image

    clip_box = float(request.forms.hidden_clipbox)*10.0
    radius = float(request.forms.hidden_radius)
    min_peak_height = float(request.forms.hidden_mph)
    start_x = int(request.forms.hidden_px)
    start_y = int(request.forms.hidden_py)
    dpi = int(request.forms.hidden_dpi)
    sid = float(request.forms.hidden_sid)
    imgdescription = request.forms.hidden_imgdescription
    station = request.forms.hidden_station
    displayname = request.forms.hidden_displayname
    acquisition_datetime = request.forms.hidden_datetime
    
    fwhm = True if request.forms.hidden_fwhm=="true" else False
    recursive = True if request.forms.hidden_recursive=="true" else False
    invert = True if request.forms.hidden_invert=="true" else False
    # Get either dicom or non-dicom file
    if imgtype == "dicom":
        temp_folder, file_path = RestToolbox.GetSingleDcm(config.ORTHANC_URL, w)
    else:
        if request.files.get("input_nondicom_file") is not None:
            upload = request.files.get("input_nondicom_file")
            if os.path.splitext(upload.filename)[1] == ".tif":
                temp_folder = tempfile.mkdtemp(prefix=os.path.splitext(upload.filename)[0]+"_", dir=config.TEMP_NONDCM_FOLDER)
                file_path = os.path.join(temp_folder, upload.filename)
                with open(file_path, "wb") as dst:
                    upload.save(dst, overwrite=False)
                dst.close()
            else:
                return template("error_template", {"error_message": "Please load a valid image file."})
        else:
            return template("error_template", {"error_message": "Please load a valid image file."})

    args = {"imgtype": imgtype, "w": w, "clip_box": clip_box, "radius":radius, "min_peak_height":min_peak_height,
            "start_x": start_x, "start_y":start_y, "dpi":dpi, "sid":sid, "fwhm":fwhm,"recursive":recursive,  "invert":invert, 
            "temp_folder": temp_folder, "file_path":file_path, "imgdescription": imgdescription,
            "station": station, "displayname": displayname, "acquisition_datetime": acquisition_datetime,
            "config": general_functions.get_configuration()}
    p = Pool(1)
    data = p.map(starshot_helperf_catch_error, [args])
    p.close()
    p.join()
    return data
