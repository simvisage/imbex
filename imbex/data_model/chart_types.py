__author__ = 'campsb'
__copyright = 'Copyright 2009, IMB, RWTH Aachen'
__date__ = 'Dec. 5, 2017'
__status__ = 'Draft'

# imports
import pylab as p

# -----------------------------------------------------------------------------
# definition of classes for the different chart types
#
# possible layout classes for different articles, presentations, reports, languages
# -----------------------------------------------------------------------------

class BasicLayout():
    """ Defines a basic layout class for charts """

    def apply_design(self):
    # function to apply the design to the generated charts

    # dictionary defining basic layout of plots
        params = {'legend.fontsize': 'large',
              'figure.figsize': (15, 5),
              'axes.labelsize': 'large',
              'axes.titlesize': 'medium',
              'xtick.labelsize': 'medium',
              'ytick.labelsize': 'medium',
              'lines.linewidth': 1,
              'axes.linewidth': 1,
              'lines.markersize': 4}
        return p.rcParams.update(params)
