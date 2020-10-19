import sys
import os
import json
import tempfile
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
import datetime
import numpy as np
from scipy import optimize
import matplotlib.style
import matplotlib
matplotlib.use('Agg')
from matplotlib.figure import Figure
from matplotlib import patches

# To revert back to matplotlib 1.0 style
matplotlib.style.use('classic')

from pylinac import WinstonLutz as WinstonLutz
from pylinac.core import image as pylinacimage

parent_module = sys.modules['.'.join(__name__.split('.')[:-1]) or '__main__']
if __name__ == '__main__' or parent_module.__name__ == '__main__':
    #sys.path.append(os.path.abspath(os.path.realpath("python_packages")))
    import config
    from python_packages.bottlepy.bottle import Bottle, request, TEMPLATE_PATH, static_file, template, redirect, response
    import general_functions
    import RestToolbox_modified as RestToolbox
    from python_packages import mpld3
else:
    from . import config
    from .python_packages.bottlepy.bottle import Bottle, request, TEMPLATE_PATH, static_file, template, redirect, response
    from . import general_functions
    from . import RestToolbox_modified as RestToolbox
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
wl_app = Bottle()


@wl_app.route(PLWEB_FOLDER + '/winston_lutz', method="POST")
def winston_lutz():
    colormaps = ["Greys", "gray", "brg", "prism"]
    displayname = request.forms.hidden_displayname
    username = request.get_cookie("account", secret=config.SECRET_KEY)
    if not username:
        redirect(PLWEB_FOLDER + "/login")
    #colormaps = matplotlib.pyplot.colormaps()
    try:
        variables = general_functions.Read_from_dcm_database()
        variables["colormaps"] = colormaps
        variables["displayname"] = displayname
        response.set_cookie("account", username, secret=config.SECRET_KEY, samesite="lax")
        return template("winston_lutz", variables)
    except ConnectionError:
        return template("error_template", {"error_message": "Orthanc is refusing connection.",
                                           "plweb_folder": PLWEB_FOLDER})

def winstonlutz_default_calculation_helperf(path):
    try:
        wl = WinstonLutz(path, use_filenames=False)
    except Exception as e:
        return e
    else:
        return wl

def winstonlutz_helperf_catch_error(args):
    try:
        return winstonlutz_helperf(args)
    except Exception as e:
        return template("error_template", {"error_message": str(e),
                                           "plweb_folder": PLWEB_FOLDER})

def winstonlutz_helperf(args):
    # This function is used to calculated results for the winstonlutz module
    # It is used with the multiprocessing module in order to clear memory
    # after execution
    clip_box = args["clip_box"]
    file_paths_full = args["file_paths_full"]
    colormap = args["colormap"]
    p = args["p"]
    pylinac_angles_full = args["pylinac_angles_full"]
    folder_path = args["folder_path"]
    c = args["c"]
    show_epid_points = args["show_epid_points"]
    file_paths = args["file_paths"]
    imglist = args["imglist"]
    test_type = args["test_type"]
    use_couch = args["use_couch"]
    station = args["station"]
    imgdescription = args["imgdescription"]
    displayname = args["displayname"]
    acquisition_datetime = args["acquisition_datetime"]
    start_x = args["start_x"]
    start_y = args["start_y"]
    general_functions.set_configuration(args["config"])  # Transfer to this process

    # Get just the basenames of files (need this for getting right order when pyl is used)
    file_paths_names = [os.path.basename(fp) for fp in file_paths_full]

    # Set colormap
    cmap = matplotlib.cm.get_cmap(colormap)

    # Collect data for "save results"
    dicomenergy = general_functions.get_energy_from_imgdescription(imgdescription)
    user_machine, user_energy = general_functions.get_user_machine_and_energy(station, dicomenergy)
    machines_and_energies = general_functions.get_machines_and_energies(general_functions.get_treatmentunits_wl())
    tolerances = general_functions.get_tolerance_user_machine_wl(user_machine)  # If user_machne has specific tolerance
    if not tolerances:
        pass_rate, success_rate, apply_tolerance_to_coll_asym, coll_asym_tol, beam_dev_tol, couch_dist_tol = general_functions.get_settings_wl()
    else:
        pass_rate, success_rate, apply_tolerance_to_coll_asym, coll_asym_tol, beam_dev_tol, couch_dist_tol = tolerances[0]

    success_rate = float(success_rate)  # If more than this, the test is "borderline", but not "failed"
    pass_rate = float(pass_rate)
    coll_asym_tol = float(coll_asym_tol)
    beam_dev_tol = float(beam_dev_tol)
    couch_dist_tol = float(couch_dist_tol)

    save_results = {
                    "user_machine": user_machine,
                    "user_energy": user_energy,
                    "machines_and_energies": machines_and_energies,
                    "phantoms": general_functions.get_phantoms_wl(),
                    "displayname": displayname
                    }

    # If the user wants pylinac's analysis:

    if p == "True":
        if pylinac_angles_full.count(None) == 0:
            use_filenames = True
        else:
            use_filenames = False
        try:
            wl = WinstonLutz(folder_path, use_filenames=use_filenames)
        except Exception as e:
            general_functions.delete_files_in_subfolders([folder_path])
            return template("error_template", {"error_message": "Module WinstonLutz cannot calculate. "+str(e),
                                               "plweb_folder": PLWEB_FOLDER})

        pdf_file = tempfile.NamedTemporaryFile(delete=False, prefix="pylinac_", suffix=".pdf", dir=config.PDF_REPORT_FOLDER)
        try:
            stationname = wl.images[0].metadata.StationName
        except:
            stationname = ""
        try:
            date_time = wl.images[0].metadata.ContentDate
            date_var = datetime.datetime.strptime(date_time, "%Y%m%d").strftime("%Y/%m/%d")
        except:
            date_var = ""
        wl.publish_pdf(pdf_file, notes=["Date = "+date_var, "Station = "+stationname])
        pdf_file.close()

        def fill_axis_figure(images):
            # Function that fills the figure with axis images. Images is a list of images.
            N = len(images)
            if N % 2 == 0:
                rows =  int(N/2)
            else:
                rows = int(N//2) + 1
            
            fig = Figure(figsize=(8, 4*rows))
            
            for m in range(0, len(images), 1):
                ax = fig.add_subplot(rows, 2, m+1)
                img = images[m]
                array = img.array

                # Plot the array and the contour of the 50 percent isodose line
                ax.imshow(array, cmap=cmap, interpolation="none",  origin='lower')
                level = np.average(np.percentile(array, [5, 99.9]))
                ax.contour(array, levels=[level], colors = ["blue"])  # CAX

                # Plot centers: field, BB, EPID
                ax.plot(img.field_cax.x, img.field_cax.y, 'b+', markersize=24, markeredgewidth=3, zorder=2)
                ax.plot(img.bb.x, img.bb.y, 'r+', markersize=24, markeredgewidth=3, zorder=2)
                ax.plot(img.epid.x, img.epid.y, 'yo', ms=10, markeredgewidth=0.0, zorder=1)

                # Set the right image number (compare with file_paths_names):
                try:
                    img_number = str(file_paths_names.index(img.file)+1)
                except ValueError:
                    img_number = "NA"

                ax.set_title(img_number+". " + f"Gantry={img.gantry_angle:.0f}, Coll.={img.collimator_angle:.0f}, Couch={img.couch_angle:.0f}")
                ax.set_ylabel(f"CAX to BB: {img.cax2bb_distance:3.2f}mm")

                # Plot edges of untouched area with a line:
                if clip_box != 0:
                    n_t = int((img.shape[0] + clip_box*img.dpmm)/2)  # Top  edge
                    n_b = int((img.shape[0] - clip_box*img.dpmm)/2)  # bottom edge
                    n_l = int((img.shape[1] - clip_box*img.dpmm)/2)  # Left  edge
                    n_r = int((img.shape[1] + clip_box*img.dpmm)/2)  #  right edge
                    ax.plot([n_l, n_l, n_r, n_r, n_l], [n_b, n_t, n_t, n_b, n_b], "-g")
        
                if c == "True":
                    # If zoom is used:
                    ax.set_ylim(img.rad_field_bounding_box[0], img.rad_field_bounding_box[1])
                    ax.set_xlim(img.rad_field_bounding_box[2], img.rad_field_bounding_box[3])
                    ax.autoscale(False)
                else:
                    ax.autoscale(True)
                fig.set_tight_layout(True)
            return fig

        # Plot images
        axis_images = [None, None, None, None, None, None]
        if wl._contains_axis_images("Gantry"):
            images = [image for image in wl.images if image.variable_axis in ("Gantry", "Reference")]
            axis_images[0] = mpld3.fig_to_html(fill_axis_figure(images), d3_url=D3_URL, mpld3_url=MPLD3_URL)
        if wl._contains_axis_images("Collimator"):
            images = [image for image in wl.images if image.variable_axis in ("Collimator", "Reference")]
            axis_images[1] = mpld3.fig_to_html(fill_axis_figure(images), d3_url=D3_URL, mpld3_url=MPLD3_URL)
        if wl._contains_axis_images("Couch"):
            images = [image for image in wl.images if image.variable_axis in ("Couch", "Reference")]
            axis_images[2] = mpld3.fig_to_html(fill_axis_figure(images), d3_url=D3_URL, mpld3_url=MPLD3_URL)
        if wl._contains_axis_images("GB Combo"):
            images = [image for image in wl.images if image.variable_axis in ("GB Combo", "Reference")]
            axis_images[3] = mpld3.fig_to_html(fill_axis_figure(images), d3_url=D3_URL, mpld3_url=MPLD3_URL)
        if wl._contains_axis_images("GBP Combo"):
            images = [image for image in wl.images if image.variable_axis in ("GBP Combo", "Reference")]
            axis_images[4] = mpld3.fig_to_html(fill_axis_figure(images), d3_url=D3_URL, mpld3_url=MPLD3_URL)
        
        # If none of the above, just plot all the images
        if all([element==None for element in axis_images[:-1]]):
            images = [image for image in wl.images]
            axis_images[5] = mpld3.fig_to_html(fill_axis_figure(images), d3_url=D3_URL, mpld3_url=MPLD3_URL)

        # Plot wobble images:
        # Take as a reference: CAX for couch images, BB for collimator and gantry images
        fig_wobble = Figure(figsize=(9, 3))
        n = 0
        for axis in ("Gantry", "Collimator", "Couch"):
            if wl._get_images((axis, "Reference"))[0] > 1:
                images = [image for image in wl.images if image.variable_axis in (axis, "Reference")]
                ax_wobble = fig_wobble.add_subplot(1, 3, n+1)
                img = images[0]
                array = img.array
                ax_wobble.imshow(array, cmap=matplotlib.cm.Greys, interpolation="none",  origin='lower')
                ax_wobble.plot(img.bb.x, img.bb.y, 'r+', markersize=12, markeredgewidth=2, zorder=2)
                ax_wobble.plot(img.field_cax.x, img.field_cax.y, 'b+', markersize=12, markeredgewidth=2, zorder=2)
                ax_wobble.plot(img.epid.x, img.epid.y, 'yo', ms=5, markeredgewidth=0.0, zorder=1)

                if axis != "Couch":
                    # plot EPID
                    ref_x = img.bb.x
                    ref_y = img.bb.y
                    epid_xs = [ref_x + imgg.epid.x - imgg.bb.x for imgg in images[1:]]
                    epid_ys = [ref_y + imgg.epid.y - imgg.bb.y for imgg in images[1:]]
                    ax_wobble.plot(epid_xs, epid_ys, 'yo', ms=5, markeredgewidth=0.0, zorder=1)
                    # get CAX positions
                    xs = [ref_x + imgg.field_cax.x - imgg.bb.x for imgg in images[1:]]
                    ys = [ref_y + imgg.field_cax.y - imgg.bb.y for imgg in images[1:]]
                    ax_wobble.plot(xs, ys, 'b+', markersize=12, markeredgewidth=2, zorder=2)
                    circle = patches.Circle((ref_x, ref_y), 1.0*img.dpmm, color='cyan', zorder=2, fill=False, linestyle='--')
                    ax_wobble.add_patch(circle)
                else:
                    # get BB positions
                    ref_x = img.field_cax.x
                    ref_y = img.field_cax.y
                    xs = [ref_x + imgg.bb.x - imgg.field_cax.x for imgg in images[1:]]
                    ys = [ref_y + imgg.bb.y - imgg.field_cax.y for imgg in images[1:]]
                    ax_wobble.plot(xs, ys, 'r+', markersize=12, markeredgewidth=2, zorder=2)
                    circle_couch = patches.Circle((ref_x, ref_y), 1.0*img.dpmm, color='cyan', zorder=2, fill=False, linestyle='--')
                    ax_wobble.add_patch(circle_couch)

                # Zoom in on BB
                center_x, center_y = int(round(ref_x)), int(round(ref_y))
                extent = int(round(5.0*img.dpmm))
                ax_wobble.set_ylim(center_y-extent, center_y+extent)
                ax_wobble.set_xlim(center_x-extent, center_x+extent)
                ax_wobble.autoscale(False)
                ax_wobble.set_title(axis + ' wobble')
                ax_wobble.set_xlabel(axis + f" iso size: {getattr(wl, axis.lower() + '_iso_size'):3.2f} mm")
                n += 1
        fig_wobble.set_tight_layout(True)

        if n == 0:
            script_wobble = None
        else:
            script_wobble = mpld3.fig_to_html(fig_wobble, d3_url=D3_URL, mpld3_url=MPLD3_URL)
        
        # Plot deviations from pylinac:
        dev_rows = 2
        if wl._get_images(("Collimator", "Reference"))[0] > 1:
            dev_rows += 1
        if wl._get_images(("Couch", "Reference"))[0] > 1:
            dev_rows += 1
        
        fig_gantry_epid_sag = Figure(figsize=(8, 3*dev_rows))
        
        gantry_sag_ax = fig_gantry_epid_sag.add_subplot(dev_rows,1,1)
        wl._plot_deviation("Gantry", gantry_sag_ax, show=False)
        gantry_sag_ax.legend(numpoints=1, framealpha =0.8)
        
        epid_sag_ax = fig_gantry_epid_sag.add_subplot(dev_rows,1,2)
        wl._plot_deviation("Epid", epid_sag_ax, show=False)
        epid_sag_ax.legend(numpoints=1, framealpha =0.8)
        
        plot_row = 0
        if wl._get_images(("Collimator", "Reference"))[0] > 1:
            coll_sag_ax = fig_gantry_epid_sag.add_subplot(dev_rows, 1, 3+plot_row)
            wl._plot_deviation("Collimator", coll_sag_ax, show=False)
            coll_sag_ax.legend(numpoints=1, framealpha =0.8)
            plot_row += 1
        if wl._get_images(("Couch", "Reference"))[0] > 1:
            couch_sag_ax = fig_gantry_epid_sag.add_subplot(dev_rows,1, 3+plot_row)
            wl._plot_deviation("Couch", couch_sag_ax, show=False)
            couch_sag_ax.legend(numpoints=1, framealpha =0.8)

        fig_gantry_epid_sag.set_tight_layout(True)
        script_gantry_epid_sag = mpld3.fig_to_html(fig_gantry_epid_sag, d3_url=D3_URL, mpld3_url=MPLD3_URL)
        
        cax_position = []
        bb_position = []
        cax2bb = []
        epid2cax = []
        result = []
        radius = []
        SIDs = []
        image_type = []
        image_num = []
        gantries = []
        collimators = []
        couches = []

        N = len(wl.images)
        for n in range(0, N, 1):
            img = wl.images[n]
            dpmm = img.dpmm
            cax_position.append([-(img.epid.x-img.field_cax.x)/dpmm, -(img.epid.y-img.field_cax.y)/dpmm])
            bb_position.append([-(img.epid.x-img.bb.x)/dpmm, -(img.epid.y-img.bb.y)/dpmm])
            vec = [(img.field_cax.x - img.bb.x)/dpmm, (img.field_cax.y - img.bb.y)/dpmm]  # From BB to CAX (BB in the center)
            cax2bb.append(vec)
            epid2cax.append([(img.epid.x - img.field_cax.x)/dpmm, (img.epid.y - img.field_cax.y)/dpmm])
            SIDs.append(img.sid)
            result.append([vec[0], vec[1]])
            radius.append(np.sqrt(vec[0]*vec[0] + vec[1]*vec[1]))
            image_type.append(img.variable_axis)
            try:
                img_number2 = str(file_paths_names.index(img.file)+1)
            except ValueError:
                img_number2 = "NA"
            image_num.append(img_number2)
            gantries.append(f"{img.gantry_angle:.0f}")
            collimators.append(f"{img.collimator_angle:.0f}")
            couches.append(f"{img.couch_angle:.0f}")

        # Get other results
        quickresults = wl.results(as_list=True)
 
        # Add scatter plot for the diagram
        fig_focal = Figure(figsize=(7, 7))
        ax_focal = fig_focal.add_subplot(1,1,1)

        cax2bb = np.asarray(cax2bb)
        epid2cax = np.asarray(epid2cax)
        image_num_order = np.argsort([int(j)-1 for j in image_num])
        colors = ["blue"]*N
        colors2 = ["yellow"]*N
        labels = ['img={}, G={:d}, B={:d}, P={:d}, x = {:04.2f} mm, y = {:04.2f} mm, R = {:04.2f} mm'.format(image_num[i], int(wl.images[i].gantry_angle), int(wl.images[i].collimator_angle),
                  int(wl.images[i].couch_angle), cax2bb[i, 0], cax2bb[i, 1], np.linalg.norm(cax2bb[i, :])) for i in range(N)]
        labels = np.array(labels)[image_num_order]

        ax_focal.scatter(cax2bb[:,0], cax2bb[:, 1], c=colors, alpha=0.5,  s=80, zorder=1, linewidths=1)
        scatter = ax_focal.plot(cax2bb[:,0][image_num_order], cax2bb[:, 1][image_num_order], linestyle="-", color="green", alpha=0.5, marker="o", markersize=12, zorder=2,  markerfacecolor='none', markeredgecolor='none')
        tooltip = mpld3.plugins.PointLabelTooltip(scatter[0], labels=labels, location="top left")
        if show_epid_points:
            labels2 = ['img={}, G={:d}, B={:d}, P={:d}, x = {:04.2f} mm, y = {:04.2f} mm, R = {:04.2f} mm'.format(image_num[i], int(wl.images[i].gantry_angle), int(wl.images[i].collimator_angle),
                      int(wl.images[i].couch_angle), epid2cax[i, 0], epid2cax[i, 1], np.linalg.norm(epid2cax[i, :])) for i in range(N)]
            labels2 = np.array(labels2)[image_num_order]
            ax_focal.scatter(epid2cax[:,0], epid2cax[:, 1], c=colors2, alpha=0.5,  s=80, zorder=1, linewidths=1)
            scatter2 = ax_focal.plot(epid2cax[:,0][image_num_order], epid2cax[:, 1][image_num_order], linestyle="-", color="none", alpha=0.5, marker="o", markersize=12, zorder=2,  markerfacecolor='none', markeredgecolor='none')
            tooltip2 = mpld3.plugins.PointLabelTooltip(scatter2[0], labels=labels2, location="top left")
            ax_focal.plot([],[], c="yellow", linestyle="None", alpha=0.5, marker="o", label="EPID")
            mpld3.plugins.connect(fig_focal, tooltip, tooltip2)
        else:
            mpld3.plugins.connect(fig_focal, tooltip)

        # Legend labels:
        ax_focal.plot([None], [None], c="blue", linestyle="None", alpha=0.5, marker="o", label="CAX")

        limits_focal = pass_rate + 0.2 # Define the extent of the diagram
        p = ax_focal.plot([0],[0], "r+", mew=3, ms=10, label="BB")
        tooltip3 = mpld3.plugins.PointLabelTooltip(p[0], labels=["Ballbearing"], location="top left")
        mpld3.plugins.connect(fig_focal, tooltip3)
        ax_focal.add_patch(patches.Circle((0, 0), pass_rate, color='r', linestyle="dashed", fill=False))
        ax_focal.add_patch(patches.Circle((0, 0), success_rate, color='g', linestyle="dashed", fill=False))
        ax_focal.autoscale(False)
        ax_focal.set_xlim([-limits_focal, limits_focal])
        ax_focal.set_ylim([-limits_focal, limits_focal])
        ax_focal.set_title("Scatter diagram")
        ax_focal.set_xlabel("X [mm]")
        ax_focal.set_ylabel("Y [mm]")
        ax_focal.legend(framealpha=0, numpoints=1, ncol=3, loc='lower right', fontsize=8)
        fig_focal.set_tight_layout(True)

        script_focal = mpld3.fig_to_html(fig_focal, d3_url=D3_URL, mpld3_url=MPLD3_URL)
        general_functions.delete_figure([fig_wobble, fig_focal, fig_gantry_epid_sag])

        general_functions.delete_files_in_subfolders([folder_path]) # Delete temporary images

        bb_shift = wl.bb_shift_vector
        variables = {
                     "institution": config.INSTITUTION,
                     "acquisition_datetime": acquisition_datetime,
                     "pdf_report_filename": os.path.basename(pdf_file.name),
                     "plweb_folder": PLWEB_FOLDER,
                     "axis_images": axis_images,
                     "max_deviation": round(np.max(radius), 2),
                     "radius": radius,
                     "pass_rate": pass_rate,
                     "success_rate": success_rate,
                     "SIDs": list(set(SIDs)),
                     "cax_position": cax_position,
                     "bb_position": bb_position,
                     "result": result,
                     "image_type": image_type,
                     "image_num": image_num,
                     "gantries": gantries,
                     "collimators": collimators,
                     "couches": couches,
                     "script_focal": script_focal,
                     "script_wobble": script_wobble,
                     "script_gantry_epid_sag": script_gantry_epid_sag,
                     "quickresults": quickresults,
                     "save_results": save_results,
                     "Max2DbbCAX": wl.cax2bb_distance('max'),
                     "Median2DbbCAX": wl.cax2bb_distance('median'),
                     "BBshiftX": bb_shift.x,
                     "BBshiftY": bb_shift.y,
                     "BBshiftZ": bb_shift.z,
                     "GntIsoSize": wl.gantry_iso_size,
                     "MaxGntRMS": max(wl.axis_rms_deviation("Gantry")),
                     "MaxEpidRMS": max(wl.axis_rms_deviation("Epid")),
                     "GntColl3DisoSize": wl.gantry_coll_iso_size,
                     "Coll2DisoSize": wl.collimator_iso_size,
                     "MaxCollRMS": max(wl.axis_rms_deviation("Collimator")),
                     "Couch2DisoDia": wl.couch_iso_size,
                     "MaxCouchRMS": max(wl.axis_rms_deviation("Couch")),
                     "plweb_folder": PLWEB_FOLDER
                     }

        return template("winston_lutz_pylinac_results", variables)

    else:
        # This is the non-pylinac analysis
        N = len(file_paths)
        if N % 2 == 0:
            rows = int(N/2)
        else:
            rows = int(N//2) + 1

        cax_position = []
        bb_position = []
        cax2bb = []
        result = []
        radius = []
        SIDs = []
        epid2cax = []
        
        # Get sequential image number:
        img_numbers = []
        for i in range(len(imglist)):
            if imglist[i]:
                img_numbers.append(i+1)
        
        # Analyze all images
        try:
            p = ThreadPool(4)
            image_list = p.map(winstonlutz_default_calculation_helperf, file_paths)
        finally:
            p.close()
            p.join()
        
        for pp in range(0, N, 1):
            if isinstance(image_list[pp], Exception):
                general_functions.delete_files_in_subfolders(file_paths) # Delete temporary images (all subfolders)
                return template("error_template", {"error_message": "Unable to analyze image " + str(pp) +". " + str(image_list[pp]),
                                                   "plweb_folder": PLWEB_FOLDER})
        try:  # Add this to prevent memory add-up because of nonkilled threads
            # Draw matrix of each image
            fig_wl = Figure(figsize=(8, 4*rows))
            for m in range(0, N, 1):
                ax = fig_wl.add_subplot(rows, 2, m+1)
                wl = image_list[m]
                img = wl.images[0]
    
                array = img.array
                dpmm = img.dpmm
    
                cax_position.append([-(img.epid.x-img.field_cax.x)/dpmm, -(img.epid.y-img.field_cax.y)/dpmm])
                bb_position.append([-(img.epid.x-img.bb.x)/dpmm, -(img.epid.y-img.bb.y)/dpmm])
                vec = [(img.field_cax.x - img.bb.x)/dpmm, (img.field_cax.y - img.bb.y)/dpmm]  # From BB to CAX (BB in the center)
                cax2bb.append(vec)
                epid2cax.append([(img.epid.x - img.field_cax.x)/dpmm, (img.epid.y - img.field_cax.y)/dpmm])
                SIDs.append(img.sid)
                result.append([vec[0], vec[1]])
                radius.append(np.sqrt(vec[0]*vec[0] + vec[1]*vec[1]))
    
                # Plot the array and the contour of the 50 percent isodose line
                ax.imshow(array, cmap=cmap, interpolation="none",  origin='lower')
                level = np.average(np.percentile(array, [5, 99.9]))
                ax.contour(array, levels=[level], colors = ["blue"])  # CAX
        
                # Plot centers: field, BB, EPID
                ax.plot(img.field_cax.x, img.field_cax.y, 'b+', markersize=24, markeredgewidth=3, zorder=2)
                ax.plot(img.bb.x, img.bb.y, 'r+', markersize=24, markeredgewidth=3, zorder=2)
                ax.plot(img.epid.x, img.epid.y, 'yo', ms=10, markeredgewidth=0.0, zorder=1)
                
                ax.set_title(str(img_numbers[m])+". dx = "+str(round(vec[0], 2))+" mm,  dy = "+str(round(vec[1], 2))+" mm")
    
                # Plot edges of untouched area with a line:
                if clip_box != 0:
                    n_t = int((img.shape[0] + clip_box*img.dpmm)/2)  # Top  edge
                    n_b = int((img.shape[0] - clip_box*img.dpmm)/2)  # bottom edge
                    n_l = int((img.shape[1] - clip_box*img.dpmm)/2)  # Left  edge
                    n_r = int((img.shape[1] + clip_box*img.dpmm)/2)  #  right edge
                    ax.plot([n_l, n_l, n_r, n_r, n_l], [n_b, n_t, n_t, n_b, n_b], "-g")
        
                if c == "True":
                    # If zoom is used:
                    ax.set_ylim(img.rad_field_bounding_box[0], img.rad_field_bounding_box[1])
                    ax.set_xlim(img.rad_field_bounding_box[2], img.rad_field_bounding_box[3])
                    ax.autoscale(False)
                else:
                    ax.autoscale(True)
            fig_wl.set_tight_layout(True)
            script = mpld3.fig_to_html(fig_wl, d3_url=D3_URL, mpld3_url=MPLD3_URL)
            general_functions.delete_figure([fig_wl])
            general_functions.delete_files_in_subfolders(file_paths)
        
        except Exception as e:
            general_functions.delete_files_in_subfolders(file_paths) # Delete temporary images (all subfolders)
            return template("error_template", {"error_message": "Unable to plot images. " + str(e),
                                               "plweb_folder": PLWEB_FOLDER})
        
        try:
            if use_couch==False:
                # Add scatter plot for the diagram
                fig_focal = Figure(figsize=(10.5, 5), tight_layout={"w_pad":0,  "pad": 0})
                ax_focal = fig_focal.add_subplot(1,2,1, aspect=1)
                ax_gantry = fig_focal.add_subplot(1,2,2, aspect=1)
        
                cax2bb = np.asarray(cax2bb)
                epid2cax = np.asarray(epid2cax)
        
                colors = ["blue"]*N
                colors2 = ["yellow"]*N
                labels = ['Img = {:d}, x = {:04.2f} mm, y = {:04.2f} mm, R = {:04.2f} mm'.format(img_numbers[i], cax2bb[i, 0], cax2bb[i, 1], 
                          np.linalg.norm(cax2bb[i, :])) for i in range(N)]
                ax_focal.scatter(cax2bb[:,0], cax2bb[:, 1], c=colors, alpha=0.5,  s=80, zorder=1, linewidths=1)
                scatter = ax_focal.plot(cax2bb[:,0], cax2bb[:, 1], linestyle="-", color="green", alpha=0.5, marker="o", markersize=12, zorder=2,  markerfacecolor='none', markeredgecolor='none')
                tooltip = mpld3.plugins.PointLabelTooltip(scatter[0], labels=labels, location="top left")
        
                if show_epid_points:
                    labels2 = ['Img = {:d}, x = {:04.2f} mm, y = {:04.2f} mm, R = {:04.2f} mm'.format(img_numbers[i], epid2cax[i, 0], epid2cax[i, 1], 
                              np.linalg.norm(epid2cax[i, :])) for i in range(N)]
                    ax_focal.scatter(epid2cax[:,0], epid2cax[:, 1], c=colors2, alpha=0.5,  s=80, zorder=1, linewidths=1)
                    scatter2 = ax_focal.plot(epid2cax[:,0], epid2cax[:, 1], linestyle="-", color="none", alpha=0.5, marker="o", markersize=12, zorder=2,  markerfacecolor='none', markeredgecolor='none')
                    tooltip2 = mpld3.plugins.PointLabelTooltip(scatter2[0], labels=labels2, location="top left")
                    mpld3.plugins.connect(fig_focal, tooltip, tooltip2)
                    ax_focal.plot([None], [None], c="yellow", linestyle=None, alpha=0.5, marker="o", label="EPID") # Legend labels
                else:
                    mpld3.plugins.connect(fig_focal, tooltip)
                
                # Legend labels:
                ax_focal.plot([None], [None], c="blue", linestyle=None, alpha=0.5, marker="o", label="CAX")
        
                limits_focal = pass_rate + 0.2 # Define the extent of the diagram
                if show_epid_points:
                    p = ax_focal.plot([0],[0], "r+", mew=3, ms=10, label="BB/CAX")
                    tooltip3 = mpld3.plugins.PointLabelTooltip(p[0], labels=["Ballbearing or CAX"], location="top left")
                else:
                    p = ax_focal.plot([0],[0], "r+", mew=3, ms=10, label="BB")
                    tooltip3 = mpld3.plugins.PointLabelTooltip(p[0], labels=["Ballbearing"], location="top left")
                mpld3.plugins.connect(fig_focal, tooltip3)
                ax_focal.add_patch(patches.Circle((0, 0), pass_rate, color='r', linestyle="dashed", fill=False))
                ax_focal.add_patch(patches.Circle((0, 0), success_rate, color='g', linestyle="dashed", fill=False))
                ax_focal.autoscale(False)
                ax_focal.set_xlim([-limits_focal, limits_focal])
                ax_focal.set_ylim([-limits_focal, limits_focal])
                ax_focal.set_title("Scatter diagram")
                ax_focal.set_xlabel("X [mm]")
                ax_focal.set_ylabel("Y [mm]")
                ax_focal.legend(framealpha=0, numpoints=1, ncol=3, loc='lower right', fontsize=8)
                fig_focal.set_tight_layout(True)
    
                # Plot Winkler gantry diagram
                if len(cax2bb) == 8:
                    gantry = np.asarray([180, 180, 270, 270, 0, 0, 90, 90])*np.pi/180
                    t = np.linspace(-10, 10, 2)
                    for i in range(len(cax2bb)):
                        x = cax2bb[i][0]*np.cos(gantry[i]) + np.sin(gantry[i])*t
                        y = cax2bb[i][0]*np.sin(gantry[i]) + np.cos(gantry[i])*t
                        ax_gantry.plot(x, y, color="grey", alpha=0.5, linewidth=1, linestyle="--" if i in range(4) else "-")
                    # Plot average lines
                    limits_gantry_list = []
                    gantry_center_x = []
                    gantry_center_y = []
                    for i in [0, 2, 4, 6]:
                        x1 = cax2bb[i][0]*np.cos(gantry[i]) + np.sin(gantry[i])*t
                        x2 = cax2bb[i+1][0]*np.cos(gantry[i+1]) + np.sin(gantry[i+1])*t
                        y1 = cax2bb[i][0]*np.sin(gantry[i]) + np.cos(gantry[i])*t
                        y2 = cax2bb[i+1][0]*np.sin(gantry[i+1]) + np.cos(gantry[i+1])*t
                        x = (x1+x2)/2
                        y = (y1+y2)/2
                        if i in [0, 4]:
                            limits_gantry_list.append(np.max(np.abs([x])))
                            gantry_center_x.append(x)
                        else:
                            limits_gantry_list.append(np.max(np.abs([y])))
                            gantry_center_y.append(y)
                        ax_gantry.plot(x, y, color="purple", linewidth=2, linestyle="--" if i in range(4) else "-")
    
                elif len(cax2bb) == 4:
                    gantry = np.asarray([180, 270, 0, 90])*np.pi/180
                    t = np.linspace(-10, 10, 2)
                    # Plot average lines
                    limits_gantry_list = []
                    gantry_center_x = []
                    gantry_center_y = []
                    for i in range(len(cax2bb)):
                        x = cax2bb[i][0]*np.cos(gantry[i]) + np.sin(gantry[i])*t
                        y = cax2bb[i][0]*np.sin(gantry[i]) + np.cos(gantry[i])*t
                        ax_gantry.plot(x, y, color="purple", linewidth=2, linestyle="--" if i in range(2) else "-")
    
                        if i in [0, 2]:
                            limits_gantry_list.append(np.max(np.abs([x])))
                            gantry_center_x.append(x)
                        else:
                            limits_gantry_list.append(np.max(np.abs([y])))
                            gantry_center_y.append(y)
                else:
                    limits_gantry_list = [-1,1]
                    gantry_center_x = []
                    gantry_center_y = []
                gantry_center_x = np.average(gantry_center_x)
                gantry_center_y = np.average(gantry_center_y)
                limits_gantry = np.max(limits_gantry_list) + 0.2
                ax_gantry.set_xlim([-limits_gantry, limits_gantry])
                ax_gantry.set_ylim([-limits_gantry, limits_gantry])
                ax_gantry.set_xlabel("LAT [mm]")
                ax_gantry.set_ylabel("VRT [mm]")
                ax_gantry.set_title("Gantry 2D CAX projection")
                ax_gantry.plot([0], [0], "r+", mew=3, ms=10, label="BB")
                ax_gantry.plot([gantry_center_x], [gantry_center_y], "x", color="black", mew=1, ms=10, label="Axis")
                ax_gantry.legend(framealpha=0, numpoints=1, ncol=2, loc='lower right', fontsize=8)
                ax_gantry.autoscale(False)
    
                script_focal = mpld3.fig_to_html(fig_focal, d3_url=D3_URL, mpld3_url=MPLD3_URL)
                general_functions.delete_figure([fig_focal])
                
                # Calculate radius from center of CAX cloud to CAX:
                average_x = np.average(cax2bb[:, 0])
                average_y = np.average(cax2bb[:, 1])
                cax_wobble = np.linalg.norm(np.column_stack((cax2bb[:, 0]-average_x, cax2bb[:, 1]-average_y)), axis=1)
                
                # Calculate EPID position with respect to CAX:
                epid2cax_dev_avg = np.average(epid2cax, axis=0)

                variables = {
                             "institution": config.INSTITUTION,
                             "acquisition_datetime": acquisition_datetime,
                             "script": script,
                             "script_focal": script_focal,
                             "cax_position": cax_position,
                             "bb_position": bb_position,
                             "result": result,
                             "max_deviation": round(np.max(radius), 2),
                             "cax_wobble_max": np.max(cax_wobble),
                             "epid2cax_dev_avg": epid2cax_dev_avg,
                             "radius": radius,
                             "pass_rate": pass_rate,
                             "image_numbers": img_numbers,
                             "success_rate": success_rate,
                             "coll_asym_tol": coll_asym_tol,
                             "beam_dev_tol": beam_dev_tol,
                             "SIDs": list(set(SIDs)),
                             "apply_tolerance_to_coll_asym": apply_tolerance_to_coll_asym,
                             "save_results": save_results,
                             "plweb_folder": PLWEB_FOLDER
                             }

                return template("winston_lutz_results", variables)
            else:
                if test_type=="Gnt/coll + couch rotation":
                    M = 8  # redefine
                    # Add scatter plot for the diagram
                    fig_focal = Figure(figsize=(10.5, 5), tight_layout={"w_pad":0,  "pad": 0})
                    ax_focal = fig_focal.add_subplot(1,2,1, aspect=1)
                    ax_couch = fig_focal.add_subplot(1,2,2, aspect=1)
                    
                    cax2bb_gntcoll = np.asarray(cax2bb)[:8]  # pick only the first 8 images!
                    epid2cax_gntcoll = np.asarray(epid2cax)[:8]
                    bb_position_couch = np.asarray(bb_position)[8:]
                    cax2epid_couch = -np.asarray(epid2cax)[8:]
    
                    colors = ["blue"]*M
                    colors2 = ["yellow"]*M
                    labels = ['Img = {:d}, x = {:04.2f} mm, y = {:04.2f} mm, R = {:04.2f} mm'.format(img_numbers[i], cax2bb_gntcoll[i, 0], cax2bb_gntcoll[i, 1], 
                              np.linalg.norm(cax2bb_gntcoll[i, :])) for i in range(M)]
                    ax_focal.scatter(cax2bb_gntcoll[:,0], cax2bb_gntcoll[:, 1], c=colors, alpha=0.5,  s=80, zorder=1, linewidths=1)
                    scatter = ax_focal.plot(cax2bb_gntcoll[:,0], cax2bb_gntcoll[:, 1], linestyle="-", color="green", alpha=0.5, marker="o", markersize=12, zorder=2,  markerfacecolor='none', markeredgecolor='none')
                    tooltip = mpld3.plugins.PointLabelTooltip(scatter[0], labels=labels, location="top left")
    
                    if show_epid_points:
                        labels2 = ['Img = {:d}, x = {:04.2f} mm, y = {:04.2f} mm, R = {:04.2f} mm'.format(img_numbers[i], epid2cax_gntcoll[i, 0], epid2cax_gntcoll[i, 1], 
                                  np.linalg.norm(epid2cax_gntcoll[i, :])) for i in range(M)]
                        ax_focal.scatter(epid2cax_gntcoll[:,0], epid2cax_gntcoll[:, 1], c=colors2, alpha=0.5,  s=80, zorder=1, linewidths=1)
                        scatter2 = ax_focal.plot(epid2cax_gntcoll[:,0], epid2cax_gntcoll[:, 1], linestyle="-", color="none", alpha=0.5, marker="o", markersize=12, zorder=2,  markerfacecolor='none', markeredgecolor='none')
                        tooltip2 = mpld3.plugins.PointLabelTooltip(scatter2[0], labels=labels2, location="top left")
                        mpld3.plugins.connect(fig_focal, tooltip, tooltip2)
                        ax_focal.plot([None], [None], c="yellow", linestyle=None, alpha=0.5, marker="o", label="EPID") # Legend labels
                    else:
                        mpld3.plugins.connect(fig_focal, tooltip)
                    
                    # Legend labels:
                    ax_focal.plot([None], [None], c="blue", linestyle=None, alpha=0.5, marker="o", label="CAX")
            
                    limits_focal = pass_rate + 0.2 # Define the extent of the diagram
                    if show_epid_points:
                        p = ax_focal.plot([0],[0], "r+", mew=3, ms=10, label="BB/CAX")
                        tooltip3 = mpld3.plugins.PointLabelTooltip(p[0], labels=["Ballbearing or CAX"], location="top left")
                    else:
                        p = ax_focal.plot([0],[0], "r+", mew=3, ms=10, label="BB")
                        tooltip3 = mpld3.plugins.PointLabelTooltip(p[0], labels=["Ballbearing"], location="top left")
                    mpld3.plugins.connect(fig_focal, tooltip3)
                    ax_focal.add_patch(patches.Circle((0, 0), pass_rate, color='r', linestyle="dashed", fill=False))
                    ax_focal.add_patch(patches.Circle((0, 0), success_rate, color='g', linestyle="dashed", fill=False))
                    ax_focal.autoscale(False)
                    ax_focal.set_xlim([-limits_focal, limits_focal])
                    ax_focal.set_ylim([-limits_focal, limits_focal])
                    ax_focal.set_title("Gnt/coll diagram")
                    ax_focal.set_xlabel("X [mm]")
                    ax_focal.set_ylabel("Y [mm]")
                    ax_focal.legend(framealpha=0, numpoints=1, ncol=3, loc='lower right', fontsize=8)
                    fig_focal.set_tight_layout(True)
            
                    # Plot scatter plot for couch!
                    # Calculate circle fit to BB point (with respect to CAX):
                    def calc_R(xc, yc):
                        #calculate the distance of each 2D points from the center (xc, yc)
                        # Do not include first point in the calculation!!!!1
                        return np.sqrt((bb_position_couch[1:,0]-xc)**2 + (bb_position_couch[1:,1]-yc)**2)
                    
                    def f_2(c):
                        #calculate the algebraic distance between the data points and the mean circle centered at c=(xc, yc)
                        Ri = calc_R(*c)
                        return Ri - Ri.mean()
                    try:
                        solution = optimize.least_squares(f_2, x0=[start_x, start_y], bounds=[-5, 5])
                        center_2 = solution.x
                    except:
                        center_2 = [np.nan, np.nan]
                    
                    Ri_2 = calc_R(*center_2)
                    R_2 = Ri_2.mean()
                    
                    # Calculate distance of couch axis from rad center
                    lat = (-result[0][0]-result[1][0]+result[4][0]+result[5][0])/4
                    long = (result[0][1]+result[1][1]+result[2][1]+result[3][1] +result[4][1]+result[5][1]+result[6][1]+result[7][1])/8
                    linac_iso_x = lat + bb_position_couch[0][0]  # Here you define the reference for linac isocenter
                    linac_iso_y = long + bb_position_couch[0][1]
                    #linac_iso_x = lat + bb_position[4][0]
                    #linac_iso_y = long + bb_position[4][1]  # Take the fitfh image from the first seuqence
                    couch_iso_dev_x = center_2[0] - linac_iso_x
                    couch_iso_dev_y = center_2[1] - linac_iso_y
                    
                    # Plot BB with respect to epid center (reference)
                    NN = len(bb_position_couch)
                    colors_couch = ["red"]*NN
                    labels_couch = ['Img = {:d}, x = {:04.2f} mm, y = {:04.2f} mm, R = {:04.2f} mm'.format(img_numbers[8+i], bb_position_couch[i, 0], bb_position_couch[i, 1], 
                                    np.linalg.norm(bb_position_couch[i, :])) for i in range(NN)]
                    ax_couch.scatter(bb_position_couch[:,0], bb_position_couch[:, 1], c=colors_couch, alpha=0.5,  s=80, zorder=1, linewidths=1)
                    scatter_couch = ax_couch.plot(bb_position_couch[:,0], bb_position_couch[:, 1], linestyle="-", color="green", alpha=0.5, marker="o", markersize=12, zorder=2,  markerfacecolor='none', markeredgecolor='none')
                    tooltip11 = mpld3.plugins.PointLabelTooltip(scatter_couch[0], labels=labels_couch, location="top left")
        
                    # Plot CAX points with respect to epid center
                    labels_couch_cax = ['Img = {:d}, x = {:04.2f} mm, y = {:04.2f} mm, R = {:04.2f} mm'.format(img_numbers[8+i], cax2epid_couch[i, 0], cax2epid_couch[i, 1], 
                                        np.linalg.norm(cax2epid_couch[i, :])) for i in range(NN)]
                    pp = ax_couch.plot(cax2epid_couch[:,0], cax2epid_couch[:,1], c="blue", linestyle=None, linewidth=0, alpha=0.85, markersize = 5, marker="o", label="CAX")
                    tooltip33 = mpld3.plugins.PointLabelTooltip(pp[0], labels=labels_couch_cax, location="top left")
                    
                    # Plot center of couch axis (circle)
                    ax_couch.add_patch(patches.Circle(center_2, R_2, color='black', alpha=0.85, fill=False, linewidth=1))
                    labels_cc = ['Couch axis, x = {:04.2f} mm, y = {:04.2f} mm'.format(center_2[0], center_2[1])]
                    ax_couch.plot([center_2[0]], [center_2[1]], linestyle="None", color="black", alpha=1, marker="x", markersize=12, zorder=2)
                    cc = ax_couch.plot([center_2[0]], [center_2[1]], linestyle="None", color="black", alpha=1, marker="o", markersize=15, zorder=2,  markerfacecolor='none', markeredgecolor='none')
                    tooltip4 = mpld3.plugins.PointLabelTooltip(cc[0], labels=labels_cc, location="top left")
                    
                    # Plot isocenter of linac
                    qq = ax_couch.plot([linac_iso_x],[linac_iso_y], c="blue", linestyle=None, linewidth=0, alpha=0.5, marker="s", markersize = 10, label="ISO")
                    tooltip331 = mpld3.plugins.PointLabelTooltip(qq[0], labels=["Linac isocenter x = {:04.2f} mm, y = {:04.2f} mm".format(linac_iso_x, linac_iso_y)], location="top left")
                    
                    # Plot pass rates as cricle etc
                    #ax_couch.add_patch(patches.Circle((0, 0), pass_rate, color='r', linestyle="dashed", fill=False))
                    #ax_couch.add_patch(patches.Circle((0, 0), success_rate, color='g', linestyle="dashed", fill=False))
    
                    ax_couch.plot([None], [None], c="red", linestyle=None, linewidth=0, alpha=0.5, marker="o", markersize = 10, label="BB")
                    ax_couch.plot([None], [None], c="black", linestyle=None, linewidth=0, alpha=1, markersize=10, marker="x", label="Axis") # Legend labels
                    
                    mpld3.plugins.connect(fig_focal, tooltip11, tooltip33, tooltip4, tooltip331)
                    
                    ax_couch.autoscale(False)
    
                    margin = 0.2
                    if 2*R_2 < 1:
                        margin = 1 - R_2 + 0.2
    
                    limits_focal_couch_xmin = center_2[0] - R_2 - margin
                    limits_focal_couch_xmax = center_2[0] + R_2 + margin
                    limits_focal_couch_ymin = center_2[1] - R_2 - margin
                    limits_focal_couch_ymax = center_2[1] + R_2 + margin
                    
                    ax_couch.set_xlim([limits_focal_couch_xmin, limits_focal_couch_xmax])
                    ax_couch.set_ylim([limits_focal_couch_ymin, limits_focal_couch_ymax])
                    ax_couch.set_title("Couch diagram")
                    ax_couch.set_xlabel("LAT [mm]")
                    ax_couch.set_ylabel("LONG [mm]")
                    ax_couch.legend(framealpha=0, numpoints=1, ncol=4, loc='lower right', fontsize=8)
            
                    script_focal = mpld3.fig_to_html(fig_focal, d3_url=D3_URL, mpld3_url=MPLD3_URL)
                    general_functions.delete_figure([fig_focal])
                    
                    # Calculate radius from center of CAX cloud to CAX:
                    average_x = np.average(cax2bb_gntcoll[:, 0])
                    average_y = np.average(cax2bb_gntcoll[:, 1])
                    cax_wobble = np.linalg.norm(np.column_stack((cax2bb_gntcoll[:, 0]-average_x, cax2bb_gntcoll[:, 1]-average_y)), axis=1)
            
                    # Calculate EPID position with respect to CAX:
                    epid2cax_dev_avg = np.average(epid2cax_gntcoll, axis=0)

                    variables = {
                                 "institution": config.INSTITUTION,
                                 "acquisition_datetime": acquisition_datetime,
                                 "script": script,
                                 "script_focal": script_focal,
                                 "cax_position": cax_position,
                                 "bb_position": bb_position,
                                 "result": result,
                                 "max_deviation": round(np.max(radius), 2),
                                 "cax_wobble_max": np.max(cax_wobble),
                                 "epid2cax_dev_avg": epid2cax_dev_avg,
                                 "radius": radius,
                                 "pass_rate": pass_rate,
                                 "image_numbers": img_numbers,
                                 "success_rate": success_rate,
                                 "coll_asym_tol": coll_asym_tol,
                                 "beam_dev_tol": beam_dev_tol,
                                 "couch_dist_tol": couch_dist_tol,
                                 "SIDs": list(set(SIDs)),
                                 "apply_tolerance_to_coll_asym": apply_tolerance_to_coll_asym,
                                 "couch_wobble": R_2,
                                 "couch_iso_dev_x": couch_iso_dev_x,
                                 "couch_iso_dev_y": couch_iso_dev_y,
                                 "save_results": save_results,
                                 "plweb_folder": PLWEB_FOLDER
                                 }
                    #gc.collect() # Collect and delete mpl plots

                    return template("winston_lutz_results_gntcollcouch", variables)
    
                elif test_type == "Couch only":  # if only the couch is rotated, no gnt or coll
                    # Add scatter plot for the diagram
                    fig_couch = Figure(figsize=(7, 7))
                    ax_couch = fig_couch.add_subplot(1,1,1, aspect=1)
    
                    epid2cax = np.asarray(epid2cax)
                    cax2epid_couch = -np.asarray(epid2cax)
                    bb_position_couch = np.asarray(bb_position)
                    
                    def calc_R(xc, yc):
                        #calculate the distance of each 2D points from the center (xc, yc)
                        return np.sqrt((bb_position_couch[:,0]-xc)**2 + (bb_position_couch[:,1]-yc)**2)
                    
                    def f_2(c):
                        #calculate the algebraic distance between the data points and the mean circle centered at c=(xc, yc)
                        Ri = calc_R(*c)
                        return Ri - Ri.mean()
                    
                    try:
                        solution = optimize.least_squares(f_2, x0=[start_x, start_y], bounds=[-5, 5])
                        center_2 = solution.x
                    except:
                        center_2 = [np.nan, np.nan]
                    
                    Ri_2 = calc_R(*center_2)
                    R_2 = Ri_2.mean()
            
                    # Plot BB with respect to epid center (reference)
                    NN = len(bb_position_couch)
                    colors_couch = ["red"]*NN
                    labels_couch = ['Img = {:d}, x = {:04.2f} mm, y = {:04.2f} mm, R = {:04.2f} mm'.format(img_numbers[i], bb_position_couch[i, 0], bb_position_couch[i, 1], 
                                    np.linalg.norm(bb_position_couch[i, :])) for i in range(NN)]
                    ax_couch.scatter(bb_position_couch[:,0], bb_position_couch[:, 1], c=colors_couch, alpha=0.5,  s=80, zorder=1, linewidths=1)
                    scatter_couch = ax_couch.plot(bb_position_couch[:,0], bb_position_couch[:, 1], linestyle="-", color="green", alpha=0.5, marker="o", markersize=12, zorder=2,  markerfacecolor='none', markeredgecolor='none')
                    tooltip11 = mpld3.plugins.PointLabelTooltip(scatter_couch[0], labels=labels_couch, location="top left")
        
                    # Plot CAX points with respect to epid center
                    labels_couch_cax = ['Img = {:d}, x = {:04.2f} mm, y = {:04.2f} mm, R = {:04.2f} mm'.format(img_numbers[i], cax2epid_couch[i, 0], cax2epid_couch[i, 1], 
                                        np.linalg.norm(cax2epid_couch[i, :])) for i in range(NN)]
                    pp = ax_couch.plot(cax2epid_couch[:,0], cax2epid_couch[:,1], c="blue", linestyle=None, linewidth=0, alpha=0.85, markersize = 5, marker="o", label="CAX")
                    tooltip33 = mpld3.plugins.PointLabelTooltip(pp[0], labels=labels_couch_cax, location="top left")
                    
                    # Plot center of couch axis (circle)
                    ax_couch.add_patch(patches.Circle(center_2, R_2, color='black', alpha=0.85, fill=False, linewidth=1))
                    labels_cc = ['Couch axis, x = {:04.2f} mm, y = {:04.2f} mm'.format(center_2[0], center_2[1])]
                    ax_couch.plot([center_2[0]], [center_2[1]], linestyle="None", color="black", alpha=1, marker="x", markersize=12, zorder=2)
                    cc = ax_couch.plot([center_2[0]], [center_2[1]], linestyle="None", color="black", alpha=1, marker="o", markersize=15, zorder=2,  markerfacecolor='none', markeredgecolor='none')
                    tooltip4 = mpld3.plugins.PointLabelTooltip(cc[0], labels=labels_cc, location="top left")
    
                    ax_couch.plot([None], [None], c="red", linestyle=None, linewidth=0, alpha=0.5, marker="o", markersize = 10, label="BB")
                    ax_couch.plot([None], [None], c="black", linestyle=None, linewidth=0, alpha=1, markersize=10, marker="x", label="couch") # Legend labels
                    
                    mpld3.plugins.connect(fig_couch, tooltip11, tooltip33, tooltip4)
                    
                    ax_couch.autoscale(False)
                    margin = 0.2
                    if 2*R_2 < 1:
                        margin = 1 - R_2 + 0.2
    
                    limits_focal_couch_xmin = center_2[0] - R_2 - margin
                    limits_focal_couch_xmax = center_2[0] + R_2 + margin
                    limits_focal_couch_ymin = center_2[1] - R_2 - margin
                    limits_focal_couch_ymax = center_2[1] + R_2 + margin
                    
                    ax_couch.set_xlim([limits_focal_couch_xmin, limits_focal_couch_xmax])
                    ax_couch.set_ylim([limits_focal_couch_ymin, limits_focal_couch_ymax])
                    ax_couch.set_title("Couch diagram")
                    ax_couch.set_xlabel("LAT [mm]")
                    ax_couch.set_ylabel("LONG [mm]")
                    ax_couch.legend(framealpha=0, numpoints=1, ncol=4, loc='lower right', fontsize=8)
            
                    script_focal = mpld3.fig_to_html(fig_couch, d3_url=D3_URL, mpld3_url=MPLD3_URL)
                    general_functions.delete_figure([fig_couch])

                    variables = {
                                 "institution": config.INSTITUTION,
                                 "acquisition_datetime": acquisition_datetime,
                                 "script": script,
                                 "script_focal": script_focal,
                                 "cax_position": cax_position,
                                 "cax_avg": np.average(cax_position, axis=0),
                                 "bb_position": bb_position,
                                 "result": result,
                                 "radius": radius,
                                 "iso_size": R_2,
                                 "iso_position": center_2,
                                 "image_numbers": img_numbers,
                                 "SIDs": list(set(SIDs)),
                                 "save_results": save_results,
                                 "plweb_folder": PLWEB_FOLDER
                                 }

                    return template("winston_lutz_results_couchonly", variables)
    
                else: #test_type == "Colimator only":  # if only the collimator is rotated
                    # Add scatter plot for the diagram
                    fig_coll = Figure(figsize=(7, 7))
                    ax_coll = fig_coll.add_subplot(1,1,1, aspect=1)
                    
                    cax2bb = np.asarray(cax2bb)
                    bb_position = np.asarray(bb_position)
                    
                    def calc_R(xc, yc):
                        #calculate the distance of each 2D points from the center (xc, yc)
                        return np.sqrt((cax2bb[:,0]-xc)**2 + (cax2bb[:,1]-yc)**2)
                    
                    def f_2(c):
                        #calculate the algebraic distance between the data points and the mean circle centered at c=(xc, yc)
                        Ri = calc_R(*c)
                        return Ri - Ri.mean()
                    
                    try:
                        solution = optimize.least_squares(f_2, x0=[start_x, start_y], bounds=[-5, 5])
                        center_2 = solution.x
                    except:
                        center_2 = [np.nan, np.nan]
                    
                    Ri_2 = calc_R(*center_2)
                    R_2 = Ri_2.mean()
            
                    # Plot BB with respect to epid center (reference)
                    NN = len(cax2bb)
    
                    # Plot CAX points with respect to epid center
                    labels_couch_cax = ['Img = {:d}, x = {:04.2f} mm, y = {:04.2f} mm, R = {:04.2f} mm'.format(img_numbers[i], cax2bb[i, 0], cax2bb[i, 1], 
                                        np.linalg.norm(cax2bb[i, :])) for i in range(NN)]
                    pp = ax_coll.plot(cax2bb[:,0], cax2bb[:,1], c="blue", linestyle="-", linewidth=1, alpha=0.5, markersize = 10, marker="o", label="CAX")
                    tooltip33 = mpld3.plugins.PointLabelTooltip(pp[0], labels=labels_couch_cax, location="top left")
                    
                    # Plot center of axis (circle)
                    ax_coll.add_patch(patches.Circle(center_2, R_2, color='black', alpha=0.85, fill=False, linewidth=1))
                    labels_cc = ['Collimator axis, x = {:04.2f} mm, y = {:04.2f} mm'.format(center_2[0], center_2[1])]
                    ax_coll.plot([center_2[0]], [center_2[1]], linestyle="None", color="black", alpha=1, marker="x", markersize=12, zorder=2)
                    cc = ax_coll.plot([center_2[0]], [center_2[1]], linestyle="None", color="black", alpha=1, marker="o", markersize=15, zorder=2,  markerfacecolor='none', markeredgecolor='none')
                    tooltip4 = mpld3.plugins.PointLabelTooltip(cc[0], labels=labels_cc, location="top left")
    
                    ax_coll.plot([None], [None], c="black", linestyle=None, linewidth=0, alpha=1, markersize=10, marker="x", label="Axis") # Legend labels
                    #ax_coll.plot([None], [None], c="red", linestyle=None, linewidth=0, alpha=1, markersize=10, marker="+", label="BB") # Legend labels
                    
                    pe = ax_coll.plot([0],[0], "r+", mew=3, ms=10, label="BB")
                    tooltip3 = mpld3.plugins.PointLabelTooltip(pe[0], labels=["Ballbearing"], location="top left")
                    
                    mpld3.plugins.connect(fig_coll, tooltip3, tooltip33, tooltip4)
                    
                    ax_coll.autoscale(False)
                    limits_focal_coll_xmin = center_2[0] - R_2 - 0.2
                    limits_focal_coll_xmax = center_2[0] + R_2 + 0.2
                    limits_focal_coll_ymin = center_2[1] - R_2 - 0.2
                    limits_focal_coll_ymax = center_2[1] + R_2 + 0.2
                    
                    ax_coll.set_xlim([limits_focal_coll_xmin, limits_focal_coll_xmax])
                    ax_coll.set_ylim([limits_focal_coll_ymin, limits_focal_coll_ymax])
                    ax_coll.set_title("Collimator diagram")
                    ax_coll.set_xlabel("LAT [mm]")
                    ax_coll.set_ylabel("LONG [mm]")
                    ax_coll.legend(framealpha=0, numpoints=1, ncol=4, loc='lower right', fontsize=8)
    
                    script_focal = mpld3.fig_to_html(fig_coll, d3_url=D3_URL, mpld3_url=MPLD3_URL)
                    general_functions.delete_figure([fig_coll])

                    variables = {
                                 "institution": config.INSTITUTION,
                                 "acquisition_datetime": acquisition_datetime,
                                 "script": script,
                                 "script_focal": script_focal,
                                 "cax_position": cax_position,
                                 "cax_avg": np.average(cax_position, axis=0),
                                 "bb_position": bb_position,
                                 "result": result,
                                 "radius": radius,
                                 "iso_size": R_2,
                                 "iso_position": center_2,
                                 "image_numbers": img_numbers,
                                 "SIDs": list(set(SIDs)),
                                 "save_results": save_results,
                                 "plweb_folder": PLWEB_FOLDER
                                 }

                    return template("winston_lutz_results_collimatoronly", variables)

        except Exception as w:
            general_functions.delete_files_in_subfolders(file_paths) # Delete temporary images (all subfolders)
            return template("error_template", {"error_message": "Unable to plot images. " + str(w),
                                               "plweb_folder": PLWEB_FOLDER})


@wl_app.route(PLWEB_FOLDER + '/winston_lutz_calculate/<w>/<c>/<p>', method="POST")
def winston_lutz_calculate(w, c, p):
    # Function that analyzes the images and sends results to the interface
    # p is for pylinac's analysis
    colormap = request.forms.hidden_colormap
    test_type = request.forms.hidden_testtype
    use_couch = True if request.forms.hidden_usecouch=="true" else False
    show_epid_points = True if request.forms.hidden_show_epid_points=="true" else False
    clip_box = float(w)*10.0
    instances_list = json.loads(request.forms.get("instances_list")) ## list of instances to analyze!
    station = request.forms.hidden_station
    imgdescription = request.forms.hidden_imgdescription
    displayname = request.forms.hidden_displayname
    acquisition_datetime = request.forms.hidden_datetime
    #acquisition_datetime = datetime.datetime.strptime(acquisition_datetime, "%Y/%m/%d | %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
    
    start_x = float(request.forms.get('hidden_startx'))
    start_y = float(request.forms.get('hidden_starty'))
    imglist = json.loads(request.forms.get("useimglist"))  # True/False -should the image be in the series?

    if not any(imglist):
        return template("error_template", {"error_message": "All images are unchecked.", "plweb_folder": PLWEB_FOLDER})

    if (sum(imglist)< 11) and (use_couch==True) and (test_type=="Gnt/coll + couch rotation"):
        return template("error_template", {"error_message": "At least 8 + 3 images are required to determine \
                                           linac isocenter and couch axis of rotation.", "plweb_folder": PLWEB_FOLDER})

    if (sum(imglist)< 3) and (use_couch==True) and (test_type=="Couch only"):
        return template("error_template", {"error_message": "At least 3 images are required to determine \
                                            couch axis of rotation.", "plweb_folder": PLWEB_FOLDER})

    if (sum(imglist)< 3) and (use_couch==True) and (test_type=="Collimator only"):
        return template("error_template", {"error_message": "At least 3 images are required to determine \
                                            collimator axis of rotation.", "plweb_folder": PLWEB_FOLDER})
    if p == "True": # if pylinac is chosen
        pylinac_angles_full = json.loads(request.forms.get("pylinacangles"))
        pylinac_angles_full = [int(float(x)) if x!="" else None for x in pylinac_angles_full]
        pylinac_angles_full_array = np.array(pylinac_angles_full).reshape((-1, 3)).tolist()
        pylinac_angles = []

        for i in range(0, len(pylinac_angles_full_array)):
            if imglist[i]:
                pylinac_angles.append(pylinac_angles_full_array[i])
        
        folder_path, file_paths, file_paths_full = RestToolbox.GetSeries2Folder(config.ORTHANC_URL, instances_list, imglist)

        # IF user entered values for gantry/couch/coll angles change file names:
        if pylinac_angles_full.count(None) == 0:
            if len(pylinac_angles) != len(file_paths):
                return template("error_template", {"error_message": "The number of angles does not match the number of images.", "plweb_folder": PLWEB_FOLDER})
            
            # Add coll/gantry/couch angles to the file name
            for z in range(0, len(file_paths)):
                f = file_paths[z]
                img_name = os.path.splitext(os.path.basename(f))[0]
                new_path = os.path.join(folder_path, img_name+"_gantry" + str(pylinac_angles[z][0]) + "_coll"+str(pylinac_angles[z][1])+
                                        "_couch"+str(pylinac_angles[z][2])+".dcm")
                os.replace(f, new_path)
                file_paths[z] = new_path
                file_paths_full[file_paths_full.index(f)] = new_path

        if clip_box != 0:
            for filename in file_paths:
                try:
                    orig_img = pylinacimage.DicomImage(filename)
                    orig_img.check_inversion() # Check inversion otherwise this might not work
                    general_functions.clip_around_image(orig_img, clip_box)
                    orig_img.save(filename)
                except:
                    return template("error_template", {"error_message": "Unable to apply clipbox.", "plweb_folder": PLWEB_FOLDER})
    else:
        pylinac_angles_full = []
        folder_path = []
        file_paths_full = RestToolbox.GetSeries2Subfolders(config.ORTHANC_URL, instances_list, imglist)
        # Get only those images that were ticked:
        
        file_paths = []
        for i in range(0, len(file_paths_full)):
            if imglist[i]:
                file_paths.append(file_paths_full[i])
        
        # Check if images are ordered correctly:
        #for subfolder in file_paths:    
        #    for filename in os.listdir(subfolder):
        #        print(general_functions.get_contenttime_seccheck_wl(pylinacimage.DicomImage(os.path.join(subfolder, filename))))
            
        if clip_box != 0:
            for subfolder in file_paths:    
                for filename in os.listdir(subfolder):
                    try:
                        orig_img = pylinacimage.DicomImage(os.path.join(subfolder, filename))
                        orig_img.check_inversion() # Check inversion otherwise this might not work
                        general_functions.clip_around_image(orig_img, clip_box)
                        orig_img.save(os.path.join(subfolder, filename))
                    except:
                        return template("error_template", {"error_message": "Unable to apply clipbox.", "plweb_folder": PLWEB_FOLDER})

    args = {"colormap": colormap,
            "clip_box": clip_box,
            "c": c,
            "p":p,
            "show_epid_points":show_epid_points,
            "file_paths_full":file_paths_full,
            "pylinac_angles_full":pylinac_angles_full,
            "folder_path":folder_path,
            "file_paths":file_paths,
            "imglist":imglist,
            "test_type":test_type,
            "use_couch":use_couch,
            "station": station,
            "imgdescription": imgdescription,
            "displayname": displayname,
            "acquisition_datetime": acquisition_datetime,
            "start_x": start_x,
            "start_y": start_y,
            "config": general_functions.get_configuration()
            }
    pool = Pool(1)
    data = pool.map(winstonlutz_helperf_catch_error, [args])
    pool.close()
    pool.join()
    return data

@wl_app.route(PLWEB_FOLDER + '/winstonlutz_pdf_export', method="post")
def winstonlutz_pdf_export():
    # Send the pdf file to the user
    pdf_file = str(request.forms.get("hidden_wl_pdf_report"))
    return static_file(pdf_file, root=config.PDF_REPORT_FOLDER, download=pdf_file)
