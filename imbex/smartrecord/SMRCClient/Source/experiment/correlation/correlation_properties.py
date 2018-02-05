"""
.. module: correlation_properties
.. moduleauthor: Marcel Kennert
"""
from json import dump, load
from logging import getLogger
from os.path import join

from traits.api import HasTraits, Instance, Int, Button, Bool
from traitsui.api import View, VGroup, Item, UItem

from application.configuration import \
    corr_properties_dir, correlation_properties_file, resized_images_dir
from basic_modules.basic_dialogs import ErrorDialogs
from basic_modules.basic_methods import get_all_files
from experiment.correlation.draw_object.roi_selector import ROISelector
from experiment.correlation.draw_object.unit_converter import UnitConverter
from experiment.correlation.methods.method_selector import MethodSelector


class CorrelationProperties(HasTraits):
    """Defines the properties for the correlation"""

    #=========================================================================
    # Important components to interact
    #=========================================================================

    unit_converter = Instance(UnitConverter, ())

    roi_selector = Instance(ROISelector, ())
    
    correlation_method = Instance(MethodSelector, ())
    
    error_dialog = ErrorDialogs()

    #=========================================================================
    # Properties of the correlation
    #=========================================================================

    subset_size = Int(30)

    record_mode = Bool()

    logger = getLogger("Application")

    def __init__(self, experiment):
        self.logger.debug("Initialize CorrelationProperties")
        self.experiment = experiment
        self.record_mode = experiment.record_mode
        self.roi_selector.set_parent(self)
        self.unit_converter.set_parent(self)
        self.path = join(corr_properties_dir, correlation_properties_file)

    def is_valid(self):
        self.roi_selector.is_valid()
        self.unit_converter.is_valid()

    #=========================================================================
    # Methods to save and load the correlation properties
    #=========================================================================

    def get_properties(self):
        return {"subset_size": self.subset_size,
                "length_per_pixel": self.unit_converter.length_per_pixel,
                "length_of_line": self.unit_converter.length_of_line,
                "roi_points": self.roi_selector.points}

    def save(self):
        """Save the properties in the temp-folder"""
        self.logger.debug("Save properties [CorrelationProperties]")
        with open(self.path, 'w') as f:
            dump(self.get_properties(), f, indent=2)

    def load(self, input_ports):
        """Loads the correlation properties"""
        self.logger.debug("Load properties [CorrelationProperties]")
        f = get_all_files(resized_images_dir)[0]
        self.experiment.recorder.update_reference(f)
        self.loaded_reference = True
        try:
            with open(self.path, 'r') as f:
                data = load(f)
            self.unit_converter.length_of_line = data["length_of_line"]
            self.subset_size = data["subset_size"]
            self.roi_selector.points = data["roi_points"]
            self.unit_converter.length_per_pixel = data["length_per_pixel"]
        except Exception:
            self.logger.debug("Correlation properties do not exist")

    #=========================================================================
    # Traitsview + Traitsevents
    #=========================================================================

    loaded_reference = Bool(False)

    reference_btn = Button("Edit")

    edit_roi_btn = Button("Edit")

    correlate_btn = Button("Correlate")

    def _reference_btn_fired(self):
        try:
            self.experiment.measuring_card_is_valid()
        except ValueError, e:
            self.error_dialog.open_error(str(e))
            return
        self.experiment.create_reference_image()
        f = get_all_files(resized_images_dir)[0]
        self.experiment.recorder.update_reference(f)
        self.loaded_reference = True

    def _edit_roi_btn_fired(self):
        self.roi_selector.open_dialog()
        f = get_all_files(resized_images_dir)[0]
        self.experiment.recorder.update_reference(f)

    def _correlate_btn_fired(self):
        self.correlation_method.correlate_all_images()

    view = View(
        VGroup(
            VGroup(
                Item("subset_size", label="Subset size [pixel]"),
                Item("reference_btn", label="Set reference Image:",
                     enabled_when='record_mode'),
                Item("edit_roi_btn", label="Define region of interest",
                     enabled_when="loaded_reference"),
                label='General'
            ),
            VGroup(
                UItem('unit_converter', style='custom'),
                enabled_when="loaded_reference"
            ),
            VGroup(
                UItem("correlation_method", style="custom",
                      enabled_when="loaded_reference"),
                UItem("correlate_btn", enabled_when="loaded_reference")
            ),
            layout='normal'
        )
    )
