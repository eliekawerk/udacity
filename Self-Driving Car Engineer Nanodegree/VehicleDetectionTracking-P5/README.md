# Vehicle Detection and Tracking

In this project, the goal is to write a software pipeline to detect vehicles in a video.  

## Results

The following videos show the final results of the lanes being detected on two different tracks with varying difficulty:

Project Track                 |Challenge Track                                   
:----------------------------:|:-----------------------------:
[![Track 1](output_images/project_track.png)](https://youtu.be/x8kqF5M8idc) | [![Track 2](output_images/challenge_track.png)](https://youtu.be/MnQ2CQFppB4) 


The steps of this project are the following:

* Perform a Histogram of Oriented Gradients (HOG) feature extraction on a labeled training set of images and train a classifier Linear SVM classifier
* Apply a color transform and append binned color features, as well as histograms of color, to your HOG feature vector. 
* Normalize features and randomize a selection for training and testing.
* Implement a sliding-window technique and use trained classifier to search for vehicles in images.
* Run pipeline on a video stream and create a heat map of recurring detections frame by frame to reject outliers and follow detected vehicles.
* Estimate a bounding box for vehicles detected.

## Data

Here are links to the labeled data for [vehicle](https://s3.amazonaws.com/udacity-sdc/Vehicle_Tracking/vehicles.zip) and [non-vehicle](https://s3.amazonaws.com/udacity-sdc/Vehicle_Tracking/non-vehicles.zip) examples to train the classifier.  These example images come from a combination of the [GTI vehicle image database](http://www.gti.ssr.upm.es/data/Vehicle_database.html), the [KITTI vision benchmark suite](http://www.cvlibs.net/datasets/kitti/), and examples extracted from the project video itself. You are welcome and encouraged to take advantage of the recently released [Udacity labeled dataset](https://github.com/udacity/self-driving-car/tree/master/annotations) to augment your training data.  

## Notebooks

Project is implemented in two jupyter notebooks:

- [Train SVM Classifier](notebooks/Train SVM Classifier.ipynb) - Here cars data is processed and used to train a SVM classifier.
- [Vehicle Detection and Tracking](notebooks/Vehicle Detection and Tracking.ipynb) - Classifier trained above is used in sliding window fashion to detect and track cars in the given scene.

## Report

Here I will consider the rubric points individually and describe how I addressed each point in my implementation. 

### Histogram of Oriented Gradients (HOG)

The code for this step is contained in the 6th cell of the [Train SVM Classifier](notebooks/Train SVM Classifier.ipynb) notebook. `get_hog_features()` is implemented in [feature_extractor.py](source_code/detect_track/feature_extractor.py) (lines 22 through 39)

I started by reading in all the `vehicle` and `non-vehicle` images.  Here are examples of one of each of the `vehicle` and `non-vehicle` classes:

![](output_images/car_not-car.png)

I then explored different color spaces and different `skimage.hog()` parameters (`orientations`, `pixels_per_cell`, and `cells_per_block`). I grabbed random images from each of the two classes and displayed them to get a feel for what the `skimage.hog()` output looks like.

![](output_images/hog_features.png)

Here is an example using the `YUV` color space and HOG parameters of `orientations=8`, `pixels_per_cell=(4, 4)` and `cells_per_block=(2, 2)`. `color_hist()` is implemented in [feature_extractor.py](source_code/detect_track/feature_extractor.py) (lines 49 through 57)

![](output_images/color_histogram.png)

Here is an example showing image colors binned as features. `bin_spatial()` is implemented in [feature_extractor.py](source_code/detect_track/feature_extractor.py) (lines 42 through 46)

![](output_images/binned_color.png)

I tried various combinations of parameters and kept on iterating until my classifier achieved desired accuracy of **99.98%**. Following are the final configurations that I settled down to.

<pre>
# Configurations
color_space = 'YUV'  # Can be RGB, HSV, LUV, HLS, YUV, YCrCb
orient = 8  # HOG orientations
pix_per_cell = 4  # HOG pixels per cell
cell_per_block = 2  # HOG cells per block
hog_channel = 0  # Can be 0, 1, 2, or "ALL"
spatial_size = (32, 32)  # Spatial binning dimensions
hist_bins = 32  # Number of histogram bins
spatial_feat = True  # Spatial features on or off
hist_feat = True  # Histogram features on or off
hog_feat = True  # HOG features on or off
</pre>

Features thus extracted are very large in number. `Cars` and `Not-Cars` features are combined into a giant matrix and then standarized using `sklearn.StandardScaler()` so that features are scaled to zero mean and unit variance before training the classifier.

Since at this point the number of features are super large, I applied PCA reduction to the features. The code for this step is contained in the 10-12th cells of the [Train SVM Classifier](notebooks/Train SVM Classifier.ipynb) notebook. 

Then I randomized the dataset and partitioned it into training and testing set using `sklearn.train_test_split()`.

Finally, I trained a linear SVM using above configurations and PCA reduced features set. SVM training took 13seconds and achieved a Test Accuracy of 99.49%. Model is then saved to the disk for later use. 

###Sliding Window Search

The system was designed to allow the definition of multiple search areas, each with different stride, size, and padding. Each search area can be processed in a different thread to improve performance. The image below shows the used search areas. The code for this step is contained in [car_finder.py](source_code/car_finder.py) in functions `slide_window()` and `search_windows()`.

![](output_images/sliding_windows.png)

Following image shows positive predictions as returned by the our trained SVM classifier on the sliding window image patch.

![](output_images/prediction.png)

For each positive prediction, the value of the decision function is added onto a heatmap in the area of the bounding box. When processing a video the heatmap is averaged over 8 frames to smoothen resulting bounding boxes. To remove false positives the heatmap is then thresholded. ([car_finder.py](source_code/car_finder.py) in functions `process_frame()` and `apply_threshold()` lines 152-156).

![](output_images/heatmap.png)

There are multiple ways of generating bounding boxes out of a heat map. I used `scipy.label()` function to draw contours around the positive detection in the heatmap image. ([car_finder.py](source_code/car_finder.py) in function `process_frame()` line 288).

![](output_images/contours.png)


### Video Implementation

I recorded the positions of positive detections in each frame of the video.  From the positive detections I created a heatmap and then thresholded that map to identify vehicle positions.  I then used blob detection in Sci-kit Image to identify individual blobs in the heatmap. I then assumed each blob corresponded to a vehicle.  I constructed bounding boxes to cover the area of each blob detected.  

Here's an example result showing bounding boxes overlaid on a frame of video:

Project Track                 |Challenge Track                                   
:----------------------------:|:-----------------------------:
[![Track 1](output_images/project_track.png)](https://youtu.be/x8kqF5M8idc) | [![Track 2](output_images/challenge_track.png)](https://youtu.be/MnQ2CQFppB4) 


### Discussion

This was a bit tricky project. It involved a lot of trial and error in finding the right thresholds to make the pipeline work. There are so many hyper-parameters to tune that I think this approach is not very robust. Although, this mechanical approach finally worked out for first two videos, I have a suspicion that it may not work for real wild world. I think Neural Network based approach is fitting for this problem. In my next version, I'll try to find a Neural Network based solution.
 
