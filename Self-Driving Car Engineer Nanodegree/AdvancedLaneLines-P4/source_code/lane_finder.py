from mask_generator import *

from perspective_transformer import PerspectiveTransformer
from camera_calibrator import CameraCalibrator
from utils.line import Line
from utils.histogram_utils import *
from utils.lane_utils import *

from PIL import Image

class LaneFinder:
    
    def __init__(self):
        """
        find lanes on images (or video frames) using Sobel operations, lane color extraction and sliding histogram.
        """
        self.camera_calibrator = CameraCalibrator()
        self.perspective_transformer = PerspectiveTransformer()
        
        self.n_frames = 7
        
        self.line_segments = 10
        self.image_offset = 250
        
        self.left_line = None
        self.right_line = None
        self.center_poly = None
        self.curvature = 0.0
        self.car_offset = 0.0
        
        self.dists = []
        
        
    def display_dashboard(self, img):
        """
        display dashboard with information like lane curvature and car's center offset. 
        """
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        text = "Radius of curvature is {:.2f}m".format(self.curvature)
        cv2.putText(img, text, (50, 50), font, 1, (255, 255, 255), 2)
        
        left_or_right = 'left' if self.car_offset < 0 else 'right'
        text = "Car is {:.2f}m {} of center".format(np.abs(self.car_offset), left_or_right)
        cv2.putText(img, text, (50, 100), font, 1, (255, 255, 255), 2)

    def render_predicted_lane_area(self, img):
        """
        render the predicted lane area onto the image
        """
        overlay = np.zeros([img.shape[0], img.shape[1], img.shape[2]])
        mask = np.zeros([img.shape[0], img.shape[1]])

        # lane area
        lane_area = calculate_lane_area((self.left_line, self.right_line), img.shape[0], 20)
        mask = cv2.fillPoly(mask, np.int32([lane_area]), 1)
        mask = self.perspective_transformer.inverse_transform(mask)

        overlay[mask == 1] = (128, 255, 0)
        selection = (overlay != 0)
        img[selection] = img[selection] * 0.5 + overlay[selection] * 0.5

        # side lines 
        mask[:] = 0
        mask = draw_poly(mask, self.left_line.best_fit_poly, 5, 255)
        mask = draw_poly(mask, self.right_line.best_fit_poly, 5, 255)
        mask = self.perspective_transformer.inverse_transform(mask)
        img[mask == 255] = (255, 200, 2)
    
    def add_logo(self, orig_frame):
        background = Image.fromarray(orig_frame)
        foreground = Image.open("../test_images/logo.png")
        background.paste(foreground, (30, orig_frame.shape[0] - 80), mask=foreground.split()[3])
        orig_frame = np.array(background.convert())
        return orig_frame
        

    def process_frame(self, frame):
        """
        apply lane detection on a single image
        :param frame: input frame
        :return: processed frame
        """
        orig_frame = np.copy(frame)

        # undistort frame
        frame = self.camera_calibrator.undistort(frame)

        # apply sobel and color transforms to create a thresholded binary image.
        frame = generate_lane_mask(frame, 400)

        # apply perspective transform to get birds-eye view
        frame = self.perspective_transformer.transform(frame)

        left_detected = right_detected = False
        left_x = left_y = right_x = right_y = []

        # if lanes were detected in the past, algorithm will first try to find new lanes along the old one. 
        # this will improve performance
        if self.left_line is not None and self.right_line is not None:
            left_x, left_y = detect_lane_along_poly(frame, self.left_line.best_fit_poly, self.line_segments)
            right_x, right_y = detect_lane_along_poly(frame, self.right_line.best_fit_poly, self.line_segments)
  
            left_detected, right_detected = self.validate_lines(left_x, left_y, right_x, right_y)

        # if no lanes were found a histogram search is performed
        if not left_detected:
            left_x, left_y = histogram_lane_detection(
                frame, self.line_segments, (self.image_offset, frame.shape[1] // 2), h_window=7)
            left_x, left_y = outlier_removal(left_x, left_y)
            
        if not right_detected:
            right_x, right_y = histogram_lane_detection(
                frame, self.line_segments, (frame.shape[1] // 2, frame.shape[1] - self.image_offset), h_window=7)
            right_x, right_y = outlier_removal(right_x, right_y)

        if not left_detected or not right_detected:
            left_detected, right_detected = self.validate_lines(left_x, left_y, right_x, right_y)

        # updated left lane information
        if left_detected:
            # switch x and y since lines are almost vertical
            if self.left_line is not None:
                self.left_line.update(y=left_x, x=left_y)
            else:
                self.left_line = Line(self.n_frames, left_y, left_x)
 
        # updated right lane information.
        if right_detected:
            # switch x and y since lines are almost vertical
            if self.right_line is not None:
                self.right_line.update(y=right_x, x=right_y)
            else:
                self.right_line = Line(self.n_frames, right_y, right_x)

        # add calculated information onto the frame
        if self.left_line is not None and self.right_line is not None:
            self.dists.append(self.left_line.get_best_fit_distance(self.right_line))
            self.center_poly = (self.left_line.best_fit_poly + self.right_line.best_fit_poly) / 2
            self.curvature = calc_curvature(self.center_poly)
            self.car_offset = (frame.shape[1] / 2 - self.center_poly(719)) * 3.7 / 700
    
            self.render_predicted_lane_area(orig_frame)
            self.display_dashboard(orig_frame)
            
        
        return self.add_logo(orig_frame)
    
    def validate_lines(self, left_x, left_y, right_x, right_y):
        """
        compare two line to each other and to their last prediction.
        :param left_x:
        :param left_y:
        :param right_x:
        :param right_y:
        :return: boolean tuple (left_detected, right_detected)
        """
        left_detected = False
        right_detected = False

        if self.is_line_plausible((left_x, left_y), (right_x, right_y)):
            left_detected = True
            right_detected = True
        elif self.left_line is not None and self.right_line is not None:
            if self.is_line_plausible((left_x, left_y), (self.left_line.ally, self.left_line.allx)):
                left_detected = True
            if self.is_line_plausible((right_x, right_y), (self.right_line.ally, self.right_line.allx)):
                right_detected = True

        return left_detected, right_detected

    def is_line_plausible(self, left, right):
        """
        determine if pixels describing two line are plausible lane lines based on curvature and distance.
        :param left: Tuple of arrays containing the coordinates of detected pixels
        :param right: Tuple of arrays containing the coordinates of detected pixels
        :return:
        """
        if len(left[0]) < 3 or len(right[0]) < 3:
            return False
        else:
            new_left = Line(y=left[0], x=left[1])
            new_right = Line(y=right[0], x=right[1])
            return are_lanes_plausible(new_left, new_right)

# quick unittest     
if __name__ == '__main__':
    
    lane_finder = LaneFinder()
    
    images_left = []
    images_right = []
    
    test_images = ["../test_images/straight_lines2.jpg", "../test_images/test5.jpg"]
    
    for image in test_images:
        image = imread(image)
        transformed = lane_finder.process_frame(image)
        images_left.append(image)
        images_right.append(transformed)
    
    plot_side_by_side_images(images_left, images_right, 'Original', 'Lane Found', '../output_images/lane_found.png')
   
    print('Done')
