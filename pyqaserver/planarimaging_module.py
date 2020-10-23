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

from pylinac.core.roi import bbox_center

parent_module = sys.modules['.'.join(__name__.split('.')[:-1]) or '__main__']
if __name__ == '__main__' or parent_module.__name__ == '__main__':
    #sys.path.append(os.path.abspath(os.path.realpath("python_packages")))
    import config
    from python_packages.bottlepy.bottle import Bottle, request, TEMPLATE_PATH, template, response, redirect
    import general_functions
    import RestToolbox_modified as RestToolbox
    from python_packages import mpld3
    # Slightly modified version:
    from python_packages.pylinac.planar_imaging232 import LeedsTOR as LeedsTOR
    from python_packages.pylinac.planar_imaging232 import StandardImagingQC3 as StandardImagingQC3
    from python_packages.pylinac.planar_imaging232 import LasVegas as LasVegas
    from python_packages.pylinac.planar_imaging232 import DoselabMC2MV as DoselabMC2MV
    from python_packages.pylinac.planar_imaging232 import DoselabMC2kV as DoselabMC2kV
else:
    from . import config
    from .python_packages.bottlepy.bottle import Bottle, request, TEMPLATE_PATH, template, response, redirect
    from . import general_functions
    from . import RestToolbox_modified as RestToolbox
    from .python_packages import mpld3
    # Slightly modified version:
    from .python_packages.pylinac.planar_imaging232 import LeedsTOR as LeedsTOR
    from .python_packages.pylinac.planar_imaging232 import StandardImagingQC3 as StandardImagingQC3
    from .python_packages.pylinac.planar_imaging232 import LasVegas as LasVegas
    from .python_packages.pylinac.planar_imaging232 import DoselabMC2MV as DoselabMC2MV
    from .python_packages.pylinac.planar_imaging232 import DoselabMC2kV as DoselabMC2kV

CUR_DIR = os.path.realpath(os.path.dirname(__file__))

# Path to Bottle templates
TEMPLATE_PATH.insert(0, os.path.join(CUR_DIR, 'views'))

# Url to mpld3 library
D3_URL = config.D3_URL
MPLD3_URL = config.MPLD3_URL

# Working directory
PLWEB_FOLDER = config.PLWEB_FOLDER

PI = np.pi

# Here starts the bottle server
plimg_app = Bottle()

@plimg_app.route(PLWEB_FOLDER + '/planar_imaging', method="POST")
def planar_imaging_start():

    colormaps = ["gray", "Greys", "brg", "prism"]
    displayname = request.forms.hidden_displayname
    username = request.get_cookie("account", secret=config.SECRET_KEY)
    if not username:
        redirect(PLWEB_FOLDER + "/login")
    try:
        variables = general_functions.Read_from_dcm_database()
    except ConnectionError:
        return template("error_template", {"error_message": "Orthanc is "
                                           "refusing connection.",
                                           "plweb_folder": PLWEB_FOLDER})
    variables["displayname"] = displayname
    response.set_cookie("account", username, secret=config.SECRET_KEY, samesite="lax")
    variables["colormaps"] = colormaps
    
    # Get list of machines/beams/phantoms from the database
    machines_and_beams = {}
    for k in config.PLANARIMAGING_PHANTOMS:
        machines_and_beams[k] = general_functions.get_machines_and_energies(general_functions.get_treatmentunits_planarimaging(k))

    variables["machines_beams_phantoms"] = machines_and_beams
    return template("planar_imaging", variables)


def planar_imaging_helperf_catch_error(args):
    try:
        return planar_imaging_helperf(args)
    except Exception as e:
        return template("error_template", {"error_message": str(e),
                                           "plweb_folder": PLWEB_FOLDER})


def planar_imaging_helperf(args):
    # This function is used in order to prevent memory problems
    clip_box = args["clip_box"]
    phantom = args["phantom"]
    machine = args["machine"]
    beam = args["beam"]
    leedsrot1 = args["leedsrot1"]
    leedsrot2 = args["leedsrot2"]
    inv = args["inv"]
    bbox = args["bbox"]
    w1 = args["w1"]
    use_reference = args["use_reference"]
    colormap = args["colormap"]
    displayname = args["displayname"]
    acquisition_datetime = args["acquisition_datetime"]
    general_functions.set_configuration(args["config"])  # Transfer to this process
    
    # Collect data for "save results"
    tolerances = general_functions.get_tolerance_user_machine_planarimaging(machine, beam, phantom)  # If user_machne has specific tolerance
    if not tolerances:
        lowtresh, hightresh, generate_pdf = 0.05, 0.1, "True"
    else:
        lowtresh, hightresh, generate_pdf = tolerances

    lowtresh = float(lowtresh)
    hightresh = float(hightresh)

    # Set colormap
    cmap = matplotlib.cm.get_cmap(colormap)
    try:
        temp_folder1, file_path1 = RestToolbox.GetSingleDcm(config.ORTHANC_URL, w1)
    except:
        return template("error_template", {"error_message": "Cannot read image.",
                                           "plweb_folder": PLWEB_FOLDER})

    ref_path1 = general_functions.get_referenceimagepath_planarimaging(machine, beam, phantom)

    if ref_path1 is not None:
        ref_path1 = os.path.join(config.WORKING_DIRECTORY, config.REFERENCE_IMAGES_FOLDER, ref_path1[0])
        if os.path.exists(ref_path1):
            ref1_exists = True
        else:
            ref1_exists = False
    else:
        ref1_exists = False

    if not use_reference:
        ref1_exists = False

    # First analyze first image
    try:
        if phantom=="QC3":
            pi1 = StandardImagingQC3(file_path1)
        elif phantom=="LeedsTOR":
            pi1 = LeedsTOR(file_path1)
        elif phantom=="Las Vegas":
            pi1 = LasVegas(file_path1)
        elif phantom=="DoselabMC2MV":
            pi1 = DoselabMC2MV(file_path1)
        else:
            pi1 = DoselabMC2kV(file_path1)
        
        if clip_box != 0:
            try:
                #pi1.image.check_inversion_by_histogram()
                general_functions.clip_around_image(pi1.image, clip_box)
            except Exception as e:
                return template("error_template", {"error_message": "Unable to apply clipbox. "+str(e), "plweb_folder": PLWEB_FOLDER})
        pi1.analyze(low_contrast_threshold=lowtresh, high_contrast_threshold=hightresh, invert=inv, angle_override=None if leedsrot2==0 else leedsrot2)
    except Exception as e:
         return template("error_template", {"error_message": "Cannot analyze image 1. " + str(e),
                                           "plweb_folder": PLWEB_FOLDER})

    # Analyze reference images if they exists

    if ref1_exists:
        try:
            if phantom == "QC3":
                ref1 = StandardImagingQC3(ref_path1)
            elif phantom == "LeedsTOR":
                ref1 = LeedsTOR(ref_path1)
            elif phantom == "Las Vegas":
                ref1 = LasVegas(ref_path1)
            elif phantom == "DoselabMC2MV":
                ref1 = DoselabMC2MV(ref_path1)
            else:
                ref1 = DoselabMC2kV(ref_path1)
            
            if clip_box != 0:
                try:
                    #ref1.image.check_inversion_by_histogram()
                    general_functions.clip_around_image(ref1.image, clip_box)
                except Exception as e:
                    return template("error_template", {"error_message": "Unable to apply clipbox. "+str(e), "plweb_folder": PLWEB_FOLDER})
            ref1.analyze(low_contrast_threshold=lowtresh, high_contrast_threshold=hightresh, invert=inv, angle_override=None if leedsrot1==0 else leedsrot1)
        except:
             return template("error_template", {"error_message": "Cannot analyze reference image."\
                                                " Check that the image in the database is valid.",
                                               "plweb_folder": PLWEB_FOLDER})
                 
    save_results = {
                    "machine": machine,
                    "beam": beam,
                    "phantom": phantom,
                    "displayname": displayname
                    }

    fig = Figure(figsize=(10.5, 5), tight_layout={"w_pad":0,  "pad": 1.5})
    ax_ref = fig.add_subplot(1,2,1)
    ax_pi = fig.add_subplot(1,2,2)

    # Plot reference image and regions
    if phantom=="QC3":
        low_contrast_rois_pi1 = pi1.low_contrast_rois[1:]  # Exclude first point which is background
    else:
        low_contrast_rois_pi1 = pi1.low_contrast_rois
    
    if ref1_exists:
        if phantom=="QC3":
            low_contrast_rois_ref1 = ref1.low_contrast_rois[1:] # Exclude first point which is background
        else:
            low_contrast_rois_ref1 = ref1.low_contrast_rois
    
    if ref1_exists:
        ax_ref.imshow(ref1.image.array, cmap=cmap, interpolation="none", aspect="equal", origin='upper')
        ax_ref.set_title(phantom+' Reference Image')
        ax_ref.axis('off')
        # plot the background ROIS 
        for roi in ref1.low_contrast_background_rois:
            roi.plot2axes(ax_ref, edgecolor='yellow')
            ax_ref.text(roi.center.x, roi.center.y ,"B", horizontalalignment='center', verticalalignment='center')
        # low contrast ROIs
        for ind, roi in enumerate(low_contrast_rois_ref1):
            roi.plot2axes(ax_ref, edgecolor=roi.plot_color)
            ax_ref.text(roi.center.x, roi.center.y, str(ind), horizontalalignment='center', verticalalignment='center')
        # plot the high-contrast ROIs
        if phantom != "Las Vegas":
            mtf_temp_ref = list(ref1.mtf.norm_mtfs.values())
            for ind, roi in enumerate(ref1.high_contrast_rois):
                color = 'b' if mtf_temp_ref[ind] > ref1._high_contrast_threshold else 'r'
                roi.plot2axes(ax_ref, edgecolor=color)
                ax_ref.text(roi.center.x, roi.center.y ,str(ind), horizontalalignment='center', verticalalignment='center')
    else:
       ax_ref.text(0.5, 0.5 ,"Reference image not available", horizontalalignment='center', verticalalignment='center')
       
    # Plot current image and regions
    ax_pi.imshow(pi1.image.array, cmap=cmap, interpolation="none", aspect="equal", origin='upper')
    ax_pi.axis('off')
    ax_pi.set_title(phantom+' Current Image')
    # plot the background ROIS 
    for roi in pi1.low_contrast_background_rois:
            roi.plot2axes(ax_pi, edgecolor='yellow')
            ax_pi.text(roi.center.x, roi.center.y ,"B", horizontalalignment='center', verticalalignment='center')
    # low contrast ROIs
    for ind, roi in enumerate(low_contrast_rois_pi1):
        roi.plot2axes(ax_pi, edgecolor=roi.plot_color)
        ax_pi.text(roi.center.x, roi.center.y ,str(ind), horizontalalignment='center', verticalalignment='center')
    # plot the high-contrast ROIs
    if phantom != "Las Vegas":
        mtf_temp_pi = list(pi1.mtf.norm_mtfs.values())
        for ind, roi in enumerate(pi1.high_contrast_rois):
            color = 'b' if mtf_temp_pi[ind] > pi1._high_contrast_threshold else 'r'
            roi.plot2axes(ax_pi, edgecolor=color)
            ax_pi.text(roi.center.x, roi.center.y ,str(ind), horizontalalignment='center', verticalalignment='center')

    # Zoom on phantom if requested:
    if bbox:
        if phantom=="QC3" or phantom=="DoselabMC2MV" or phantom=="DoselabMC2kV":
            pad = 15  # Additional space between cyan bbox and plot
            if ref1_exists:
                bounding_box_ref = ref1.phantom_ski_region.bbox
                bbox_center_ref = ref1.phantom_center
    
                if abs(bounding_box_ref[1] - bounding_box_ref[3]) >= abs(bounding_box_ref[2] - bounding_box_ref[0]):
                    dist = abs(bounding_box_ref[1] - bounding_box_ref[3])/2
                    ax_ref.set_ylim(bbox_center_ref.y + dist + pad, bbox_center_ref.y - dist - pad)
                    ax_ref.set_xlim(bbox_center_ref.x - dist - pad, bbox_center_ref.x + dist + pad)
                else:
                    dist = abs(bounding_box_ref[2] - bounding_box_ref[0])/2
                    ax_ref.set_ylim(bbox_center_ref.y + dist + pad, bbox_center_ref.y - dist - pad)
                    ax_ref.set_xlim(bbox_center_ref.x - dist - pad, bbox_center_ref.x + dist + pad)
    
                ax_ref.plot([bounding_box_ref[1], bounding_box_ref[1], bounding_box_ref[3], bounding_box_ref[3], bounding_box_ref[1]],
                            [bounding_box_ref[2], bounding_box_ref[0], bounding_box_ref[0], bounding_box_ref[2], bounding_box_ref[2]], c="cyan")
                ax_ref.autoscale(False)
    
            bounding_box_pi = pi1.phantom_ski_region.bbox
            bbox_center_pi = pi1.phantom_center
            if abs(bounding_box_pi[1] - bounding_box_pi[3]) >= abs(bounding_box_pi[2] - bounding_box_pi[0]):
                dist = abs(bounding_box_pi[1] - bounding_box_pi[3])/2
                ax_pi.set_ylim(bbox_center_pi.y + dist + pad, bbox_center_pi.y - dist - pad)
                ax_pi.set_xlim(bbox_center_pi.x - dist - pad, bbox_center_pi.x + dist + pad)
            else:
                dist = abs(bounding_box_pi[2] - bounding_box_pi[0])/2
                ax_pi.set_ylim(bbox_center_pi.y + dist + pad, bbox_center_pi.y - dist - pad)
                ax_pi.set_xlim(bbox_center_pi.x - dist - pad, bbox_center_pi.x + dist + pad)
    
            ax_pi.plot([bounding_box_pi[1], bounding_box_pi[1], bounding_box_pi[3], bounding_box_pi[3], bounding_box_pi[1]],
                        [bounding_box_pi[2], bounding_box_pi[0], bounding_box_pi[0], bounding_box_pi[2], bounding_box_pi[2]], c="cyan")
            ax_pi.autoscale(False)
        
        elif phantom=="Las Vegas":  # For some reason phantom_ski_regio has an underscore
            pad = 15  # Additional space between cyan bbox and plot
            if ref1_exists:
                bounding_box_ref = ref1._phantom_ski_region.bbox
                bbox_center_ref = ref1.phantom_center
    
                if abs(bounding_box_ref[1] - bounding_box_ref[3]) >= abs(bounding_box_ref[2] - bounding_box_ref[0]):
                    dist = abs(bounding_box_ref[1] - bounding_box_ref[3])/2
                    ax_ref.set_ylim(bbox_center_ref.y + dist + pad, bbox_center_ref.y - dist - pad)
                    ax_ref.set_xlim(bbox_center_ref.x - dist - pad, bbox_center_ref.x + dist + pad)
                else:
                    dist = abs(bounding_box_ref[2] - bounding_box_ref[0])/2
                    ax_ref.set_ylim(bbox_center_ref.y + dist + pad, bbox_center_ref.y - dist - pad)
                    ax_ref.set_xlim(bbox_center_ref.x - dist - pad, bbox_center_ref.x + dist + pad)
    
                ax_ref.plot([bounding_box_ref[1], bounding_box_ref[1], bounding_box_ref[3], bounding_box_ref[3], bounding_box_ref[1]],
                            [bounding_box_ref[2], bounding_box_ref[0], bounding_box_ref[0], bounding_box_ref[2], bounding_box_ref[2]], c="cyan")
                ax_ref.autoscale(False)
    
            bounding_box_pi = pi1._phantom_ski_region.bbox
            bbox_center_pi = pi1.phantom_center
            if abs(bounding_box_pi[1] - bounding_box_pi[3]) >= abs(bounding_box_pi[2] - bounding_box_pi[0]):
                dist = abs(bounding_box_pi[1] - bounding_box_pi[3])/2
                ax_pi.set_ylim(bbox_center_pi.y + dist + pad, bbox_center_pi.y - dist - pad)
                ax_pi.set_xlim(bbox_center_pi.x - dist - pad, bbox_center_pi.x + dist + pad)
            else:
                dist = abs(bounding_box_pi[2] - bounding_box_pi[0])/2
                ax_pi.set_ylim(bbox_center_pi.y + dist + pad, bbox_center_pi.y - dist - pad)
                ax_pi.set_xlim(bbox_center_pi.x - dist - pad, bbox_center_pi.x + dist + pad)
    
            ax_pi.plot([bounding_box_pi[1], bounding_box_pi[1], bounding_box_pi[3], bounding_box_pi[3], bounding_box_pi[1]],
                        [bounding_box_pi[2], bounding_box_pi[0], bounding_box_pi[0], bounding_box_pi[2], bounding_box_pi[2]], c="cyan")
            ax_pi.autoscale(False)
        
        
        elif phantom=="LeedsTOR":
            pad = 15  # Additional space between cyan bbox and plot
            if ref1_exists:
                big_circle_idx = np.argsort([ref1._regions[roi].major_axis_length for roi in ref1._blobs])[-1]
                circle_roi = ref1._regions[ref1._blobs[big_circle_idx]]
                bounding_box_ref = circle_roi.bbox
                bbox_center_ref = bbox_center(circle_roi)
                max_xy = max([abs(bounding_box_ref[1]-bounding_box_ref[3])/2, abs(bounding_box_ref[0]-bounding_box_ref[2])/2])
                ax_ref.set_ylim(bbox_center_ref.y + max_xy + pad, bbox_center_ref.y - max_xy - pad)
                ax_ref.set_xlim(bbox_center_ref.x - max_xy - pad, bbox_center_ref.x + max_xy + pad)
                ax_ref.plot([bounding_box_ref[1], bounding_box_ref[1], bounding_box_ref[3], bounding_box_ref[3], bounding_box_ref[1]],
                            [bounding_box_ref[2], bounding_box_ref[0], bounding_box_ref[0], bounding_box_ref[2], bounding_box_ref[2]], c="cyan")
                ax_ref.autoscale(False)

            big_circle_idx = np.argsort([pi1._regions[roi].major_axis_length for roi in pi1._blobs])[-1]
            circle_roi = pi1._regions[pi1._blobs[big_circle_idx]]
            bounding_box_pi = circle_roi.bbox
            bbox_center_pi = bbox_center(circle_roi)

            max_xy = max([abs(bounding_box_pi[1]-bounding_box_pi[3])/2, abs(bounding_box_pi[0]-bounding_box_pi[2])/2])

            ax_pi.set_ylim(bbox_center_pi.y + max_xy + pad, bbox_center_pi.y - max_xy - pad)
            ax_pi.set_xlim(bbox_center_pi.x - max_xy - pad, bbox_center_pi.x + max_xy + pad)
            ax_pi.plot([bounding_box_pi[1], bounding_box_pi[1], bounding_box_pi[3], bounding_box_pi[3], bounding_box_pi[1]],
                        [bounding_box_pi[2], bounding_box_pi[0], bounding_box_pi[0], bounding_box_pi[2], bounding_box_pi[2]], c="cyan")
            ax_pi.autoscale(False)
        
    # Add phantom outline:
    outline_obj_pi1, settings_pi1 = pi1._create_phantom_outline_object()
    outline_obj_pi1.plot2axes(ax_pi, edgecolor='g', **settings_pi1)
    if ref1_exists:
        outline_obj_ref1, settings_ref1 = ref1._create_phantom_outline_object()
        outline_obj_ref1.plot2axes(ax_ref, edgecolor='g', **settings_ref1)
    
    # Plot low frequency contrast, CNR and rMTF
    fig2 = Figure(figsize=(10.5, 10), tight_layout={"w_pad":1})
    ax_lfc = fig2.add_subplot(2,2,1)
    ax_lfcnr = fig2.add_subplot(2,2,2)
    ax_rmtf = fig2.add_subplot(2,2,3)
    
    # lfc
    ax_lfc.plot([abs(roi.contrast) for roi in low_contrast_rois_pi1], marker='o', markersize=8, color='r')
    if ref1_exists:
        ax_lfc.plot([abs(roi.contrast) for roi in low_contrast_rois_ref1], marker='o', color='r', markersize=8,
                     markerfacecolor="None", linestyle="--")
    ax_lfc.plot([], [], color='r', linestyle="--", label='Reference')
    ax_lfc.plot([], [], color='r', label='Current')
    ax_lfc.plot([0, len(low_contrast_rois_pi1)-1], [lowtresh, lowtresh], "-g")
    ax_lfc.grid(True)
    ax_lfc.set_title('Low-frequency Contrast')
    ax_lfc.set_xlabel('ROI #')
    ax_lfc.set_ylabel('Contrast')
    ax_lfc.set_xticks(np.arange(0, len(low_contrast_rois_pi1), 1))
    ax_lfc.legend(loc='upper right', ncol=2, columnspacing=0, fontsize=12, handletextpad=0)
    ax_lfc.margins(0.05)

    # CNR
    ax_lfcnr.plot([abs(roi.contrast_to_noise) for roi in low_contrast_rois_pi1], marker='^', markersize=8, color='r')
    if ref1_exists:
        ax_lfcnr.plot([abs(roi.contrast_to_noise) for roi in low_contrast_rois_ref1], marker='^', color='r', markersize=8, markerfacecolor="None", linestyle="--")
    ax_lfcnr.plot([], [], color='r', linestyle="--", label='Reference')
    ax_lfcnr.plot([], [], color='r', label='Current')
    ax_lfcnr.grid(True)
    ax_lfcnr.set_title('Contrast-Noise Ratio')
    ax_lfcnr.set_xlabel('ROI #')
    ax_lfcnr.set_ylabel('CNR')
    ax_lfcnr.set_xticks(np.arange(0, len(low_contrast_rois_pi1), 1))
    ax_lfcnr.legend(loc='upper right', ncol=2, columnspacing=0, fontsize=12, handletextpad=0)
    ax_lfcnr.margins(0.05)

    # rMTF
    if phantom != "Las Vegas":
        mtfs_pi1 = list(pi1.mtf.norm_mtfs.values())
        if ref1_exists:
            mtfs_ref1 = list(ref1.mtf.norm_mtfs.values())
        else:
            mtfs_ref1 = [np.nan]*len(mtfs_pi1)
    
        lppmm = pi1.mtf.spacings
    
        ax_rmtf.plot(lppmm, mtfs_pi1, marker='D', markersize=8, color='b')
        ax_rmtf.plot([min(lppmm), max(lppmm)], [hightresh, hightresh], "-g")
        
        if ref1_exists:
            ax_rmtf.plot(lppmm, mtfs_ref1, marker='D', color='b', markersize=8, markerfacecolor="None", linestyle="--")
    
        ax_rmtf.plot([], [], color='b', linestyle="--", label='Reference')
        ax_rmtf.plot([], [], color='b', label='Current')
        ax_rmtf.grid(True)
        ax_rmtf.set_title('High-frequency rMTF')
        ax_rmtf.set_xlabel('Line pairs / mm')
        ax_rmtf.set_ylabel('relative MTF')
        ax_rmtf.legend(loc='upper right', ncol=2, columnspacing=0, fontsize=12, handletextpad=0)
        ax_rmtf.margins(0.05)
    
        f30 = [ref1.mtf.relative_resolution(30) if ref1_exists else np.nan, pi1.mtf.relative_resolution(30)]
        f40 = [ref1.mtf.relative_resolution(40) if ref1_exists else np.nan, pi1.mtf.relative_resolution(40)]
        f50 = [ref1.mtf.relative_resolution(50) if ref1_exists else np.nan, pi1.mtf.relative_resolution(50)]
        f80 = [ref1.mtf.relative_resolution(80) if ref1_exists else np.nan, pi1.mtf.relative_resolution(80)]
    else:
        ax_rmtf.text(0.5, 0.5 ,"MTF not available", horizontalalignment='center', verticalalignment='center')
        f30 = [np.nan, np.nan]
        f40 = [np.nan, np.nan]
        f50 = [np.nan, np.nan]
        f80 = [np.nan, np.nan]
       
    if ref1_exists:
        median_contrast = [np.median([roi.contrast for roi in low_contrast_rois_ref1]), np.median([roi.contrast for roi in low_contrast_rois_pi1])]
        median_CNR = [np.median([roi.contrast_to_noise for roi in low_contrast_rois_ref1]), np.median([roi.contrast_to_noise for roi in low_contrast_rois_pi1])]
        phantom_angle = [ref1.phantom_angle, pi1.phantom_angle]
    else:
        median_contrast = [np.nan, np.median([roi.contrast for roi in low_contrast_rois_pi1])]
        median_CNR = [np.nan, np.median([roi.contrast_to_noise for roi in low_contrast_rois_pi1])]
        phantom_angle = [np.nan, pi1.phantom_angle]

    script = mpld3.fig_to_html(fig, d3_url=D3_URL, mpld3_url=MPLD3_URL)
    script2 = mpld3.fig_to_html(fig2, d3_url=D3_URL, mpld3_url=MPLD3_URL)

    variables = {"script": script,
         "script2": script2,
         "plweb_folder": PLWEB_FOLDER,
         "f30": f30,
         "f40": f40,
         "f50": f50,
         "f80": f80,
         "median_contrast": median_contrast,
         "median_CNR": median_CNR,
         "pdf_report_enable": generate_pdf,
         "save_results": save_results,
         "acquisition_datetime": acquisition_datetime,
         "phantom_angle": phantom_angle
         }

    if generate_pdf == "True":
        pdf_file = tempfile.NamedTemporaryFile(delete=False, prefix="PlanarImaging_", suffix=".pdf", dir=config.PDF_REPORT_FOLDER)
        metadata = RestToolbox.GetInstances(config.ORTHANC_URL, [w1])
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
        pi1.publish_pdf(pdf_file, notes=["Date = "+date_var, "Patient = "+patient, "Station = "+stationname])

        variables["pdf_report_filename"] = os.path.basename(pdf_file.name)
    
    general_functions.delete_figure([fig, fig2])
    general_functions.delete_files_in_subfolders([temp_folder1]) # Delete image

    #gc.collect()
    return template("planar_imaging_results", variables)


@plimg_app.route(PLWEB_FOLDER + '/planar_imaging_calculate/<w1>', method="POST")
def planar_imaging_calculate(w1):
    # This function gets data from website and starts the calculation

    clip_box = float(request.forms.hidden_clipbox)*10.0
    phantom = request.forms.hidden_phantom
    machine = request.forms.hidden_machine
    beam = request.forms.hidden_beam
    leedsrot1 = float(request.forms.hidden_leedsrot1)
    leedsrot2 = float(request.forms.hidden_leedsrot2)
    inv = request.forms.hidden_inv
    bbox = request.forms.hidden_bbox
    use_reference = request.forms.hidden_ref
    use_reference = True if use_reference == "true" else False
    colormap = request.forms.hidden_colormap
    displayname = request.forms.hidden_displayname
    acquisition_datetime = request.forms.hidden_datetime

    inv = True if inv == "true" else False
    # To show the phantom region and zoom in
    bbox = True if bbox == "true" else False

    args = {"clip_box": clip_box, "phantom": phantom, "machine": machine,
            "beam":beam, "leedsrot1": leedsrot1, "leedsrot2": leedsrot2, "inv": inv,
            "bbox": bbox, "use_reference": use_reference, "w1": w1, "colormap": colormap,
            "config": general_functions.get_configuration(),
            "displayname": displayname, "acquisition_datetime": acquisition_datetime}
    p = Pool(1)
    data = p.map(planar_imaging_helperf_catch_error, [args])
    p.close()
    p.join()
    return data
