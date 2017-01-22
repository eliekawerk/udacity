from moviepy.video.io.VideoFileClip import VideoFileClip

from lane_finder import LaneFinder

harder = "../videos/harder_challenge_video.mp4"
easy = "../videos/project_video.mp4"
hard = "../videos/challenge_video.mp4"

input_video = harder

if __name__ == '__main__':
    """
    driver code that processes each frame of a video to detect lanes and produces processed output video
    """
    lane_finder = LaneFinder()
    
    video_clip = VideoFileClip(input_video)
    processed_clip = video_clip.fl_image(lane_finder.process_frame)

    # save video
    processed_clip.write_videofile(input_video[:-4] + '_processed.mp4', audio=False)
    
    print('Done')