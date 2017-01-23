# Advanced Lane Finding

The goal of this project is to detect lane lines on videos through advance techniques such as color transforms, gradients, perspective transform and fitting polynomial. 

---

## Result

The following videos show the final results of the lanes being detected on three different tracks with varying difficulty:

Project Track                 |Challenge Track                |Harder Challenge Track                    
:----------------------------:|:-----------------------------:|:------------------------------:
[![Track 1](output_images/project_track.png)](https://youtu.be/9OrWgTO0ZbY) | [![Track 2](output_images/challenge_track.png)](https://youtu.be/2cPPiAE76mk) | [![Track 3](output_images/harder_challenge_track.png)](https://youtu.be/L_QP8J84Jj8)


The steps of this project are the following:

* Compute the camera calibration matrix and distortion coefficients given a set of chessboard images.
* Apply a distortion correction to raw images.
* Use color transforms, gradients, etc., to create a thresholded binary image.
* Apply a perspective transform to rectify binary image ("birds-eye view").
* Detect lane pixels and fit to find the lane boundary.
* Determine the curvature of the lane and vehicle position with respect to center.
* Warp the detected lane boundaries back onto the original image.
* Output visual display of the lane boundaries and numerical estimation of lane curvature and vehicle position.



## Rubric Points

Here I will consider the rubric points individually and describe how I addressed each point in my implementation.  

### Camera Calibration

Images or videos captured by a camera are typically distorted by the lens. Using a image like that would cause problems when trying to calculate the curvature or the car's offset to the center line. That's why it is important to undistort images first. For that a distortion matrix is calculated based on several images of a chessboard captured by the same camera. The matrix can then be used to undistort other images.

The code for this step is contained in [camera_calibrator.py](https://github.com/srikanthpagadala/udacity/blob/master/Self-Driving%20Car%20Engineer%20Nanodegree/AdvancedLaneLines-P4/source_code/camera_calibrator.py)

I start by preparing "object points", which will be the (x, y, z) coordinates of the chessboard corners in the world. Here I am assuming the chessboard is fixed on the (x, y) plane at z=0, such that the object points are the same for each calibration image.  Thus, `objp` is just a replicated array of coordinates, and `objpoints` will be appended with a copy of it every time I successfully detect all chessboard corners in a test image.  `imgpoints` will be appended with the (x, y) pixel position of each of the corners in the image plane with each successful chessboard detection.  

I then used the output `objpoints` and `imgpoints` to compute the camera calibration and distortion coefficients using the `cv2.calibrateCamera()` function.  I applied this distortion correction to the test image using the `cv2.undistort()` function and obtained this result: 

![camera_calibrated](output_images/camera_calibrated.png)

### Pipeline 

Let us now go over individual steps of lane detection pipeline.

#### Distortion Correction

The code for this step is contained in [camera_calibrator.py](https://github.com/srikanthpagadala/udacity/blob/master/Self-Driving%20Car%20Engineer%20Nanodegree/AdvancedLaneLines-P4/source_code/camera_calibrator.py). Camera images are calibrated in the function `calibrate_camera()` (lines 77 through 111) using provided chessboard images. Then frames from the car videos are corrected by applying the calculated distortion matrix in `undistort()` (lines 32 through 36) function. 

![distortion_corrected](output_images/distortion_corrected.png)

#### Lane Mask Generation

The code for Lane Mask Generation is contained in [mask_generator.py](https://github.com/srikanthpagadala/udacity/blob/master/Self-Driving%20Car%20Engineer%20Nanodegree/AdvancedLaneLines-P4/source_code/mask_generator.py). It combines various techniques like sobel operations, color transforms, gradients, color extraction and noise reduction to generate an image mask that can later be used to extract lane pixels from a given video frame. Through a lot of trial and error, various thresholds are chosen. `generate_lane_mask()` function in lines 113 through 147 is the entry point. It makes use of other helper functions in the same file to generate the combined mask image. 

![combined_mask](output_images/combined_mask.png)

#### Perspective Transformation

The code for my perspective transform includes a function called `transform()`, which appears in lines 30 through 31 in the file [perspective_transformer.py](https://github.com/srikanthpagadala/udacity/blob/master/Self-Driving%20Car%20Engineer%20Nanodegree/AdvancedLaneLines-P4/source_code/perspective_transformer.py).  The `transform()` function takes as inputs an image (`img`), as well as source (`src`) and destination (`dst`) points.  Through experimentation, I chose to hardcode the source and destination points in the following manner:

```
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
```

I verified that my perspective transform was working as expected by drawing the `src` and `dst` points onto a test image and its warped counterpart to verify that the lines appear parallel in the warped image.

![perspective_transformed](output_images/perspective_transformed.png)

#### Pixel Histogram Analysis

The code for this step is contained in [histogram_utils.py](https://github.com/srikanthpagadala/udacity/blob/master/Self-Driving%20Car%20Engineer%20Nanodegree/AdvancedLaneLines-P4/source_code/utils/histogram_utils.py)

#### Polynomial Fitting

The code for this step is contained in [lane_utils.py](https://github.com/srikanthpagadala/udacity/blob/master/Self-Driving%20Car%20Engineer%20Nanodegree/AdvancedLaneLines-P4/source_code/utils/lane_utils.py)

![polygon_marked](output_images/polygon_marked.png)

#### Final Step: Overlay & Inverse Transformation

![lane_found](output_images/lane_found.png)


####1. Provide an example of a distortion-corrected image.
To demonstrate this step, I will describe how I apply the distortion correction to one of the test images like this one:
![alt text][image2]
####2. Describe how (and identify where in your code) you used color transforms, gradients or other methods to create a thresholded binary image.  Provide an example of a binary image result.
I used a combination of color and gradient thresholds to generate a binary image (thresholding steps at lines # through # in `another_file.py`).  Here's an example of my output for this step.  (note: this is not actually from one of the test images)

![alt text][image3]

---

###Pipeline (video)

####1. Provide a link to your final video output.  Your pipeline should perform reasonably well on the entire project video (wobbly lines are ok but no catastrophic failures that would cause the car to drive off the road!).

Here's a [link to my video result](./project_video.mp4)

---

###Discussion

####1. Briefly discuss any problems / issues you faced in your implementation of this project.  Where will your pipeline likely fail?  What could you do to make it more robust?

Here I'll talk about the approach I took, what techniques I used, what worked and why, where the pipeline might fail and how I might improve it if I were going to pursue this project further.  

