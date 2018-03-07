"""
.. module: roi_selector
.. moduleauthor: Marcel Kennert
"""
from copy import deepcopy
from os.path import join, basename

from cv2 import rectangle, imshow, imread, imwrite
from cv2 import resize
from numpy import zeros
from pyface.image_resource import ImageResource
from traits.api import HasTraits, Button
from traitsui.api import View, UItem, Image, VGroup, HGroup

from application.configuration import \
    images_dir, roi_file, corr_properties_dir, resized_images_dir
from basic_modules.basic_methods import resize_image, get_all_files
from experiment.correlation.draw_object.draw_methods import IDraw


class ROISelector(IDraw):
    """
    The class ROISelector was developed to select the region of 
    interest for the correlation. 
    """

    def __init__(self):
        self.dialog = ROIDialog(self)

    def is_valid(self):
        if len(self.points) < 1:
            raise ValueError("Define a region of interest")

    def open_dialog(self):
        f = get_all_files(resized_images_dir)[0]
        ref_image = join(resized_images_dir, f)
        self.dialog.open_dialog(ref_image)

    def set_parent(self, parent):
        self.parent = parent

    def update_image(self):
        """Draw the region of the interest in the copied image"""
        self.img_copy = deepcopy(self.img)
        p_1, p_2 = self.temp_points
        rectangle(self.img_copy, p_1, p_2, color=self.color,
                  thickness=self.thick)
        imshow('image', self.img_copy)

    #=========================================================================
    # Methods to save the properties
    #=========================================================================

    def create_roi(self, img, points):
        """Create the region of interest as a array"""
        roi = zeros((img.shape[0], img.shape[1]))
        for p in points:
            p1, p2 = p
            roi[p1[1]:p2[1], p1[0]:p2[0]] = 255
        return roi

    def define_roi(self):
        # make it possible to define a new region of interest
        f = get_all_files(images_dir)[0]
        ref_image = join(images_dir, f)
        self.draw(ref_image)
        return self.points


class ROIDialog(HasTraits):

    add_btn = Button("Add region of interest")

    reset_btn = Button("Reset")

    ref_image = Image()

    def __init__(self, roi_selector):
        self.roi_selector = roi_selector
        self.points = []

    def open_dialog(self, fname):
        self.fname = fname
        self.ref_image = ImageResource(self.fname)
        self.configure_traits(kind="livemodal")

    def _reset_btn_fired(self):
        del self.points[:]
        files = get_all_files(images_dir)
        for f in files:
            resize_image(f)
        self.ref_image = ImageResource(self.fname)

    def _add_btn_fired(self):
        points = self.roi_selector.define_roi()
        if len(points) > 1:
            self.points.append(deepcopy(points))
            fpath = join(corr_properties_dir, roi_file)
            img_name = join(images_dir, basename(self.fname))
            roi = self.roi_selector.create_roi(imread(img_name), self.points)
            imwrite(fpath, roi)
            imwrite(
                join(resized_images_dir, roi_file), resize(roi, (300, 225)))
            files = get_all_files(images_dir)
            for f in files:
                resize_image(join(images_dir, f), True)
            self.ref_image = ImageResource(self.fname)

    view = View(
        HGroup(
            VGroup(
                UItem("add_btn"),
                UItem("reset_btn")
            ),
            UItem('ref_image')
        ),
        title="Define regions of interest"
    )
