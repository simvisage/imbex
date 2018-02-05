"""
.. module: unit_converter
.. moduleauthor: Marcel Kennert
"""

from copy import deepcopy
from os.path import join

from cv2 import line, imshow
from numpy import abs, sqrt
from traits.api import Float, Button
from traitsui.api import View, VGroup, Item

from application.configuration import images_dir, resized_images_dir
from basic_modules.basic_methods import get_all_files
from experiment.correlation.draw_object.draw_methods import IDraw


class UnitConverter(IDraw):
    """Make it possible to define the length for a pixel"""

    # save how long (in [mm]) is one pixel
    length_per_pixel = Float

    # Set the length of the selected line
    length_of_line = Float

    # Length of the selected line
    length_in_pixel = Float

    def is_valid(self):
        if len(self.points) < 1 or self.length_in_pixel <= 0:
            raise ValueError("Length in pixel is not define")

    def set_parent(self, parent):
        self.parent = parent

    def update_image(self):
        self.img_copy = deepcopy(self.img)
        p_1, p_2 = self.temp_points
        line(self.img_copy, p_1, p_2, color=self.color,
             thickness=self.thick)
        imshow('image', self.img_copy)

    def get_length(self):
        """Returns the length of the line."""
        p1, p2 = self.points
        dx, dy = abs(p1[0] - p2[0]), abs(p1[1] - p2[1])
        return sqrt(dx**2 + dy**2)

    #=========================================================================
    # Traitsview + Traitsevents
    #=========================================================================

    set_length_btn = Button("Edit")

    def _set_length_btn_fired(self):
        # make it possible to define a new line
        f = get_all_files(resized_images_dir)[0]
        ref_image = join(images_dir, f)
        self.draw(ref_image)
        self.length_in_pixel = self.get_length()
        self.length_per_pixel = self.length_of_line / self.length_in_pixel

    def _length_of_line_changed(self, old, new):
        try:
            self.length_per_pixel = new / self.length_in_pixel
        except Exception:
            self.length_per_pixel = 0

    view = View(
        VGroup(
            Item("set_length_btn", label="Define line"),
            Item("length_of_line", label='Length of the line [mm]'),
            Item("length_per_pixel", style="readonly",
                 label='Length/pixel [mm]'),
            label='Define length of pixel'
        )
    )
