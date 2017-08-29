
from glob import glob
import os, math, cv2, shutil, collections, json
import numpy as np
from PIL import Image

SRC_DIR = "/home/ai/eclipse-workspace/image_2"
RUN_DIR = "/home/ai/eclipse-workspace/runs"
DST_DIR = SRC_DIR.replace("2", "3")
logo_fn = '/home/ai/Downloads/logo.png'

# load images
PATTERN = SRC_DIR + "/*.png"
source_images = list(glob(PATTERN))

processed_images = []

def add_logo(orig_frame):
    background = Image.fromarray(orig_frame)
    foreground = Image.open(logo_fn)
    background.paste(foreground, (10, orig_frame.shape[0] - 50), mask=foreground.split()[3])
    orig_frame = np.array(background.convert())
    return orig_frame

for source_image in source_images:
    
    
    image = cv2.imread(source_image)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, (576, 160)) 
    
    # run image
    run_image = source_image.replace(SRC_DIR, RUN_DIR)
    run_image = cv2.imread(run_image)
    run_image = cv2.cvtColor(run_image, cv2.COLOR_BGR2RGB)
    
    image = np.concatenate((image, run_image), axis=0)
    image = add_logo(image)
     
    # save
    fn = source_image.replace(SRC_DIR, "")
    cv2.imwrite(DST_DIR + "/" + fn, image)
    
    processed_images.append(image)

from moviepy.editor import VideoFileClip, ImageSequenceClip

def build_movie(files, movie_fn):
    clip = ImageSequenceClip(files, fps=10)
    clip.write_videofile(movie_fn)

movie_fn = '/home/ai/eclipse-workspace/movie.mp4'
build_movie(processed_images, movie_fn)
    
print("Done")