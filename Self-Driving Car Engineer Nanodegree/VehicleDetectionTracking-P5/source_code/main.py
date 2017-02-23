from moviepy.video.io.VideoFileClip import VideoFileClip

from car_finder import CarFinder
from lane_finder import LaneFinder
import numpy as np

short = "../videos/short_movie.mp4"
hard = "../videos/project_video.mp4"
harder = "../videos/challenge_video.mp4"

input_video = short

def process_frame(frame, lane_finder, car_finder):
    
    frame_copy = np.copy(frame)
    
    frame_lane = lane_finder.process_frame(frame_copy)
    _ = car_finder.process_frame(frame_copy)
    
    car_finder.draw_info(frame_lane)

    return frame_lane
    
if __name__ == '__main__':
    """
    driver code that processes each frame of a video to detect lanes and nearby cars and produces processed output video
    """
    lane_finder = LaneFinder()
    car_finder = CarFinder()
    
    video_clip = VideoFileClip(input_video)
    processed_clip = video_clip.fl_image(lambda frame: process_frame(frame, lane_finder, car_finder))

    # save video
    processed_clip.write_videofile(input_video[:-4] + '_processed.mp4', audio=False)
    
    print('Done')