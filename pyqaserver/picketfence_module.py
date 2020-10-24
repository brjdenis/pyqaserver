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
from mpl_toolkits.axes_grid1 import make_axes_locatable

# To revert back to matplotlib 1.0 style
matplotlib.style.use('classic')

from pylinac.core.profile import SingleProfile as PylinacSingleProfile

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
pf_app = Bottle()

@pf_app.route('/picket_fence', method="POST")
def picket_fence():

    displayname = request.forms.hidden_displayname
    username = request.get_cookie("account", secret=config.SECRET_KEY)
    if not username:
        redirect("/login")
    try:
        variables = general_functions.Read_from_dcm_database()
        variables["displayname"] = displayname
    except ConnectionError:
        return template("error_template", {"error_message": "Orthanc is refusing connection."})
    variables["LEAF_TYPE"] = LEAF_TYPE
    response.set_cookie("account", username, secret=config.SECRET_KEY, samesite="lax")
    return template("picket_fence", variables)

def picket_fence_helperf_catch_error(args):
    try:
        return picket_fence_helperf(args)
    except Exception as e:
        return template("error_template", {"error_message": str(e)})

def picket_fence_helperf(args):
    '''This function is used in order to prevent memory problems'''
    temp_folder = args["temp_folder"]
    file_path = args["file_path"]
    clip_box = args["clip_box"]
    py_filter = args["py_filter"]
    num_pickets = args["num_pickets"]
    sag = args["sag"]
    mlc = args["mlc"]
    invert = args["invert"]
    orientation = args["orientation"]
    w = args["w"]
    imgdescription = args["imgdescription"]
    station = args["station"]
    displayname = args["displayname"]
    acquisition_datetime = args["acquisition_datetime"]
    general_functions.set_configuration(args["config"])  # Transfer to this process
    
    # Chose module:
    if mlc in ["Varian_80", "Elekta_80", "Elekta_160"]:
        use_original_pylinac = "False"
    else:
        use_original_pylinac = "True"
    
    # Collect data for "save results"
    dicomenergy = general_functions.get_energy_from_imgdescription(imgdescription)
    user_machine, user_energy = general_functions.get_user_machine_and_energy(station, dicomenergy)
    machines_and_energies = general_functions.get_machines_and_energies(general_functions.get_treatmentunits_picketfence())
    tolerances = general_functions.get_tolerance_user_machine_picketfence(user_machine)  # If user_machne has specific tolerance
    if not tolerances:
        action_tolerance, tolerance, generate_pdf_report = general_functions.get_settings_picketfence()
    else:
        action_tolerance, tolerance, generate_pdf_report = tolerances[0]

    tolerance = float(tolerance)
    action_tol = float(action_tolerance)
    
    save_results = {
                    "user_machine": user_machine,
                    "user_energy": user_energy,
                    "machines_and_energies": machines_and_energies,
                    "displayname": displayname
                    }

    # Import either original pylinac module or the modified module
    if use_original_pylinac == "True":
        from pylinac import PicketFence as PicketFence  # Original pylinac analysis
    else:
        if __name__ == '__main__' or parent_module.__name__ == '__main__':
            from python_packages.pylinac.picketfence_modified import PicketFence as PicketFence
        else:
            from .python_packages.pylinac.picketfence_modified import PicketFence as PicketFence

    try:
        pf = PicketFence(file_path, filter=py_filter)
    except Exception as e:
        return template("error_template", {"error_message": "Module PicketFence cannot calculate. "+str(e)})

    # Here we force pixels to background outside of box:
    if clip_box != 0:
        try:
            pf.image.check_inversion_by_histogram(percentiles=[4, 50, 96]) # Check inversion otherwise this might not work
            general_functions.clip_around_image(pf.image, clip_box)
        except Exception as e:
            return template("error_template", {"error_message": "Unable to apply clipbox. "+str(e)})

    # Now invert if needed
    if invert:
        try:
            pf.image.invert()
        except Exception as e:
            return template("error_template", {"error_message": "Unable to invert the image. "+str(e)})
    
    # Now analyze
    try:
        if use_original_pylinac == "True":
            hdmlc = True if mlc=="Varian_120HD" else False
            pf.analyze(tolerance=tolerance, action_tolerance=action_tol, hdmlc=hdmlc, sag_adjustment=float(sag), num_pickets=num_pickets,
                       orientation=orientation)
        else:
            pf.analyze(tolerance=tolerance, action_tolerance=action_tol, mlc_type=mlc, sag_adjustment=float(sag), num_pickets=num_pickets,
                       orientation=orientation)
    except Exception as e:
        return template("error_template", {"error_message": "Picket fence module cannot analyze. "+str(e)})
        
    # Added an if clause to tell if num of mlc's are not the same on all pickets:

    num_mlcs = len(pf.pickets[0].mlc_meas)
    for p in pf.pickets:
        if len(p.mlc_meas) != num_mlcs:
            return template("error_template", {"error_message": "Not all pickets have the same number of leaves. "+
                                               "Probably your image si too skewed. Rotate your collimator a bit "+
                                               "and try again. Use the jaws perpendicular to MLCs to set the right "+
                                               "collimator angle."})
    error_array = np.array([])
    max_error = []
    max_error_leaf = []
    passed_tol = []
    picket_offsets = []
    picket_nr = pf.num_pickets
    for k in pf.pickets.pickets:
        error_array = np.concatenate((error_array, k.error_array))
        max_error.append(k.max_error)
        max_err_leaf_ind = np.argmax(k.error_array)

        max_error_leaf.append(max_err_leaf_ind)
        passed_tol.append("Passed" if k.passed else "Failed")
        picket_offsets.append(k.dist2cax)

    # Plot images
    if pf.settings.orientation == "Left-Right":
        fig_pf = Figure(figsize=(9, 10), tight_layout={"w_pad":0})
    else:
        fig_pf = Figure(figsize=(9.5, 7), tight_layout={"w_pad":0})

    img_ax = fig_pf.add_subplot(1,1,1)
    img_ax.imshow(pf.image.array, cmap=matplotlib.cm.gray, interpolation="none", aspect="equal", origin='upper')

    # Taken from pylinac: leaf_error_subplot:
    tol_line_height = [pf.settings.tolerance, pf.settings.tolerance]
    tol_line_width = [0, max(pf.image.shape)]
    # make the new axis
    divider = make_axes_locatable(img_ax)
    if pf.settings.orientation == 'Up-Down':
        axtop = divider.append_axes('right', 1.75, pad=0.2, sharey=img_ax)
    else:
        axtop = divider.append_axes('bottom', 1.75, pad=0.5, sharex=img_ax)

    # get leaf positions, errors, standard deviation, and leaf numbers
    pos, vals, err, leaf_nums = pf.pickets.error_hist()

    # Changed leaf_nums to sequential numbers:
    leaf_nums = list(np.arange(0, len(leaf_nums), 1))

    # plot the leaf errors as a bar plot
    if pf.settings.orientation == 'Up-Down':
        axtop.barh(pos, vals, xerr=err, height=pf.pickets[0].sample_width * 2, alpha=0.4, align='center')
        # plot the tolerance line(s)
        axtop.plot(tol_line_height, tol_line_width, 'r-', linewidth=3)
        if pf.settings.action_tolerance is not None:
            tol_line_height_action = [pf.settings.action_tolerance, pf.settings.action_tolerance]
            tol_line_width_action = [0, max(pf.image.shape)]
            axtop.plot(tol_line_height_action, tol_line_width_action, 'y-', linewidth=3)

        # reset xlims to comfortably include the max error or tolerance value
        axtop.set_xlim([0, max(max(vals), pf.settings.tolerance) + 0.1])
    else:
        axtop.bar(pos, vals, yerr=err, width=pf.pickets[0].sample_width * 2, alpha=0.4, align='center')
        axtop.plot(tol_line_width, tol_line_height, 'r-', linewidth=3)
        if pf.settings.action_tolerance is not None:
            tol_line_height_action = [pf.settings.action_tolerance, pf.settings.action_tolerance]
            tol_line_width_action = [0, max(pf.image.shape)]
            axtop.plot(tol_line_width_action, tol_line_height_action, 'y-', linewidth=3)
        axtop.set_ylim([0, max(max(vals), pf.settings.tolerance) + 0.1])

    # add formatting to axis
    axtop.grid(True)
    axtop.set_title("Average Error (mm)")

    # add tooltips if interactive
    # Copied this from previous version of pylinac
    interactive = True
    if interactive:
        if pf.settings.orientation == 'Up-Down':
            labels = [['Leaf pair: {0} <br> Avg Error: {1:3.3f} mm <br> Stdev: {2:3.3f} mm'.format(leaf_num, err, std)]
                      for leaf_num, err, std in zip(leaf_nums, vals, err)]
            voffset = 0
            hoffset = 20
        else:
            labels = [['Leaf pair: {0}, Avg Error: {1:3.3f} mm, Stdev: {2:3.3f} mm'.format(leaf_num, err, std)]
                      for leaf_num, err, std in zip(leaf_nums, vals, err)]

        if pf.settings.orientation == 'Up-Down':
            for num, patch in enumerate(axtop.axes.patches):
                ttip = mpld3.plugins.PointHTMLTooltip(patch, labels[num], voffset=voffset, hoffset=hoffset)
                mpld3.plugins.connect(fig_pf, ttip)
                mpld3.plugins.connect(fig_pf, mpld3.plugins.MousePosition(fontsize=14))
        else:
            for num, patch in enumerate(axtop.axes.patches):
                ttip = mpld3.plugins.PointLabelTooltip(patch, labels[num], location='top left')
                mpld3.plugins.connect(fig_pf, ttip)
                mpld3.plugins.connect(fig_pf, mpld3.plugins.MousePosition(fontsize=14))

    for p_num, picket in enumerate(pf.pickets):
        picket.add_guards_to_axes(img_ax.axes)
        for idx, mlc_meas in enumerate(picket.mlc_meas):
            mlc_meas.plot2axes(img_ax.axes, width=1.5)

    # plot CAX
    img_ax.plot(pf.settings.image_center.x, pf.settings.image_center.y, 'r+', ms=12, markeredgewidth=3)

    # tighten up the plot view
    img_ax.set_xlim([0, pf.image.shape[1]])
    img_ax.set_ylim([pf.image.shape[0], 0])
    img_ax.axis('off')
    img_ax.set_xticks([])
    img_ax.set_yticks([])
    
    # Histogram of all errors and average profile plot
    upper_bound = pf.settings.tolerance
    upper_outliers = np.sum(error_array.flatten()>=upper_bound)
    fig_pf2 = Figure(figsize=(10, 4), tight_layout={"w_pad":2})
    ax2 = fig_pf2.add_subplot(1,2,1)
    ax3 = fig_pf2.add_subplot(1,2,2)
    n, bins = np.histogram(error_array.flatten(), density=False, bins=10, range=(0, upper_bound))
    ax2.bar(bins[0:-1], n, width=np.diff(bins)[0], facecolor='green', alpha=0.75)
    ax2.bar([upper_bound,upper_bound*1.1], upper_outliers, width=0.1*upper_bound, facecolor='red', alpha=0.75)
    ax2.plot([pf.settings.action_tolerance,pf.settings.action_tolerance], [0,max(n)/2] , color="orange")
    ax2.annotate("Action Tol.", (pf.settings.action_tolerance, 1.05*max(n)/2), color='black',
                 fontsize=6, ha='center', va='bottom')
    ax2.plot([pf.settings.tolerance,pf.settings.tolerance], [0,max(n)/2] , color="darkred")
    ax2.annotate("Tol.", (pf.settings.tolerance, 1.05*max(n)/2), color='black',
                 fontsize=6, ha='center', va='bottom')

    # Plot mean inplane profile and calculate FWHM:
    mlc_mean_profile = pf.pickets.image_mlc_inplane_mean_profile
    ax3.plot(mlc_mean_profile.values, "b-")
    picket_fwhm = []
    fwhm_mean = 0
    try:
        peaks = mlc_mean_profile.find_peaks(max_number=picket_nr, min_distance=0.02, threshold=0.5)
        peaks = np.sort(peaks)
        ax3.plot(peaks, mlc_mean_profile[peaks], "ro")

        separation = int(np.mean(np.diff(peaks))/3)
        mmpd = 1/pf.image.dpmm
        # Get valleys
        valleys = []
        for p in np.arange(0, len(peaks)-1, 1):
            prof_partial = mlc_mean_profile[peaks[p]: peaks[p+1]]
            valleys.append(peaks[p]+np.argmin(prof_partial))
        edge_points = [peaks[0]-separation] + valleys + [peaks[-1]+separation]
        ax3.plot(edge_points, mlc_mean_profile[edge_points], "yo")

        for k in np.arange(0, len(edge_points)-1, 1):
            pr = PylinacSingleProfile(mlc_mean_profile[edge_points[k]:edge_points[k+1]])
            left = pr[0]
            right = pr[-1]
            amplitude = mlc_mean_profile[peaks[k]]
            if left < right:
                x = 100*((amplitude-left)*0.5 +left-right)/(amplitude-right)
                a = pr._penumbra_point(x=50, side="left", interpolate=True)
                b = pr._penumbra_point(x=x, side="right", interpolate=True)
            else:
                x = 100*((amplitude-right)*0.5 +right-left)/(amplitude-left)
                a = pr._penumbra_point(x=x, side="left", interpolate=True)
                b = pr._penumbra_point(x=50, side="right", interpolate=True)
            left_point = edge_points[k]+a
            right_point = edge_points[k]+b
            ax3.plot([left_point, right_point], [np.interp(left_point, np.arange(0, len(mlc_mean_profile.values), 1), mlc_mean_profile.values),
                     np.interp(right_point, np.arange(0, len(mlc_mean_profile.values), 1), mlc_mean_profile.values)], "-k", alpha=0.5)
            picket_fwhm.append(np.abs(a-b)*mmpd)
            
        fwhm_mean = np.mean(picket_fwhm)
    except:
        picket_fwhm = [np.nan]*picket_nr
        fwhm_mean = np.nan
    if len(picket_fwhm) != picket_nr:
        fwhm_mean = np.mean(picket_fwhm)
        picket_fwhm = [np.nan]*picket_nr

    ax2.set_xlim([-0.025, pf.settings.tolerance*1.15])
    ax3.set_xlim([0, pf.image.shape[1]])
    ax2.set_title("Leaf error")
    ax3.set_title("MLC mean profile")
    ax2.set_xlabel("Error [mm]")
    ax2.set_ylabel("Counts")
    ax3.set_xlabel("Pixel")
    ax3.set_ylabel("Grey value")

    passed = "Passed" if pf.passed else "Failed"

    script = mpld3.fig_to_html(fig_pf, d3_url=D3_URL, mpld3_url=MPLD3_URL)
    script2 = mpld3.fig_to_html(fig_pf2, d3_url=D3_URL, mpld3_url=MPLD3_URL)
    variables = {
                 "script": script,
                 "script2": script2,
                 "passed": passed,
                 "max_error": max_error,
                 "max_error_leaf": max_error_leaf,
                 "passed_tol": passed_tol,
                 "picket_nr": picket_nr,
                 "tolerance": pf.settings.tolerance,
                 "perc_passing": pf.percent_passing,
                 "max_error_all": pf.max_error,
                 "max_error_picket_all": pf.max_error_picket,
                 "max_error_leaf_all": pf.max_error_leaf,
                 "median_error": pf.abs_median_error,
                 "spacing": pf.pickets.mean_spacing,
                 "picket_offsets": picket_offsets,
                 "fwhm_mean": fwhm_mean,
                 "picket_fwhm": picket_fwhm,
                 "pdf_report_enable": generate_pdf_report,
                 "save_results": save_results,
                 "acquisition_datetime": acquisition_datetime
                 }

    # Generate pylinac report:
    if generate_pdf_report == "True":
        pdf_file = tempfile.NamedTemporaryFile(delete=False, prefix="PicketFence_", suffix=".pdf", dir=config.PDF_REPORT_FOLDER)
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
        pf.publish_pdf(pdf_file, notes=["Date = "+date_var, "Patient = "+patient, "Station = "+stationname])

        variables["pdf_report_filename"] = os.path.basename(pdf_file.name)
    #gc.collect()

    general_functions.delete_files_in_subfolders([temp_folder]) # Delete image
    return template("picket_fence_results", variables)

@pf_app.route('/picket_fence_calculate/<w>', method="POST")
def picket_fence_calculate(w):
    # w is the image, m is the mlc type
    
    temp_folder, file_path = RestToolbox.GetSingleDcm(config.ORTHANC_URL, w)
    clip_box = float(request.forms.hidden_clipbox)*10.0
    py_filter = int(request.forms.hidden_filter)
    py_filter = None if py_filter==0 else py_filter
    num_pickets = int(request.forms.hidden_peaks)
    num_pickets = None if num_pickets==0 else num_pickets
    sag = float(request.forms.hidden_sag)
    mlc = request.forms.hidden_mlc
    invert = True if request.forms.hidden_invert=="true" else False
    orientation = request.forms.hidden_orientation
    orientation = None if orientation=="Automatic" else orientation
    imgdescription = request.forms.hidden_imgdescription
    station = request.forms.hidden_station
    displayname = request.forms.hidden_displayname
    acquisition_datetime = request.forms.hidden_datetime

    args = {"temp_folder": temp_folder, "file_path": file_path, "clip_box": clip_box, "py_filter":py_filter,
            "num_pickets":num_pickets, "sag": sag, "mlc":mlc, "invert":invert, "orientation":orientation,
             "w":w, "imgdescription": imgdescription,"station": station, "displayname": displayname,
             "acquisition_datetime": acquisition_datetime, "config": general_functions.get_configuration()}
    p = Pool(1)
    data = p.map(picket_fence_helperf_catch_error, [args])
    p.close()
    p.join()
    return data
