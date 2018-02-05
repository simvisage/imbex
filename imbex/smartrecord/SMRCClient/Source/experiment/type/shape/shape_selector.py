"""
.. module: shape_selector
.. moduleauthor: Marcel Kennert
"""
from traits.api import HasTraits, Instance, List
from traitsui.api import View, ListEditor, UItem

from basic_modules.basic_classes import Combobox
from experiment.type.shape.all_shapes import IShape, all_shapes


class ShapeSelector(HasTraits):
    """Make it possible to choose a shape."""

    shape = Instance(Combobox, ())

    shape_views = List(IShape)

    def __init__(self):
        for shape in all_shapes:
            if all_shapes[shape].show:
                self.shape_views.append(all_shapes[shape])
            self.shape.add_item(shape, all_shapes[shape])
        self.shape.add_listener(self)

    def get_selected_key(self):
        """Returns the selected shape-name.

        :returns: Name of the shape.
        :rtype: string
        """
        return self.shape.selected_key

    def get_selected_value(self):
        """Returns the selected shape.

        :returns: Selected shape.
        :rtype: IShape
        """
        return self.shape.get_selected_value()

    def save(self):
        """Returns a dictionary to save the shape-properties.

        :returns: The properties of the shape.
        :rtype: Dictionary
        """
        shape = self.shape.get_selected_value()
        data = shape.save()
        return {'shape': data}

    def load(self, data):
        """Loads the properties by the given date. 

        :param data: Properties of the shape.
        :type data: Dictionary.
        """
        shape = data['shape'].lower()
        args = data['shape_data']
        del self.shape_views[:]
        for d in all_shapes:
            if d == shape:
                all_shapes[shape].load(args)
                self.shape_views.append(all_shapes[shape])
                all_shapes[shape].show = True

    def selected_changed(self, selected_key):
        if selected_key in all_shapes:
            del self.shape_views[:]
            self.shape_views.append(all_shapes[selected_key])

    view = View(
        UItem('shape', style='custom'),
        UItem('shape_views', style='custom',
              editor=ListEditor(use_notebook=True, deletable=False,
                                page_name='.shape_name')
              )
    )
