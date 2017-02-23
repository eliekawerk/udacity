from scipy.misc import imresize, imread

import cv2
import numpy as np
from utils.plot_utils import *

# we can guess these cooridnates from ticks mark in img plots.
OFFSET = 250

PERSPECTIVE_SRC = np.float32([
                    (132, 703),
                    (540, 466),
                    (740, 466),
                    (1147, 703)])

PERSPECTIVE_DST = np.float32([
                    (PERSPECTIVE_SRC[0][0] + OFFSET, 720),
                    (PERSPECTIVE_SRC[0][0] + OFFSET, 0),
                    (PERSPECTIVE_SRC[-1][0] - OFFSET, 0),
                    (PERSPECTIVE_SRC[-1][0] - OFFSET, 720)])

class PerspectiveTransformer:
    def __init__(self):
        """
        Transform the perspective of an image
        """
        self.M = cv2.getPerspectiveTransform(PERSPECTIVE_SRC, PERSPECTIVE_DST)
        self.M_inv = cv2.getPerspectiveTransform(PERSPECTIVE_DST, PERSPECTIVE_SRC)

    def transform(self, img):
        return cv2.warpPerspective(img, self.M, (img.shape[1], img.shape[0]), flags=cv2.INTER_LINEAR)

    def inverse_transform(self, img):
        return cv2.warpPerspective(img, self.M_inv, (img.shape[1], img.shape[0]), flags=cv2.INTER_LINEAR)

# quick unittest     
if __name__ == '__main__':
    
    perspective_transformer = PerspectiveTransformer()
    
    images_left = []
    images_right = []
    
    test_images = ["../test_images/straight_lines2.jpg", "../test_images/test5.jpg"]
    
    for image in test_images:
        image = imread(image)
        
        a = tuple(PERSPECTIVE_SRC[0])
        b = tuple(PERSPECTIVE_SRC[1])
        c = tuple(PERSPECTIVE_SRC[2])
        d = tuple(PERSPECTIVE_SRC[3])

        # draw lines
        color=[0, 255, 255]
        thickness=3
        cv2.line(image, a, b, color, thickness)
        cv2.line(image, b, c, color, thickness)
        cv2.line(image, c, d, color, thickness)
        cv2.line(image, d, a, color, thickness)

        transformed = perspective_transformer.transform(image)
        images_left.append(image)
        images_right.append(transformed)
    
    plot_side_by_side_images(images_left, images_right, 'Original', 'Perspective Transformed', '../output_images/perspective_transformed.png')
   
    print('Done')
