"""
.. module: reinforcements
.. moduleauthor: Marcel Kennert
"""
from traits.api import HasTraits, Str, Float, Instance, List
from traitsui.api import View


class Material(HasTraits):
    """Represents a material."""
    name = Str()

    density = Float()

    stiffness = Float()

    strength = Float()

    def save(self):
        """Saves the properties of the material in a dictionary."""
        return {'name': self.name, 'density': self.density,
                'stiffness': self.stiffness, 'strength': self.strength}

    def load(self, data):
        """
        Loads the given properties.

        :param data: All properties of the material
        :type data: Dictionary
        """
        self.name = data['name']
        self.density = data['density']
        self.stiffness = data['stiffness']
        self.strength = data['strength']


class Matrix(HasTraits):
    """Represents the matrix of the experiment body."""
    material = Instance(Material)

    def save(self):
        """Saves the properties of the matrix in a dictionary."""
        return {}

    def load(self, data):
        """
        Loads the given properties.

        :param data: All properties of the material
        :type data: Dictionary
        """
        return


class IReinforcement(HasTraits):
    """Interface for the reinforcement components."""
    material = Instance(Material)

    def save(self):
        """Saves the properties of the reinforcement in a dictionary."""
        raise NotImplementedError()

    def load(self, data):
        """
        Loads the given properties.

        :param data: All properties of the material
        :type data: Dictionary
        """
        raise NotImplementedError()


class Bar(IReinforcement):
    """Represents a bar."""
    x_coordinate = Float()

    y_coordinate = Float()

    radius = Float()

    def save(self):
        """Saves the properties of the bar in a dictionary."""
        return {'x_coordinate': self.x_coordinate,
                'y_coordinate': self.y_coordinate,
                'radius': self.radius,
                'material': self.material.save()}

    def load(self, data):
        """
        Loads the given properties.

        :param data: All properties of the material
        :type data: Dictionary
        """
        self.x_coordinate = data['x_coordinate']
        self.y_coordinate = data['y_coordinate']
        self.radius = data['radius']
        self.material = self.material.load(data['material'])


class Layer(IReinforcement):
    """Represents a layer of the experiment body."""
    y_coordinate = Float()

    height = Float()

    def save(self):
        """Saves the properties of the layer in a dictionary."""
        return {'y_coordinate': self.y_coordinate,
                'material': self.material.save()}

    def load(self, data):
        """
        Loads the given properties.

        :param data: All properties of the material
        :type data: Dictionary
        """
        self.y_coordinate = data['y_coordinate']
        self.material = self.material.load(data['material'])


class ReinforcementSelector(HasTraits):
    """Component to define the reinforcement in the experiment body."""
    matrix = Instance(Matrix)

    reinforcements = List(IReinforcement)

    def save(self):
        """Saves the properties of the reinforcements and the matrix."""
        return {}

    def load(self, data):
        """
        Loads the given properties.

        :param data: All properties of the material
        :type data: Dictionary
        """
        return

    def add_reinforcement(self, reinforcement):
        """Add a new reinforcement. 

        :param reinforcement: The reinforcement
        :type reinforcement: IReinforcement
        """
        self.reinforcements.append(reinforcement)

    view = View()
