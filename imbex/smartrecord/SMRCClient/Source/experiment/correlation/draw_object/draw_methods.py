"""
.. module: draw_objects
.. moduleauthor: Marcel Kennert
"""

from copy import deepcopy

from cv2 import \
    imread, namedWindow, WINDOW_NORMAL, setMouseCallback, resizeWindow, \
    imshow, waitKey, destroyAllWindows, EVENT_LBUTTONDOWN, EVENT_LBUTTONUP,\
    EVENT_MOUSEMOVE, line, circle, FONT_HERSHEY_SIMPLEX, putText, LINE_AA
from traits.api import HasTraits, List, Bool, Int


class IDraw(HasTraits):
    """Base class for components which allowed the user to draw on a image"""

    points = List()

    temp_points = List()

    thick = Int()

    color = (0, 0, 255)

    drawing = Bool(False)

    def update_image(self):
        """Update the image with the drawed points"""
        raise NotImplementedError()

    def draw(self, image_path):
        del self.points[:]
        del self.temp_points[:]
        self.drawing = False
        self.img = imread(image_path)
        self.thick = int(self.img.shape[1] * 0.005)
        self.img_copy = deepcopy(self.img)
        namedWindow('image', WINDOW_NORMAL)
        setMouseCallback('image', self.draw_rect)
        while True:
            resizeWindow('image', 800, 500)
            imshow('image', self.img_copy)
            key = waitKey(1) & 0xFF
            if key == 13:  # enter
                break
            elif key == 27:  # escape
                self.points = []
                self.temp_points = []
        # close all open windows
        destroyAllWindows()
        return self.img_copy

    # mouse callback function
    def draw_rect(self, event, x, y, flags, param):
        if event == EVENT_LBUTTONDOWN:
            if len(self.points) > 0:
                del self.points[:]
                del self.temp_points[:]
            self.points.append((x, y))
            self.temp_points.append((x, y))
            self.drawing = True
        # check to see if the left mouse button was released
        elif event == EVENT_LBUTTONUP:
            # record the ending (x, y) coordinates and indicate that
            # drawing operation is finished
            self.points.append((x, y))
            self.drawing = False
        # if mouse is drawing set tmp rectangle endpoint to (x,y)
        elif event == EVENT_MOUSEMOVE and self.drawing:
            if len(self.temp_points) > 1:
                self.temp_points[1] = (x, y)
            else:
                self.temp_points.append((x, y))
            self.update_image()


class TravelSensorDraw(IDraw):

    def update_image(self):
        self.img_copy = deepcopy(self.img)
        p_1, p_2 = self.temp_points
        line(self.img_copy, p_1, p_2, color=self.color,
             thickness=2)
        imshow('image', self.img_copy)

    def draw_travel_sensor(self, img, travel_sensor, u1=0, u2=0, v1=0, v2=0):
        p1, p2 = travel_sensor.points
        x1, y1 = p1
        x2, y2 = p2
        r = travel_sensor.radius
        p1 = tuple((int(x1 + u1), int(y1 + v1)))
        p2 = tuple((int(x2 + u2), int(y2 + v2)))
        line(img, p1, p2, color=self.color, thickness=2)
        font = FONT_HERSHEY_SIMPLEX
        s = travel_sensor.name
        putText(img, s.split('-')[1][0], (int(x1 + u1 + 10), int(y1 + v1 + 15)),
                font, 0.4, self.color, 2, LINE_AA)
        circle(img, p1, r, self.color, -1)
        circle(img, p2, r, self.color, -1)
        return img
