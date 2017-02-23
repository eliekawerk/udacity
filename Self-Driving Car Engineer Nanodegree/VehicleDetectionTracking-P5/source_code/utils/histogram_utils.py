from scipy import signal

import cv2
import numpy as np

def histogram_lane_detection(img, steps, search_window, h_window):
    """
    try to detect lane line pixels by applying a sliding histogram.
    :param img: binary image
    :param steps: steps for the sliding histogram
    :param search_window: Tuple which limits the horizontal search space.
    :param h_window: window size for horizontal histogram smoothing
    :return: x, y of detected pixels
    """
    all_x = []
    all_y = []
    masked_img = img[:, search_window[0]:search_window[1]]
    pixels_per_step = img.shape[0] // steps

    for i in range(steps):
        start = masked_img.shape[0] - (i * pixels_per_step)
        end = start - pixels_per_step
        histogram = np.sum(masked_img[end:start, :], axis=0)
        histogram_smooth = signal.medfilt(histogram, h_window)
        peaks = np.array(signal.find_peaks_cwt(histogram_smooth, np.arange(1, 5)))

        highest_peak = highest_n_peaks(histogram_smooth, peaks, n=1, threshold=5)
        if len(highest_peak) == 1:
            highest_peak = highest_peak[0]
            center = (start + end) // 2
            x, y = get_pixel_in_window(masked_img, highest_peak, center, pixels_per_step)

            all_x.extend(x)
            all_y.extend(y)

    all_x = np.array(all_x) + search_window[0]
    all_y = np.array(all_y)

    return all_x, all_y

def highest_n_peaks(histogram, peaks, n=2, threshold=0):
    """
    return the n highest peaks of a histogram above a given threshold.
    :param histogram:
    :param peaks: list of peak indexes
    :param n: number of peaks to select
    :param threshold:
    :return:
    """
    if len(peaks) == 0:
        return []

    peak_list = [(peak, histogram[peak]) for peak in peaks if histogram[peak] > threshold]
    peak_list = sorted(peak_list, key=lambda x: x[1], reverse=True)

    if len(peak_list) == 0:
        return []

    x, y = zip(*peak_list)
    x = list(x)

    if len(peak_list) < n:
        return x

    return x[:n]

def get_pixel_in_window(img, x_center, y_center, size):
    """
    return selected pixel inside a window.
    :param img: binary image
    :param x_center: x coordinate of the window center
    :param y_center: y coordinate of the window center
    :param size: size of the window in pixel
    :return: x, y of detected pixels
    """
    half_size = size // 2
    window = img[y_center - half_size:y_center + half_size, x_center - half_size:x_center + half_size]

    x, y = (window.T == 1).nonzero()

    x = x + x_center - half_size
    y = y + y_center - half_size

    return x, y
