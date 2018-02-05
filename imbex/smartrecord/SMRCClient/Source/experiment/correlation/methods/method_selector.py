"""
.. module: method_selector
.. moduleauthor: Marcel Kennert
"""
from traits.api import HasTraits, Instance, List
from traitsui.api import View, ListEditor, UItem

from basic_modules.basic_classes import Combobox
from experiment.correlation.methods.correlation_methods import \
    all_methods, ICorrelate


class MethodSelector(HasTraits):
    """MethodSelector makes it possible to switch the correlate-method."""
    method = Instance(Combobox, ())

    method_views = List(ICorrelate)

    def __init__(self):
        for method in all_methods:
            if all_methods[method].show:
                self.method_views.append(all_methods[method])
            self.method.add_item(method, all_methods[method])
        self.method.add_listener(self)

    def get_selected_value(self):
        """Returns the selected value"""
        return self.method.get_selected_value()

    def selected_changed(self, selected_key):
        """Informs the parent that the selected method has changed.

        :param selected_key: Name of the current selected key
        :type selected_key: string
        """
        if selected_key in all_methods:
            del self.method_views[:]
            self.method_views.append(all_methods[selected_key])

    def correlate_all_images(self):
        """Correlates all images with the specific method."""
        method = self.get_selected_value()
        method.correlate_all_images()

    view = View(
        UItem('method', style='custom'),
        UItem('method_views', style='custom',
              editor=ListEditor(use_notebook=True, deletable=False)
              )
    )
