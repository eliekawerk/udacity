
import cv2
import numpy as np

from utils.histogram_utils import *

def detect_lane_along_poly(img, poly, steps):
    """
    slide a window along a polynomial and select all pixels inside.
    :param img: binary image
    :param poly: polynomial to follow
    :param steps: number of steps for the sliding window
    :return: x, y of detected pixels
    """
    pixels_per_step = img.shape[0] // steps
    all_x = []
    all_y = []

    for i in range(steps):
        start = img.shape[0] - (i * pixels_per_step)
        end = start - pixels_per_step

        center = (start + end) // 2
        x = poly(center)

        x, y = get_pixel_in_window(img, x, center, pixels_per_step)

        all_x.extend(x)
        all_y.extend(y)

    return all_x, all_y

def calculate_lane_area(lanes, area_height, steps):
    """
    return a list of pixel coordinates marking the area between two lanes
    :param lanes: Tuple of Lines. Expects the line polynomials to be a function of y.
    :param area_height:
    :param steps:
    :return:
    """
    points_left = np.zeros((steps + 1, 2))
    points_right = np.zeros((steps + 1, 2))

    for i in range(steps + 1):
        pixels_per_step = area_height // steps
        start = area_height - i * pixels_per_step

        points_left[i] = [lanes[0].best_fit_poly(start), start]
        points_right[i] = [lanes[1].best_fit_poly(start), start]

    return np.concatenate((points_left, points_right[::-1]), axis=0)

def are_lanes_plausible(lane_one, lane_two, parallel_thresh=(0.0003, 0.55), dist_thresh=(350, 460)):
    """
    check if two lines are plausible lanes by comparing the curvature and distance.
    :param lane_one:
    :param lane_two:
    :param parallel_thresh: Tuple of float values representing the delta threshold for the
    first and second coefficient of the polynomials.
    :param dist_thresh: Tuple of integer values marking the lower and upper threshold
    for the distance between plausible lanes.
    :return:
    """
    is_parallel = lane_one.is_current_fit_parallel(lane_two, threshold=parallel_thresh)
    dist = lane_one.get_current_fit_distance(lane_two)
    is_plausible_dist = dist_thresh[0] < dist < dist_thresh[1]

    return is_parallel & is_plausible_dist

def draw_poly(img, poly, steps, color, thickness=10, dashed=False):
    """
    draw a polynomial onto an image. used to draw lines on sides of lane area
    :param img:
    :param poly:
    :param steps:
    :param color:
    :param thickness:
    :param dashed:
    :return:
    """
    img_height = img.shape[0]
    pixels_per_step = img_height // steps

    for i in range(steps):
        start = i * pixels_per_step
        end = start + pixels_per_step

        start_point = (int(poly(start)), start)
        end_point = (int(poly(end)), end)

        if dashed is False or i % 2 == 1:
            img = cv2.line(img, end_point, start_point, color, thickness)

    return img

def calc_curvature(fit_cr):
    """
    calculate the curvature of a line in meters
    :param fit_cr:
    :return: radius of curvature in meters
    """

    # Define conversions in x and y from pixels space to meters
    ym_per_pix = 30 / 720  # meters per pixel in y dimension
    xm_per_pix = 3.7 / 700  # meteres per pixel in x dimension

    y = np.array(np.linspace(0, 719, num=10))
    x = np.array([fit_cr(x) for x in y])
    y_eval = np.max(y)

    fit_cr = np.polyfit(y * ym_per_pix, x * xm_per_pix, 2)

    curverad = ((1 + (2 * fit_cr[0] * y_eval + fit_cr[1]) ** 2) ** 1.5) / np.absolute(2 * fit_cr[0])

    return curverad