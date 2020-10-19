# Certain methods are copied from pylinac
import numpy as np
import copy
from scipy import ndimage
from skimage import filters, measure, segmentation, feature
from pylinac.core import profile, image
from pylinac.core.mask import bounding_box
import sys

parent_module = sys.modules['.'.join(__name__.split('.')[:-1]) or '__main__']
if __name__ == '__main__' or parent_module.__name__ == '__main__':
    import config
else:
    from . import config

# Added leaf side positions taken from dicom RT plan files [values are in mm]
LEAF_TYPE = {"Varian_120": [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0, 55.0, 60.0, 65.0, 70.0, 75.0, 80.0, 85.0, 90.0, 95.0, 100.0, 110.0, 120.0, 130.0, 140.0, 150.0, 160.0, 170.0, 180.0, 190.0, 200.0],
             "Varian_120HD": [0.0, 2.5, 5, 7.5, 10, 12.5, 15, 17.5, 20, 22.5, 25, 27.5, 30, 32.5, 35, 37.5, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110],
             "Varian_80": [0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0, 110.0, 120.0, 130.0, 140.0, 150.0, 160.0, 170.0, 180.0, 190.0, 200.0],
             "Elekta_80": [0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0, 110.0, 120.0, 130.0, 140.0, 150.0, 160.0, 170.0, 180.0, 190.0, 200.0],
             "Elekta_160": [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0, 55.0, 60.0, 65.0, 70.0, 75.0, 80.0, 85.0, 90.0, 95.0, 100.0, 105.0, 110.0, 115.0, 120.0, 125.0, 130.0, 135.0, 140.0, 145.0, 150.0, 155.0, 160.0, 165.0, 170.0, 175.0, 180.0, 185.0, 190.0, 195.0, 200.0]
             }

def _find_field_centroid(img):
    """Find the centroid of the radiation field based on a 50% height threshold.

    Returns
    -------
    p
        The CAX point location.
    edges
        The bounding box of the field, plus a small margin.
    """
    min, max = np.percentile(img.array, [5, 99.9])
    threshold_img = img.as_binary((max - min)/2 + min)
    # clean single-pixel noise from outside field
    cleaned_img = ndimage.binary_erosion(threshold_img)
    edges_nomargin = bounding_box(cleaned_img)
    ymin,ymax,xmin,xmax = edges_nomargin
    cleaned_img[ymin:ymax,xmin:xmax] = ndimage.binary_fill_holes(cleaned_img[ymin:ymax,xmin:xmax])
    #cleaned_img = ndimage.binary_fill_holes(cleaned_img)
    [*edges] = edges_nomargin
    edges[0] -= 10
    edges[1] += 10
    edges[2] -= 10
    edges[3] += 10
    coords = ndimage.measurements.center_of_mass(cleaned_img)
    return [coords[-1], coords[0]], edges

def is_symmetric(logical_array):
    """Whether the binary object's dimensions are symmetric, i.e. a perfect circle. Used to find the BB."""
    ymin, ymax, xmin, xmax = bounding_box(logical_array)
    y = abs(ymax - ymin)
    x = abs(xmax - xmin)
    if x > max(y * 1.05, y + 3) or x < min(y * 0.95, y - 3):
        return False
    return True


def is_modest_size(logical_array, field_bounding_box):
    """Decide whether the ROI is roughly the size of a BB; not noise and not an artifact. Used to find the BB."""
    bbox = field_bounding_box
    rad_field_area = (bbox[1] - bbox[0]) * (bbox[3] - bbox[2])
    return rad_field_area * 0.0001 < np.sum(logical_array) < rad_field_area * 0.3


def is_round(rprops):
    """Decide if the ROI is circular in nature by testing the filled area vs bounding box. Used to find the BB."""
    expected_fill_ratio = np.pi / 4
    actual_fill_ratio = rprops.filled_area / rprops.bbox_area
    return expected_fill_ratio * 1.2 > actual_fill_ratio > expected_fill_ratio * 0.8

def _find_bb(img, bb_box):
    """Find the BB within the radiation field. Iteratively searches for a circle-like object
    by lowering a low-pass threshold value until found.

    Returns
    -------
    Point
        The weighted-pixel value location of the BB.
    """
    # get initial starting conditions
    hmin, hmax = np.percentile(img.array, [5, 99.9])
    spread = hmax - hmin
    max_thresh = hmax
    lower_thresh = hmax - spread / 1.5
    # search for the BB by iteratively lowering the low-pass threshold value until the BB is found.
    found = False
    iteration = 0
    while not found:
        try:
            binary_arr = np.logical_and((max_thresh > img), (img >= lower_thresh))
            labeled_arr, num_roi = ndimage.measurements.label(binary_arr)
            roi_sizes, bin_edges = np.histogram(labeled_arr, bins=num_roi + 1)
            bw_bb_img = np.where(labeled_arr == np.argsort(roi_sizes)[-3], 1, 0)
            bw_bb_img = ndimage.binary_fill_holes(bw_bb_img).astype(int)  # fill holes for low energy beams like 2.5MV
            bb_regionprops = measure.regionprops(bw_bb_img)[0]

            if not is_round(bb_regionprops):
                raise ValueError
            if not is_modest_size(bw_bb_img, bb_box):
                raise ValueError
            if not is_symmetric(bw_bb_img):
                raise ValueError
        except (IndexError, ValueError):
            max_thresh -= 0.05 * spread
            if max_thresh < hmin:
                raise ValueError("Unable to locate the BB. Make sure the field edges do not obscure the BB and that there is no artifacts in the images.")
        else:
            found = True
        if iteration > 100: # Allow only 100 iterations, then abort (addition)
            raise ValueError("Unable to locate the BB. It is possible that your image does not contain a BB.")
        iteration += 1

    # determine the center of mass of the BB
    inv_img = image.load(img.array)
    # we invert so BB intensity increases w/ attenuation
    inv_img.check_inversion_by_histogram(percentiles=(99.99, 50, 0.01))
    bb_rprops = measure.regionprops(bw_bb_img, intensity_image=inv_img)[0]

    # Added output to show BB contour!
    return [[bb_rprops.weighted_centroid[1], bb_rprops.weighted_centroid[0]], bw_bb_img]


def _find_bb2(img, rad_field_bounding_box):
    # Taken from pylinac'c ct module. Should work for kV images
    threshold = "otsu"
    clear_borders = False
    fill_holes = False
    if threshold == 'otsu':
        thresmeth = filters.threshold_otsu
    elif threshold == 'mean':
        thresmeth = np.mean
    edges = filters.scharr(img.array.astype(np.float))
    edges = filters.gaussian(edges, sigma=1)
    thres = thresmeth(edges)
    bw = edges > thres
    if clear_borders:
        segmentation.clear_border(bw, buffer_size=int(max(bw.shape)/50), in_place=True)
    if fill_holes:
        bw = ndimage.binary_fill_holes(bw)
    labeled_arr, num_roi = measure.label(bw, return_num=True)
    regionprops = measure.regionprops(labeled_arr, edges)
    
    if num_roi < 2:
        raise ValueError("Unable to locate the BB. Make sure the BB is located within the field "
                         "away from field edges and that there is no significant noise or artifact in "
                         "the image. The field must not cover the whole image.")
    elif num_roi >= 2:
        regionprops = sorted(regionprops, key=lambda x: x.filled_area, reverse=True)[1:2]

    sorted_regions = sorted(regionprops, key=lambda x: (x.centroid[1]))
    
    centers = [(r.weighted_centroid[1], r.weighted_centroid[0]) for r in sorted_regions]
    roi_sizes, bin_edges = np.histogram(labeled_arr, bins=num_roi + 1)
    bw_bb_img1 = np.where(labeled_arr == np.argsort(roi_sizes)[-3], 1, 0)  
    bw_bb_img1 = ndimage.binary_fill_holes(bw_bb_img1).astype(int)
    return [centers[0], bw_bb_img1]


def sample_points_mlc(nr_leaf_sample_points, leaf_type="Elekta_160"):
    # Prepare sampling points for leaves
    leaf_edges = np.array(LEAF_TYPE[leaf_type])
    leaf_widths = np.diff(leaf_edges)
    leaf_sample_points = []
    for i in np.arange(0, leaf_edges.shape[0]-1, 1):
        temp_samples = []
        for n in range(1, nr_leaf_sample_points+1):
            temp_samples.append(leaf_edges[i] + n*leaf_widths[i]/(nr_leaf_sample_points+1))
        leaf_sample_points.append(temp_samples)
    return np.vstack((-np.flipud(np.fliplr(leaf_sample_points)), np.asarray(leaf_sample_points)))

def points_to_pixels_mlc(leaf_scaling, leaf_sample_points, min_px, max_px, center_pixel):
    leaf_sample_pixels = leaf_sample_points*leaf_scaling + center_pixel
    leaf_sample_pixels = leaf_sample_pixels[np.all(np.logical_and(leaf_sample_pixels > min_px, leaf_sample_pixels < max_px), axis=1)]
    return np.rint(leaf_sample_pixels).astype(int)

def sample_pixels_jaws(nr_jaw_sample_points, min_px, max_px):
    first_pixel_jaw = min_px
    length_jaws = np.abs(max_px-min_px)
    jaw_sample_pixels = []
    for k in np.arange(1, nr_jaw_sample_points+1, 1):
        jaw_sample_pixels.append(first_pixel_jaw + k*length_jaws/(nr_jaw_sample_points+1))
    return np.rint(jaw_sample_pixels).astype(int)

def calculate_penumbra_pixels_mlc(img, leaf_sample_pixels, mlc_direction):
    penumbra_L = []
    penumbra_R = []
    for a in np.arange(0, leaf_sample_pixels.shape[0], 1):
        temp_L = []
        temp_R = []
        for b in np.arange(0, leaf_sample_pixels.shape[1], 1):
            line = leaf_sample_pixels[a][b]
            if mlc_direction=="X":
                sp = profile.SingleProfile(img.array[line, :])
            else:
                sp = profile.SingleProfile(img.array[:, line])
            sp.ground()
            sp.filter()
            pR = sp._penumbra_point(side="right", x=50, interpolate=True)
            pL = sp._penumbra_point(side="left", x=50, interpolate=True)
            temp_L.append(pL)
            temp_R.append(pR)
        penumbra_L.append(temp_L)
        penumbra_R.append(temp_R)
    return np.asarray(penumbra_L), np.asarray(penumbra_R)

def calculate_penumbra_pixels_jaws(img, jaw_sample_pixels, mlc_direction):
    penumbra_L = []
    penumbra_R = []
    for a in np.arange(0, jaw_sample_pixels.shape[0], 1):
        if mlc_direction=="X":
            sp = profile.SingleProfile(img.array[:, jaw_sample_pixels[a]])
        else:
            sp = profile.SingleProfile(img.array[jaw_sample_pixels[a], :])
        sp.ground()
        sp.filter()
        pR = sp._penumbra_point(side="right", x=50, interpolate=True)
        pL = sp._penumbra_point(side="left", x=50, interpolate=True)
        penumbra_L.append(pL)
        penumbra_R.append(pR)
    return np.asarray(penumbra_L), np.asarray(penumbra_R)

def _get_canny_regions(img, sigma=2, percentiles=(0.001, 0.01)):
    """Compute the canny edges of the image and return the connected regions found."""
    # copy, filter, and ground the image
    img_copy = copy.copy(img)
    img_copy.filter(kind='gaussian', size=sigma)
    img_copy.ground()

    # compute the canny edges with very low thresholds (detects nearly everything)
    lo_th, hi_th = np.percentile(img_copy, percentiles)
    c = feature.canny(img_copy, low_threshold=lo_th, high_threshold=hi_th)

    # label the canny edge regions
    labeled = measure.label(c)
    regions = measure.regionprops(labeled, intensity_image=img_copy)
    return regions

def as_binary(img_array, threshold):
    """Return a binary (black & white) image based on the given threshold.

    Parameters
    ----------
    threshold : int, float
        The threshold value. If the value is above or equal to the threshold it is set to 1, otherwise to 0.

    Returns
    -------
    ArrayImage
    """
    array = np.where(img_array >= threshold, 1, 0)
    return array

def _find_plate_center(plate):
    """Find the center of the plate that defines the mechanical isocenter.
    """
    min, max = np.percentile(plate.array, [5, 99.9])
    threshold_img = as_binary(plate.array, (max - min)/2 + min)
    coords = ndimage.measurements.center_of_mass(threshold_img)
    return (coords[-1], coords[0])

def plate_ud_width(img_copy, samples_vertical, filter_size, up_end, down_start, sample_box):
    # Calculate the width of the windows in the Elekta plate (UP - DOWN direction)
    width_vert_up = []
    width_vert_down = []
    fwhm_center_vert_up = []
    fwhm_center_vert_down = []
    for v in np.arange(0, len(samples_vertical), 1):
        vrt_profile_up = profile.SingleProfile(np.average(img_copy.array[0:up_end, samples_vertical[v]-sample_box:samples_vertical[v]+sample_box], axis=1))
        vrt_profile_down = profile.SingleProfile(np.average(img_copy.array[down_start:, samples_vertical[v]-sample_box:samples_vertical[v]+sample_box], axis=1))
        vrt_profile_up.ground()
        vrt_profile_down.ground()
        vrt_profile_up.filter(filter_size)
        vrt_profile_down.filter(filter_size)
        width_vert_up.append(vrt_profile_up.fwxm(x=50, interpolate=True))
        width_vert_down.append(vrt_profile_down.fwxm(x=50, interpolate=True))
        fwhm_center_vert_up.append(vrt_profile_up.fwxm_center(x=50, interpolate=True))
        fwhm_center_vert_down.append(vrt_profile_down.fwxm_center(x=50, interpolate=True))
    return np.asarray(width_vert_up), np.asarray(fwhm_center_vert_up), np.asarray(width_vert_down), np.asarray(fwhm_center_vert_down)


def plate_lr_width(img_copy, samples_horizontal, filter_size, left_end, right_start, sample_box):
    # Calculate the width of the windows in the Elekta plate (LEFT - RIGHT direction)
    width_hor_left = []
    width_hor_right = []
    fwhm_center_hor_left = []
    fwhm_center_hor_right = []
    for v in np.arange(0, len(samples_horizontal), 1):
        hor_profile_left = profile.SingleProfile(np.average(img_copy.array[samples_horizontal[v]-sample_box:samples_horizontal[v]+sample_box, 0:left_end], axis=0))
        hor_profile_right = profile.SingleProfile(np.average(img_copy.array[samples_horizontal[v]-sample_box:samples_horizontal[v]+sample_box, right_start:], axis=0))
        hor_profile_left.ground()
        hor_profile_right.ground()
        hor_profile_left.filter(size=filter_size)
        hor_profile_right.filter(size=filter_size)
        width_hor_left.append(hor_profile_left.fwxm(x=50, interpolate=True))
        width_hor_right.append(hor_profile_right.fwxm(x=50, interpolate=True))
        fwhm_center_hor_left.append(hor_profile_left.fwxm_center(x=50, interpolate=True))
        fwhm_center_hor_right.append(hor_profile_right.fwxm_center(x=50, interpolate=True))
    return np.asarray(width_hor_left), np.asarray(fwhm_center_hor_left),  np.asarray(width_hor_right), np.asarray(fwhm_center_hor_right)