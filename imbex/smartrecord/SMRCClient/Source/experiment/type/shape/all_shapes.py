"""
.. module: all_shapes
.. moduleauthor: Marcel Kennert
"""
from traits.api import HasTraits, Str, Float, Bool
from traitsui.api import View, Item, VGroup
from numpy import pi


class IShape(HasTraits):
    """Baseclass for the shapes"""

    shape_name = Str()

    area = Float()

    show = Bool(False)

    def save(self):
        """Returns the properties of the shape as a dictionary.

        :returns: Properties
        :rtype: Dictionary
        """
        raise NotImplementedError()

    def load(self, args):
        """Loads the given properties.

        :param args: Properties of the shape.
        :type args: Dictionary
        """
        raise NotImplementedError()


class Cuboid(IShape):

    length = Float(0)

    width = Float(0)

    height = Float(0)

    def __init__(self):
        IShape.__init__(self)
        self.shape_name = "Cuboid"
        self.show = True

    def save(self):
        """Returns the properties of the shape as a dictionary.

        :returns: Properties
        :rtype: Dictionary
        """
        return {'shape': self.shape_name,
                'shape_data': {'length': self.length,
                               'width': self.width,
                               'height': self.height,
                               'area': self.area}}

    def load(self, args):
        """Loads the given properties.

        :param args: Properties of the shape.
        :type args: Dictionary
        """
        self.length = args['length']
        self.width = args['width']
        self.height = args['height']
        self.show

    def __str__(self, *args, **kwargs):
        return "Type=Cuboid; Properties:{0}".format(self.__dict__)
    
    
    def _width_changed(self):
        self.area = self.width * self.length

    def _length_changed(self):
        self.area = self.width * self.length

    view = View(
        VGroup(
            Item('height', label='Height [mm]:'),
            Item('length', label='Length [mm]:'),
            Item('width', label='Width [mm]:'),
            Item('area', style='readonly', label="Area [mm^2]:"),
            visible_when="show"
        )
    )


class Cylinder(IShape):

    radius = Float()

    height = Float()

    def __init__(self):
        IShape.__init__(self)
        self.shape_name = "Cylinder"

    def save(self):
        """Returns the properties of the shape as a dictionary.

        :returns: Properties
        :rtype: Dictionary
        """
        return {'shape': self.shape_name,
                'shape_data': {
                    'radius': self.radius,
                    'height': self.height}
                }

    def load(self, args):
        """Loads the given properties.

        :param args: Properties of the shape.
        :type args: Dictionary
        """
        self.radius = args['radius']
        self.height = args['height']
        self.show

    def __str__(self, *args, **kwargs):
        return "Type=Cylinder; Properties:{0}".format(self.__dict__)

    def _radius_changed(self):
        self.area = pi * self.radius**2

    view = View(
        VGroup(
            Item('radius', label='Length [mm]:'),
            Item('height', label='Height [mm]:'),
            Item('area', style='readonly', label="Area [mm^2]:"),
            visible_when="show"
        )
    )

all_shapes = {'cuboid': Cuboid(), 'cylinder': Cylinder()}
