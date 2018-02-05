"""
.. module: all_types
.. moduleauthor: Marcel Kennert
"""
from traits.api import HasTraits, Str
from traitsui.api import View


class IExperimentType(HasTraits):
    """Bascelass for the experiment-types"""

    type_name = Str()

    def save(self):
        """Returns the properties a dictionary"""
        return {'type_name': self.type_name}

    def load(self, args):
        """Load the given properties

        :param args: Loaded parameters
        :type args: Dictionary
        """
        self.type_name = args['type_name']

    view = View()


class TensileExperiment(IExperimentType):

    def __init__(self):
        IExperimentType.__init__(self)
        self.type_name = 'Tensile'

class BendingExperiment(IExperimentType):
    
    def __init__(self):
        IExperimentType.__init__(self)
        self.type_name = 'Bending'

class CompressionExperiment(IExperimentType):
    
    def __init__(self):
        IExperimentType.__init__(self)
        self.type_name = 'Compression'

class ShearExperiment(IExperimentType):
     
    def __init__(self):
        IExperimentType.__init__(self)
        self.type_name = 'Shear'
        
all_types = {'tensile': TensileExperiment(), 'bending':BendingExperiment(),
             'compression': CompressionExperiment(), 'shear': ShearExperiment()}