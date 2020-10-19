import sys
import os
from scipy import ndimage
from multiprocessing import Pool
import tempfile
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
    # Import version 2.3.1 of the module flatsym (v2.3.2 is broken)
    from python_packages.pylinac.flatsym_version231 import FlatSym as FlatSym
    from python_packages import mpld3
else:
    from . import config
    from .python_packages.bottlepy.bottle import Bottle, request, TEMPLATE_PATH, template, redirect, response
    from . import general_functions
    from . import RestToolbox_modified as RestToolbox
    # Import version 2.3.1 of the module flatsym (v2.3.2 is broken)
    from .python_packages.pylinac.flatsym_version231 import FlatSym as FlatSym
    from .python_packages import mpld3

CUR_DIR = os.path.realpath(os.path.dirname(__file__))

# Path to Bottle templates
TEMPLATE_PATH.insert(0, os.path.join(CUR_DIR, 'views'))

# Url to some mpld3 library
D3_URL = config.D3_URL
MPLD3_URL = config.MPLD3_URL

# Working directory
PLWEB_FOLDER = config.PLWEB_FOLDER

PI = np.pi

# Here starts the bottle server
flatsym_app = Bottle()

@flatsym_app.route(PLWEB_FOLDER + '/flatsym', method="POST")
def flatsym():
    username = request.get_cookie("account", secret=config.SECRET_KEY)
    displayname = request.forms.hidden_displayname
    if not username:
        redirect(PLWEB_FOLDER + "/login")
    
    try:
        variables = general_functions.Read_from_dcm_database()
        variables["displayname"] = displayname
        response.set_cookie("account", username, secret=config.SECRET_KEY, samesite="lax")
    except ConnectionError:
        return template("error_template", {"error_message": "Orthanc is refusing connection.",
                                           "plweb_folder": PLWEB_FOLDER})
    return template("flatsym", variables)


def flatsym_helper_catch_error(args):
    try:
        return flatsym_helper(args)
    except Exception as e:
        return template("error_template", {"error_message": str(e),
                                           "plweb_folder": PLWEB_FOLDER})


def flatsym_helper(args):
    calc_definition = args["calc_definition"]
    center_definition = args["center_definition"]
    center_x = args["center_x"]
    center_y = args["center_y"]
    invert = args["invert"]
    w = args["instance"]
    station = args["station"]
    imgdescription = args["imgdescription"]
    displayname = args["displayname"]
    acquisition_datetime = args["acquisition_datetime"]

    general_functions.set_configuration(args["config"])  # Transfer to this process

    # Collect data for "save results"
    dicomenergy = general_functions.get_energy_from_imgdescription(imgdescription)
    user_machine, user_energy = general_functions.get_user_machine_and_energy(station, dicomenergy)
    machines_and_energies = general_functions.get_machines_and_energies(general_functions.get_treatmentunits_flatsym())
    tolerances = general_functions.get_tolerance_user_machine_flatsym(user_machine)  # If user_machne has specific tolerance
    if not tolerances:
        tolerance_flat, tolerance_sym, pdf_report_enable = general_functions.get_settings_flatsym()
    else:
        tolerance_flat, tolerance_sym, pdf_report_enable = tolerances[0]
    
    tolerance_flat = float(tolerance_flat)
    tolerance_sym = float(tolerance_sym)

    save_results = {
                    "user_machine": user_machine,
                    "user_energy": user_energy,
                    "machines_and_energies": machines_and_energies,
                    "displayname": displayname
                    }


    temp_folder, file_path = RestToolbox.GetSingleDcm(config.ORTHANC_URL, w)
    
    try:
        flatsym = FlatSym(file_path)
    except Exception as e:
        return template("error_template", {"error_message": "The FlatSym module cannot calculate. "+str(e),
                                           "plweb_folder": PLWEB_FOLDER})

    # Define the center pixel where to get profiles:
    def find_field_centroid(img):
        '''taken from pylinac WL module'''
        min, max = np.percentile(img.image.array, [5, 99.9])
        # min, max = np.amin(img.array), np.max(img.array)

        threshold_img = img.image.as_binary((max - min)/2 + min)
        # clean single-pixel noise from outside field
        coords = ndimage.measurements.center_of_mass(threshold_img)
        return (int(coords[-1]), int(coords[0]))

    flatsym.image.crop(pixels=2)
    flatsym.image.check_inversion()
    if invert:
        flatsym.image.invert()
    flatsym.image.array = np.flipud(flatsym.image.array)
    vmax = flatsym.image.array.max()

    if center_definition == "Automatic":
        center_int = [int(flatsym.image.array.shape[1]/2), int(flatsym.image.array.shape[0]/2)]
        center = [0.5, 0.5]
    elif center_definition == "CAX":
        center_int = find_field_centroid(flatsym)  # Define as mechanical isocenter
        center = [int(center_int[0])/flatsym.image.array.shape[1], int(center_int[1])/flatsym.image.array.shape[0]]
    else:
        center_int = [int(center_x), int(center_y)]
        center = [int(center_x)/flatsym.image.array.shape[1], int(center_y)/flatsym.image.array.shape[0]]

    fig = Figure(figsize=(9, 9), tight_layout={"w_pad":1})
    ax = fig.add_subplot(1,1,1)
    ax.imshow(flatsym.image.array, cmap=matplotlib.cm.jet, interpolation="none", vmin=0.9*vmax, vmax=vmax,
              aspect="equal", origin='lower')
    ax.autoscale(tight=True)

    # Plot lines along which the profiles are calculated:
    ax.plot([0, flatsym.image.array.shape[1]], [center_int[1], center_int[1]], "b-", linewidth=2)
    ax.plot([center_int[0], center_int[0]], [0, flatsym.image.array.shape[0]] , c="darkgreen", linestyle="-", linewidth=2)
    ax.set_xlim([0, flatsym.image.array.shape[1]])
    ax.set_ylim([0, flatsym.image.array.shape[0]])

    # Get profiles
    crossplane = PylinacSingleProfile(flatsym.image.array[center_int[1], :])
    inplane = PylinacSingleProfile(flatsym.image.array[:, center_int[0]])

    # Do some filtering:
    crossplane.filter(kind='median', size=0.01)
    inplane.filter(kind='median', size=0.01)

    # Normalize profiles
    norm_val_crossplane = crossplane.values[center_int[0]]
    norm_val_inplane = inplane.values[center_int[1]]
    crossplane.normalize(norm_val=norm_val_crossplane)
    inplane.normalize(norm_val=norm_val_inplane)

    # Get index of CAX of both profiles(different than center) to be used for mirroring:
    fwhm_crossplane = crossplane.fwxm_center(interpolate=True)
    fwhm_inplane = inplane.fwxm_center(interpolate=True)

    # Plot profiles
    divider = make_axes_locatable(ax)

    ax_crossplane = divider.append_axes("bottom", size="40%", pad=0.25, sharex=ax)
    ax_crossplane.set_xlim([0, flatsym.image.array.shape[1]])
    ax_crossplane.set_xticks([])
    ax_crossplane.set_title("Crossplane")

    ax_inplane = divider.append_axes("right", size="40%", pad=0.25, sharey=ax)
    ax_inplane.set_ylim([0, flatsym.image.array.shape[0]])
    ax_inplane.set_yticks([])
    ax_inplane.set_title("Inplane")

    ax_crossplane.plot(crossplane._indices, crossplane, "b-")
    ax_crossplane.plot(2*fwhm_crossplane - crossplane._indices, crossplane, "b--")
    ax_inplane.plot(inplane, inplane._indices, c="darkgreen", linestyle="-")
    ax_inplane.plot(inplane, 2*fwhm_inplane - inplane._indices, c="darkgreen", linestyle="--")

    ax_inplane.grid(alpha=0.5)
    ax_crossplane.grid(alpha=0.5)
    mpld3.plugins.connect(fig, mpld3.plugins.MousePosition(fontsize=14, fmt=".2f"))

    script = mpld3.fig_to_html(fig, d3_url=D3_URL, mpld3_url=MPLD3_URL)

    if calc_definition == "Elekta":
        method = "elekta"
    else:
        method = "varian"
        
    try:
        flatsym.analyze(flatness_method=method, symmetry_method=method, vert_position=center[0], horiz_position=center[1])
    except Exception as e:
        return template("error_template", {"error_message": "Analysis failed. "+str(e),
                                           "plweb_folder": PLWEB_FOLDER})

    symmetry_hor = round(flatsym.symmetry['horizontal']['value'], 2)
    symmetry_vrt = round(flatsym.symmetry['vertical']['value'], 2)
    flatness_hor = round(flatsym.flatness['horizontal']['value'], 2)
    flatness_vrt = round(flatsym.flatness['vertical']['value'], 2)
    horizontal_width = round(flatsym.symmetry['horizontal']['profile'].fwxm(interpolate=True) / flatsym.image.dpmm, 2)
    vertical_width = round(flatsym.symmetry['vertical']['profile'].fwxm(interpolate=True) / flatsym.image.dpmm, 2)
    horizontal_penumbra_width = round(flatsym.symmetry['horizontal']['profile'].penumbra_width(interpolate=True) / flatsym.image.dpmm, 2)
    vertical_penumbra_width = round(flatsym.symmetry['vertical']['profile'].penumbra_width(interpolate=True) / flatsym.image.dpmm, 2)
    
    # Check if passed
    if method == "varian":
        if (flatness_hor < tolerance_flat) and (flatness_vrt < tolerance_flat) and (symmetry_hor < tolerance_sym) and (symmetry_vrt < tolerance_sym):
            passed = True
        else:
            passed = False
    else:
        if (abs(flatness_hor-100) < tolerance_flat) and (abs(flatness_vrt-100) < tolerance_flat) and (abs(symmetry_hor-100) < tolerance_sym) and (abs(symmetry_vrt-100) < tolerance_sym):
            passed = True
        else:
            passed = False
    
    variables = {
                "symmetry_hor": symmetry_hor,
                "symmetry_vrt": symmetry_vrt,
                "flatness_hor": flatness_hor,
                "flatness_vrt": flatness_vrt,
                "horizontal_width": horizontal_width,
                "vertical_width": vertical_width,
                "horizontal_penumbra_width": horizontal_penumbra_width,
                "vertical_penumbra_width": vertical_penumbra_width,
                "passed": passed,
                "pdf_report_enable": pdf_report_enable,
                "script": script,
                "save_results": save_results,
                "acquisition_datetime": acquisition_datetime,
                "calc_definition": calc_definition,
                "plweb_folder": PLWEB_FOLDER
                }
    
        # Generate pylinac report:
    if pdf_report_enable == "True":
        pdf_file = tempfile.NamedTemporaryFile(delete=False, prefix="FlatSym", suffix=".pdf", dir=config.PDF_REPORT_FOLDER)
        flatsym.publish_pdf(pdf_file)
        variables["pdf_report_filename"] = os.path.basename(pdf_file.name)
    
    general_functions.delete_files_in_subfolders([temp_folder]) # Delete image
    
    return template("flatsym_results", variables)


@flatsym_app.route(PLWEB_FOLDER + '/flatsym_calculate/<w>', method="POST")
def flatsym_calculate(w):
    calc_definition = request.forms.hidden_definition
    center_definition = request.forms.hidden_center
    center_x = request.forms.hidden_coox
    center_y = request.forms.hidden_cooy
    invert = True if request.forms.hidden_invert=="true" else False
    station = request.forms.hidden_station
    imgdescription = request.forms.hidden_imgdescription
    displayname = request.forms.hidden_displayname
    acquisition_datetime = request.forms.hidden_datetime

    args = {"calc_definition": calc_definition, "center_definition": center_definition,
            "center_x": center_x, "center_y": center_y, "invert": invert, "instance": w,
            "station": station, "imgdescription": imgdescription, "displayname": displayname,
            "acquisition_datetime": acquisition_datetime, "config": general_functions.get_configuration()}
    p = Pool(1)
    data = p.map(flatsym_helper_catch_error, [args])
    p.close()
    p.join()
    return data