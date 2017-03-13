import glob
import multiprocessing
import time

from joblib import Parallel
from joblib import delayed
from scipy.ndimage.measurements import label
from skimage.feature import hog
from skimage.feature import hog
from sklearn.model_selection import train_test_split
from sklearn.externals import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC

import cv2
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np

from feature_extractor import FeatureExtractor

# Finds cars in the given image by applying pretrained svm classifier over image in sliding window fashion on image pyramid
class CarFinder:
    
    def __init__(self):
        self.feature_extractor = FeatureExtractor()
        self.frames = 10 # num of frames to aggregate heatmaps over
        self.heatmaps = [] # collection of heatmaps over past 10 frames
        self.cummulative_heatmap = np.zeros((720, 1280)).astype(np.float64) # cummulative heat map over 10 frames
        
        self.cars_detected = 0 # count of cars detected in this frame
        self.contours_detected = [] 
    
    # function that find cars in the image
    def find_cars(self, img, ystart, ystop, scales, svc, X_scaler, orient, pix_per_cell, 
                  cell_per_block, spatial_size, hist_bins):
        
        bbox_list = self.predict_bboxes(img, ystart, ystop, scales, svc, X_scaler, orient, pix_per_cell, 
                                   cell_per_block, spatial_size, hist_bins)
        
        heatmap = self.predict_heatmap(img, bbox_list)

        draw_img = self.predict_contours(img, heatmap)
        return draw_img
    
    # draws detecton on the given image frame
    def draw_detections(self, img):
        
        for bbox in self.contours_detected:
             # Draw the box on the image
            cv2.rectangle(img, bbox[0], bbox[1], (0, 0, 255), 3)
            
        cv2.putText(img, 'Cars detected: %s' % self.cars_detected, (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
        return img
    
    # function that computes the heatmap of bounding boxes
    def predict_heatmap(self, image, bbox_list, threshold=1):
        heat = np.zeros_like(image[:, :, 0]).astype(np.float)
        # Add heat to each box in box list
        heat = self.add_heat(heat, bbox_list)
            
        # Apply threshold to help remove false positives
        heat = self.apply_threshold(heat, threshold)
        
        # Visualize the heatmap when displaying    
        heatmap = np.clip(heat, 0, 255)
        
        # accumulate heatmaps for 10 frames. Makes smooth/accurate bounding boxes
        self.heatmaps.append(heatmap)
        self.cummulative_heatmap = self.cummulative_heatmap + heatmap
        if len(self.heatmaps) > self.frames:
            self.cummulative_heatmap = self.cummulative_heatmap - self.heatmaps.pop(0)
            self.cummulative_heatmap = np.clip(self.cummulative_heatmap, 0.0, 9999999.0)
        
        return self.cummulative_heatmap
        
    # function that draws the contour around the detected hot blob
    def predict_contours(self, image, heatmap):
        # Find final boxes from heatmap using label function
        labels = label(heatmap)
        draw_img = self.draw_labeled_bboxes(np.copy(image), labels)
        
        return draw_img
        
    # for each positive detection bounding box, add to the heatmap
    def add_heat(self, heatmap, bbox_list):
        # Iterate through list of bboxes
        for box in bbox_list:
            # Add += 1 for all pixels inside each bbox
            # Assuming each "box" takes the form ((x1, y1), (x2, y2))
            heatmap[box[0][1]:box[1][1], box[0][0]:box[1][0]] += 1
    
        # Return updated heatmap
        return heatmap  # Iterate through list of bboxes
        
    # threshold the heatmap to eliminate false positives
    def apply_threshold(self, heatmap, threshold):
        # Zero out pixels below the threshold
        heatmap[heatmap <= threshold] = 0
        # Return thresholded map
        return heatmap
    
    # find the bounding boxes of car in the image by using svm classifier over image pyramid
    def predict_bboxes(self, img, ystart, ystop, scales, svc, X_scaler, orient, pix_per_cell, 
                       cell_per_block, spatial_size, hist_bins, vis=False):
        
        xstart = img.shape[1] // 2
        xstop = img.shape[1]
             
        bbox_list = []  # box" takes the form ((x1, y1), (x2, y2))
        for scale in scales:
            bboxes = self.scan_image_pyramid(img, ystart, ystop, xstart, xstop, scale, svc, X_scaler, orient, pix_per_cell, 
                                        cell_per_block, spatial_size, hist_bins)
            bbox_list.extend(bboxes)
           
        if vis == True:
            draw_img = np.copy(img)
            for bbox in bbox_list:
                cv2.rectangle(draw_img, (bbox[0][0], bbox[0][1]), (bbox[1][0], bbox[1][1]), (0, 0, 255), 6)
            return draw_img, bbox_list
        else:
            return bbox_list
        
    # function that find the bounding boxes for detected cars
    def scan_image_pyramid(self, img, ystart, ystop, xstart, xstop, scale, svc, X_scaler, orient, pix_per_cell, 
                           cell_per_block, spatial_size, hist_bins, vis=False):
    
        draw_img = np.copy(img)
        img = img.astype(np.float32) / 255
        
        img_tosearch = img[ystart:ystop, xstart:xstop, :]
        ctrans_tosearch = cv2.cvtColor(img_tosearch, cv2.COLOR_RGB2YCrCb)
        if scale != 1:
            imshape = ctrans_tosearch.shape
            ctrans_tosearch = cv2.resize(ctrans_tosearch, (np.int(imshape[1] / scale), np.int(imshape[0] / scale)))
            
        ch1 = ctrans_tosearch[:, :, 0]
        ch2 = ctrans_tosearch[:, :, 1]
        ch3 = ctrans_tosearch[:, :, 2]
    
        # Define blocks and steps as above
        nxblocks = (ch1.shape[1] // pix_per_cell) - 1
        nyblocks = (ch1.shape[0] // pix_per_cell) - 1 
        
        # 64 was the orginal sampling rate, with 8 cells and 8 pix per cell
        window = 64
        nblocks_per_window = (window // pix_per_cell) - 1 
        cells_per_step = 2  # Instead of overlap, define how many cells to step
        nxsteps = (nxblocks - nblocks_per_window) // cells_per_step
        nysteps = (nyblocks - nblocks_per_window) // cells_per_step
        
        # Compute individual channel HOG features for the entire image
        hog1 = self.feature_extractor.get_hog_features(ch1, orient, pix_per_cell, cell_per_block, feature_vec=False)
        hog2 = self.feature_extractor.get_hog_features(ch2, orient, pix_per_cell, cell_per_block, feature_vec=False)
        hog3 = self.feature_extractor.get_hog_features(ch3, orient, pix_per_cell, cell_per_block, feature_vec=False)
        
        bbox_list = []  # box" takes the form ((x1, y1), (x2, y2))
        for xb in range(nxsteps):
            for yb in range(nysteps):
                ypos = yb * cells_per_step
                xpos = xb * cells_per_step
                # Extract HOG for this patch
                hog_feat1 = hog1[ypos:ypos + nblocks_per_window, xpos:xpos + nblocks_per_window].ravel() 
                hog_feat2 = hog2[ypos:ypos + nblocks_per_window, xpos:xpos + nblocks_per_window].ravel() 
                hog_feat3 = hog3[ypos:ypos + nblocks_per_window, xpos:xpos + nblocks_per_window].ravel() 
                hog_features = np.hstack((hog_feat1, hog_feat2, hog_feat3))
                
                xleft = xpos * pix_per_cell
                ytop = ypos * pix_per_cell
    
                # Extract the image patch
                subimg = cv2.resize(ctrans_tosearch[ytop:ytop + window, xleft:xleft + window], (64, 64))
              
                # Get color features
                spatial_features = self.feature_extractor.bin_spatial(subimg, size=spatial_size)
                hist_features = self.feature_extractor.color_hist(subimg, nbins=hist_bins)
    
                # Scale features and make a prediction
                test_features = X_scaler.transform(np.hstack((spatial_features, hist_features, hog_features)).reshape(1, -1))
                test_prediction = svc.predict(test_features)
                
                if test_prediction == 1:
                    xbox_left = np.int(xleft * scale)
                    ytop_draw = np.int(ytop * scale)
                    win_draw = np.int(window * scale)
                    # cv2.rectangle(draw_img, (xbox_left + xstart, ytop_draw + ystart), (xbox_left + win_draw + xstart, ytop_draw + win_draw + ystart), (0, 0, 255), 6) 
                    bbox_list.append(((xbox_left + xstart, ytop_draw + ystart), (xbox_left + win_draw + xstart, ytop_draw + win_draw + ystart)))
                 
                if vis == True:
                    xbox_left = np.int(xleft * scale)
                    ytop_draw = np.int(ytop * scale)
                    win_draw = np.int(window * scale)
                    cv2.rectangle(draw_img, (xbox_left + xstart, ytop_draw + ystart), (xbox_left + win_draw + xstart, ytop_draw + win_draw + ystart), (0, 0, 255), 2)
             
        if vis == True:
            return draw_img, bbox_list
        else:
            return bbox_list
    
    # draw the contour line around the detected hot blobs
    def draw_labeled_bboxes(self, img, labels):
        
        self.cars_detected = labels[1]# count of cars detected in this frame
        self.contours_detected = [] 
        
        # Iterate through all detected cars
        for car_number in range(1, labels[1] + 1):
            # Find pixels with each car_number label value
            nonzero = (labels[0] == car_number).nonzero()
            # Identify x and y values of those pixels
            nonzeroy = np.array(nonzero[0])
            nonzerox = np.array(nonzero[1])
            # Define a bounding box based on min/max x and y
            bbox = ((np.min(nonzerox), np.min(nonzeroy)), (np.max(nonzerox), np.max(nonzeroy)))
            
            # Draw the box on the image
            cv2.rectangle(img, bbox[0], bbox[1], (0, 0, 255), 3)
            
            self.contours_detected.append(bbox)
        # Return the image
        return img
