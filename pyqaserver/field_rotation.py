# Many functions/methods in this module were taken from pylinac
# brjdenis ...
import numpy as np
from pylinac.core import profile, image, geometry
from scipy import ndimage
from scipy.stats import linregress as scipy_linregress
from skimage import filters, measure, segmentation
from pylinac.core.mask import  bounding_box
import sys, os

parent_module = sys.modules['.'.join(__name__.split('.')[:-1]) or '__main__']
if __name__ == '__main__' or parent_module.__name__ == '__main__':
    #sys.path.append(os.path.abspath(os.path.realpath("python_packages")))  # To import mpld3
    import config
    from python_packages.minimumboundingbox import minimumboundingbox
else:
    from . import config
    from .python_packages.minimumboundingbox import minimumboundingbox


def find_field_corners(field_contour):
    '''This function is using MinimumBoundingBox.py'''
    bounding_box = minimumboundingbox.MinimumBoundingBox(field_contour)
    return np.asarray(bounding_box.corner_points)

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
    field_contour = measure.find_contours(cleaned_img, 0.5)[0]
    field_corners = find_field_corners(field_contour)
    return (coords[-1], coords[0]), edges, field_corners

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
    # Changed the minimum BB size to 0.001 (for large fields) and max size to 0.05
    return rad_field_area * 0.0001 < np.sum(logical_array) < rad_field_area * 0.05


def is_round(rprops):
    """Decide if the ROI is circular in nature by testing the filled area vs bounding box. Used to find the BB."""
    expected_fill_ratio = np.pi / 4  # area of a circle inside a square
    actual_fill_ratio = rprops.filled_area / rprops.bbox_area
    return expected_fill_ratio * 1.2 > actual_fill_ratio > expected_fill_ratio * 0.8

def get_regions(slice_or_arr, fill_holes=False, clear_borders=True, threshold='otsu'):
    """Get the skimage regions of a black & white image."""
    if threshold == 'otsu':
        thresmeth = filters.threshold_otsu
    elif threshold == 'mean':
        thresmeth = np.mean
    edges = filters.scharr(slice_or_arr.astype(np.float))
    edges = filters.gaussian(edges, sigma=1)

    thres = thresmeth(edges)
    bw = edges > thres
    if clear_borders:
        segmentation.clear_border(bw, buffer_size=int(max(bw.shape)/50), in_place=True)
    if fill_holes:
        bw = ndimage.binary_fill_holes(bw)
    labeled_arr, num_roi = measure.label(bw, return_num=True)
    regionprops = measure.regionprops(labeled_arr, edges)
    return labeled_arr, regionprops, num_roi


def _find_bb(img, rad_field_bounding_box):
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

            if num_roi != 3:  # if not background, field, and 2 BBs
                raise ValueError
            
            bw_bb_img1 = np.where(labeled_arr == np.argsort(roi_sizes)[-3], 1, 0)  
            bw_bb_img1 = ndimage.binary_fill_holes(bw_bb_img1).astype(int)
            bb_regionprops1 = measure.regionprops(bw_bb_img1)[0]
            
            bw_bb_img2 = np.where(labeled_arr == np.argsort(roi_sizes)[-4], 1, 0)  
            bw_bb_img2 = ndimage.binary_fill_holes(bw_bb_img2).astype(int) 
            bb_regionprops2 = measure.regionprops(bw_bb_img2)[0]
    
            if not is_round(bb_regionprops1) and not is_round(bb_regionprops2):
                raise ValueError
            if not is_modest_size(bw_bb_img1, rad_field_bounding_box) and not is_modest_size(bw_bb_img2, rad_field_bounding_box):
                raise ValueError
            if not is_symmetric(bw_bb_img1) and not is_symmetric(bw_bb_img2):
                raise ValueError
        
        except (IndexError, ValueError):
            max_thresh -= 0.05 * spread
            if max_thresh < hmin or iteration > 50:
                raise ValueError("Unable to locate the two BBs. Make sure the BBs are located within the field away from field edges and that there is no significant noise or artifact in the image.")
        else:
            found = True
        iteration += 1
    
    # determine the center of mass of the BB
    inv_img = image.load(img.array)
    # we invert so BB intensity increases w/ attenuation
    inv_img.check_inversion_by_histogram(percentiles=(99.99, 50, 0.01))
    bb_rprops1 = measure.regionprops(bw_bb_img1, intensity_image=inv_img)[0]
    bb_rprops2 = measure.regionprops(bw_bb_img2, intensity_image=inv_img)[0]
    return [[[bb_rprops1.weighted_centroid[1], bb_rprops1.weighted_centroid[0]], bw_bb_img1],
            [[bb_rprops2.weighted_centroid[1], bb_rprops2.weighted_centroid[0]], bw_bb_img2]]


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
    
    if num_roi < 3:
        raise ValueError("Unable to locate the two BBs. Make sure the BBs are located within the field "
                         "away from field edges and that there is no significant noise or artifact in "
                         "the image. The field must not cover the whole image.")
    elif num_roi >= 3:
        regionprops = sorted(regionprops, key=lambda x: x.filled_area, reverse=True)[1:3]

    sorted_regions = sorted(regionprops, key=lambda x: (x.centroid[1]))
    
    centers = [(r.weighted_centroid[1], r.weighted_centroid[0]) for r in sorted_regions]
    roi_sizes, bin_edges = np.histogram(labeled_arr, bins=num_roi + 1)
    bw_bb_img1 = np.where(labeled_arr == np.argsort(roi_sizes)[-4], 1, 0)  
    bw_bb_img1 = ndimage.binary_fill_holes(bw_bb_img1).astype(int)
    bw_bb_img2 = np.where(labeled_arr == np.argsort(roi_sizes)[-3], 1, 0)  
    bw_bb_img2 = ndimage.binary_fill_holes(bw_bb_img1).astype(int)
    return [[centers[0], bw_bb_img1], [centers[1], bw_bb_img2]]


def fill_BB_hole(bb_coord, bw_bb_im, im_array):
    # Calculate the average value of pixels around the BB. This is used to 
    # fill the hole where the BB is located. So as not to get problems when
    # calculating profiles
    bb_radius = np.sqrt(np.sum(bw_bb_im)/np.pi) + 7 + 2  # Add 5 to get away from the gradient
    ne = profile.CollapsedCircleProfile(center=geometry.Point(x=bb_coord[0], y=bb_coord[1]), radius=bb_radius, 
                                        width_ratio=0.1, image_array=im_array)
    #ne.plot2axes()
    bb_avg = np.average(ne._profile)
    im_array[bw_bb_im==1] = bb_avg
    return


def find_penumbra_points(direction, num_profiles, field_corners, margin, im_array):
    # Careful! x and y are in different order within the field_corners array
    p_left = []
    p_right = []
    if direction=="X":
        field_corners_order = np.argsort(field_corners[:, 0])
        field_corners = field_corners[field_corners_order]
        y1, x1 = field_corners[0]
        y4, x4 = field_corners[3]
        if field_corners[1, 1] < field_corners[2, 1]:
            y2, x2 = field_corners[1]
            y3, x3 = field_corners[2]
        else:
            y2, x2 = field_corners[2]
            y3, x3 = field_corners[1]
        
        a = y2 - y1  # Y direction upper distance
        b = y4 - y2  # Y direction lower distance
        if a >= b:
            samples_left = np.arange(y1+margin, y2-margin, int((y2-y1-2*margin)/num_profiles))
            samples_right = np.arange(y3+margin, y4-margin, int((y4-y3-2*margin)/num_profiles))
        else:
            samples_left = np.arange(y2+margin, y4-margin, int((y4-y2-2*margin)/num_profiles))
            samples_right = np.arange(y1+margin, y3-margin, int((y3-y1-2*margin)/num_profiles))

        for a in samples_left:
            sp = profile.SingleProfile(im_array[a, :])
            sp.filter()
            sp.ground()
            #sp.plot()
            p_left.append(sp._penumbra_point(side="left", x=50, interpolate=True))  # left or bottom
            
        for a in samples_right:
            sp = profile.SingleProfile(im_array[a, :])
            sp.filter()
            sp.ground()
            p_right.append(sp._penumbra_point(side="right", x=50, interpolate=True))  # left or bottom
    else:
        # If in Y direction
        field_corners_order = np.argsort(field_corners[:, 1])
        field_corners = field_corners[field_corners_order]
        y1, x1 = field_corners[0]
        y4, x4 = field_corners[3]
        if field_corners[1, 0] < field_corners[2, 0]:
            y2, x2 = field_corners[1]
            y3, x3 = field_corners[2]
        else:
            y2, x2 = field_corners[2]
            y3, x3 = field_corners[1]
        
        a = x2 - x1  # Y direction upper distance
        b = x4 - x2  # Y direction lower distance
        if a >= b:
            samples_left = np.arange(x1+margin, x2-margin, int((x2-x1-2*margin)/num_profiles))
            samples_right = np.arange(x3+margin, x4-margin, int((x4-x3-2*margin)/num_profiles))
        else:
            samples_left = np.arange(x2+margin, x4-margin, int((x4-x2-2*margin)/num_profiles))
            samples_right = np.arange(x1+margin, x3-margin, int((x3-x1-2*margin)/num_profiles))
        
        for a in samples_left:
            sp = profile.SingleProfile(im_array[:, a])
            sp.filter()
            sp.ground()
            p_left.append(sp._penumbra_point(side="left", x=50, interpolate=True))  # left or bottom
        for a in samples_right:
            sp = profile.SingleProfile(im_array[:, a])
            sp.filter()
            sp.ground()
            p_right.append(sp._penumbra_point(side="right", x=50, interpolate=True))  # left or bottom
    return samples_left, samples_right, p_left, p_right

def calculate_regression(x, y, pmin, pmax):
    x = np.asarray(x)
    y = np.asarray(y)
    if np.abs(np.std(y)/np.std(x)) > 5:
        k, n,_,_,_ = scipy_linregress(y, x)
        swap = True
    else:
        k, n,_,_,_ = scipy_linregress(x, y)
        swap = False
    if swap:
        return 1/k, [[pmin*k+n, pmax*k+n], [pmin, pmax]], (k*y+n)-x
    else:
        return k, [[pmin, pmax], [pmin*k+n, pmax*k+n]], (k*x+n)-y
            
            