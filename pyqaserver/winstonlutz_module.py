import sys
import os
import json
import tempfile
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
import numpy as np
from scipy import optimize
from pylinac import WinstonLutz
from pylinac.core import image as pylinacimage
import matplotlib.style
import matplotlib
from matplotlib.figure import Figure
from matplotlib import patches
matplotlib.use('Agg')
matplotlib.style.use('classic')


parent_module = sys.modules['.'.join(__name__.split('.')[:-1]) or '__main__']
if __name__ == '__main__' or parent_module.__name__ == '__main__':
    # sys.path.append(os.path.abspath(os.path.realpath("python_packages")))
    import config
    from python_packages.bottlepy.bottle import Bottle, request, \
        TEMPLATE_PATH, static_file, template, redirect, response
    from python_packages import mpld3
    from general_functions import get_energy_from_imgdescription
    from general_functions import get_user_machine_and_energy
    from general_functions import get_machines_and_energies
    from general_functions import get_tolerance_user_machine_wl
    from general_functions import get_settings_wl
    from general_functions import get_treatmentunits_wl
    import general_functions
    import RestToolbox_modified as RestToolbox
else:
    from . import config
    from .python_packages.bottlepy.bottle import Bottle, request, \
        TEMPLATE_PATH, static_file, template, redirect, response
    from .python_packages import mpld3
    from .general_functions import get_energy_from_imgdescription
    from .general_functions import get_user_machine_and_energy
    from .general_functions import get_machines_and_energies
    from .general_functions import get_tolerance_user_machine_wl
    from .general_functions import get_settings_wl
    from .general_functions import get_treatmentunits_wl
    from . import general_functions
    from . import RestToolbox_modified as RestToolbox


CUR_DIR = os.path.realpath(os.path.dirname(__file__))
TEMPLATE_PATH.insert(0, os.path.join(CUR_DIR, 'views'))
D3_URL = config.D3_URL
MPLD3_URL = config.MPLD3_URL


def collect_data(images):
    # images is a list o WLimages (wl.images)
    cax_position = []
    bb_position = []
    cax2bb = []
    epid2cax = []
    result = []
    radius = []
    SIDs = []
    image_type = []
    gantries = []
    collimators = []
    couches = []

    N = len(images)
    for n in range(0, N, 1):
        img = images[n]
        dpmm = img.dpmm
        cax_position.append([-(img.epid.x - img.field_cax.x)/dpmm, -(img.epid.y - img.field_cax.y)/dpmm])
        bb_position.append([-(img.epid.x-img.bb.x)/dpmm, -(img.epid.y-img.bb.y)/dpmm])
        vec = [(img.field_cax.x - img.bb.x)/dpmm, (img.field_cax.y - img.bb.y)/dpmm]
        epid2cax.append([(img.epid.x - img.field_cax.x)/dpmm, (img.epid.y - img.field_cax.y)/dpmm])
        cax2bb.append(vec)
        result.append([vec[0], vec[1]])
        radius.append(np.sqrt(vec[0]**2 + vec[1]**2))
        SIDs.append(img.sid)
        image_type.append(img.variable_axis)
        gantries.append(f"{img.gantry_angle:.0f}")
        collimators.append(f"{img.collimator_angle:.0f}")
        couches.append(f"{img.couch_angle:.0f}")
    return {
        "cax_position": cax_position,
        "bb_position": bb_position,
        "cax2bb": cax2bb,
        "epid2cax": epid2cax,
        "result": result,
        "radius": radius,
        "SIDs": SIDs,
        "image_type": image_type,
        "gantries": gantries,
        "collimators": collimators,
        "couches": couches
    }


def plot_scatter_diagram(cax2bb, epid2cax, image_numbers, gantries, collimators,
                         couches, pass_rate, success_rate, show_epid_points,
                         use_pylinac, use_couch, test_type,
                         circle_center=None, circle_radius=None,
                         linac_iso_x=None, linac_iso_y=None):

    cax2bb = np.asarray(cax2bb)
    epid2cax = np.asarray(epid2cax)
    image_order = np.argsort([int(j)-1 for j in image_numbers])
    N = len(image_numbers)

    if use_pylinac:
        fig_focal = Figure(figsize=(7, 7), tight_layout={"w_pad": 0, "pad": 0})
        ax_focal = fig_focal.add_subplot(1, 1, 1)
    elif use_couch is False:
        fig_focal = Figure(figsize=(10.5, 5), tight_layout={"w_pad": 0, "pad": 0})
        ax_focal = fig_focal.add_subplot(1, 2, 1, aspect=1)
        ax_gantry = fig_focal.add_subplot(1, 2, 2, aspect=1)
    elif test_type == "Gnt/coll + couch rotation":
        fig_focal = Figure(figsize=(10.5, 5), tight_layout={"w_pad": 0, "pad": 0})
        ax_focal = fig_focal.add_subplot(1, 2, 1, aspect=1)
        ax_couch = fig_focal.add_subplot(1, 2, 2, aspect=1)
        # Redefine
        N = 8
        image_order = np.argsort([int(j)-1 for j in image_numbers[:8]])

    labels = []
    for i in range(N):
        if use_pylinac:
            label = "img={}, G={:d}, B={:d}, P={:d}, x = {:04.2f} mm, y = {:04.2f} mm, R = {:04.2f} mm".format(
                image_numbers[i],
                int(gantries[i]),
                int(collimators[i]),
                int(couches[i]),
                cax2bb[i, 0],
                cax2bb[i, 1],
                np.linalg.norm(cax2bb[i, :])
            )
        elif use_couch is False or test_type == "Gnt/coll + couch rotation":
            label = 'Img = {:d}, x = {:04.2f} mm, y = {:04.2f} mm, R = {:04.2f} mm'.format(
                image_numbers[i],
                cax2bb[i, 0],
                cax2bb[i, 1],
                np.linalg.norm(cax2bb[i, :])
            )
        labels.append(label)
    labels = np.array(labels)[image_order]

    # Plot scatter points and green lines between them. Add tooltips.
    ax_focal.scatter(
        cax2bb[:, 0][image_order][:N], cax2bb[:, 1][image_order][:N],
        c=["blue"]*N, alpha=0.5, s=80, zorder=1, linewidths=1
    )
    scatter = ax_focal.plot(
        cax2bb[:, 0][image_order][:N], cax2bb[:, 1][image_order][:N],
        linestyle="-", color="green", alpha=0.5, marker="o", markersize=12,
        zorder=2, markerfacecolor='none', markeredgecolor='none'
    )
    tooltip = mpld3.plugins.PointLabelTooltip(scatter[0], labels=labels, location="top left")

    # Plot yellow epid points when needed
    if show_epid_points:
        labels2 = []
        for i in range(N):
            if use_pylinac:
                label2 = "img={}, G={:d}, B={:d}, P={:d}, x = {:04.2f} mm, y = {:04.2f} mm, R = {:04.2f} mm".format(
                    image_numbers[i],
                    int(gantries[i]),
                    int(collimators[i]),
                    int(couches[i]),
                    epid2cax[i, 0],
                    epid2cax[i, 1],
                    np.linalg.norm(epid2cax[i, :])
                )
            elif use_couch is False or test_type == "Gnt/coll + couch rotation":
                label2 = "Img = {:d}, x = {:04.2f} mm, y = {:04.2f} mm, R = {:04.2f} mm".format(
                    image_numbers[i],
                    epid2cax[i, 0],
                    epid2cax[i, 1],
                    np.linalg.norm(epid2cax[i, :])
                )
            labels2.append(label2)
        labels2 = np.array(labels2)[image_order]

        ax_focal.scatter(
            epid2cax[:, 0][:N], epid2cax[:, 1][:N],
            c=["yellow"]*N, alpha=0.5, s=80, zorder=1, linewidths=1
        )
        scatter2 = ax_focal.plot(
            epid2cax[:, 0][image_order][:N], epid2cax[:, 1][image_order][:N],
            linestyle="-", color="none", alpha=0.5, marker="o", markersize=12,
            zorder=2, markerfacecolor='none', markeredgecolor='none'
        )
        tooltip2 = mpld3.plugins.PointLabelTooltip(scatter2[0], labels=labels2, location="top left")
        ax_focal.plot([None], [None], c="yellow", linestyle="None", alpha=0.5, marker="o", label="EPID")
        mpld3.plugins.connect(fig_focal, tooltip, tooltip2)
    else:
        mpld3.plugins.connect(fig_focal, tooltip)

    # Legend labels:
    ax_focal.plot([None], [None], c="blue", linestyle="None", alpha=0.5, marker="o", label="CAX")

    # Add BB marker
    if show_epid_points:
        p = ax_focal.plot([0], [0], "r+", mew=3, ms=10, label="BB/CAX")
        tooltip3 = mpld3.plugins.PointLabelTooltip(p[0], labels=["Ballbearing or CAX"], location="top left")
    else:
        p = ax_focal.plot([0], [0], "r+", mew=3, ms=10, label="BB")
        tooltip3 = mpld3.plugins.PointLabelTooltip(p[0], labels=["Ballbearing"], location="top left")
    mpld3.plugins.connect(fig_focal, tooltip3)

    # Add tolerance circles
    limits_focal = pass_rate + 0.2
    ax_focal.add_patch(patches.Circle((0, 0), pass_rate, color='r', linestyle="dashed", fill=False))
    ax_focal.add_patch(patches.Circle((0, 0), success_rate, color='g', linestyle="dashed", fill=False))

    # Set diagram limits and labels and legend
    ax_focal.autoscale(False)
    ax_focal.set_xlim([-limits_focal, limits_focal])
    ax_focal.set_ylim([-limits_focal, limits_focal])
    ax_focal.set_title("Scatter diagram")
    ax_focal.set_xlabel("X [mm]")
    ax_focal.set_ylabel("Y [mm]")
    ax_focal.legend(framealpha=0, numpoints=1, ncol=3, loc='lower right', fontsize=8)

    # Plot Winkler-style diagram or couch semi-circle
    if not use_pylinac and use_couch is False:
        dis = cax2bb[:, 0]

        if len(cax2bb) == 8:
            lines180 = np.array(
                [
                    [-dis[0], -dis[0], -10, 10],
                    [-dis[1], -dis[1], -10, 10]
                ]
            )
            lines270 = np.array(
                [
                    [-10, 10, dis[2], dis[2]],
                    [-10, 10, dis[3], dis[3]]
                ]
            )
            lines0 = np.array(
                [
                    [dis[4], dis[4], -10, 10],
                    [dis[5], dis[5], -10, 10]
                ]
            )
            lines90 = np.array(
                [
                    [-10, 10, -dis[6], -dis[6]],
                    [-10, 10, -dis[7], -dis[7]]
                ]
            )

            ln1 = ax_gantry.plot(lines180[0, 0:2], lines180[0, 2:], color="grey", alpha=0.5, linewidth=1, linestyle="--")
            ln2 = ax_gantry.plot(lines180[1, 0:2], lines180[1, 2:], color="grey", alpha=0.5, linewidth=1, linestyle="--")
            ln3 = ax_gantry.plot(lines270[0, 0:2], lines270[0, 2:], color="grey", alpha=0.5, linewidth=1, linestyle="--")
            ln4 = ax_gantry.plot(lines270[1, 0:2], lines270[1, 2:], color="grey", alpha=0.5, linewidth=1, linestyle="--")
            ln5 = ax_gantry.plot(lines0[0, 0:2], lines0[0, 2:], color="grey", alpha=0.5, linewidth=1, linestyle="-")
            ln6 = ax_gantry.plot(lines0[1, 0:2], lines0[1, 2:], color="grey", alpha=0.5, linewidth=1, linestyle="-")
            ln7 = ax_gantry.plot(lines90[0, 0:2], lines90[0, 2:], color="grey", alpha=0.5, linewidth=1, linestyle="-")
            ln8 = ax_gantry.plot(lines90[1, 0:2], lines90[1, 2:], color="grey", alpha=0.5, linewidth=1, linestyle="-")

            # Add simple line tooltips (just gantry angle)
            mpld3.plugins.connect(fig_focal, mpld3.plugins.LineLabelTooltip(ln1[0], label="1"))
            mpld3.plugins.connect(fig_focal, mpld3.plugins.LineLabelTooltip(ln2[0], label="2"))
            mpld3.plugins.connect(fig_focal, mpld3.plugins.LineLabelTooltip(ln3[0], label="3"))
            mpld3.plugins.connect(fig_focal, mpld3.plugins.LineLabelTooltip(ln4[0], label="4"))
            mpld3.plugins.connect(fig_focal, mpld3.plugins.LineLabelTooltip(ln5[0], label="5"))
            mpld3.plugins.connect(fig_focal, mpld3.plugins.LineLabelTooltip(ln6[0], label="6"))
            mpld3.plugins.connect(fig_focal, mpld3.plugins.LineLabelTooltip(ln7[0], label="7"))
            mpld3.plugins.connect(fig_focal, mpld3.plugins.LineLabelTooltip(ln8[0], label="8"))

            # Plot average lines
            avg180 = np.average(lines180, axis=0)
            avg270 = np.average(lines270, axis=0)
            avg0 = np.average(lines0, axis=0)
            avg90 = np.average(lines90, axis=0)

            la1 = ax_gantry.plot(avg180[0:2], avg180[2:], color="purple", linewidth=2, linestyle="--")
            la2 = ax_gantry.plot(avg270[0:2], avg270[2:], color="purple", linewidth=2, linestyle="--")
            la3 = ax_gantry.plot(avg0[0:2], avg0[2:], color="purple", linewidth=2, linestyle="-")
            la4 = ax_gantry.plot(avg90[0:2], avg90[2:], color="purple", linewidth=2, linestyle="-")

            # Add tooltips
            mpld3.plugins.connect(fig_focal, mpld3.plugins.LineLabelTooltip(la1[0], label="Gantry 180"))
            mpld3.plugins.connect(fig_focal, mpld3.plugins.LineLabelTooltip(la2[0], label="Gantry 270"))
            mpld3.plugins.connect(fig_focal, mpld3.plugins.LineLabelTooltip(la3[0], label="Gantry 0"))
            mpld3.plugins.connect(fig_focal, mpld3.plugins.LineLabelTooltip(la4[0], label="Gantry 90"))

            gantry_center_x = [avg180[0:2], avg0[0:2]]
            gantry_center_y = [avg270[2:], avg90[2:]]

        elif len(cax2bb) == 4:
            lines180 = np.array(
                [-dis[0], -dis[0], -10, 10]
            )
            lines270 = np.array(
                [-10, 10, dis[1], dis[1]]
            )
            lines0 = np.array(
                [dis[2], dis[2], -10, 10]
            )
            lines90 = np.array(
                [-10, 10, -dis[3], -dis[3]]
            )

            la1 = ax_gantry.plot(lines180[0:2], lines180[2:], color="purple", linewidth=2, linestyle="--")
            la2 = ax_gantry.plot(lines270[0:2], lines270[2:], color="purple", linewidth=2, linestyle="--")
            la3 = ax_gantry.plot(lines0[0:2], lines0[2:], color="purple", linewidth=2, linestyle="-")
            la4 = ax_gantry.plot(lines90[0:2], lines90[2:], color="purple", linewidth=2, linestyle="-")

            # Add tooltips
            mpld3.plugins.connect(fig_focal, mpld3.plugins.LineLabelTooltip(la1[0], label="Gantry 180"))
            mpld3.plugins.connect(fig_focal, mpld3.plugins.LineLabelTooltip(la2[0], label="Gantry 270"))
            mpld3.plugins.connect(fig_focal, mpld3.plugins.LineLabelTooltip(la3[0], label="Gantry 0"))
            mpld3.plugins.connect(fig_focal, mpld3.plugins.LineLabelTooltip(la4[0], label="Gantry 90"))

            gantry_center_x = [lines180[0:2], lines0[0:2]]
            gantry_center_y = [lines270[2:], lines90[2:]]
        else:
            gantry_center_x = []
            gantry_center_y = []

        gantry_center_x = np.average(gantry_center_x)
        gantry_center_y = np.average(gantry_center_y)
        limits_gantry = np.max(np.abs(cax2bb[:, 0])) + 0.2

        ax_gantry.set_xlim([-limits_gantry, limits_gantry])
        ax_gantry.set_ylim([-limits_gantry, limits_gantry])
        ax_gantry.set_xlabel("LAT [mm]")
        ax_gantry.set_ylabel("VRT [mm]")
        ax_gantry.set_title("Gantry 2D CAX projection")

        bb = ax_gantry.plot([0], [0], "r+", mew=3, ms=10, label="BB")
        axis = ax_gantry.plot([gantry_center_x], [gantry_center_y], "x", color="black", mew=1, ms=10, label="Axis")

        # Add tooltips for BB and gantry axis
        tooltip_bb = mpld3.plugins.PointLabelTooltip(bb[0], labels=["Ballbearing"], location="top left")
        tooltip_axis = mpld3.plugins.PointLabelTooltip(axis[0], labels=["Gantry axis"], location="top left")
        mpld3.plugins.connect(fig_focal, tooltip_bb, tooltip_axis)

        ax_gantry.legend(framealpha=0, numpoints=1, ncol=2, loc='lower right', fontsize=8)
        ax_gantry.autoscale(False)

    elif use_couch and test_type == "Gnt/coll + couch rotation":

        bb_position_couch = -(cax2bb + epid2cax)[8:]
        cax2epid_couch = -epid2cax[8:]
        M = len(bb_position_couch)

        if test_type == "Gnt/coll + couch rotation":
            # Plot couch points with labels
            labels_couch = []
            for i in range(M):
                label3 = "Img = {:d}, x = {:04.2f} mm, y = {:04.2f} mm, R = {:04.2f} mm".format(
                    image_numbers[N+i],
                    bb_position_couch[i, 0],
                    bb_position_couch[i, 1],
                    np.linalg.norm(bb_position_couch[i, :])
                )
                labels_couch.append(label3)
            labels_couch = np.array(labels_couch)

            ax_couch.scatter(
                bb_position_couch[:, 0], bb_position_couch[:, 1],
                c=["red"]*M, alpha=0.5, s=80, zorder=1, linewidths=1
            )
            scatter_couch = ax_couch.plot(
                bb_position_couch[:, 0], bb_position_couch[:, 1],
                linestyle="-", color="green", alpha=0.5, marker="o", markersize=12,
                zorder=2, markerfacecolor='none', markeredgecolor='none'
            )
            tooltip4 = mpld3.plugins.PointLabelTooltip(scatter_couch[0], labels=labels_couch, location="top left")

            # Plot CAX points (with respect to EPID)
            labels_couch_cax = []
            for i in range(M):
                label4 = "Img = {:d}, x = {:04.2f} mm, y = {:04.2f} mm, R = {:04.2f} mm".format(
                    image_numbers[N+i],
                    cax2epid_couch[i, 0],
                    cax2epid_couch[i, 1],
                    np.linalg.norm(cax2epid_couch[i, :])
                )
                labels_couch_cax.append(label4)

            cax_points = ax_couch.plot(
                cax2epid_couch[:, 0], cax2epid_couch[:, 1],
                c="blue", linestyle=None, linewidth=0, alpha=0.85,
                markersize=5, marker="o", label="CAX"
            )
            tooltip5 = mpld3.plugins.PointLabelTooltip(cax_points[0], labels=labels_couch_cax, location="top left")

            # Plot center of couch axis and fitted circle
            ax_couch.add_patch(
                patches.Circle(
                    circle_center, circle_radius,
                    color='black', alpha=0.85, fill=False, linewidth=1
                )
            )

            labels_caxis = ['Couch axis, x = {:04.2f} mm, y = {:04.2f} mm'.format(circle_center[0], circle_center[1])]
            ax_couch.plot(
                [circle_center[0]], [circle_center[1]],
                linestyle="None", color="black", alpha=1, marker="x",
                markersize=12, zorder=2
            )
            couch_circle = ax_couch.plot(
                [circle_center[0]], [circle_center[1]],
                linestyle="None", color="black", alpha=1, marker="o",
                markersize=15, zorder=2, markerfacecolor='none', markeredgecolor='none'
            )
            tooltip6 = mpld3.plugins.PointLabelTooltip(couch_circle[0], labels=labels_caxis, location="top left")

            # Plot isocenter of linac
            liso = ax_couch.plot(
                [linac_iso_x], [linac_iso_y],
                c="blue", linestyle=None, linewidth=0, alpha=0.5, marker="s",
                markersize=10, label="ISO"
            )
            labels_iso = ["Linac isocenter x = {:04.2f} mm, y = {:04.2f} mm".format(linac_iso_x, linac_iso_y)]
            tooltip7 = mpld3.plugins.PointLabelTooltip(liso[0], labels=labels_iso, location="top left")

            # Add labels
            ax_couch.plot(
                [None], [None],
                c="red", linestyle=None, linewidth=0, alpha=0.5, marker="o",
                markersize=10, label="BB"
            )
            ax_couch.plot(
                [None], [None],
                c="black", linestyle=None, linewidth=0, alpha=1, marker="x",
                markersize=10, label="Axis"
            )
            mpld3.plugins.connect(fig_focal, tooltip4, tooltip5, tooltip6, tooltip7)
            ax_couch.autoscale(False)

            margin = 0.2
            if np.all(np.isnan(circle_center)):
                limits_couch = np.max(np.abs(cax2bb[:, 0])) + margin
                ax_couch.set_xlim([-limits_couch, limits_couch])
                ax_couch.set_ylim([-limits_couch, limits_couch])
            else:
                limits_couch_left = circle_center[0] - circle_radius - margin
                limits_couch_right = circle_center[0] + circle_radius + margin
                limits_couch_bottom = circle_center[1] - circle_radius - margin
                limits_couch_top = circle_center[1] + circle_radius + margin
                ax_couch.set_xlim([limits_couch_left, limits_couch_right])
                ax_couch.set_ylim([limits_couch_bottom, limits_couch_top])

            ax_couch.set_title("Couch diagram")
            ax_couch.set_xlabel("LAT [mm]")
            ax_couch.set_ylabel("LONG [mm]")
            ax_couch.legend(framealpha=0, numpoints=1, ncol=4, loc='lower right', fontsize=8)

    fig_focal.set_tight_layout(True)
    return fig_focal


def plot_couchcoll_scatter_diagram(cax2bb, epid2cax, image_numbers,
                                   test_type, circle_center=None,
                                   circle_radius=None):
    cax2bb = np.asarray(cax2bb)
    epid2cax = np.asarray(epid2cax)
    N = len(image_numbers)

    fig = Figure(figsize=(7, 7))
    ax = fig.add_subplot(1, 1, 1, aspect=1)

    if test_type == "Couch only":
        scatter_points = -(cax2bb + epid2cax)
        scatter_color = "red"
        scatter_points_aux = -epid2cax  # CAX to epid
        scatter_color_aux = "blue"
    else:  # Coll only
        scatter_points = cax2bb
        scatter_color = "blue"
        scatter_points_aux = np.array([[0, 0]])  # The BB at the center
        scatter_color_aux = "red"

    # Plot BB or CAX scatter points
    labels = []
    for i in range(N):
        label = 'Img = {:d}, x = {:04.2f} mm, y = {:04.2f} mm, R = {:04.2f} mm'.format(
            image_numbers[i], scatter_points[i, 0],
            scatter_points[i, 1], np.linalg.norm(scatter_points[i, :]))
        labels.append(label)

    ax.scatter(
        scatter_points[:, 0], scatter_points[:, 1],
        c=[scatter_color]*N, alpha=0.5, s=80, zorder=1, linewidths=1
    )
    scatter = ax.plot(
        scatter_points[:, 0], scatter_points[:, 1],
        linestyle="-", color=scatter_color, alpha=0.5, marker="o", markersize=12,
        zorder=2, markerfacecolor='none', markeredgecolor='none'
    )
    tooltip1 = mpld3.plugins.PointLabelTooltip(scatter[0], labels=labels, location="top left")

    # Plot CAX or BB points (auxiliary)
    labels_aux = []
    for i in range(len(scatter_points_aux)):
        label = 'Img = {:d}, x = {:04.2f} mm, y = {:04.2f} mm, R = {:04.2f} mm'.format(
            image_numbers[i], scatter_points_aux[i, 0],
            scatter_points_aux[i, 1], np.linalg.norm(scatter_points_aux[i, :]))
        labels_aux.append(label)

    scatter_aux = ax.plot(
        scatter_points_aux[:, 0], scatter_points_aux[:, 1],
        linestyle="none", linewidth=0, color=scatter_color_aux, alpha=0.85, marker="+", markersize=10,
        zorder=2, markeredgewidth=2
    )
    if test_type != "Couch only":
        labels_aux = ["BB"]
    tooltip2 = mpld3.plugins.PointLabelTooltip(scatter_aux[0], labels=labels_aux, location="top left")

    # Plot circle and center
    ax.add_patch(
        patches.Circle(
            circle_center, circle_radius,
            color='black', alpha=0.85, fill=False, linewidth=1
        )
    )

    labels_caxis = ['Axis, x = {:04.2f} mm, y = {:04.2f} mm'.format(circle_center[0], circle_center[1])]
    cc = ax.plot(
        [circle_center[0]], [circle_center[1]],
        linestyle="None", linewidth=0, color="black", alpha=1, marker="x",
        markersize=10, markeredgewidth=2, zorder=2
    )
    tooltip3 = mpld3.plugins.PointLabelTooltip(cc[0], labels=labels_caxis, location="top left")
    mpld3.plugins.connect(fig, tooltip1, tooltip2, tooltip3)

    margin = 0.2
    if np.all(np.isnan(circle_center)):
        limits = np.max(np.abs(scatter_points[:, 0])) + margin
        ax.set_xlim([-limits, limits])
        ax.set_ylim([-limits, limits])
    else:
        limits_left = circle_center[0] - circle_radius - margin
        limits_right = circle_center[0] + circle_radius + margin
        limits_bottom = circle_center[1] - circle_radius - margin
        limits_top = circle_center[1] + circle_radius + margin
        ax.set_xlim([limits_left, limits_right])
        ax.set_ylim([limits_bottom, limits_top])

    ax.set_title("Scatter diagram")
    ax.set_xlabel("LAT [mm]")
    ax.set_ylabel("LONG [mm]")
    fig.set_tight_layout(True)
    return fig


def determine_image_numbers(file_paths_names, images, img_numbers):
    image_numbers = []
    for img in images:
        image_numbers.append(img_numbers[file_paths_names.index(img.file)])
    return image_numbers


def create_2D_figure(images, img_numbers, clipbox, zoom, use_pylinac, cmap):
    # Function that fills the figure with axis images.
    N = len(images)
    if N % 2 == 0:
        rows = int(N/2)
    else:
        rows = int(N//2) + 1

    fig = Figure(figsize=(8, 4*rows))

    for m in range(0, len(images), 1):

        ax = fig.add_subplot(rows, 2, m+1)
        img = images[m]
        array = img.array

        # Plot the array and the contour of the 50 percent isodose line
        ax.imshow(array, cmap=cmap, interpolation="none", origin='lower')
        level = np.average(np.percentile(array, [5, 99.9]))
        ax.contour(array, levels=[level], colors=["blue"])  # CAX

        # Plot centers: field, BB, EPID
        ax.plot(img.field_cax.x, img.field_cax.y, 'b+', markersize=24, markeredgewidth=3, zorder=2)
        ax.plot(img.bb.x, img.bb.y, 'r+', markersize=24, markeredgewidth=3, zorder=2)
        ax.plot(img.epid.x, img.epid.y, 'yo', ms=10, markeredgewidth=0.0, zorder=1)

        if use_pylinac:
            title = "{}. Gantry={}, Coll.={}, Couch={}".format(
                img_numbers[m],
                int(img.gantry_angle),
                int(img.collimator_angle),
                int(img.couch_angle)
            )
        else:
            dx = (img.field_cax.x - img.bb.x)/img.dpmm
            dy = (img.field_cax.y - img.bb.y)/img.dpmm
            title = "{}. dx = {} mm, dy = {} mm".format(
                img_numbers[m],
                round(dx, 2),
                round(dy, 2)
            )

        ax.set_title(title)
        ax.set_ylabel(f"CAX to BB: {img.cax2bb_distance:3.2f}mm")

        # Plot edges of untouched area with a line:
        if clipbox != 0:
            t = int((img.shape[0] + clipbox*img.dpmm)/2)  # Top edge
            b = int((img.shape[0] - clipbox*img.dpmm)/2)  # Bottom edge
            ll = int((img.shape[1] - clipbox*img.dpmm)/2)  # Left edge
            r = int((img.shape[1] + clipbox*img.dpmm)/2)  # Right edge
            ax.plot([ll, ll, r, r, ll], [b, t, t, b, b], "-g")

        if zoom == "True":
            # If zoom is used:
            ax.set_ylim(img.rad_field_bounding_box[0], img.rad_field_bounding_box[1])
            ax.set_xlim(img.rad_field_bounding_box[2], img.rad_field_bounding_box[3])
            ax.autoscale(False)
        else:
            ax.autoscale(True)
    fig.set_tight_layout(True)
    return fig


def create_wobble_figure(wl):
    # wl - instance of the WLmanager
    # Take as a reference:
    # CAX for couch images, BB for collimator and gantry images
    fig_wobble = Figure(figsize=(9, 3))
    n = 0
    for axis in ("Gantry", "Collimator", "Couch"):
        if wl._get_images((axis, "Reference"))[0] > 1:
            images = [image for image in wl.images if image.variable_axis in (axis, "Reference")]
            ax_wobble = fig_wobble.add_subplot(1, 3, n+1)
            img = images[0]
            array = img.array
            ax_wobble.imshow(array, cmap=matplotlib.cm.Greys, interpolation="none", origin='lower')
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
                # CAX positions
                xs = [ref_x + imgg.field_cax.x - imgg.bb.x for imgg in images[1:]]
                ys = [ref_y + imgg.field_cax.y - imgg.bb.y for imgg in images[1:]]
                ax_wobble.plot(xs, ys, 'b+', markersize=12, markeredgewidth=2, zorder=2)
                circle = patches.Circle((ref_x, ref_y), 1.0*img.dpmm, color='cyan', zorder=2, fill=False, linestyle='--')
                ax_wobble.add_patch(circle)
            else:
                # BB positions
                ref_x = img.field_cax.x
                ref_y = img.field_cax.y
                xs = [ref_x + imgg.bb.x - imgg.field_cax.x for imgg in images[1:]]
                ys = [ref_y + imgg.bb.y - imgg.field_cax.y for imgg in images[1:]]
                ax_wobble.plot(xs, ys, 'r+', markersize=12, markeredgewidth=2, zorder=2)
                circle_couch = patches.Circle(
                    (ref_x, ref_y), 1.0*img.dpmm,
                    color='cyan', zorder=2, fill=False, linestyle='--')
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
        return None
    else:
        return fig_wobble


# Here starts the bottle server
wl_app = Bottle()


@wl_app.route('/winston_lutz', method="POST")
def winston_lutz():
    colormaps = ["Greys", "gray", "brg", "prism"]
    displayname = request.forms.hidden_displayname
    username = request.get_cookie("account", secret=config.SECRET_KEY)

    if not username:
        redirect("/login")

    variables = general_functions.Read_from_dcm_database()
    response.set_cookie(
        "account",
        username,
        secret=config.SECRET_KEY,
        samesite="lax"
    )

    return template(
        "winston_lutz.tpl",
        colormaps=colormaps,
        displayname=displayname,
        orthanc_id=variables["orthanc_id"],
        names=variables["names"],
        IDs=variables["IDs"],
        orthanc_url=variables["orthanc_url"]
    )


def winstonlutz_helperf(args):
    folder_path = args["folder_path"]
    file_paths = args["file_paths"]
    img_numbers = args["img_numbers"]
    use_pylinac = args["use_pylinac"]
    use_filenames = args["use_filenames"]
    clipbox = args["clipbox"]
    colormap = args["colormap"]
    zoom = args["zoom"]
    show_epid_points = args["show_epid_points"]
    test_type = args["test_type"]
    use_couch = args["use_couch"]
    station = args["station"]
    imgdescription = args["imgdescription"]
    displayname = args["displayname"]
    acquisition_datetime = args["acquisition_datetime"]
    start_x = args["start_x"]
    start_y = args["start_y"]
    general_functions.set_configuration(args["config"])

    # Collect data for "save results"
    dicomenergy = get_energy_from_imgdescription(imgdescription)
    user_machine, user_energy = get_user_machine_and_energy(station, dicomenergy)
    machines_and_energies = get_machines_and_energies(get_treatmentunits_wl())
    tolerances = get_tolerance_user_machine_wl(user_machine)

    if not tolerances:
        (pass_rate, success_rate, apply_tolerance_to_coll_asym, coll_asym_tol,
         beam_dev_tol, couch_dist_tol) = get_settings_wl()
    else:
        (pass_rate, success_rate, apply_tolerance_to_coll_asym, coll_asym_tol,
         beam_dev_tol, couch_dist_tol) = tolerances[0]

    success_rate = float(success_rate)
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

    file_paths_names = [os.path.basename(fp) for fp in file_paths]

    if use_pylinac:
        try:
            wl = WinstonLutz(folder_path, use_filenames=use_filenames)
        except Exception as e:
            general_functions.delete_files_in_subfolders([folder_path])
            return template(
                "error_template.tpl",
                error_message="Module WinstonLutz cannot calculate. "+str(e)
            )

        pdf_file = tempfile.NamedTemporaryFile(
            delete=False,
            prefix="pylinac_",
            suffix=".pdf",
            dir=config.PDF_REPORT_FOLDER
        )
        wl.publish_pdf(pdf_file)
        pdf_file.close()

        # Plot images
        axis_images = [None, None, None, None, None, None]
        if wl._contains_axis_images("Gantry"):
            images = [image for image in wl.images if image.variable_axis in ("Gantry", "Reference")]
            image_numbers = determine_image_numbers(file_paths_names, images, img_numbers)
            fig = create_2D_figure(images, image_numbers, clipbox, zoom, use_pylinac, colormap)
            axis_images[0] = mpld3.fig_to_html(fig, d3_url=D3_URL, mpld3_url=MPLD3_URL)

        if wl._contains_axis_images("Collimator"):
            images = [image for image in wl.images if image.variable_axis in ("Collimator", "Reference")]
            image_numbers = determine_image_numbers(file_paths_names, images, img_numbers)
            fig = create_2D_figure(images, image_numbers, clipbox, zoom, use_pylinac, colormap)
            axis_images[1] = mpld3.fig_to_html(fig, d3_url=D3_URL, mpld3_url=MPLD3_URL)

        if wl._contains_axis_images("Couch"):
            images = [image for image in wl.images if image.variable_axis in ("Couch", "Reference")]
            image_numbers = determine_image_numbers(file_paths_names, images, img_numbers)
            fig = create_2D_figure(images, image_numbers, clipbox, zoom, use_pylinac, colormap)
            axis_images[2] = mpld3.fig_to_html(fig, d3_url=D3_URL, mpld3_url=MPLD3_URL)

        if wl._contains_axis_images("GB Combo"):
            images = [image for image in wl.images if image.variable_axis in ("GB Combo", "Reference")]
            image_numbers = determine_image_numbers(file_paths_names, images, img_numbers)
            fig = create_2D_figure(images, image_numbers, clipbox, zoom, use_pylinac, colormap)
            axis_images[3] = mpld3.fig_to_html(fig, d3_url=D3_URL, mpld3_url=MPLD3_URL)

        if wl._contains_axis_images("GBP Combo"):
            images = [image for image in wl.images if image.variable_axis in ("GBP Combo", "Reference")]
            image_numbers = determine_image_numbers(file_paths_names, images, img_numbers)
            fig = create_2D_figure(images, image_numbers, clipbox, zoom, use_pylinac, colormap)
            axis_images[4] = mpld3.fig_to_html(fig, d3_url=D3_URL, mpld3_url=MPLD3_URL)

        # If none of the above, just plot all the images
        if all([element is None for element in axis_images[:-1]]):
            images = wl.images
            image_numbers = determine_image_numbers(file_paths_names, images, img_numbers)
            fig = create_2D_figure(images, image_numbers, clipbox, zoom, use_pylinac, colormap)
            axis_images[5] = mpld3.fig_to_html(fig, d3_url=D3_URL, mpld3_url=MPLD3_URL)

        # Plot wobble images
        fig_wobble = create_wobble_figure(wl)
        if fig_wobble is None:
            script_wobble = None
        else:
            script_wobble = mpld3.fig_to_html(fig_wobble, d3_url=D3_URL, mpld3_url=MPLD3_URL)

        # Plot Pylinac's deviations
        dev_rows = 2
        if wl._get_images(("Collimator", "Reference"))[0] > 1:
            dev_rows += 1
        if wl._get_images(("Couch", "Reference"))[0] > 1:
            dev_rows += 1

        fig_gantry_epid_sag = Figure(figsize=(8, 3*dev_rows))

        gantry_sag_ax = fig_gantry_epid_sag.add_subplot(dev_rows, 1, 1)
        epid_sag_ax = fig_gantry_epid_sag.add_subplot(dev_rows, 1, 2)
        wl._plot_deviation("Gantry", gantry_sag_ax, show=False)
        gantry_sag_ax.legend(numpoints=1, framealpha=0.8)
        wl._plot_deviation("Epid", epid_sag_ax, show=False)
        epid_sag_ax.legend(numpoints=1, framealpha=0.8)

        plot_row = 0
        if wl._get_images(("Collimator", "Reference"))[0] > 1:
            coll_sag_ax = fig_gantry_epid_sag.add_subplot(dev_rows, 1, 3 + plot_row)
            wl._plot_deviation("Collimator", coll_sag_ax, show=False)
            coll_sag_ax.legend(numpoints=1, framealpha=0.8)
            plot_row += 1
        if wl._get_images(("Couch", "Reference"))[0] > 1:
            couch_sag_ax = fig_gantry_epid_sag.add_subplot(dev_rows, 1, 3 + plot_row)
            wl._plot_deviation("Couch", couch_sag_ax, show=False)
            couch_sag_ax.legend(numpoints=1, framealpha=0.8)

        fig_gantry_epid_sag.set_tight_layout(True)
        script_gantry_epid_sag = mpld3.fig_to_html(fig_gantry_epid_sag, d3_url=D3_URL, mpld3_url=MPLD3_URL)

        # Calculate stuff
        collected_data = collect_data(wl.images)
        cax_position = collected_data["cax_position"]
        bb_position = collected_data["bb_position"]
        cax2bb = collected_data["cax2bb"]
        epid2cax = collected_data["epid2cax"]
        result = collected_data["result"]
        radius = collected_data["radius"]
        SIDs = collected_data["SIDs"]
        image_type = collected_data["image_type"]
        gantries = collected_data["gantries"]
        collimators = collected_data["collimators"]
        couches = collected_data["couches"]
        image_numbers = determine_image_numbers(file_paths_names, wl.images, img_numbers)

        # Get other results
        quickresults = wl.results(as_list=True)

        # Add scatter plot
        fig_focal = plot_scatter_diagram(cax2bb, epid2cax, image_numbers, gantries,
                                         collimators, couches, pass_rate,
                                         success_rate, show_epid_points,
                                         use_pylinac, use_couch, test_type)

        script_focal = mpld3.fig_to_html(fig_focal, d3_url=D3_URL, mpld3_url=MPLD3_URL)

        general_functions.delete_files_in_subfolders([folder_path])

        variables = {
            "acquisition_datetime": acquisition_datetime,
            "pdf_report_filename": os.path.basename(pdf_file.name),
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
            "image_numbers": image_numbers,
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
            "BBshiftX": wl.bb_shift_vector.x,
            "BBshiftY": wl.bb_shift_vector.y,
            "BBshiftZ": wl.bb_shift_vector.z,
            "GntIsoSize": wl.gantry_iso_size,
            "MaxGntRMS": max(wl.axis_rms_deviation("Gantry")),
            "MaxEpidRMS": max(wl.axis_rms_deviation("Epid")),
            "GntColl3DisoSize": wl.gantry_coll_iso_size,
            "Coll2DisoSize": wl.collimator_iso_size,
            "MaxCollRMS": max(wl.axis_rms_deviation("Collimator")),
            "Couch2DisoDia": wl.couch_iso_size,
            "MaxCouchRMS": max(wl.axis_rms_deviation("Couch"))
        }

        return template("winston_lutz_pylinac_results", variables)

    else:
        # This is the non-pylinac analysis
        def winstonlutz_default_calculation_helperf(path):
            return WinstonLutz(path, use_filenames=False)

        p = ThreadPool()
        image_list = p.map(winstonlutz_default_calculation_helperf, file_paths)
        p.close()
        p.join()

        images = [image.images[0] for image in image_list]
        fig_wl = create_2D_figure(images, img_numbers, clipbox, zoom, use_pylinac, colormap)

        # Collect stuff
        collected_data = collect_data(images)
        cax_position = collected_data["cax_position"]
        bb_position = collected_data["bb_position"]
        cax2bb = collected_data["cax2bb"]
        epid2cax = collected_data["epid2cax"]
        result = collected_data["result"]
        radius = collected_data["radius"]
        SIDs = collected_data["SIDs"]
        gantries = collected_data["gantries"]
        collimators = collected_data["collimators"]
        couches = collected_data["couches"]

        script = mpld3.fig_to_html(fig_wl, d3_url=D3_URL, mpld3_url=MPLD3_URL)
        general_functions.delete_files_in_subfolders(file_paths)

        if use_couch is False:
            cax2bb = np.asarray(cax2bb)
            epid2cax = np.asarray(epid2cax)

            fig_focal = plot_scatter_diagram(
                cax2bb, epid2cax, img_numbers, gantries, collimators,
                couches, pass_rate, success_rate, show_epid_points,
                use_pylinac, use_couch, test_type
            )

            script_focal = mpld3.fig_to_html(fig_focal, d3_url=D3_URL, mpld3_url=MPLD3_URL)

            # Calculate radius from center of CAX cloud to CAX:
            average_x = np.average(cax2bb[:, 0])
            average_y = np.average(cax2bb[:, 1])
            cax_wobble = np.linalg.norm(np.column_stack((cax2bb[:, 0]-average_x, cax2bb[:, 1]-average_y)), axis=1)

            # Calculate EPID position with respect to CAX:
            epid2cax_dev_avg = np.average(epid2cax, axis=0)

            variables = {
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
                "save_results": save_results
            }
            return template("winston_lutz_results", variables)
        else:
            if test_type == "Gnt/coll + couch rotation":
                cax2bb_gntcoll = np.asarray(cax2bb)[:8]  # pick only the first 8 images!
                epid2cax_gntcoll = np.asarray(epid2cax)[:8]
                bb_position_couch = np.asarray(bb_position)[8:]

                # Plot scatter plot for couch!
                def calc_distance2center(xc, yc):
                    # Calculate the distance of 2D points from the center (xc, yc)
                    # Do not include first point in the calculation.
                    return np.sqrt((bb_position_couch[1:, 0]-xc)**2 + (bb_position_couch[1:, 1]-yc)**2)

                def calc_distance(c):
                    # Calculate the algebraic distance between the data points and
                    # the mean circle centered at c=(xc, yc)
                    Ri = calc_distance2center(*c)
                    return Ri - Ri.mean()

                try:
                    solution = optimize.least_squares(calc_distance, x0=[start_x, start_y], bounds=[-5, 5])
                    circle_center = solution.x
                except:
                    circle_center = [np.nan, np.nan]

                circle_radius = calc_distance2center(*circle_center).mean()

                # Calculate distance of couch axis from rad center
                lat = (-result[0][0] - result[1][0] + result[4][0] + result[5][0])/4
                long = (result[0][1] + result[1][1] + result[2][1] + result[3][1]
                        + result[4][1] + result[5][1] + result[6][1] + result[7][1])/8

                linac_iso_x = lat + bb_position_couch[0][0]
                linac_iso_y = long + bb_position_couch[0][1]

                couch_iso_dev_x = circle_center[0] - linac_iso_x
                couch_iso_dev_y = circle_center[1] - linac_iso_y

                fig_focal = plot_scatter_diagram(
                    cax2bb, epid2cax, img_numbers, gantries, collimators,
                    couches, pass_rate, success_rate, show_epid_points,
                    use_pylinac, use_couch, test_type,
                    circle_center, circle_radius, linac_iso_x, linac_iso_y
                )
                script_focal = mpld3.fig_to_html(fig_focal, d3_url=D3_URL, mpld3_url=MPLD3_URL)

                # Calculate radius from center of CAX cloud to CAX:
                average_x = np.average(cax2bb_gntcoll[:, 0])
                average_y = np.average(cax2bb_gntcoll[:, 1])
                cax_wobble = np.linalg.norm(
                    np.column_stack(
                        (cax2bb_gntcoll[:, 0]-average_x, cax2bb_gntcoll[:, 1]-average_y)),
                    axis=1
                )

                # Calculate EPID position with respect to CAX:
                epid2cax_dev_avg = np.average(epid2cax_gntcoll, axis=0)

                variables = {
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
                    "couch_wobble": circle_radius,
                    "couch_iso_dev_x": couch_iso_dev_x,
                    "couch_iso_dev_y": couch_iso_dev_y,
                    "save_results": save_results
                }

                return template("winston_lutz_results_gntcollcouch", variables)

            elif test_type == "Couch only":  # if only the couch is rotated, no gnt or coll
                bb_position_couch = np.asarray(bb_position)

                def calc_distance2center(xc, yc):
                    # Calculate the distance of 2D points from the center (xc, yc)
                    # Do not include first point in the calculation.
                    return np.sqrt((bb_position_couch[:, 0]-xc)**2 + (bb_position_couch[:, 1]-yc)**2)

                def calc_distance(c):
                    # Calculate the algebraic distance between the data points and
                    # the mean circle centered at c=(xc, yc)
                    Ri = calc_distance2center(*c)
                    return Ri - Ri.mean()

                try:
                    solution = optimize.least_squares(calc_distance, x0=[start_x, start_y], bounds=[-5, 5])
                    circle_center = solution.x
                except:
                    circle_center = [np.nan, np.nan]

                circle_radius = calc_distance2center(*circle_center).mean()

                fig_couch = plot_couchcoll_scatter_diagram(
                    cax2bb, epid2cax, img_numbers, test_type,
                    circle_center=circle_center, circle_radius=circle_radius
                )

                script_focal = mpld3.fig_to_html(fig_couch, d3_url=D3_URL, mpld3_url=MPLD3_URL)

                variables = {
                    "acquisition_datetime": acquisition_datetime,
                    "script": script,
                    "script_focal": script_focal,
                    "cax_position": cax_position,
                    "cax_avg": np.average(cax_position, axis=0),
                    "bb_position": bb_position,
                    "result": result,
                    "radius": radius,
                    "iso_size": circle_radius,
                    "iso_position": circle_center,
                    "image_numbers": img_numbers,
                    "SIDs": list(set(SIDs)),
                    "save_results": save_results
                }

                return template("winston_lutz_results_couchonly", variables)

            else:
                cax2bb = np.asarray(cax2bb)
                def calc_distance2center(xc, yc):
                    # Calculate the distance of 2D points from the center (xc, yc)
                    # Do not include first point in the calculation.
                    return np.sqrt((cax2bb[:, 0]-xc)**2 + (cax2bb[:, 1]-yc)**2)

                def calc_distance(c):
                    # Calculate the algebraic distance between the data points and
                    # the mean circle centered at c=(xc, yc)
                    Ri = calc_distance2center(*c)
                    return Ri - Ri.mean()

                try:
                    solution = optimize.least_squares(calc_distance, x0=[start_x, start_y], bounds=[-5, 5])
                    circle_center = solution.x
                except:
                    circle_center = [np.nan, np.nan]

                circle_radius = calc_distance2center(*circle_center).mean()

                fig_coll = plot_couchcoll_scatter_diagram(
                    cax2bb, epid2cax, img_numbers, test_type,
                    circle_center=circle_center, circle_radius=circle_radius
                )

                script_focal = mpld3.fig_to_html(fig_coll, d3_url=D3_URL, mpld3_url=MPLD3_URL)

                variables = {
                    "acquisition_datetime": acquisition_datetime,
                    "script": script,
                    "script_focal": script_focal,
                    "cax_position": cax_position,
                    "cax_avg": np.average(cax_position, axis=0),
                    "bb_position": bb_position,
                    "result": result,
                    "radius": radius,
                    "iso_size": circle_radius,
                    "iso_position": circle_center,
                    "image_numbers": img_numbers,
                    "SIDs": list(set(SIDs)),
                    "save_results": save_results
                }

                return template("winston_lutz_results_collimatoronly", variables)

def winstonlutz_helperf_catch_error(args):
    try:
        return winstonlutz_helperf(args)
    except Exception as e:
        return template("error_template", {"error_message": str(e)})


@wl_app.route('/winston_lutz_calculate/<clipbox>/<zoom>/<use_pylinac>', method="POST")
def winston_lutz_calculate(clipbox, zoom, use_pylinac):
    colormap = request.forms.hidden_colormap
    test_type = request.forms.hidden_testtype
    use_couch = True if request.forms.hidden_usecouch == "true" else False
    show_epid_points = True if request.forms.hidden_show_epid_points == "true" else False
    use_pylinac = True if use_pylinac == "True" else False
    station = request.forms.hidden_station
    imgdescription = request.forms.hidden_imgdescription
    displayname = request.forms.hidden_displayname
    acquisition_datetime = request.forms.hidden_datetime
    instances_list = json.loads(request.forms.get("instances_list"))
    clipbox = float(clipbox)*10.0
    start_x = float(request.forms.hidden_startx)
    start_y = float(request.forms.hidden_starty)
    imglist = json.loads(request.forms.useimglist)  # True/False array
    use_filenames = False

    if not any(imglist):
        return template(
            "error_template.tpl",
            error_message="All images are unchecked."
        )

    if (sum(imglist) < 11) and (use_couch) and (test_type == "Gnt/coll + couch rotation"):
        return template(
            "error_template.tpl",
            error_message="At least 8 + 3 images are required to determine "
                          "linac isocenter and couch axis of rotation."
        )

    if (sum(imglist) < 3) and (use_couch) and (test_type == "Couch only"):
        return template(
            "error_template.tpl",
            error_message="At least 3 images are required to determine "
                          "couch axis of rotation."
        )

    if (sum(imglist) < 3) and (use_couch) and (test_type == "Collimator only"):
        return template(
            "error_template.tpl",
            error_message="At least 3 images are required to determine "
                          "collimator axis of rotation."
        )

    # Get sequential image number:
    img_numbers = []  # Starting with 1
    for i in range(len(imglist)):
        if imglist[i]:
            img_numbers.append(i+1)

    if use_pylinac:
        pylinac_angles_full = json.loads(request.forms.pylinacangles)
        pylinac_angles_full = [int(float(x)) if x != "" else None for x in pylinac_angles_full]

        if pylinac_angles_full.count(None) == 0:
            use_filenames = True

        pylinac_angles_full = np.array(pylinac_angles_full).reshape((-1, 3)).tolist()
        pylinac_angles = []

        for i in range(len(pylinac_angles_full)):
            if imglist[i]:
                pylinac_angles.append(pylinac_angles_full[i])

        (folder_path, file_paths, file_paths_full) = RestToolbox.GetSeries2Folder(
            config.ORTHANC_URL, instances_list, imglist
        )

        if use_filenames:
            # Add coll/gantry/couch angles to the file name
            for z in range(len(file_paths)):
                f = file_paths[z]
                img_name = os.path.splitext(os.path.basename(f))[0]
                new_name = img_name + "_gantry" + str(pylinac_angles[z][0]) \
                           + "_coll" + str(pylinac_angles[z][1]) + "_couch" \
                           + str(pylinac_angles[z][2])+".dcm"
                new_path = os.path.join(folder_path, new_name)
                os.replace(f, new_path)
                file_paths[z] = new_path
                file_paths_full[file_paths_full.index(f)] = new_path

        if clipbox != 0:
            for filename in file_paths:
                try:
                    orig_img = pylinacimage.DicomImage(filename)
                    orig_img.check_inversion()
                    general_functions.clip_around_image(orig_img, clipbox)
                    orig_img.save(filename)
                except:
                    return template(
                        "error_template.tpl",
                        error_message="Unable to apply clipbox."
                    )
    else:
        folder_path = []
        file_paths_full = RestToolbox.GetSeries2Subfolders(config.ORTHANC_URL, instances_list, imglist)

        # Get only those images that were ticked:
        file_paths = []
        for i in range(0, len(file_paths_full)):
            if imglist[i]:
                file_paths.append(file_paths_full[i])

        if clipbox != 0:
            for subfolder in file_paths:
                for filename in os.listdir(subfolder):
                    try:
                        orig_img = pylinacimage.DicomImage(os.path.join(subfolder, filename))
                        orig_img.check_inversion() # Check inversion first
                        general_functions.clip_around_image(orig_img, clipbox)
                        orig_img.save(os.path.join(subfolder, filename))
                    except:
                        return template(
                            "error_template.tpl",
                            error_message="Unable to apply clipbox."
                        )

    # Note that file_paths are dcm files if use_pylinac==True else subfolders

    args = {
        "folder_path": folder_path,
        "file_paths": file_paths,
        "img_numbers": img_numbers,
        "colormap": colormap,
        "clipbox": clipbox,
        "zoom": zoom,
        "use_pylinac": use_pylinac,
        "show_epid_points": show_epid_points,
        "use_filenames": use_filenames,
        "test_type": test_type,
        "use_couch": use_couch,
        "station": station,
        "imgdescription": imgdescription,
        "displayname": displayname,
        "acquisition_datetime": acquisition_datetime,
        "start_x": start_x,
        "start_y": start_y,
        "config": general_functions.get_configuration()
    }

    pool = Pool(1)
    try:
        data = pool.map(winstonlutz_helperf, [args])
        pool.close()
        pool.join()
    except Exception as e:
        pool.terminate()
        return template("error_template.tpl", error_message=str(e))
    return data

@wl_app.route('/winstonlutz_pdf_export', method="post")
def winstonlutz_pdf_export():
    pdf_file = str(request.forms.hidden_wl_pdf_report)
    return static_file(pdf_file, root=config.PDF_REPORT_FOLDER, download=pdf_file)
