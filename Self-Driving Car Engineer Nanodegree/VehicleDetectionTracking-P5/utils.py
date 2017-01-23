import threading
import math
import numpy as np

from keras.preprocessing.image import *

# def get_random_image(dataset, fish_type=None, 
#                      resize_img_rows=64,
#                      resize_img_cols=64):
#     
#     if fish_type:
#         dataset = dataset[dataset.fish_type == fish_type]
# 
#     random_index = np.random.randint(len(dataset))
#     image_path = dataset.iloc[random_index]['image_path']
# 
#     img = load_img(image_path, target_size=(resize_img_cols, resize_img_rows))
#     # img = img_to_array(img)
#     return img

# generators in multi-threaded applications is not thread-safe. Hence below:
class threadsafe_iter:
    """Takes an iterator/generator and makes it thread-safe by
    serializing call to the `next` method of given iterator/generator.
    """
    def __init__(self, it):
        self.it = it
        self.lock = threading.Lock()

    def __iter__(self):
        return self
    
    def __next__(self):
        with self.lock:
            return self.it.__next__()
        
def threadsafe_generator(f):
    """A decorator that takes a generator function and makes it thread-safe.
    """
    def g(*a, **kw):
        return threadsafe_iter(f(*a, **kw))
    return g

@threadsafe_generator
def generate_batch_data(_data, batch_size=32, 
                        num_classes=8, 
                        resize_img_rows=64,
                        resize_img_cols=64,
                        resize_img_channels=3,
                        image_column_name='image_path', 
                        label_column_name='one_hot_fish'):
    
    batch_images = np.zeros((batch_size, resize_img_rows, resize_img_cols, resize_img_channels))
    batch_labels = np.zeros((batch_size, num_classes))
    
    while 1:
        for batch_index in range(batch_size):
            row_index = np.random.randint(len(_data))
            line_data = _data.iloc[[row_index]].reset_index()
            
            image_path = line_data[image_column_name][0].strip()
            label = list(line_data[label_column_name][0])
            img = load_img(image_path, target_size=(resize_img_cols, resize_img_rows))
            
            batch_images[batch_index] = img
            batch_labels[batch_index] = label
            
        yield batch_images, batch_labels
        
# Calculate the correct number of samples per epoch based on batch size
def calc_samples_per_epoch(array_size, batch_size):
    num_batches = array_size / batch_size
    samples_per_epoch = math.ceil(num_batches)
    samples_per_epoch = samples_per_epoch * batch_size
    return samples_per_epoch  

