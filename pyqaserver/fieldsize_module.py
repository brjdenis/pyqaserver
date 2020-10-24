import sys
import os
import copy
from multiprocessing import Pool
import numpy as np
import matplotlib.style
import matplotlib
matplotlib.use('Agg')
from matplotlib.figure import Figure

# To revert back to matplotlib 1.0 style
matplotlib.style.use('classic')

from pylinac.core import image as pylinac_image

parent_module = sys.modules['.'.join(__name__.split('.')[:-1]) or '__main__']
if __name__ == '__main__' or parent_module.__name__ == '__main__':
    #sys.path.append(os.path.abspath(os.path.realpath("python_packages")))
    import config
    from python_packages.bottlepy.bottle import Bottle, request, TEMPLATE_PATH, template, redirect, response
    import general_functions
    import MLC_fieldsize as MLC_fieldsize
    import RestToolbox_modified as RestToolbox
    from python_packages import mpld3
else:
    from . import config
    from .python_packages.bottlepy.bottle import Bottle, request, TEMPLATE_PATH, template, redirect, response
    from . import general_functions
    from . import MLC_fieldsize as MLC_fieldsize
    from . import RestToolbox_modified as RestToolbox
    from .python_packages import mpld3

CUR_DIR = os.path.realpath(os.path.dirname(__file__))

# Path to Bottle templates
TEMPLATE_PATH.insert(0, os.path.join(CUR_DIR, 'views'))

# Url to some mpld3 library
D3_URL = config.D3_URL
MPLD3_URL = config.MPLD3_URL

PI = np.pi

# MLC type
LEAF_TYPE = ["Varian_120", "Varian_120HD", "Varian_80", "Elekta_80", "Elekta_160"]

# Here starts the bottle server
fieldsize_app = Bottle()

@fieldsize_app.route('/fieldsize', method="POST")
def fieldsize():
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
    variables["LEAF_TYPE"] = LEAF_TYPE
    return template("fieldsize", variables)


def fieldsize_helperf_catch_error(args):
    try:
        return fieldsize_helperf(args)
    except Exception as e:
        return template("error_template", {"error_message": str(e)})
    

def fieldsize_helperf(args):
    mlc_type = args["mlc_type"]
    iso_method = args["iso_method"]
    mlc_direction = args["mlc_direction"]
    mlc_points = args["mlc_points"]
    jaw_points = args["jaw_points"]
    mmpd = args["mmpd"]
    cax_x = args["cax_x"]
    cax_y = args["cax_y"]
    clipbox = args["clipbox"]
    invert = args["invert"]
    imgdescription = args["imgdescription"]
    station = args["station"]
    displayname = args["displayname"]
    acquisition_datetime = args["acquisition_datetime"]
    w1 = args["w1"]
    w2 = args["w2"]
    general_functions.set_configuration(args["config"])
    high_contrast = args["high_contrast"]
    filter_size = args["filter_size"]
    
    # Collect data for "save results"
    dicomenergy = general_functions.get_energy_from_imgdescription(imgdescription)
    user_machine, user_energy = general_functions.get_user_machine_and_energy(station, dicomenergy)
    machines_and_energies = general_functions.get_machines_and_energies(general_functions.get_treatmentunits_fieldsize())
    tolerances = general_functions.get_tolerance_user_machine_fieldsize(user_machine)  # If user_machne has specific tolerance
    if not tolerances:
        tt = general_functions.get_settings_fieldsize()
    else:
        tt = tolerances[0]
    (small_nominal, medium_nominal, large_nominal,
     small_exp_mlc, medium_exp_mlc, large_exp_mlc,
     small_exp_jaw, medium_exp_jaw, large_exp_jaw,
     tolerance_small_mlc, tolerance_medium_mlc, tolerance_large_mlc,
     tolerance_small_jaw, tolerance_medium_jaw, tolerance_large_jaw,
     tolerance_iso) = tt

    small_exp_mlc = float(small_exp_mlc)
    medium_exp_mlc = float(medium_exp_mlc)
    large_exp_mlc = float(large_exp_mlc)
    small_exp_jaw = float(small_exp_jaw)
    medium_exp_jaw = float(medium_exp_jaw)
    large_exp_jaw = float(large_exp_jaw)
    tolerance_small_mlc = float(tolerance_small_mlc)
    tolerance_medium_mlc = float(tolerance_medium_mlc)
    tolerance_large_mlc = float(tolerance_large_mlc)
    tolerance_small_jaw = float(tolerance_small_jaw)
    tolerance_medium_jaw = float(tolerance_medium_jaw)
    tolerance_large_jaw = float(tolerance_large_jaw)
    tolerance_iso = float(tolerance_iso)

    save_results = {
                    "user_machine": user_machine,
                    "user_energy": user_energy,
                    "machines_and_energies": machines_and_energies,
                    "displayname": displayname,
                    "testtype": ["MLC and Jaws", "Jaws only", "MLC only"]
                    }
    
    try:
        temp_folder1, file_path1 = RestToolbox.GetSingleDcm(config.ORTHANC_URL, w1)
        temp_folder2, file_path2 = RestToolbox.GetSingleDcm(config.ORTHANC_URL, w2)
    except:
        return template("error_template", {"error_message": "Cannot read images."})
    
    # Load first image
    try:
        img1 = pylinac_image.DicomImage(file_path1)
        # Here we force pixels to background outside of box:
        if clipbox != 0:
            try:
                img1.check_inversion_by_histogram(percentiles=[4, 50, 96]) # Check inversion otherwise this might not work
                general_functions.clip_around_image(img1, clipbox)
            except Exception as e:
                return template("error_template", {"error_message": "Unable to apply clipbox. "+str(e)})
        else:
            img1.remove_edges(pixels=2)
        if invert:
            img1.invert()
        else:
            img1.check_inversion()
        img1.flipud()
        if filter_size != 0:
            img1.filter(filter_size)
            
    except:
        return template("error_template", {"error_message": "Cannot read image."})

    try:
        img2 = pylinac_image.DicomImage(file_path2)
        if clipbox != 0:
            try:
                img2.check_inversion_by_histogram(percentiles=[4, 50, 96]) # Check inversion otherwise this might not work
                general_functions.clip_around_image(img2, clipbox)
            except Exception as e:
                return template("error_template", {"error_message": "Unable to apply clipbox. "+str(e)})
        else:
            img2.remove_edges(pixels=2)
        if invert:
            img2.invert()
        else:
            img2.check_inversion()
        img2.flipud()
        if filter_size != 0:
            img1.filter(filter_size)
    except:
        return template("error_template", {"error_message": "Cannot read image."})

    # FIRST IMAGE (to get isocenter):
    if iso_method == "Manual":
        center = (float(cax_x), float(cax_y))

    elif iso_method == "Plate (Elekta)":
        img1_copy = copy.copy(img1) # Copy because you will need the original later

        reg = MLC_fieldsize._get_canny_regions(img1)
        size = [r.area for r in reg]
        sort = np.argsort(size)[::-1]
        # Get the region with the right area:
        for s in range(0, len(reg), 1):
            if 0.9 < (reg[sort[s]].image.size/(img1.dpmm*img1.dpmm) / 31420) < 1.1:
                break
        max_area_index = sort[s]
        bb_box = reg[max_area_index].bbox  # (min_row, min_col, max_row, max_col)
        margin = 15 # pixels

        img1.array = img1.array[bb_box[0]+margin:bb_box[2]-margin, bb_box[1]+margin:bb_box[3]-margin]
        center = MLC_fieldsize._find_plate_center(img1)  # This is chosen as the mechanical center!!!

        filter_size = 0.05  # Don't go higher!
        sample_length = 15 # mm to both sides from the center!
        sample_box = 5  # Half the number of lines per averaged profile minus one(must be odd number)
        hor_margin = 50
        vrt_margin = 30

        # Vertical profiles (two regions):
        samples_vertical = np.rint(center[0]-sample_length*img1.dpmm + np.arange(1, 2*sample_length*img1.dpmm+1, 2*sample_box+1)).astype(int)
        up_end = np.rint(center[1]-vrt_margin*img1.dpmm).astype(int)
        down_start = np.rint(center[1] + vrt_margin*img1.dpmm).astype(int)
        width_vert_up, fwhm_center_vert_up, width_vert_down, fwhm_center_vert_down = MLC_fieldsize.plate_ud_width(img1, samples_vertical, filter_size, up_end, down_start, sample_box)

        # Horizontal profiles (two regions):
        samples_horizontal = np.rint(center[1]-sample_length*img1.dpmm + np.arange(1, 2*sample_length*img1.dpmm+1, 2*sample_box+1)).astype(int)
        left_end = np.rint(center[0]-hor_margin*img1.dpmm).astype(int)
        right_start = np.rint(center[0] + hor_margin*img1.dpmm).astype(int)
        width_hor_left, fwhm_center_hor_left, width_hor_right, fwhm_center_hor_right = MLC_fieldsize.plate_lr_width(img1, samples_horizontal, filter_size, left_end, right_start, sample_box)
        vrt_px = (np.average(width_vert_up)+np.average(width_vert_down))/2
        hor_px = (np.average(width_hor_left)+np.average(width_hor_right))/2
        center_fwhm_x = (np.average(fwhm_center_hor_left) + right_start + np.average(fwhm_center_hor_right))/2
        center_fwhm_y = (np.average(fwhm_center_vert_up) + down_start + np.average(fwhm_center_vert_down))/2

        # Redefine center to the original image:
        center_plate = [center_fwhm_x, center_fwhm_y]
        center = (bb_box[1]+margin+center_plate[0], bb_box[0]+margin+center_plate[1])

    elif iso_method == "BB":
        center, bb_box = MLC_fieldsize._find_field_centroid(img1)
        if high_contrast:
            bb_coord, bw_bb_im = MLC_fieldsize._find_bb2(img1, bb_box)  # Define as mechanical isocenter
        else:
            bb_coord, bw_bb_im = MLC_fieldsize._find_bb(img1, bb_box)  # Define as mechanical isocenter
        center = (bb_coord[0], bb_coord[1])

    elif iso_method == "CAX":
        center, bb_box = MLC_fieldsize._find_field_centroid(img1)  # Define as mechanical isocenter

    elif iso_method == "Opposing coll angle":
        # Two fields with opposing collimator angles can be used to define the coll axis
        center, bb_box = MLC_fieldsize._find_field_centroid(img1)  # Same as any field but now:
        # Go to line below where center is redefined to account for image 2 CAX.
        
    
    # Now calculate field size from second image
    # Calculate mlc and jaw positions
    # Define pixel size. Use either that from the dcm file or calculate it via Elekta plate:
    if iso_method == "Plate (Elekta)":
        dpmm = (vrt_px/20.0 + hor_px/20.0)/2
    else:
        if mmpd != 0:
            dpmm = 1.0/mmpd
        else:
            dpmm = img2.dpmm

    center_rad, bb_box2 = MLC_fieldsize._find_field_centroid(img2)
    
    # If Opposing coll angle is used for isocenter definition, redefine center:
    if iso_method == "Opposing coll angle":
        center[0], center[1] = (center[0] + center_rad[0])/2.0, (center[1] + center_rad[1])/2.0
    marg_bb = 10  # This additional margin is included in the caluclation of bb_box2. Subtract it when needed!

    nr_leaf_sample_points = int(mlc_points)
    nr_jaw_sample_points = int(jaw_points)
    leaf_scaling = dpmm
    mlc_points = MLC_fieldsize.sample_points_mlc(nr_leaf_sample_points, leaf_type=mlc_type)
    # Sample mlc-s according o mlc_points, sample jaws equidistanly with center at rad center (derived from bb_box2)

    if mlc_direction == "X":
        # MLCS are horizontal
        center_pixel_mlc = center[0]
        center_pixel_jaws = center[1]
        mlc_pixels = MLC_fieldsize.points_to_pixels_mlc(leaf_scaling, mlc_points, bb_box2[0]+marg_bb, bb_box2[1]-marg_bb, center_pixel_jaws)
        jaw_pixels = MLC_fieldsize.sample_pixels_jaws(nr_jaw_sample_points, bb_box2[2]+marg_bb, bb_box2[3]-marg_bb)
    else:
        # MLCs are vertical
        center_pixel_mlc = center[1]
        center_pixel_jaws = center[0]
        mlc_pixels = MLC_fieldsize.points_to_pixels_mlc(leaf_scaling, mlc_points, bb_box2[2]+marg_bb, bb_box2[3]-marg_bb, center_pixel_jaws)
        jaw_pixels = MLC_fieldsize.sample_pixels_jaws(nr_jaw_sample_points, bb_box2[0]+marg_bb, bb_box2[1]-marg_bb)

    penL, penR = MLC_fieldsize.calculate_penumbra_pixels_mlc(img2, mlc_pixels, mlc_direction)
    penL_abs = np.abs(penL-center_pixel_mlc)
    penL_abs_avg = np.average(penL_abs, axis=1)
    penR_abs = np.abs(penR-center_pixel_mlc)
    penR_abs_avg = np.average(penR_abs, axis=1)
    widths_mlc = np.abs(penL-penR)
    widths_mlc_avg = np.average(widths_mlc, axis=1)

    penL_jaw, penR_jaw = MLC_fieldsize.calculate_penumbra_pixels_jaws(img2, jaw_pixels, mlc_direction)
    penL_jaw_abs = np.abs(penL_jaw-center_pixel_jaws)
    penR_jaw_abs = np.abs(penR_jaw-center_pixel_jaws)
    widths_jaw = np.abs(penL_jaw-penR_jaw)

    # Skewness of the rectangle (a measure of collimator angle):
    # linear regression of mlc/jaw points (except the first and the last) y=mx+c
    first_leaf = np.rint(np.searchsorted((mlc_pixels-center_pixel_jaws).flatten(), 0)/mlc_pixels.shape[1]).astype(int)
    leaf_numbers = np.hstack((-np.arange(1, first_leaf+1, 1)[::-1], np.arange(1, mlc_pixels.shape[0]-first_leaf+1, 1)))

    temp_mlc = np.vstack([(mlc_pixels[1:-1,:].flatten()-center_pixel_mlc)/dpmm, np.ones(len(mlc_pixels[1:-1,:].flatten()))]).T
    m_mlcL, c_mlcL = np.linalg.lstsq(temp_mlc, penL_abs[1:-1,:].flatten()/dpmm, rcond=None)[0]
    m_mlcR, c_mlcR = np.linalg.lstsq(temp_mlc, penR_abs[1:-1,:].flatten()/dpmm, rcond=None)[0]
    temp_jaws = np.vstack([(jaw_pixels[1:-1]-center_pixel_jaws)/dpmm, np.ones(len(jaw_pixels[1:-1]))]).T
    m_jawL, c_jawL = np.linalg.lstsq(temp_jaws, penL_jaw_abs[1:-1]/dpmm, rcond=None)[0]
    m_jawR, c_jawR = np.linalg.lstsq(temp_jaws, penR_jaw_abs[1:-1]/dpmm, rcond=None)[0]
    
    # Not do some heavy plotting
    size = 7
    fig1 = Figure(figsize=(size, size), tight_layout={"w_pad":1, "pad": 1})
    ax1 = fig1.add_subplot(1,1,1)

    if iso_method == "BB":
        ax1.imshow(img1.array, cmap=matplotlib.cm.Greys, interpolation="none", origin="lower", extent=[0, img1.shape[1], 0, img1.shape[0]])
        ax1.plot(center[0], center[1],  'b+', markersize=24, markeredgewidth=3, zorder=2)
        border = np.average(np.percentile(bw_bb_im, [5, 99.9]))
        ax1.contour(bw_bb_im, levels=[border], colors = ["red"])  # BB
        ax1.set_ylim(0, img1.shape[0])
        ax1.set_xlim(0, img1.shape[1])
        ax1.autoscale(enable=False)

    if iso_method == "Plate (Elekta)":
        ax1.imshow(img1_copy.array, cmap=matplotlib.cm.prism_r, interpolation="none", origin="lower", extent=[0, img1_copy.shape[1], 0, img1_copy.shape[0]])
        ax1.plot(center[0], center[1],  'b+', markersize=24, markeredgewidth=3, zorder=2)
        ax1.plot([left_end+center[0]-center_plate[0]]*len(samples_horizontal), samples_horizontal+center[1]-center_plate[1],'wo', markersize=3, markeredgewidth=0, zorder=2 )
        ax1.plot([right_start+center[0]-center_plate[0]]*len(samples_horizontal), samples_horizontal+center[1]-center_plate[1],'wo', markersize=3, markeredgewidth=0, zorder=2 )
        ax1.plot(samples_vertical+center[0]-center_plate[0], [up_end+center[1]-center_plate[1]]*len(samples_vertical),'wo', markersize=3, markeredgewidth=0, zorder=2 )
        ax1.plot(samples_vertical+center[0]-center_plate[0], [down_start+center[1]-center_plate[1]]*len(samples_vertical), 'wo', markersize=3, markeredgewidth=0, zorder=2 )
        ax1.set_ylim(bb_box[0]+margin, bb_box[2]-margin)
        ax1.set_xlim(bb_box[1]+margin, bb_box[3]-margin)
        ax1.autoscale(enable=False)

    if iso_method == "Manual" or iso_method == "CAX" or iso_method == "Opposing coll angle":
        ax1.imshow(img1.array, cmap=matplotlib.cm.prism_r, interpolation="none", origin="lower", extent=[0, img1.shape[1], 0, img1.shape[0]])
        ax1.plot(center[0], center[1],  'b+', markersize=24, markeredgewidth=3, zorder=2)
        ax1.set_ylim(0, img1.shape[0])
        ax1.set_xlim(0, img1.shape[1])
        ax1.autoscale(enable=False)

    mpld3.plugins.connect(fig1, mpld3.plugins.MousePosition(fontsize=14, fmt=".1f"))
    script1 = mpld3.fig_to_html(fig1, d3_url=D3_URL, mpld3_url=MPLD3_URL)
    
    # Second plot
    fig2 = Figure(figsize=(size, size), tight_layout={"w_pad":1, "pad": 1})

    ax2 = fig2.add_subplot(1,1,1)
    ax2.imshow(img2.array, cmap=matplotlib.cm.Greys, interpolation="none", origin="lower", extent=[0, img2.shape[1], 0, img2.shape[0]])
    ax2.plot(center[0], center[1],  marker='+', color="dodgerblue", markersize=24, markeredgewidth=3)
    level = np.average(np.percentile(img2.array, [5, 99.9]))
    ax2.contour(img2.array, levels=[level], colors = ["magenta"], linewidths=1, alpha=0.7, zorder=1)
    ax2.plot(center_rad[0], center_rad[1],  'm+', markersize=24, markeredgewidth=3, zorder=2)
    ax2.plot([None],[None], marker='+', color="dodgerblue", ms=15, mew=3, label="Mechanical")
    ax2.plot([None],[None], "m+", ms=15, mew=3, label="Radiation")
    ax2.plot([0, img2.shape[1]], [center[1], center[1]], linestyle="--", color="dodgerblue", alpha=0.5)
    ax2.plot([center[0], center[0]], [0, img2.shape[0]], linestyle="--", color="dodgerblue", alpha=0.5)
    ax2.legend(framealpha=0, numpoints=1, ncol=2, loc='lower left', fontsize=8)

    m1s = 5
    ms2 = 6
    if mlc_direction == "X":
        m1 = ax2.plot(penL.flatten(), mlc_pixels.flatten(), 'ro', markersize=m1s, markeredgewidth=0, zorder=2)
        m2 = ax2.plot(penR.flatten(), mlc_pixels.flatten(), 'bo', markersize=m1s, markeredgewidth=0, zorder=2)
        j1 = ax2.plot(jaw_pixels, penL_jaw, 'go', markersize=ms2, markeredgewidth=0, zorder=2)
        j2 = ax2.plot(jaw_pixels, penR_jaw, 'yo', markersize=ms2, markeredgewidth=0, zorder=2)
        #ax2.plot(np.average((penL+penR)/2), np.average((penL_jaw+penR_jaw)/2), 'y+', markersize=24, markeredgewidth=3, zorder=2)
    else:
        m1 = ax2.plot(mlc_pixels.flatten(), penL.flatten(), 'ro', markersize=m1s, markeredgewidth=0, zorder=2)
        m2 = ax2.plot(mlc_pixels.flatten(), penR.flatten(), 'bo', markersize=m1s, markeredgewidth=0, zorder=2)
        j1 = ax2.plot(penL_jaw, jaw_pixels, 'go', markersize=ms2, markeredgewidth=0, zorder=2)
        j2 = ax2.plot(penR_jaw, jaw_pixels, 'yo', markersize=ms2, markeredgewidth=0, zorder=2)
        #ax2.plot(np.average((penL_jaw+penR_jaw)/2), np.average((penL+penR)/2), 'y+', markersize=24, markeredgewidth=3, zorder=2)

    labels_m1 = ["Distance from center = {:04.2f} mm, width = {:04.2f} mm".format(penL_abs.flatten()[k]/dpmm, widths_mlc.flatten()[k]/dpmm) for k in range(0, len(penL_abs.flatten()), 1)]
    labels_m2 = ["Distance from center = {:04.2f} mm, width = {:04.2f} mm".format(penR_abs.flatten()[k]/dpmm, widths_mlc.flatten()[k]/dpmm) for k in range(0, len(penR_abs.flatten()), 1)]
    labels_j1 = ["Distance from center = {:04.2f} mm, width = {:04.2f} mm".format(penL_jaw_abs[k]/dpmm, widths_jaw[k]/dpmm) for k in range(0, len(penL_jaw_abs), 1)]
    labels_j2 = ["Distance from center = {:04.2f} mm, width = {:04.2f} mm".format(penR_jaw_abs[k]/dpmm, widths_jaw[k]/dpmm) for k in range(0, len(penR_jaw_abs), 1)]
    ttip1 = mpld3.plugins.PointLabelTooltip(m1[0], labels_m1, location='top left')
    ttip2 = mpld3.plugins.PointLabelTooltip(m2[0], labels_m2, location='top left')
    ttip3 = mpld3.plugins.PointLabelTooltip(j1[0], labels_j1, location='top left')
    ttip4 = mpld3.plugins.PointLabelTooltip(j2[0], labels_j2, location='top left')

    margin_imshow = 35
    ax2.set_ylim(bb_box2[0]-margin_imshow, bb_box2[1]+margin_imshow)
    ax2.set_xlim(bb_box2[2]-margin_imshow, bb_box2[3]+margin_imshow)
    ax2.autoscale(enable=False)

    mpld3.plugins.connect(fig2, mpld3.plugins.MousePosition(fontsize=14, fmt=".1f"))

    mpld3.plugins.connect(fig2, ttip1)
    mpld3.plugins.connect(fig2, ttip2)
    mpld3.plugins.connect(fig2, ttip3)
    mpld3.plugins.connect(fig2, ttip4)

    script2 = mpld3.fig_to_html(fig2, d3_url=D3_URL, mpld3_url=MPLD3_URL)

    # Third plot
    fig3 = Figure(figsize=(10, 9), tight_layout={"w_pad":2, "pad": 2})
    ax3 = fig3.add_subplot(3,1,1)
    ax4 = fig3.add_subplot(3,1,2)
    ax5 = fig3.add_subplot(3,1,3)

    ax3.plot(np.arange(0, len(leaf_numbers), 1), penR_abs_avg/dpmm, "bo-", linewidth=0.8)
    ax3.set_xticks(np.arange(0, len(leaf_numbers), 1))
    ax3.set_xticklabels([])
    ax3.grid(linestyle='dotted', color="gray")
    ax3.set_title("Right leaf distance from center [mm]")
    ax3.margins(0.05)

    ax4.plot(np.arange(0, len(leaf_numbers), 1),-penL_abs_avg/dpmm, "ro-", linewidth=0.8)
    ax4.set_xticks(np.arange(0, len(leaf_numbers), 1))
    ax4.grid(linestyle='dotted', color="gray")
    ax4.set_xticklabels([])
    ax4.set_title("Left leaf distance from center [mm]")
    ax4.margins(0.05)

    ax5.plot(np.arange(0, len(leaf_numbers), 1),widths_mlc_avg/dpmm, "ko-", linewidth=0.8)
    ax5.set_xticks(np.arange(0, len(leaf_numbers), 1))
    ax5.set_xticklabels(leaf_numbers)
    ax5.grid(linestyle='dotted', color="gray")
    ax5.set_xlabel("Leaf index")
    ax5.set_title("Distance between leaves [mm]")
    ax5.margins(0.05)

    script3 = mpld3.fig_to_html(fig3, d3_url=D3_URL, mpld3_url=MPLD3_URL)

    # Fourth plot
    fig4 = Figure(figsize=(10, 9), tight_layout={"w_pad":2, "pad": 2})
    ax6 = fig4.add_subplot(3,1,1)
    ax7 = fig4.add_subplot(3,1,2)
    ax8 = fig4.add_subplot(3,1,3)

    ax6.plot(np.arange(0, len(penR_jaw_abs), 1), penR_jaw_abs/dpmm, "yo-", linewidth=0.8)
    ax6.set_xticks(np.arange(0, len(penR_jaw_abs), 1))
    ax6.set_xticklabels([])
    ax6.grid(linestyle='dotted', color="gray")
    ax6.set_title("Right jaw distance from center [mm]")
    ax6.margins(0.05)

    ax7.plot(np.arange(0, len(penL_jaw_abs), 1),-penL_jaw_abs/dpmm, "go-", linewidth=0.8)
    ax7.set_xticks(np.arange(0, len(penL_jaw_abs), 1))
    ax7.grid(linestyle='dotted', color="gray")
    ax7.set_xticklabels([])
    ax7.set_title("Left jaw distance from center [mm]")
    ax7.margins(0.05)

    ax8.plot(np.arange(0, len(widths_jaw), 1), widths_jaw/dpmm, "ko-", linewidth=0.8)
    ax8.set_xticks(np.arange(0, len(widths_jaw), 1))
    ax8.set_xticklabels(np.arange(1, len(widths_jaw)+1, 1))
    ax8.grid(linestyle='dotted', color="gray")
    ax8.set_xlabel("Jaw sample point")
    ax8.set_title("Distance between jaws [mm]")
    ax8.margins(0.05)

    script4 = mpld3.fig_to_html(fig4, d3_url=D3_URL, mpld3_url=MPLD3_URL)
    
    # Caclculate stuff for the web interface
    MLC_size_full = np.average(widths_mlc_avg[1:-1]/dpmm)
    jaw_size_full = np.average(widths_jaw[1:-1]/dpmm)
    
    #sizes_nominal = np.array([small_nominal, medium_nominal, large_nominal])
    size_nominal_names = ["Small field", "Medium field", "Large field"]
    sizes_exp_mlc = np.array([small_exp_mlc, medium_exp_mlc, large_exp_mlc])*10.0
    sizes_exp_jaw = np.array([small_exp_jaw, medium_exp_jaw, large_exp_jaw])*10.0
    tolerances_list_mlc = np.array([tolerance_small_mlc, tolerance_medium_mlc, tolerance_large_mlc])*10.0
    tolerances_list_jaw = np.array([tolerance_small_jaw, tolerance_medium_jaw, tolerance_large_jaw])*10.0
    
    # Guess which field was chosen
    guess_ind_mlc = np.argmin(np.abs(sizes_exp_mlc - MLC_size_full))
    guess_ind_jaw = np.argmin(np.abs(sizes_exp_jaw - jaw_size_full))
    guessed_exp_mlc = sizes_exp_mlc[guess_ind_mlc]
    guessed_exp_jaw = sizes_exp_jaw[guess_ind_jaw]
    guessed_nominal_name = size_nominal_names[guess_ind_mlc]
    
    tolerance_final_mlc = tolerances_list_mlc[guess_ind_mlc]
    tolerance_final_jaw = tolerances_list_jaw[guess_ind_jaw]
    tolerance_iso = tolerance_iso*10.0  # Redefine to mm
    
    if abs(guessed_exp_mlc - MLC_size_full) <= tolerance_final_mlc:
        passed_mlc = True
    else:
        passed_mlc = False
    
    if abs(guessed_exp_jaw - jaw_size_full) <= tolerance_final_jaw:
        passed_jaw = True
    else:
        passed_jaw = False
    
    if (center_rad[0]-center[0])**2 + (center_rad[1]-center[1])**2 <= dpmm*dpmm*tolerance_iso**2:
        passed_iso = True
    else:
        passed_iso = False
    
    variables = {
                 "script1": script1,
                 "script2": script2,
                 "script3": script3,
                 "script4": script4,
                 "MLC_position_L": penL_abs_avg/dpmm,
                 "MLC_position_R": penR_abs_avg/dpmm,
                 "MLC_width": widths_mlc_avg/dpmm,
                 "jaw_position_L": penL_jaw_abs/dpmm,
                 "jaw_position_R": penR_jaw_abs/dpmm,
                 "jaw_width": widths_jaw/dpmm,
                 "leaf_numbers": leaf_numbers,
                 "angle_mlc_L": np.arctan(m_mlcL)*180/PI,
                 "angle_mlc_R": -np.arctan(m_mlcR)*180/PI,  # changed sign!
                 "angle_jaw_L": -np.arctan(m_jawL)*180/PI,  # changed sign!
                 "angle_jaw_R": np.arctan(m_jawR)*180/PI,
                 "MLC_size_L": np.average(penL_abs_avg[1:-1]/dpmm),
                 "MLC_size_R": np.average(penR_abs_avg[1:-1]/dpmm),
                 "MLC_size_full": MLC_size_full,
                 "jaw_size_L": np.average(penL_jaw_abs[1:-1]/dpmm),
                 "jaw_size_R": np.average(penR_jaw_abs[1:-1]/dpmm),
                 "jaw_size_full": jaw_size_full,
                 "center_offset_x": (center_rad[0]-center[0])/dpmm,
                 "center_offset_y": (center_rad[1]-center[1])/dpmm,
                 "dpmm": 1/dpmm,
                 "center": center,
                 "mlc_direction": mlc_direction,
                 "center_rad": center_rad,
                 "save_results": save_results,
                 "passed_mlc": passed_mlc,
                 "passed_jaw": passed_jaw,
                 "passed_iso": passed_iso,
                 "tolerance_mlc": tolerance_final_mlc,
                 "tolerance_jaw": tolerance_final_jaw,
                 "tolerance_iso": tolerance_iso,
                 "expected_mlc": guessed_exp_mlc,
                 "expected_jaw": guessed_exp_jaw,
                 "guessed_fieldsize": guessed_nominal_name,
                 "acquisition_datetime": acquisition_datetime,
                 "iso_method": iso_method
                 }
    general_functions.delete_files_in_subfolders([temp_folder1, temp_folder2]) # Delete image
    return template("fieldsize_results", variables)

@fieldsize_app.route('/fieldsize/<w1>/<w2>', method="POST")
def fieldsize_calculate(w1, w2):
    mlc_type = request.forms.hidden_mlctype
    iso_method = request.forms.hidden_setcenter
    mlc_direction = request.forms.hidden_mlcdirection
    mlc_points = request.forms.hidden_mlcpoints
    jaw_points = request.forms.hidden_jawpoints
    mmpd = float(request.forms.hidden_mmpd)
    cax_x = request.forms.hidden_cax_x
    cax_y = request.forms.hidden_cax_y
    clipbox = float(request.forms.hidden_clipbox)*10.0
    invert = True if request.forms.hidden_invert=="true" else False
    filter_size = int(request.forms.hidden_filter_size)
    high_contrast = True if request.forms.hidden_high_contrast=="true" else False
    imgdescription = request.forms.hidden_imgdescription
    station = request.forms.hidden_station
    displayname = request.forms.hidden_displayname
    acquisition_datetime = request.forms.hidden_datetime
    
    args = {"mlc_type": mlc_type, "iso_method": iso_method, "mlc_direction": mlc_direction,
            "mlc_points": mlc_points, "jaw_points": jaw_points, "mmpd": mmpd,
            "cax_x": cax_x, "cax_y": cax_y, "clipbox": clipbox, "invert": invert,
            "displayname": displayname, "acquisition_datetime": acquisition_datetime,
            "imgdescription": imgdescription, "station": station, "w1": w1, "w2": w2,
            "high_contrast": high_contrast, "filter_size": filter_size,
            "config": general_functions.get_configuration()
            }
    p = Pool(1)
    data = p.map(fieldsize_helperf_catch_error, [args])
    p.close()
    p.join()
    return data