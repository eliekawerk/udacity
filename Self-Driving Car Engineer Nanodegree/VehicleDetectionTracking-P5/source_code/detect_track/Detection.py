import cv2
import numpy as np

# Describes a detection on a image.
class Detection:
    def __init__(self, box):
        """
        Describes a detection on a image.
        :param box: initial bounding box
        """
        self.is_hidden = False
        self.last_boxes = []
        self.best_box = None
        self.frames_undetected = 0
        self.age = 0
        self.n_frames = 10

        self.update(box)

    def update(self, box):
        """
        Updates the detection object with a new bounding box.
        :param box:
        :return:
        """
        if box is not None:
            self.last_boxes.append(box)
            bound = min(len(self.last_boxes), self.n_frames)
            self.best_box = np.mean(self.last_boxes[-bound:], axis=0).astype(np.uint32)

            self.frames_undetected = 0
        else:
            self.frames_undetected += 1

        self.age += 1

    def unhide(self, box):
        """
        Unhides the detection and sets the bounding box to the no value
        :param box:
        """
        if self.is_hidden:
            self.last_boxes.extend([box] * self.n_frames)
            self.is_hidden = False

    def draw(self, img, color=(0, 0, 255), thick=3):
        """
        Draws the bounding box of the detection on a given image.
        It also adds information on how long the detection has been active.
        :param img: image to draw on
        :param color:
        :param thick:
        :return:
        """
        if self.best_box is None:
            return img

        box_to_draw = np.zeros(4, dtype=np.uint32)
        if self.is_hidden:
            w = self.best_box[2] - self.best_box[0]
            h = self.best_box[3] - self.best_box[1]

            box_to_draw[:2] = self.best_box[:2] + min(25, w // 2)
            box_to_draw[2:] = self.best_box[2:] - min(25, h // 2)
        else:
            box_to_draw = self.best_box

        cv2.rectangle(img, (box_to_draw[0], box_to_draw[1]), (box_to_draw[2], box_to_draw[3]), color, thick)
        return img

    def relative_distance_with(self, boxes):
        """
        Calculates the relative distance with all the given bounding boxes by
        calculating the mean diagonal and dividing it by the distance.
        :param boxes:
        :return:
        """
        return self.relative_distance(self.best_box, boxes)

    def relative_distance(self, box, o_box):
        """
        Calculates the average diagonal between the given box and each of the other boxes and
        puts it in relation to the distance of the center points.
        :param box: [left_upper_x, left_upper_y, right_lower_x, right_lower_y]
        :param o_box: [[left_upper_x, left_upper_y, right_lower_x, right_lower_y]]
        :return:
        """
    
        box = box.astype(np.float)
        o_box = o_box.astype(np.float)
        mean_diag = (np.sqrt(box[0] ** 2 + box[2] ** 2) + np.sqrt(o_box[:, 0] ** 2 + o_box[:, 2] ** 2)) / 2
    
        c_box = self.center_points(np.expand_dims(box, axis=0))[0]
        c_o_box = self.center_points(o_box)
        dist_centers = np.sqrt(np.power(c_box[0] - c_o_box[:, 0], 2) + np.power(c_box[1] - c_o_box[:, 1], 2))
    
        return dist_centers / mean_diag
    
    def center_points(self, boxes):
        """
        Calculates the center coordinates of multiple bounding boxes.
    
        :param boxes: [[left_upper_x, left_upper_y, right_lower_x, right_lower_y]]
        :return:
        """
    
        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = boxes[:, 2]
        y2 = boxes[:, 3]
        width = x2 - x1
        height = y2 - y1
        x = x1 + width // 2
        y = y1 + height // 2
    
        return np.stack((x, y)).T
