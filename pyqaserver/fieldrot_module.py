import sys
import os
from multiprocessing import Pool
import numpy as np
from pylinac.core import image as pylinac_image
import matplotlib.style
import matplotlib
matplotlib.use('Agg')
from matplotlib.figure import Figure

# To revert back to matplotlib 1.0 style
matplotlib.style.use('classic')

parent_module = sys.modules['.'.join(__name__.split('.')[:-1]) or '__main__']
if __name__ == '__main__' or parent_module.__name__ == '__main__':
    #sys.path.append(os.path.abspath(os.path.realpath("python_packages")))
    import config
    from python_packages.bottlepy.bottle import Bottle, request, TEMPLATE_PATH, template, redirect, response
    from python_packages import mpld3
    import general_functions
    import RestToolbox_modified as RestToolbox
    import field_rotation as field_rotation
else:
    from . import config
    from .python_packages.bottlepy.bottle import Bottle, request, TEMPLATE_PATH, template, redirect, response
    from .python_packages import mpld3
    from . import general_functions
    from . import RestToolbox_modified as RestToolbox
    from . import field_rotation as field_rotation

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
fieldrot_app = Bottle()

@fieldrot_app.route(PLWEB_FOLDER + '/fieldrot', method="POST")
def fieldrot():
    colormaps = ["Greys", "brg", "gray", "prism"]
    displayname = request.forms.hidden_displayname
    username = request.get_cookie("account", secret=config.SECRET_KEY)
    if not username:
        redirect(PLWEB_FOLDER + "/login")
    try:
        variables = general_functions.Read_from_dcm_database()
        variables["colormaps"] = colormaps
        variables["displayname"] = displayname
        response.set_cookie("account", username, secret=config.SECRET_KEY, samesite="lax")
    except ConnectionError:
        return template("error_template", {"error_message": "Orthanc is refusing connection.",
                                           "plweb_folder": PLWEB_FOLDER})
    return template("fieldrot", variables)


def fieldrot_helperf_catch_error(args):
    try:
        return fieldrot_helperf(args)
    except Exception as e:
        return template("error_template", {"error_message": str(e),
                                           "plweb_folder": PLWEB_FOLDER})


def fieldrot_helperf(args):

    test_type = args["test_type"]
    direction = args["direction"]
    direction2 = args["direction2"]
    number_samples = args["number_samples"]
    margin = args["margin"]
    clipbox = args["clipbox"]
    invert = args["invert"]
    w1 = args["w1"]
    w2 = args["w2"]
    colormap = args["colormap"]
    med_filter = args["med_filter"]
    general_functions.set_configuration(args["config"])
    imgdescription = args["imgdescription"]
    station = args["station"]
    displayname = args["displayname"]
    acquisition_datetime = args["acquisition_datetime"]
    high_contrast = args["high_contrast"]
    
    # Collect data for "save results"
    dicomenergy = general_functions.get_energy_from_imgdescription(imgdescription)
    user_machine, user_energy = general_functions.get_user_machine_and_energy(station, dicomenergy)
    machines_and_energies = general_functions.get_machines_and_energies(general_functions.get_treatmentunits_fieldrotation())
    tolerances = general_functions.get_tolerance_user_machine_fieldrotation(user_machine)  # If user_machne has specific tolerance
    
    if not tolerances:
        tt = general_functions.get_settings_fieldrotation()
    else:
        tt = tolerances[0]
    
    (tolerance_collabs, tolerance_collrel, tolerance_couchrel) = tt

    tolerance_collabs = float(tolerance_collabs)
    tolerance_collrel = float(tolerance_collrel)
    tolerance_couchrel = float(tolerance_couchrel)
    
    save_results = {
                    "user_machine": user_machine,
                    "user_energy": user_energy,
                    "machines_and_energies": machines_and_energies,
                    "displayname": displayname,
                    "nominal_angle": np.linspace(360, -360, 49).tolist()
                    }
    
    try:
        temp_folder1, file_path1 = RestToolbox.GetSingleDcm(config.ORTHANC_URL, w1)
        temp_folder2, file_path2 = RestToolbox.GetSingleDcm(config.ORTHANC_URL, w2)
    except:
        return template("error_template", {"error_message": "Cannot read images.",
                                           "plweb_folder": PLWEB_FOLDER})
    
    # Load first image
    try:
        img1 = pylinac_image.DicomImage(file_path1)
        # Here we force pixels to background outside of box:
        if clipbox != 0:
            try:
                img1.check_inversion_by_histogram(percentiles=[4, 50, 96]) # Check inversion otherwise this might not work
                general_functions.clip_around_image(img1, clipbox)
            except Exception as e:
                return template("error_template", {"error_message": "Unable to apply clipbox. "+str(e), "plweb_folder": PLWEB_FOLDER})
        else:
            img1.remove_edges(pixels=2)
        if invert:
            img1.invert()
        else:
            img1.check_inversion()
        img1.flipud()
    except:
        return template("error_template", {"error_message": "Cannot read image.",
                                           "plweb_folder": PLWEB_FOLDER})
    try:
        img2 = pylinac_image.DicomImage(file_path2)
        if clipbox != 0:
            try:
                img2.check_inversion_by_histogram(percentiles=[4, 50, 96]) # Check inversion otherwise this might not work
                general_functions.clip_around_image(img2, clipbox)
            except Exception as e:
                return template("error_template", {"error_message": "Unable to apply clipbox. "+str(e), "plweb_folder": PLWEB_FOLDER})
        else:
            img2.remove_edges(pixels=2)
        if invert:
            img2.invert()
        else:
            img2.check_inversion()
        img2.flipud()
    except:
        return template("error_template", {"error_message": "Cannot read image.",
                                           "plweb_folder": PLWEB_FOLDER})

    # Apply some filtering
    if med_filter > 0:
        img1.filter(med_filter)
        img2.filter(med_filter)

    # Get radiation field box:
    try:
        center_cax1, rad_field_bounding_box1, field_corners1 = field_rotation._find_field_centroid(img1)
        center_cax2, rad_field_bounding_box2, field_corners2 = field_rotation._find_field_centroid(img2)
    except Exception as e:
        return template("error_template", {"error_message": str(e), "plweb_folder": PLWEB_FOLDER})
    
    field_corners1 = field_corners1.astype(int)
    field_corners2 = field_corners2.astype(int)

    # Set colormap
    cmap = matplotlib.cm.get_cmap(colormap)
    
    if test_type == "Collimator absolute":
        # Get BBs
        try:
            if high_contrast:
                bbs1 = field_rotation._find_bb2(img1, rad_field_bounding_box1)
                bbs2 = field_rotation._find_bb2(img2, rad_field_bounding_box2)
            else:
                bbs1 = field_rotation._find_bb(img1, rad_field_bounding_box1)
                bbs2 = field_rotation._find_bb(img2, rad_field_bounding_box2)
        except Exception as e:
            return template("error_template", {"error_message": str(e), "plweb_folder": PLWEB_FOLDER})

        bb_coord1_1, bw_bb_im1_1 = bbs1[0]
        bb_coord1_2, bw_bb_im1_2 = bbs1[1]
        bb_coord2_1, bw_bb_im2_1 = bbs2[0]
        bb_coord2_2, bw_bb_im2_2 = bbs2[1]
        
        center1_1 = (bb_coord1_1[0], bb_coord1_1[1])
        center1_2 = (bb_coord1_2[0], bb_coord1_2[1])
        center2_1 = (bb_coord2_1[0], bb_coord2_1[1])
        center2_2 = (bb_coord2_2[0], bb_coord2_2[1])
        
        # Line between BBs:
        bb_angle1 = np.arctan(
            np.inf if bb_coord1_1[0]-bb_coord1_2[0] == 0 else 
            (bb_coord1_1[1]-bb_coord1_2[1]) / (bb_coord1_1[0]-bb_coord1_2[0])
            )*180/np.pi
        bb_angle2 = np.arctan(
            np.inf if bb_coord2_1[0]-bb_coord2_2[0] == 0 else 
            (bb_coord2_1[1]-bb_coord2_2[1]) / (bb_coord2_1[0]-bb_coord2_2[0])
            )*180/np.pi

        img1_filled = np.copy(img1.array)
        img2_filled = np.copy(img2.array)
        
        # Fill BBs area with neighbouring values
        field_rotation.fill_BB_hole(bb_coord1_1, bw_bb_im1_1, img1_filled)
        field_rotation.fill_BB_hole(bb_coord1_2, bw_bb_im1_2, img1_filled)
        field_rotation.fill_BB_hole(bb_coord2_1, bw_bb_im2_1, img2_filled)
        field_rotation.fill_BB_hole(bb_coord2_2, bw_bb_im2_2, img2_filled)
        
        # Get penumbra points
        try:
            samples_left1, samples_right1, p_left1, p_right1 = field_rotation.find_penumbra_points(direction, number_samples, field_corners1, margin, img1_filled)
            samples_left2, samples_right2, p_left2, p_right2 = field_rotation.find_penumbra_points(direction2, number_samples, field_corners2, margin, img2_filled)
        except Exception as e:
            return template("error_template", {"error_message": str(e), "plweb_folder": PLWEB_FOLDER})

        # Calculate field edge slopes
        pmin = 0
        pmax = np.max(img1.shape)  # Maksimum point for drawing regression lines

        if direction=="X":
            left_slope1, left_P1, left_err1 = field_rotation.calculate_regression(p_left1, samples_left1, pmin, pmax)
            right_slope1, right_P1, right_err1 = field_rotation.calculate_regression(p_right1, samples_right1, pmin, pmax)
        else:
            left_slope1, left_P1, left_err1 = field_rotation.calculate_regression(samples_left1, p_left1, pmin, pmax)
            right_slope1, right_P1, right_err1 = field_rotation.calculate_regression(samples_right1, p_right1, pmin, pmax)

        if direction2=="X":
            left_slope2, left_P2, left_err2 = field_rotation.calculate_regression(p_left2, samples_left2, pmin, pmax)
            right_slope2, right_P2, right_err2 = field_rotation.calculate_regression(p_right2, samples_right2, pmin, pmax)
        else:

            left_slope2, left_P2, left_err2 = field_rotation.calculate_regression(samples_left2, p_left2, pmin, pmax)
            right_slope2, right_P2, right_err2 = field_rotation.calculate_regression(samples_right2, p_right2, pmin, pmax)

        left_edge_angle1 = np.arctan(left_slope1)*180/np.pi
        left_edge_angle2 = np.arctan(left_slope2)*180/np.pi
        right_edge_angle1 = np.arctan(right_slope1)*180/np.pi
        right_edge_angle2 = np.arctan(right_slope2)*180/np.pi

        # First plot: field and penumbra points
        fig1 = Figure(figsize=(10.5, 5.5), tight_layout={"w_pad":3,  "pad": 3})
        ax1 = fig1.add_subplot(1,2,1)
        ax2 = fig1.add_subplot(1,2,2)
        # Plot error bars and goodness of fit
        fig2 = Figure(figsize=(10, 4), tight_layout={"w_pad":0,  "pad": 1})
        ax3 = fig2.add_subplot(1,2,1)
        ax4 = fig2.add_subplot(1,2,2)
        # Plot angled lines
        fig3 = Figure(figsize=(10, 4), tight_layout={"w_pad":0,  "pad": 1})
        ax5 = fig3.add_subplot(1,2,1)
        ax6 = fig3.add_subplot(1,2,2)
    
        ax1.imshow(img1.array, cmap=cmap, interpolation="none", aspect="equal", origin='lower')
        ax1.set_title('Image 1')
        ax1.axis('off')
        ax2.imshow(img2.array, cmap=cmap, interpolation="none", aspect="equal", origin='lower')
        ax2.set_title('Image 2')
        ax2.axis('off')
    
        #Plot field corners
        ax1.plot(field_corners1[:, 1], field_corners1[:, 0], "mo",  markersize=5, markeredgewidth=0)
        ax2.plot(field_corners2[:, 1], field_corners2[:, 0], "mo",  markersize=5, markeredgewidth=0)
        
        # Plot penumbra points
        if direction=="X":
            ax1.plot(p_left1, samples_left1, "bx", markersize=5, markeredgewidth=2)
            ax1.plot(p_right1, samples_right1, "yx", markersize=5, markeredgewidth=2)
        else:
            ax1.plot(samples_left1, p_left1, "bx", markersize=5, markeredgewidth=2)
            ax1.plot(samples_right1, p_right1,  "yx", markersize=5, markeredgewidth=2)
        
        ax1.plot(left_P1[0], left_P1[1],  "b--")
        ax1.plot(right_P1[0], right_P1[1], "y--")
        
        if direction2=="X":
            ax2.plot(p_left2, samples_left2, "bx", markersize=5, markeredgewidth=2)
            ax2.plot(p_right2, samples_right2, "yx", markersize=5, markeredgewidth=2)
        else:
            ax2.plot(samples_left2, p_left2, "bx", markersize=5, markeredgewidth=2)
            ax2.plot(samples_right2, p_right2,  "yx", markersize=5, markeredgewidth=2)

        ax2.plot(left_P2[0], left_P2[1],  "b--")
        ax2.plot(right_P2[0], right_P2[1], "y--")
        
        # Plot errors:
        ax3.plot(samples_left1, left_err1, "bx", markeredgewidth = 2)
        ax3.plot(samples_right1, right_err1, "yx", markeredgewidth = 2)
        ax4.plot(samples_left2, left_err2, "bx", markeredgewidth = 2)
        ax4.plot(samples_right2, right_err2, "yx", markeredgewidth = 2)

        limits_max = np.amax([np.amax(left_err1), np.amax(right_err1), np.amax(left_err2), np.amax(right_err2)])*1.05
        limits_min = np.amin([np.amin(left_err1), np.amin(right_err1), np.amin(left_err2), np.amin(right_err2)])*0.95
        limits = np.amax([abs(limits_max), abs(limits_min)])
        limits = limits if limits > 1 else 1
        
        ax3.set_ylim([-limits, limits])
        ax4.set_ylim([-limits, limits])
        ax3.set_ylabel("Deviation from fit [px]")
        ax4.set_ylabel("Deviation from fit [px]")
        ax3.set_xlabel("Field edge [px]")
        ax4.set_xlabel("Field edge [px]")
        ax3.set_title('Image 1 - Regression error')
        ax4.set_title('Image 2 - Regression error')
        
        # Plot angled lines:
        # If angles are negative, convert to [pi, 2pi]
        if abs(bb_angle1) > 80 and abs(bb_angle1) <= 90:
            B1 = left_edge_angle1 if left_edge_angle1 >= 0 else 180 + left_edge_angle1
            Y1 = right_edge_angle1 if right_edge_angle1 >= 0 else 180 + right_edge_angle1
            BB1 = bb_angle1 if bb_angle1 >= 0 else 180 + bb_angle1
            ref_angle_plot = PI/2  # Reference angle for drawing (either 0 or 90)
        else:
            B1 = left_edge_angle1
            Y1 = right_edge_angle1
            BB1 = bb_angle1
            ref_angle_plot = 0
        
        if abs(bb_angle2) > 80 and abs(bb_angle2) <= 90:
            B2 = left_edge_angle2 if left_edge_angle2 >= 0 else 180 + left_edge_angle2
            Y2 = right_edge_angle2 if right_edge_angle2 >= 0 else 180 + right_edge_angle2
            BB2 = bb_angle2 if bb_angle2 >= 0 else 180 + bb_angle2
        else:
            B2 = left_edge_angle2
            Y2 = right_edge_angle2
            BB2 = bb_angle2

        a = 2
        x_bb1 = [-a*np.cos(BB1*PI/180), a*np.cos(BB1*PI/180)]
        y_bb1 = [-a*np.sin(BB1*PI/180), a*np.sin(BB1*PI/180)]

        x_b1 = [-a*np.cos((B1)*PI/180), a*np.cos((B1)*PI/180)]
        y_b1 = [-a*np.sin((B1)*PI/180), a*np.sin((B1)*PI/180)]
        
        x_b2 = [-a*np.cos((BB1-(B2-BB2))*PI/180), a*np.cos((BB1-(B2-BB2))*PI/180)] 
        y_b2 = [-a*np.sin((BB1-(B2-BB2))*PI/180), a*np.sin((BB1-(B2-BB2))*PI/180)]
        
        x_y1 = [-a*np.cos((Y1)*PI/180), a*np.cos((Y1)*PI/180)]
        y_y1 = [-a*np.sin((Y1)*PI/180), a*np.sin((Y1)*PI/180)]
        
        x_y2 = [-a*np.cos((BB1-(Y2-BB2))*PI/180), a*np.cos((BB1-(Y2-BB2))*PI/180)]
        y_y2 = [-a*np.sin((BB1-(Y2-BB2))*PI/180), a*np.sin((BB1-(Y2-BB2))*PI/180)]

        ax5.plot(x_bb1, y_bb1, "g-", label="BB")
        ax5.plot(x_b1, y_b1, "b-", label="Gantry 0")
        ax5.plot(x_b2, y_b2, "b--", label="Gantry 180")
        
        ax6.plot(x_bb1, y_bb1, "g-", label="BB")
        ax6.plot(x_y1, y_y1, "y-", label="Gantry 0")
        ax6.plot(x_y2, y_y2, "y--", label="Gantry 180")
        
        if ref_angle_plot == PI/2:
            max_xb = np.amax([np.abs(x_b1), np.abs(x_b2)])
            max_xy = np.amax([np.abs(x_y1), np.abs(x_y2)])
            ax5.set_xlim([-2*max_xb, 2*max_xb])
            ax5.set_ylim([-1, 1])
            ax6.set_xlim([-2*max_xy, 2*max_xy])
            ax6.set_ylim([-1, 1])
        else:
            max_y = np.amax([np.abs(y_b1), np.abs(y_b2)])
            max_yy = np.amax([np.abs(y_y1), np.abs(y_y2)])
            ax5.set_ylim([-2*max_y, 2*max_y])
            ax5.set_xlim([-1, 1])
            ax6.set_ylim([-2*max_yy, 2*max_yy])
            ax6.set_xlim([-1, 1])
        
        ax5.legend(loc='upper right', fontsize=10, edgecolor="none")
        ax5.set_title("Blue edge")
        ax5.set_xlabel("LAT [px]")
        ax5.set_ylabel("LONG [px]")
        ax6.legend(loc='upper right', fontsize=10, edgecolor="none")
        ax6.set_title("Yellow edge")
        ax6.set_xlabel("LAT [px]")
        ax6.set_ylabel("LONG [px]")
        
        # Plot BB line and crosses
        ax1.plot([bb_coord1_1[0], bb_coord1_2[0]], [bb_coord1_1[1], bb_coord1_2[1]], "g-")
        ax2.plot([bb_coord2_1[0], bb_coord2_2[0]], [bb_coord2_1[1], bb_coord2_2[1]], "g-")
        ax1.plot(center1_1[0], center1_1[1],  'r+', markersize=10, markeredgewidth=2)
        ax1.plot(center1_2[0], center1_2[1],  'r+', markersize=10, markeredgewidth=2)
        ax2.plot(center2_1[0], center2_1[1],  'r+', markersize=10, markeredgewidth=2)
        ax2.plot(center2_2[0], center2_2[1],  'r+', markersize=10, markeredgewidth=2)
        
        ax1.set_xlim([0, img1.shape[1]])
        ax1.set_ylim([0, img1.shape[0]])
        ax2.set_xlim([0, img2.shape[1]])
        ax2.set_ylim([0, img2.shape[0]])
    
        script1 = mpld3.fig_to_html(fig1, d3_url=D3_URL, mpld3_url=MPLD3_URL)
        script2 = mpld3.fig_to_html(fig2, d3_url=D3_URL, mpld3_url=MPLD3_URL)
        script3 = mpld3.fig_to_html(fig3, d3_url=D3_URL, mpld3_url=MPLD3_URL)

        variables = {"script1": script1,
                     "script2": script2,
                     "script3": script3,
                     "left_edge_angle1": left_edge_angle1,
                     "left_edge_angle2": left_edge_angle2,
                     "right_edge_angle1": right_edge_angle1,
                     "right_edge_angle2": right_edge_angle2,
                     "bb_angle1": bb_angle1,
                     "bb_angle2": bb_angle2,
                     "test_type":test_type,
                     "tolerance": tolerance_collabs
                     }

    elif test_type == "Collimator relative":

        # Get penumbra points
        try:
            samples_left1, samples_right1, p_left1, p_right1 = field_rotation.find_penumbra_points(direction, number_samples, field_corners1, margin, img1.array)
            samples_left2, samples_right2, p_left2, p_right2 = field_rotation.find_penumbra_points(direction2, number_samples, field_corners2, margin, img2.array)
        except Exception as e:
            return template("error_template", {"error_message": str(e), "plweb_folder": PLWEB_FOLDER})

        # Calculate field edge slopes
        pmin = 0
        pmax = np.max(img1.shape)  # Maksimum point for drawing regression lines
        
        if direction=="X":
            left_slope1, left_P1, left_err1 = field_rotation.calculate_regression(p_left1, samples_left1, pmin, pmax)
            right_slope1, right_P1, right_err1 = field_rotation.calculate_regression(p_right1, samples_right1, pmin, pmax)
        else:
            left_slope1, left_P1, left_err1 = field_rotation.calculate_regression(samples_left1, p_left1, pmin, pmax)
            right_slope1, right_P1, right_err1 = field_rotation.calculate_regression(samples_right1, p_right1, pmin, pmax)
        
        if direction2=="X":
            left_slope2, left_P2, left_err2 = field_rotation.calculate_regression(p_left2, samples_left2, pmin, pmax)
            right_slope2, right_P2, right_err2 = field_rotation.calculate_regression(p_right2, samples_right2, pmin, pmax)
        else:
            left_slope2, left_P2, left_err2 = field_rotation.calculate_regression(samples_left2, p_left2, pmin, pmax)
            right_slope2, right_P2, right_err2 = field_rotation.calculate_regression(samples_right2, p_right2, pmin, pmax)

        left_edge_angle1 = np.arctan(left_slope1)*180/np.pi
        left_edge_angle2 = np.arctan(left_slope2)*180/np.pi
        right_edge_angle1 = np.arctan(right_slope1)*180/np.pi
        right_edge_angle2 = np.arctan(right_slope2)*180/np.pi

        # First plot: field and penumbra points
        fig1 = Figure(figsize=(10.5, 5.5), tight_layout={"w_pad":3,  "pad": 3})
        ax1 = fig1.add_subplot(1,2,1)
        ax2 = fig1.add_subplot(1,2,2)
        # Plot error bars and goodness of fit
        fig2 = Figure(figsize=(10, 4), tight_layout={"w_pad":0,  "pad": 1})
        ax3 = fig2.add_subplot(1,2,1)
        ax4 = fig2.add_subplot(1,2,2)
    
        ax1.imshow(img1.array, cmap=cmap, interpolation="none", aspect="equal", origin='lower')
        ax1.set_title('Image 1')
        ax1.axis('off')
        ax2.imshow(img2.array, cmap=cmap, interpolation="none", aspect="equal", origin='lower')
        ax2.set_title('Image 2')
        ax2.axis('off')
    
        #Plot field corners
        ax1.plot(field_corners1[:, 1], field_corners1[:, 0], "mo",  markersize=5, markeredgewidth=0)
        ax2.plot(field_corners2[:, 1], field_corners2[:, 0], "mo",  markersize=5, markeredgewidth=0)
        
        # Plot penumbra points
        if direction=="X":
            ax1.plot(p_left1, samples_left1, "bx", markersize=5, markeredgewidth=2)
            ax1.plot(p_right1, samples_right1, "yx", markersize=5, markeredgewidth=2)

        else:
            ax1.plot(samples_left1, p_left1, "bx", markersize=5, markeredgewidth=2)
            ax1.plot(samples_right1, p_right1,  "yx", markersize=5, markeredgewidth=2)
            
        ax1.plot(left_P1[0], left_P1[1],  "b--")
        ax1.plot(right_P1[0], right_P1[1], "y--")

        if direction2=="X":
            ax2.plot(p_left2, samples_left2, "bx", markersize=5, markeredgewidth=2)
            ax2.plot(p_right2, samples_right2, "yx", markersize=5, markeredgewidth=2)

        else:
            ax2.plot(samples_left2, p_left2, "bx", markersize=5, markeredgewidth=2)
            ax2.plot(samples_right2, p_right2,  "yx", markersize=5, markeredgewidth=2)

        ax2.plot(left_P2[0], left_P2[1],  "b--")
        ax2.plot(right_P2[0], right_P2[1], "y--")
            
        ax1.set_xlim([0, img1.shape[1]])
        ax1.set_ylim([0, img1.shape[0]])
        ax2.set_xlim([0, img2.shape[1]])
        ax2.set_ylim([0, img2.shape[0]])
        
        # Plot errors:
        ax3.plot(samples_left1, left_err1, "bx", markeredgewidth = 2)
        ax3.plot(samples_right1, right_err1, "yx", markeredgewidth = 2)
        ax4.plot(samples_left2, left_err2, "bx", markeredgewidth = 2)
        ax4.plot(samples_right2, right_err2, "yx", markeredgewidth = 2)

        limits_max = np.amax([np.amax(left_err1), np.amax(right_err1), np.amax(left_err2), np.amax(right_err2)])*1.05
        limits_min = np.amin([np.amin(left_err1), np.amin(right_err1), np.amin(left_err2), np.amin(right_err2)])*0.95
        limits = np.amax([abs(limits_max), abs(limits_min)])
        limits = limits if limits > 1 else 1
        
        ax3.set_ylim([-limits, limits])
        ax4.set_ylim([-limits, limits])
        ax3.set_ylabel("Deviation from fit [px]")
        ax4.set_ylabel("Deviation from fit [px]")
        ax3.set_xlabel("Field edge [px]")
        ax4.set_xlabel("Field edge [px]")
        ax3.set_title('Image 1 - Regression error')
        ax4.set_title('Image 2 - Regression error')
        
        script1 = mpld3.fig_to_html(fig1, d3_url=D3_URL, mpld3_url=MPLD3_URL)
        script2 = mpld3.fig_to_html(fig2, d3_url=D3_URL, mpld3_url=MPLD3_URL)
        
        variables = {"script1": script1,
                     "script2": script2,
                     "script3": "",
                     "left_edge_angle1": left_edge_angle1,
                     "left_edge_angle2": left_edge_angle2,
                     "right_edge_angle1": right_edge_angle1,
                     "right_edge_angle2": right_edge_angle2,
                     "test_type": test_type,
                     "tolerance": tolerance_collrel
                     }

    else:  # Couch rotation
        # Get BBs
        try:
            if high_contrast:
                bbs1 = field_rotation._find_bb2(img1, rad_field_bounding_box1)
                bbs2 = field_rotation._find_bb2(img2, rad_field_bounding_box2)
            else:
                bbs1 = field_rotation._find_bb(img1, rad_field_bounding_box1)
                bbs2 = field_rotation._find_bb(img2, rad_field_bounding_box2)
        except Exception as e:
            return template("error_template", {"error_message": str(e), "plweb_folder": PLWEB_FOLDER})
        
        bb_coord1_1, bw_bb_im1_1 = bbs1[0]
        bb_coord1_2, bw_bb_im1_2 = bbs1[1]
        bb_coord2_1, bw_bb_im2_1 = bbs2[0]
        bb_coord2_2, bw_bb_im2_2 = bbs2[1]
        
        center1_1 = [bb_coord1_1[0], bb_coord1_1[1]]
        center1_2 = [bb_coord1_2[0], bb_coord1_2[1]]
        center2_1 = [bb_coord2_1[0], bb_coord2_1[1]]
        center2_2 = [bb_coord2_2[0], bb_coord2_2[1]]
        
        bb_line_center1 = [np.average([center1_1[0], center1_2[0]]), np.average([center1_1[1], center1_2[1]])]
        bb_line_center2 = [np.average([center2_1[0], center2_2[0]]), np.average([center2_1[1], center2_2[1]])]
        
        # Line between BBs:
        bb_angle1 = np.arctan(
            np.inf if bb_coord1_1[0]-bb_coord1_2[0] == 0 else 
            (bb_coord1_1[1]-bb_coord1_2[1]) / (bb_coord1_1[0]-bb_coord1_2[0])
            )*180/np.pi
        bb_angle2 = np.arctan(
            np.inf if bb_coord2_1[0]-bb_coord2_2[0] == 0 else 
            (bb_coord2_1[1]-bb_coord2_2[1]) / (bb_coord2_1[0]-bb_coord2_2[0])
            )*180/np.pi

        fig1 = Figure(figsize=(10.5, 5.5), tight_layout={"w_pad":3,  "pad": 3})
        ax1 = fig1.add_subplot(1,2,1)
        ax2 = fig1.add_subplot(1,2,2)
    
        ax1.imshow(img1.array, cmap=cmap, interpolation="none", aspect="equal", origin='lower')
        ax1.set_title('Image 1')
        ax1.axis('off')
        ax2.imshow(img2.array, cmap=cmap, interpolation="none", aspect="equal", origin='lower')
        ax2.set_title('Image 2')
        ax2.axis('off')

        # Plot BB line and crosses
        ax1.plot([bb_coord1_1[0], bb_coord1_2[0]], [bb_coord1_1[1], bb_coord1_2[1]], "g-")
        ax2.plot([bb_coord2_1[0], bb_coord2_2[0]], [bb_coord2_1[1], bb_coord2_2[1]], "g-")
        ax1.plot(center1_1[0], center1_1[1],  'r+', markersize=10, markeredgewidth=2)
        ax1.plot(center1_2[0], center1_2[1],  'r+', markersize=10, markeredgewidth=2)
        ax2.plot(center2_1[0], center2_1[1],  'r+', markersize=10, markeredgewidth=2)
        ax2.plot(center2_2[0], center2_2[1],  'r+', markersize=10, markeredgewidth=2)
        
        ax1.set_xlim([0, img1.shape[1]])
        ax1.set_ylim([0, img1.shape[0]])
        ax2.set_xlim([0, img2.shape[1]])
        ax2.set_ylim([0, img2.shape[0]])
    
        script1 = mpld3.fig_to_html(fig1, d3_url=D3_URL, mpld3_url=MPLD3_URL)

        variables = {"script1": script1,
                     "script2": "",
                     "script3": "",
                     "bb_angle1": bb_angle1,
                     "bb_angle2": bb_angle2,
                     "bb_line_center1": bb_line_center1,
                     "bb_line_center2": bb_line_center2,
                     "test_type":test_type,
                     "tolerance": tolerance_couchrel
                     }
    variables["acquisition_datetime"] = acquisition_datetime
    variables["save_results"] = save_results
    variables["plweb_folder"] =  PLWEB_FOLDER
    general_functions.delete_files_in_subfolders([temp_folder1, temp_folder2]) # Delete image
    return template("fieldrot_results", variables)

@fieldrot_app.route(PLWEB_FOLDER + '/fieldrot/<w1>/<w2>', method="POST")
def fieldrot_calculate(w1, w2):
    colormap = request.forms.hidden_colormap
    test_type = request.forms.hidden_type
    direction = request.forms.hidden_direction
    direction2 = request.forms.hidden_direction2
    number_samples = int(request.forms.hidden_points)
    margin = int(request.forms.hidden_margin)
    med_filter = int(request.forms.hidden_filter)
    imgdescription = request.forms.hidden_imgdescription
    station = request.forms.hidden_station
    displayname = request.forms.hidden_displayname
    acquisition_datetime = request.forms.hidden_datetime

    clipbox = float(request.forms.hidden_clipbox)*10.0
    invert = True if request.forms.hidden_invert=="true" else False
    high_contrast = True if request.forms.hidden_high_contrast=="true" else False
    
    args = {"test_type": test_type, "direction": direction, "direction2": direction2, 
            "number_samples":number_samples, "margin":margin, "clipbox": clipbox,
            "invert":invert, "w1": w1, "w2": w2, "colormap": colormap, "med_filter": med_filter,
            "imgdescription": imgdescription, "station": station, "displayname": displayname,
            "acquisition_datetime": acquisition_datetime, "high_contrast": high_contrast,
            "config": general_functions.get_configuration()}
    p = Pool(1)
    data = p.map(fieldrot_helperf_catch_error, [args])
    p.close()
    p.join()
    return data
