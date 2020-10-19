# I tried to implement multithreading but it turns out that python doesnt allow it....
import sys
import os
import tempfile
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
import numpy as np
import matplotlib.style
import matplotlib
matplotlib.use('Agg')
from matplotlib.figure import Figure

# To revert back to matplotlib 1.0 style
matplotlib.style.use('classic')

# pylinac
from pylinac import ct as pylinac_ct

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

# Working directory
PLWEB_FOLDER = config.PLWEB_FOLDER

PI = np.pi

def catphan_helperf_analyze(args):
    phantom = args["phantom"]
    general_functions.set_configuration(args["config"])  # Transfer to this process
    hu_tolerance = args["hu_tolerance"]
    scaling_tolerance = args["scaling_tolerance"]
    thickness_tolerance = args["thickness_tolerance"]
    low_contrast_tolerance = args["low_contrast_tolerance"]
    cnr_threshold = args["cnr_threshold"]
    path = args["path"]
    try:
        if phantom == "Catphan 503":
            mycbct_temp = pylinac_ct.CatPhan503(path)
        elif phantom == "Catphan 504":
            mycbct_temp = pylinac_ct.CatPhan504(path)
        elif phantom == "Catphan 600":
            mycbct_temp = pylinac_ct.CatPhan600(path)
        elif phantom == "Catphan 604":
            mycbct_temp = pylinac_ct.CatPhan604(path)
    
        mycbct_temp.analyze(hu_tolerance=hu_tolerance, scaling_tolerance=scaling_tolerance,
                            thickness_tolerance=thickness_tolerance, low_contrast_tolerance=low_contrast_tolerance,
                            cnr_threshold=cnr_threshold)
    except Exception as e:
        return e
    else:
        return mycbct_temp


# Here starts the bottle server
ctp_app = Bottle()

@ctp_app.route(PLWEB_FOLDER + '/catphan', method="POST")
def catphan_start():
    colormaps = ["gray", "Greys", "brg", "prism"]
    displayname = request.forms.hidden_displayname
    username = request.get_cookie("account", secret=config.SECRET_KEY)
    if not username:
        redirect(PLWEB_FOLDER + "/login")

    try:
        variables = general_functions.Read_from_dcm_database()
    except ConnectionError:
        return template("error_template", {"error_message": "Orthanc is refusing connection.",
                                           "plweb_folder": PLWEB_FOLDER})
    variables["displayname"] = displayname
    response.set_cookie("account", username, secret=config.SECRET_KEY, samesite="lax")
    
    # Get list of machines/beams/phantoms from the database
    machines_and_beams = {}
    for k in config.CATPHAN_PHANTOMS:
        machines_and_beams[k] = general_functions.get_machines_and_energies(general_functions.get_treatmentunits_catphan(k))
    variables["machines_beams_phantoms"] = machines_and_beams
    variables["colormaps"] = colormaps
    return template("catphan", variables)

@ctp_app.route(PLWEB_FOLDER + '/catphan_calculate/<s>', method="POST")
def catphan_calculate(s):
    use_reference = request.forms.hidden_ref
    use_reference = True if use_reference=="true" else False
    phantom = request.forms.hidden_phantom
    machine = request.forms.hidden_machine
    beam = request.forms.hidden_beam
    HU_delta = request.forms.hidden_HUdelta
    HU_delta = True if HU_delta=="true" else False
    colormap = request.forms.hidden_colormap
    displayname = request.forms.hidden_displayname
    acquisition_datetime = request.forms.hidden_datetime
    
    args = {"use_reference": use_reference, "phantom": phantom, "machine": machine,
            "beam": beam, "HU_delta": HU_delta, "colormap": colormap, "s": s,
            "displayname": displayname, "acquisition_datetime": acquisition_datetime,
            "config": general_functions.get_configuration()}
    
    p = Pool(1)
    data = p.map(catphan_calculate_helperf_catch_error, [args])
    p.close()
    p.join()
    return data

def catphan_calculate_helperf_catch_error(args):
    try:
        return catphan_calculate_helperf(args)
    except Exception as e:
        return template("error_template", {"error_message": str(e),
                                           "plweb_folder": PLWEB_FOLDER})


def catphan_calculate_helperf(args):
    use_reference = args["use_reference"]
    phantom = args["phantom"]
    machine = args["machine"]
    beam = args["beam"]
    HU_delta = args["HU_delta"]
    colormap = args["colormap"]
    displayname = args["displayname"]
    acquisition_datetime = args["acquisition_datetime"]
    s = args["s"]
    general_functions.set_configuration(args["config"])  # Transfer to this process

    save_results = {
                    "machine": machine,
                    "beam": beam,
                    "phantom": phantom,
                    "displayname": displayname
                    }
    # Set colormap
    cmap = matplotlib.cm.get_cmap(colormap)

    # Collect data for "save results"
    tolerances = general_functions.get_tolerance_user_machine_catphan(machine, beam, phantom)  # If user_machne has specific tolerance
    if not tolerances:
        hu, lcv, scaling, thickness, lowcontrast, cnr, mtf, uniformityidx, pdf_report_enable = "100", "2", "0.5", "0.25", "1", "10", "10", "3", "False"
    else:
        hu, lcv, scaling, thickness, lowcontrast, cnr, mtf, uniformityidx, pdf_report_enable = tolerances

    hu_tolerance = float(hu)
    lcv_tolerance = float(lcv)
    scaling_tolerance = float(scaling)
    thickness_tolerance = float(thickness)
    low_contrast_tolerance = float(lowcontrast)
    cnr_threshold = float(cnr)
    mtf_tolerance = float(mtf)
    uniformityidx_tolerance = float(uniformityidx)

    ref_path = general_functions.get_referenceimagepath_catphan(machine, beam, phantom)

    if ref_path is not None:
        ref_path = os.path.join(config.WORKING_DIRECTORY, config.REFERENCE_IMAGES_FOLDER, ref_path[0])
        if os.path.exists(ref_path):
            ref_exists = True
        else:
            ref_exists = False
    else:
        ref_exists = False
    
    folder_path = RestToolbox.GetSeries2Folder2(config.ORTHANC_URL, s)

    # Use two threads to speedup the calculation (if ref exists)
    args_current = {"hu_tolerance": hu_tolerance, "scaling_tolerance": scaling_tolerance,
                    "thickness_tolerance": thickness_tolerance, 
                    "cnr_threshold": cnr_threshold, "path": folder_path, 
                    "phantom": phantom, "low_contrast_tolerance": low_contrast_tolerance,
                    "config": general_functions.get_configuration()}
    
    args_ref = {"hu_tolerance": hu_tolerance, "scaling_tolerance": scaling_tolerance,
                "thickness_tolerance": thickness_tolerance, 
                "cnr_threshold": cnr_threshold, "path": ref_path, 
                "phantom": phantom, "low_contrast_tolerance": low_contrast_tolerance,
                "config": general_functions.get_configuration()}

    if use_reference and ref_exists:
        try:
            p = ThreadPool(2)
            [mycbct, mycbct_ref] = p.map(catphan_helperf_analyze, [args_current, args_ref])
        finally:
            p.close()
            p.join()
    else:
        mycbct = catphan_helperf_analyze(args_current)

    if use_reference and ref_exists:
        if isinstance(mycbct_ref, Exception):
            return template("error_template", {"error_message": "Unable to analyze reference image. " + str(mycbct_ref),
                                               "plweb_folder": PLWEB_FOLDER})
    if isinstance(mycbct, Exception):
        general_functions.delete_files_in_subfolders([folder_path]) # Delete temporary images
        return template("error_template", {"error_message": "Unable to analyze image. " + str(mycbct),
                                           "plweb_folder": PLWEB_FOLDER})
    
    try:  # add this to prevent memory problems when threads with exceptions are still alive
        
        # ######################### CTP528 - Resolution ###################################
        fig_dcm = Figure(figsize=(10.5, 5), tight_layout={"w_pad":0,  "pad": 1.5})
        ax1 = fig_dcm.add_subplot(1,2,1)
        ax2 = fig_dcm.add_subplot(1,2,2)
    
        # Reference image array
        if use_reference and ref_exists:
            ax1.imshow(mycbct_ref.ctp528.image.array, cmap=cmap, interpolation="none", aspect="equal", origin='upper')
            ax1.autoscale(enable=False)
        else:
            ax1.text(0.5, 0.5 ,"Reference image not available", horizontalalignment='center', verticalalignment='center')
    
        # Analysed current array
        ax2.imshow(mycbct.ctp528.image.array, cmap=cmap, interpolation="none", aspect="equal", origin='upper')
        ax2.set_title('CTP528 current image')
        ax1.set_title('CTP528 reference image')
        ax2.autoscale(enable=False)
    
        # Plot rMTF and gather some data
        fig_mtf = Figure(figsize=(5, 5), tight_layout={"w_pad":2, "pad": 1})
        ax_mtf = fig_mtf.add_subplot(1,1,1)
        msize = 8
        if use_reference and ref_exists:
            ax_mtf.plot(list(mycbct_ref.ctp528.mtf.norm_mtfs.keys()), list(mycbct_ref.ctp528.mtf.norm_mtfs.values()), marker='o', color="blue",
                        markersize=msize, markerfacecolor="None", linestyle="--")
    
        ax_mtf.plot(list(mycbct.ctp528.mtf.norm_mtfs.keys()), list(mycbct.ctp528.mtf.norm_mtfs.values()), marker='o', color="blue", markersize=msize)
        ax_mtf.margins(0.05)
        ax_mtf.grid('on')
        ax_mtf.set_xlabel('Line pairs / mm')
        ax_mtf.set_ylabel("Relative MTF")
        ax_mtf.set_title('Modulation transfer function')
        
        script_ctp528 = mpld3.fig_to_html(fig_dcm, d3_url=D3_URL, mpld3_url=MPLD3_URL)
        script_ctp528mtf = mpld3.fig_to_html(fig_mtf, d3_url=D3_URL, mpld3_url=MPLD3_URL)
    
        # Some data:
        mtf30_ref = mycbct_ref.ctp528.mtf.relative_resolution(30) if use_reference and ref_exists else np.nan
        mtf30 = mycbct.ctp528.mtf.relative_resolution(30)
        mtf50_ref = mycbct_ref.ctp528.mtf.relative_resolution(50) if use_reference and ref_exists else np.nan
        mtf50 = mycbct.ctp528.mtf.relative_resolution(50)
        mtf80_ref = mycbct_ref.ctp528.mtf.relative_resolution(80) if use_reference and ref_exists else np.nan
        mtf80 = mycbct.ctp528.mtf.relative_resolution(80)
    
        if use_reference and ref_exists:
            mtf_passing = True if abs(100*(mtf50-mtf50_ref)/mtf50_ref)<=mtf_tolerance else False
        else:
            mtf_passing = None
    
        # ####################### CTP404 - GEOMETRY HU LINEARITY ####################
        fig_404 = Figure(figsize=(10.5, 5), tight_layout={"w_pad":0,  "pad": 1.5})
        ax404_1 = fig_404.add_subplot(1,2,1)
        ax404_2 = fig_404.add_subplot(1,2,2)
    
        def ctp404_plotROI(mycbct, fig, axis):
            # Plot lines and circles - taken from pylinac
            # plot HU linearity ROIs
            for roi in mycbct.ctp404.hu_rois.values():
                axis.add_patch(matplotlib.patches.Circle((roi.center.x, roi.center.y), edgecolor=roi.plot_color, radius=roi.radius, fill=False))
            for roi in mycbct.ctp404.bg_hu_rois.values():
                axis.add_patch(matplotlib.patches.Circle((roi.center.x, roi.center.y), edgecolor='blue', radius=roi.radius, fill=False))
            # plot thickness ROIs
            for roi in mycbct.ctp404.thickness_rois.values():
                axis.add_patch(matplotlib.patches.Rectangle((roi.bl_corner.x, roi.bl_corner.y), width=roi.width, height=roi.height,
                                                               angle=0, edgecolor="blue", alpha=1, facecolor="g", fill=False))
            # plot geometry lines
            for line in mycbct.ctp404.lines.values():
                axis.plot((line.point1.x, line.point2.x), (line.point1.y, line.point2.y), linewidth=1, color=line.pass_fail_color)
    
            # Plot tooltips for patches
            names = []
            hu_rois_centers_x = []
            hu_rois_centers_y = []
            hu_rois_radius = []
    
            for name, roi in mycbct.ctp404.hu_rois.items():
                names.append(name)
                hu_rois_centers_x.append(roi.center.x)
                hu_rois_centers_y.append(roi.center.y)
                hu_rois_radius.append((roi.radius)**2)
    
            hu_rois_ttip = axis.scatter(hu_rois_centers_x, hu_rois_centers_y, s = hu_rois_radius, alpha=0)
            labels = [names[i] for i in range(len(names))]
            tooltip = mpld3.plugins.PointLabelTooltip(hu_rois_ttip, labels=labels)
            mpld3.plugins.connect(fig, tooltip)
            # Add tooltips for 4 lines
            inc = 1
            for line in mycbct.ctp404.lines.values():
                hu_lines_ttip = axis.plot((line.point1.x, line.point2.x), (line.point1.y, line.point2.y), alpha=0, lw=7)
                tooltip2 = mpld3.plugins.LineLabelTooltip(hu_lines_ttip[0], label="Line "+str(inc))
                mpld3.plugins.connect(fig, tooltip2)
                inc += 1
    
        # Reference image
        if use_reference and ref_exists:
            ax404_1.imshow(mycbct_ref.ctp404.image.array, cmap=cmap, interpolation="none", aspect="equal", origin='upper')
            #mycbct_ref.ctp404.plot_rois(ax404_1)
            ctp404_plotROI(mycbct_ref, fig_404, ax404_1)  # alternative
            ax404_1.autoscale(enable=False)
            ax404_1.set_xlim([0, mycbct_ref.ctp404.image.shape[1]])
            ax404_1.set_ylim([mycbct_ref.ctp404.image.shape[0], 0])
        else:
            ax404_1.text(0.5, 0.5 ,"Reference image not available", horizontalalignment='center', verticalalignment='center')
        # Current image
        ax404_2.imshow(mycbct.ctp404.image.array, cmap=cmap, interpolation="none", aspect="equal", origin='upper')
        ctp404_plotROI(mycbct, fig_404, ax404_2)  # alternative
        #mycbct.ctp404.plot_rois(ax404_2)
        ax404_2.set_xlim([0, mycbct.ctp404.image.shape[1]])
        ax404_2.set_ylim([mycbct.ctp404.image.shape[0], 0])
        ax404_1.set_title('CTP404 reference image')
        ax404_2.set_title('CTP404 current image')
        ax404_2.autoscale(enable=False)
    
        # Draw HU linearity plot
        def plot_linearity(mycbct, fig, axis, plot_delta):
            '''Taken from pylinac'''
            nominal_x_values = [roi.nominal_val for roi in mycbct.ctp404.hu_rois.values()]
            actual_values = []
            diff_values = []
            if plot_delta:
                values = []
                names = []
                for name, roi in mycbct.ctp404.hu_rois.items():
                    names.append(name)
                    values.append(roi.value_diff)
                    actual_values.append(roi.pixel_value)
                    diff_values.append(roi.value_diff)
                nominal_measurements = [0]*len(values)
                ylabel = 'HU Delta'
            else:
                values = []
                names = []
                for name, roi in mycbct.ctp404.hu_rois.items():
                    names.append(name)
                    values.append(roi.pixel_value)
                    actual_values.append(roi.pixel_value)
                    diff_values.append(roi.value_diff)
                nominal_measurements = nominal_x_values
                ylabel = 'Measured Values'
    
            points = axis.plot(nominal_x_values, values, 'g+', markersize=15, mew=2)
            axis.plot(nominal_x_values, nominal_measurements)
            axis.plot(nominal_x_values, np.array(nominal_measurements) + mycbct.ctp404.hu_tolerance, 'r--')
            axis.plot(nominal_x_values, np.array(nominal_measurements) - mycbct.ctp404.hu_tolerance, 'r--')
            axis.margins(0.07)
            axis.grid(True, alpha=0.35)
            axis.set_xlabel("Nominal Values")
            axis.set_ylabel(ylabel)
            axis.set_title("HU linearity")
            labels = [names[i]+" -- Nom.={:.1f}, Act.={:.1f}, Diff.={:.1f}".format(nominal_x_values[i], actual_values[i], diff_values[i]) for i in range(len(names))]
            tooltip = mpld3.plugins.PointLabelTooltip(points[0], labels=labels, location="top right")
            mpld3.plugins.connect(fig, tooltip)
    
        fig_404_HU = Figure(figsize=(10.5, 5), tight_layout={"w_pad":1})
        ax_HU_ref = fig_404_HU.add_subplot(1,2,1)
        ax_HU = fig_404_HU.add_subplot(1,2,2)
        # Reference HU linearity
        if use_reference and ref_exists:
            plot_linearity(mycbct_ref, fig_404_HU, ax_HU_ref, plot_delta=HU_delta)
        else:
            ax_HU_ref.text(0.5, 0.5 ,"Reference image not available", horizontalalignment='center', verticalalignment='center')
            ax_HU_ref.set_title("HU linearity")
        # Current HU linearity
        plot_linearity(mycbct, fig_404_HU, ax_HU, plot_delta=HU_delta)
        
        # Gather data from HU holes:
        if use_reference and ref_exists:
            HU_values_ref = []
            HU_std_ref = []
            HU_diff_ref = []
            cnrs404_ref = []
            for key, value in mycbct_ref.ctp404.hu_rois.items():
                HU_values_ref.append(value.pixel_value)
                HU_std_ref.append(round(value.std, 1))
                HU_diff_ref.append(value.value_diff)
                cnrs404_ref.append(round(value.cnr, 1))

            # Background HU ROIs
            for key, value in mycbct_ref.ctp404.bg_hu_rois.items():
                HU_values_ref.append(value.pixel_value)
                HU_std_ref.append(round(value.std, 1))
                HU_diff_ref.append(np.nan)
                cnrs404_ref.append(np.nan)
            
            lcv_ref = round(mycbct_ref.ctp404.lcv, 2)
            slice_thickness_ref = round(mycbct_ref.ctp404.meas_slice_thickness, 2)
            lines_ref = []  # Line length
            for l in mycbct_ref.ctp404.lines.values():
                lines_ref.append(round(l.length_mm, 2))
            lines_avg_ref = round(mycbct_ref.ctp404.avg_line_length, 2)
            phantom_roll_ref = round(mycbct_ref.ctp404.catphan_roll, 2)
            dicom_slice_thickness_ref = round(mycbct_ref.ctp404.slice_thickness, 2)
        else:
            length = len(list(mycbct.ctp404.hu_rois.values())+list(mycbct.ctp404.bg_hu_rois.values()))
            HU_values_ref = [np.nan]*length
            HU_std_ref = [np.nan]*length
            HU_diff_ref = [np.nan]*length
            cnrs404_ref = [np.nan]*length
            lcv_ref = np.nan
            slice_thickness_ref = np.nan
            lines_ref = [np.nan]*len(mycbct.ctp404.lines.values())
            lines_avg_ref = np.nan
            phantom_roll_ref = np.nan
            dicom_slice_thickness_ref = np.nan
            
    
        HU_values = []
        HU_std = []
        HU_diff = []
        HU_nominal = []
        HU_names = []
        cnrs404 = []
        HU_CNR_values_dict = {}
        for key, value in mycbct.ctp404.hu_rois.items():
            HU_values.append(value.pixel_value)
            HU_std.append(round(value.std, 1))
            HU_diff.append(value.value_diff)
            HU_nominal.append(value.nominal_val)
            HU_names.append(key)
            cnrs404.append(round(value.cnr, 1))
            HU_CNR_values_dict[key] = [value.pixel_value, round(value.cnr, 1)] 
        
        # Background HU ROIs
        for key, value in mycbct.ctp404.bg_hu_rois.items():
            HU_values.append(value.pixel_value)
            HU_std.append(round(value.std, 1))
            HU_diff.append(np.nan)
            HU_nominal.append(0)
            HU_names.append("Background "+str(key))
            cnrs404.append(np.nan)
            HU_CNR_values_dict[key] = [value.pixel_value, np.nan] 
        
        # For easier acces of values in results
        save_results["HU_CNR_values_dict"] = HU_CNR_values_dict
        
        lcv = mycbct.ctp404.lcv
        slice_thickness = round(mycbct.ctp404.meas_slice_thickness, 2)
        phantom_roll = round(mycbct.ctp404.catphan_roll, 2)
        dicom_slice_thickness = round(mycbct.ctp404.slice_thickness, 2)

        # Get origin slice and phantom center and slice number of other modules
        if use_reference and ref_exists:
            mm_per_pixel_ref = round(mycbct_ref.mm_per_pixel, 2)
            origin_slice_ref = mycbct_ref.origin_slice
            ctp528_slice_ref = mycbct_ref.ctp528.slice_num
            ctp486_slice_ref = mycbct_ref.ctp486.slice_num
            ctp515_slice_ref = mycbct_ref.ctp515.slice_num if phantom != "Catphan 503" else np.nan
            phantom_center_ref = [round(mycbct_ref.ctp404.phan_center.x, 2),
                                  round(mycbct_ref.ctp404.phan_center.y, 2)]
        else:
            mm_per_pixel_ref = np.nan
            origin_slice_ref = np.nan
            ctp528_slice_ref = np.nan
            ctp486_slice_ref = np.nan
            ctp515_slice_ref = np.nan
            phantom_center_ref = [np.nan, np.nan]
        mm_per_pixel = round(mycbct.mm_per_pixel, 2)
        origin_slice = mycbct.origin_slice
        ctp528_slice = mycbct.ctp528.slice_num
        ctp486_slice = mycbct.ctp486.slice_num
        ctp515_slice = mycbct.ctp515.slice_num if phantom != "Catphan 503" else np.nan
        phantom_center = [round(mycbct.ctp404.phan_center.x, 2), 
                          round(mycbct.ctp404.phan_center.y, 2)]
        
        lines = []  # Line length
        for l in mycbct.ctp404.lines.values():
            lines.append(round(l.length_mm, 2))
        lines_avg = round(mycbct.ctp404.avg_line_length, 2)
    
        passed_HU = mycbct.ctp404.passed_hu
        passed_thickness = mycbct.ctp404.passed_thickness
        passed_geometry = mycbct.ctp404.passed_geometry
    
        passed_lcv = True if lcv >= lcv_tolerance else False
        passed_404 = passed_HU and passed_thickness and passed_geometry and passed_lcv
    
        script_404 = mpld3.fig_to_html(fig_404, d3_url=D3_URL, mpld3_url=MPLD3_URL)
        script_404_HU = mpld3.fig_to_html(fig_404_HU, d3_url=D3_URL, mpld3_url=MPLD3_URL)
    
        # ############################## CTP486 - UNIFORMITY ####################
        fig_486 = Figure(figsize=(10.5, 5), tight_layout={"w_pad":0,  "pad": 1.5})
        ax486_1 = fig_486.add_subplot(1,2,1)
        ax486_2 = fig_486.add_subplot(1,2,2)
    
        if use_reference and ref_exists:
            ax486_1.imshow(mycbct_ref.ctp486.image.array, cmap=cmap, interpolation="none", aspect="equal", origin='upper')
            mycbct_ref.ctp486.plot_rois(ax486_1)
            # Add text inside ROI for reference to uniformity index:
            for ind, roi in enumerate(mycbct_ref.ctp486.rois.values()):
                ax486_1.text(roi.center.x, roi.center.y, str(ind), horizontalalignment='center', verticalalignment='center')
        else:
            ax486_1.text(0.5, 0.5 ,"Reference image not available", horizontalalignment='center', verticalalignment='center')
    
        ax486_2.imshow(mycbct.ctp486.image.array, cmap=cmap, interpolation="none", aspect="equal", origin='upper')
        mycbct.ctp486.plot_rois(ax486_2)
        # Add text inside ROI for reference to uniformity index:
        for ind, roi in enumerate(mycbct.ctp486.rois.values()):
            ax486_2.text(roi.center.x, roi.center.y, str(ind), horizontalalignment='center', verticalalignment='center')
        ax486_1.set_title('CTP486 reference image')
        ax486_1.autoscale(enable=False)
        ax486_2.set_title('CTP486 current image')
        ax486_2.autoscale(enable=False)
    
        script_486 = mpld3.fig_to_html(fig_486, d3_url=D3_URL, mpld3_url=MPLD3_URL)
    
        # Draw orthogonal profiles:
        fig_486_profile = Figure(figsize=(10.5, 5), tight_layout={"w_pad":0,  "pad": 1.5})
        ax486_profile_ref = fig_486_profile.add_subplot(1,2,1)
        ax486_profile = fig_486_profile.add_subplot(1,2,2)
        if use_reference and ref_exists:
            mycbct_ref.ctp486.plot_profiles(ax486_profile_ref)
        else:
            ax486_profile_ref.text(0.5, 0.5 ,"Reference image not available", horizontalalignment='center', verticalalignment='center')
        mycbct.ctp486.plot_profiles(ax486_profile)
        ax486_profile_ref.set_title('Reference uniformity profiles')
        ax486_profile.set_title('Current uniformity profiles')
    
        script_486_profile = mpld3.fig_to_html(fig_486_profile, d3_url=D3_URL, mpld3_url=MPLD3_URL)
    
        # Get mean pixel values and uniformity index:
        # take into account slope and intercept HU = slope * px + intercept
    
        if use_reference and ref_exists:
            hvalues_ref = [roi.pixel_value for roi in mycbct_ref.ctp486.rois.values()]
            uidx_ref = round(mycbct_ref.ctp486.uniformity_index, 2)
        else:
            hvalues_ref = [np.nan]*len(mycbct.ctp486.rois.values())
            uidx_ref = np.nan
        hvalues = [roi.pixel_value for roi in mycbct.ctp486.rois.values()]
        passed_uniformity = mycbct.ctp486.overall_passed
    
        uidx = round(mycbct.ctp486.uniformity_index, 2)
    
        passed_uniformity_index = True if abs(uidx)<=uniformityidx_tolerance else False
    
        # ############################## CTP515 - LOW CONTRAST ####################
        if phantom != "Catphan 503":
            show_ctp515 = True
            fig_515 = Figure(figsize=(10.5, 5), tight_layout={"w_pad":0,  "pad": 1.5})
            ax515_1 = fig_515.add_subplot(1,2,1)
            ax515_2 = fig_515.add_subplot(1,2,2)
            if use_reference and ref_exists:
                ax515_1.imshow(mycbct_ref.ctp515.image.array, cmap=cmap, interpolation="none", aspect="equal", origin='upper')
                mycbct_ref.ctp515.plot_rois(ax515_1)
            else:
                ax515_1.text(0.5, 0.5 ,"Reference image not available", horizontalalignment='center', verticalalignment='center')
        
            ax515_2.imshow(mycbct.ctp515.image.array, cmap=cmap, interpolation="none", aspect="equal", origin='upper')
            mycbct.ctp515.plot_rois(ax515_2)
            ax515_1.set_title('CTP515 reference image')
            ax515_1.autoscale(enable=False)
            ax515_2.set_title('CTP515 current image')
            ax515_2.autoscale(enable=False)
            
            script_515 = mpld3.fig_to_html(fig_515, d3_url=D3_URL, mpld3_url=MPLD3_URL)
        
            fig_515_contrast = Figure(figsize=(10, 5), tight_layout={"w_pad":1, "pad": 1})
            ax515_contrast = fig_515_contrast.add_subplot(1,2,1)
            ax515_cnr = fig_515_contrast.add_subplot(1,2,2)
            
            cnrs_names = []
            contrasts_515 = []
            cnrs515 = []
            for key, value in mycbct.ctp515.rois.items():
                cnrs_names.append(key)
                contrasts_515.append(value.contrast_constant)
                cnrs515.append(round(value.cnr_constant, 2))
            sizes_515 = np.array(cnrs_names, dtype=int)
            
            ax515_contrast.plot(sizes_515, contrasts_515, marker='o', color="blue",
                                markersize=8, markerfacecolor="None", linestyle="-")
            ax515_cnr.plot(sizes_515, cnrs515, marker='o', color="blue",
                                markersize=8, markerfacecolor="None", linestyle="-")
            
            if use_reference and ref_exists:
                contrasts_515_ref = []
                cnrs515_ref = []
                cnrs_names_ref = []
                for key, value in mycbct_ref.ctp515.rois.items():
                    cnrs_names_ref.append(key)
                    contrasts_515_ref.append(value.contrast_constant)
                    cnrs515_ref.append(round(value.cnr_constant, 2))
                sizes_515_ref = np.array(cnrs_names_ref, dtype=int)
                ax515_contrast.plot(sizes_515_ref, contrasts_515_ref, marker='o', color="blue",
                                    markersize=8, markerfacecolor="None", linestyle="--")
                ax515_cnr.plot(sizes_515_ref, cnrs515_ref, marker='o', color="blue",
                                    markersize=8, markerfacecolor="None", linestyle="--")
                ctp515_visible_ref = mycbct_ref.ctp515.rois_visible
            else:
                ctp515_visible_ref = np.nan
                cnrs515_ref = [np.nan]*len(mycbct.ctp515.rois.values())
            ax515_contrast.margins(0.05)
            ax515_contrast.grid(True)
            ax515_contrast.set_xlabel('ROI size (mm)')
            ax515_contrast.set_ylabel("Contrast * Diameter")
            ax515_cnr.margins(0.05)
            ax515_cnr.grid(True)
            ax515_cnr.set_xlabel('ROI size (mm)')
            ax515_cnr.set_ylabel("CNR * Diameter")
    
            script_515_contrast = mpld3.fig_to_html(fig_515_contrast, d3_url=D3_URL, mpld3_url=MPLD3_URL)
    
            ctp515_passed = mycbct.ctp515.overall_passed
            #ctp515_passed = None
            ctp515_visible = mycbct.ctp515.rois_visible
        else:
            show_ctp515 = False
            script_515_contrast = None
            script_515 = None
            ctp515_visible_ref = np.nan
            ctp515_passed = None
            ctp515_visible = np.nan
            cnrs515_ref = None
            cnrs515 = None
            cnrs_names = None
    
        general_functions.delete_files_in_subfolders([folder_path]) # Delete temporary images

        variables = {
                    "script_ctp528": script_ctp528,
                    "script_ctp528mtf": script_ctp528mtf,
                    "mtf30_ref": round(mtf30_ref, 2),
                    "mtf30": round(mtf30, 2),
                    "mtf50_ref": round(mtf50_ref, 2),
                    "mtf50": round(mtf50, 2),
                    "mtf80_ref": round(mtf80_ref, 2),
                    "mtf80": round(mtf80, 2),
                    "mtf_passing": mtf_passing,
                    "script_404": script_404,
                    "script_404_HU": script_404_HU,
                    "HU_values_ref": HU_values_ref,
                    "HU_std_ref": HU_std_ref,
                    "HU_values": HU_values,
                    "HU_std": HU_std,
                    "HU_nominal": HU_nominal,
                    "HU_names": HU_names,
                    "HU_diff_ref": HU_diff_ref,
                    "HU_diff": HU_diff,
                    "passed_HU": passed_HU,
                    "passed_thickness": passed_thickness,
                    "passed_geometry": passed_geometry,
                    "passed_lcv": passed_lcv,
                    "passed_404": passed_404,
                    "lcv_ref": lcv_ref,
                    "lcv": round(lcv, 2),
                    "slice_thickness": slice_thickness,
                    "slice_thickness_ref": slice_thickness_ref,
                    "dicom_slice_thickness": dicom_slice_thickness,
                    "dicom_slice_thickness_ref": dicom_slice_thickness_ref,
                    "lines_ref": lines_ref,
                    "lines": lines,
                    "lines_avg": lines_avg,
                    "lines_avg_ref": lines_avg_ref,
                    "phantom_roll": phantom_roll,
                    "phantom_roll_ref": phantom_roll_ref,
                    "origin_slice_ref": origin_slice_ref,
                    "origin_slice": origin_slice,
                    "ctp528_slice": ctp528_slice,
                    "ctp486_slice": ctp486_slice,
                    "ctp515_slice": ctp515_slice,
                    "ctp528_slice_ref": ctp528_slice_ref,
                    "ctp486_slice_ref": ctp486_slice_ref,
                    "ctp515_slice_ref": ctp515_slice_ref,
                    "phantom_center_ref": phantom_center_ref,
                    "phantom_center": phantom_center,
                    "mm_per_pixel": mm_per_pixel,
                    "mm_per_pixel_ref": mm_per_pixel_ref,
                    "cnrs404_ref" : cnrs404_ref,
                    "cnrs404": cnrs404,
                    "script_486": script_486,
                    "script_486_profile": script_486_profile,
                    "hvalues_ref": hvalues_ref,
                    "hvalues": hvalues,
                    "passed_uniformity": passed_uniformity,
                    "passed_uniformity_index": passed_uniformity_index,
                    "uidx": uidx,
                    "uidx_ref": uidx_ref,
                    "script_515": script_515,
                    "script_515_contrast": script_515_contrast,
                    "show_ctp515": show_ctp515,
                    "ctp515_passed": ctp515_passed,
                    "ctp515_visible": ctp515_visible,
                    "ctp515_visible_ref": ctp515_visible_ref,
                    "cnrs515_ref": cnrs515_ref,
                    "cnrs515": cnrs515,
                    "cnrs_names": cnrs_names,
                    "save_results": save_results,
                    "acquisition_datetime": acquisition_datetime,
                    "pdf_report_enable": pdf_report_enable,
                    "plweb_folder": PLWEB_FOLDER
                    }

        # Generate pylinac report:
        if pdf_report_enable == "True":
            pdf_file = tempfile.NamedTemporaryFile(delete=False, prefix="Catphan", suffix=".pdf", dir=config.PDF_REPORT_FOLDER)
            mycbct.publish_pdf(pdf_file)
            variables["pdf_report_filename"] = os.path.basename(pdf_file.name)
    except Exception as e:
        general_functions.delete_files_in_subfolders([folder_path]) # Delete temporary images
        return template("error_template", {"error_message": "Cannot analyze image. "+str(e),
                                           "plweb_folder": PLWEB_FOLDER})
    else:
        return template("catphan_results", variables)

