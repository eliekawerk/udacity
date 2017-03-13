from moviepy.video.io.VideoFileClip import VideoFileClip

from car_finder import CarFinder
from lane_finder import LaneFinder
import numpy as np
from sklearn.externals import joblib

short = "../videos/short_movie.mp4"
hard = "../videos/project_video.mp4"
harder = "../videos/challenge_video.mp4"

input_video = hard

def process_frame(frame, lane_finder, car_finder, ystart, ystop, scales, svc, X_scaler, 
                  orient, pix_per_cell, cell_per_block, spatial_size, hist_bins):
    
    frame_copy = np.copy(frame)
    
    frame_lane = lane_finder.process_frame(frame_copy)
    _ = car_finder.find_cars(frame_copy, ystart, ystop, scales, svc, X_scaler, 
                  orient, pix_per_cell, cell_per_block, spatial_size, hist_bins)
    
    car_finder.draw_detections(frame_lane)

    return frame_lane
    
if __name__ == '__main__':
    """
    driver code that processes each frame of a video to detect lanes and nearby cars and produces processed output video
    """
    
    # Configurations
    MODEL_FOLDER = '../gen'
    
    ystart = 400
    ystop = 656
    scales = [1.0, 1.5, 2.0]
    
    orient = 9  # HOG orientations
    pix_per_cell = 8  # HOG pixels per cell
    cell_per_block = 2  # HOG cells per block
    spatial_size = (32, 32)  # Spatial binning dimensions
    hist_bins = 32  # Number of histogram bins

    # load svm classifiers
    svc = joblib.load(MODEL_FOLDER + '/svc.pkl') 
    X_scaler = joblib.load(MODEL_FOLDER + '/x_scaler.pkl') 
    
    lane_finder = LaneFinder()
    car_finder = CarFinder()
    
    video_clip = VideoFileClip(input_video)
    processed_clip = video_clip.fl_image(lambda frame: process_frame(frame, lane_finder, car_finder,
                                                ystart, ystop, scales, svc, X_scaler, orient, pix_per_cell, 
                                                cell_per_block, spatial_size, hist_bins))

    # save video
    processed_clip.write_videofile(input_video[:-4] + '_processed.mp4', audio=False)
    
    print('Done')