from glob import glob
from os.path import isfile
import pickle

from scipy.misc import imresize, imread
from tqdm import tqdm

import cv2
import numpy as np

from utils.plot_utils import *


nx = 9  # the number of inside corners in x direction on chessboard
ny = 6  # the number of inside corners in y direction on chessboard

STD_IMG_SIZE = (720, 1280, 3)
CHESSBOARD_IMAGES = '../camera_cal/calibration*.jpg'
SAVE_PATH = '../camera_cal/camera_calibration.p'

class CameraCalibrator:

    def __init__(self):
        
        # if needed, calibrate camera
        if not isfile(SAVE_PATH):
            self.calibrate_camera()  
            
        # preload camera calibration and be ready
        self.load_calibration()  

    def undistort(self, img):
        """
        undistort a given image using pre computed camera calibrations 
        """
        return cv2.undistort(img, self.mtx, self.dist, None, self.mtx)
 
    def load_calibration(self):
        """
        load pickled camera calibrations 
        """
        
        with open(SAVE_PATH, "rb") as f:
            calibration = pickle.load(f)
            
        self.objpoints = calibration['objpoints']
        self.imgpoints = calibration['imgpoints']
        self.mtx = calibration['mtx']
        self.dist = calibration['dist']
        

    def save_calibration(self):
        """
        pickle computed camera calibrations to avoid repeated calculations
        """
        
        # Do camera calibration given object points and image points
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(self.objpoints, self.imgpoints, STD_IMG_SIZE[:-1], None, None)
    
        calibration = {'objpoints': self.objpoints,
                       'imgpoints': self.imgpoints,
                       'mtx': mtx,
                       'dist': dist,
                       'rvecs': rvecs,
                       'tvecs': tvecs}
        
        # save
        with open(SAVE_PATH, 'wb') as f:
            pickle.dump(calibration, file=f)
            
        print("camera calibrations saved")
        
    def calibrate_camera(self):
        """
        calibrates camera using chessboard images.
        """
        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
        objp = np.zeros((nx * ny, 3), np.float32)
        objp[:, :2] = np.mgrid[0:nx, 0:ny].T.reshape(-1, 2)

        # Arrays to store object points and image points from all the images.
        self.objpoints = []  # 3d points in real world space
        self.imgpoints = []  # 2d points in image plane.

        # Make a list of calibration images
        images = glob(CHESSBOARD_IMAGES)
    
        processed_count = 0
        
        # Step through the list and search for chessboard corners
        for idx, fname in enumerate(tqdm(images, desc='Calibrating images')):
            
            img = imread(fname)
            
            if img.shape[0] != STD_IMG_SIZE[0] or img.shape[1] != STD_IMG_SIZE[1]:
                img = imresize(img, STD_IMG_SIZE)
    
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            
            # Find the chessboard corners
            ret, corners = cv2.findChessboardCorners(gray, (nx, ny), None)
    
            if ret == True:
                self.objpoints.append(objp)
                self.imgpoints.append(corners)
                processed_count += 1
        
        print("Calibrated {}/{} images".format(processed_count, len(images)))
    
        # pickle computed calibrations
        self.save_calibration()
   
# quick unittest     
if __name__ == '__main__':
    
    camera_calibrator = CameraCalibrator()
    
    images_left = []
    images_right = []
    
    test_images = ["../camera_cal/calibration1.jpg", "../test_images/test5.jpg"]
    
    for image in test_images:
        image = imread(image)
        undistort = camera_calibrator.undistort(image)
        images_left.append(image)
        images_right.append(undistort)
    
    plot_side_by_side_images(images_left, images_right, 'Original', 'Undistorted', '../output_images/camera_calibrated.png')
   
    print('Done')

