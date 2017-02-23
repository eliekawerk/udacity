
import matplotlib.pyplot as plt


def plot_side_by_side_images(images_left, images_right, title_left, title_right, save_as_fn):
    """
    plot given set of images side by side to show before and after pictures
    """
    plt.rcParams.update({'font.size': 8})
    plt.figure(figsize=(10, 5))
    
    num_rows = len(images_left)
    
    image_num = 1
    for i in range(num_rows):
        
        plt.subplot(num_rows, 2, image_num)
        plt.imshow(images_left[i])
        plt.axis('on')
        if i == 0: plt.title(title_left)
        image_num += 1
        
        plt.subplot(num_rows, 2, image_num)
        plt.imshow(images_right[i])
        # plt.imshow(images_right[i], cmap="gray")
        plt.axis('on')
        if i == 0:  plt.title(title_right)
        image_num += 1
        
    plt.savefig(save_as_fn, bbox_inches='tight')
    
    
