import matplotlib.image as mpimg
import numpy as np
import pandas as pd
import cv2
import os
import glob
from sklearn.svm import LinearSVC
from sklearn.preprocessing import StandardScaler
from skimage.feature import hog
from sklearn.model_selection import train_test_split

######################################################
### Helper method: Extract HOG features
######################################################
def read_image(image_path, new_img_rows, new_img_cols):
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (new_img_rows, new_img_cols))
    return img

def get_rand_image(image_paths, new_img_rows, new_img_cols):
    random_index = np.random.randint(len(image_paths))
    image_path = image_paths[random_index]
    return read_image(image_path, new_img_rows, new_img_cols)

def get_rand_image_from_df(df, new_img_rows, new_img_cols):
    random_index = np.random.randint(len(df))
    image_path = df.iloc[random_index]['image_path']
    return read_image(image_path, new_img_rows, new_img_cols)

# a function to return HOG features and visualization
def get_hog_features(img, orient=8, pix_per_cell=4, cell_per_block=2, vis=False, feature_vec=True):
    
    img = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
    
    # Call with two outputs if vis==True
    if vis == True:
        features, hog_image = hog(img, orientations=orient, pixels_per_cell=(pix_per_cell, pix_per_cell),
                                  cells_per_block=(cell_per_block, cell_per_block), transform_sqrt=True, 
                                  visualise=vis, feature_vector=feature_vec)
        return features, hog_image
    # Otherwise call with one output
    else:      
        features = hog(img, orientations=orient, pixels_per_cell=(pix_per_cell, pix_per_cell),
                       cells_per_block=(cell_per_block, cell_per_block), transform_sqrt=True, 
                       visualise=vis, feature_vector=feature_vec)
        return features

######################################################################## 
### Helper method: Extract color histogram features   
########################################################################
# a function to compute color histogram features  
def color_hist(img, cspace='RGB', nbins=32, bins_range=(0, 256)):
    
    if cspace != 'RGB':
        if cspace == 'HSV':
            img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        elif cspace == 'LUV':
            img = cv2.cvtColor(img, cv2.COLOR_RGB2LUV)
        elif cspace == 'HLS':
            img = cv2.cvtColor(img, cv2.COLOR_RGB2HLS)
        elif cspace == 'YUV':
            img = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)

    # Compute the histogram of the color channels separately
    channel1_hist = np.histogram(img[:,:,0], bins=nbins, range=bins_range)
    channel2_hist = np.histogram(img[:,:,1], bins=nbins, range=bins_range)
    channel3_hist = np.histogram(img[:,:,2], bins=nbins, range=bins_range)
    # Concatenate the histograms into a single feature vector
    hist_features = np.concatenate((channel1_hist[0], channel2_hist[0], channel3_hist[0]))
    # Return the individual histograms, bin_centers and feature vector
    return hist_features

###########################################################################
### Helper method: Compute binned color features
###########################################################################
# a function to compute binned color features  
def bin_spatial(img, size=(32, 32)):
    # Use cv2.resize().ravel() to create the feature vector
    features = cv2.resize(img, size).ravel() 
    # Return the feature vector
    return features

###########################################################################
### Helper method: Extract features from a list of images
###########################################################################
# a function to extract features from a list of images
# this function calls bin_spatial() and color_hist()
def extract_features(image):
    hist_features = color_hist(image, cspace='YUV')
    hog_features = get_hog_features(image, vis=False)
    spatial_features = bin_spatial(image)
    
    return  np.concatenate((hist_features, hog_features, spatial_features))

###########################################################################
### Apply PCA reduction
###########################################################################
from sklearn.decomposition import RandomizedPCA, PCA
def apply_pca_reduction(X):
    n_comp = 5000
    pca = PCA(n_components=n_comp, whiten=True)
    print('x:',X.shape)
    pca = pca.fit(X)
    pca_features = pca.transform(X)
    print('pca_features:',pca_features.shape)
    return pca, pca_features

###########################################################################
### Wrapper method: extract_features_and_apply_pca
###########################################################################
def extract_features_and_apply_pca(image_path, new_img_rows, new_img_cols, pca):

    img = read_image(image_path, new_img_rows, new_img_cols)
    features = extract_features(img)
    features = np.expand_dims(features, axis=0)
    pca_features = pca.transform(features)
    return pca_features

def extract_features_and_apply_pca2(img, new_img_rows, new_img_cols, pca):

    img = cv2.resize(img, (new_img_rows, new_img_cols))
    features = extract_features(img)
    features = np.expand_dims(features, axis=0)
    pca_features = pca.transform(features)
    return pca_features
