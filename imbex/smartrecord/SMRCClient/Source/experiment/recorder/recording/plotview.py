import logging

from matplotlib.backends.backend_qt4agg import \
    FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import \
    NavigationToolbar2QT as NavigationToolbar2QTAgg
from matplotlib.figure import Figure
from matplotlib.patches import Ellipse
from numpy import amax, amin
from pyface.qt import QtGui
from traits.api import HasTraits, List, Instance, Str
from traits.etsconfig.api import ETSConfig
from traitsui.api import Handler
from traitsui.api import View, UItem, VGroup, ListEditor
from traitsui.qt4.basic_editor_factory import BasicEditorFactory
from traitsui.qt4.editor import Editor

from application.configuration import toolbar_background, stylesheet_qtoolbutton
import matplotlib as mpl


ETSConfig.toolkit = "qt4"

mpl.rcParams["backend.qt4"] = "PySide"

mpl.use("Qt4Agg")


class PlotView(HasTraits):
    """
    Object to manage the plots of the experiment. The plot
    shows the recorded values and make it possible to follow 
    the history of the experiment
    """

    plots = List()

    logger = logging.getLogger("application")

    def __init__(self):
        self.logger.debug("Initialize PlotView")
        self.model = None
        plot = Plot(self.model)
        plot.update_title(" ")
        self.plots.append(plot)
    
    def reset_subplots(self, title):
        del self.plots[:]
        plot = Plot(self.model)
        plot.update_title(title)
        self.plots.append(plot)
        
    def update_subplots(self, input_ports):
        """
        Update the number and the title of all sub plots.
        Every input port of the measuring card get a own plot
        to show the records of the port.

        :param input_ports: All input ports of the measuring card
        :type input_ports: List(Port)
        """
        del self.plots[:]
        for i in range(len(input_ports)):
            self.set_title(input_ports[i].name)

    def set_title(self, title):
        plot = Plot(self.model)
        plot.update_title(title)
        self.plots.append(plot)

    def set_labels(self, xlabel, ylabel, title):
        del self.plots[:]
        plot = Plot(self.model)
        plot.update_labels(xlabel, ylabel, title)
        self.plots.append(plot)

    def update_values(self, values):
        """Update all values of all plots.

        :param values: Recorded values of the experiment
        :type values: ndarray
        """
        for i in range(1, len(values[0])):
            val = values[:, i]
            try:
                self.plots[i - 1].update_plot(val)
            except IndexError:
                pass

    def update_focus_point(self, index):
        for p in self.plots:
            p.update_focus_point(index)

    def plot_graph(self, plot_index, x_values, y_values, color='b', label=""):
        self.plots[plot_index].plot(x_values, y_values, color, label)

    view = View(
        VGroup(
            UItem("plots", style="custom",
                  editor=ListEditor(use_notebook=True, deletable=False,
                                    page_name=".title"),
                  ),
            label="Plots"
        )
    )


class _MPLFigureEditor(Editor):

    scrollable = True

    def init(self, parent):
        self.control = self._create_canvas(parent)
        self.set_tooltip()

    def update_editor(self):
        pass

    def _create_canvas(self, parent):
        """ Create the MPL canvas. """
        # matplotlib commands to create a canvas
        frame = QtGui.QWidget()
        mpl_canvas = FigureCanvas(self.value)
        mpl_canvas.setParent(frame)
        mpl_toolbar = NavigationToolbar2QTAgg(mpl_canvas, frame)
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(mpl_canvas)
        vbox.addWidget(mpl_toolbar)
        frame.setLayout(vbox)
        return frame


class MPLFigureEditor(BasicEditorFactory):

    klass = _MPLFigureEditor


class MPLInitHandler(Handler):
    """Handler calls mpl_setup() to initialize mpl events"""

    def init(self, info):
        """This method gets called after the controls have all been
        created but before they are displayed.
        """
        info.object.mpl_setup()
        info.ui.control.setStyleSheet(
            '*{background-color: ' + toolbar_background + '}' + stylesheet_qtoolbutton)
        return True


class Plot(HasTraits):
    """
    The class Plot was developed to show the history of the 
    experiment and the recorded values. The class make it possible 
    to click a recording and show the information of the 
    selected point in the model.
    """

    figure = Instance(Figure, ())

    title = Str()

    def __init__(self, model):
        """Creates a instance of the class Plot

        :param experiment: Related experiment
        :type experiment: ExperimentModel
        """
        self.model = model
        self.xmin = 0
        self.xmax = 20
        self.ticks = 10
        self.ellipse_size = 6
        self.focus = False
        self.focus_circel = Ellipse((0.0, 0.0), 0.0, 0, color='r')

    def update_title(self, title):
        """Update the title of the plot.

        :param title: Title for the plot
        :type title: Str
        """
        self.title = title
        self.axes = self.figure.add_subplot(111)
        self.axes.set_xlim([self.xmin, self.xmax])
        self.axes.set_ylabel(title)
        self.axes.set_title(title)
        self.axes.grid(True)

    def update_labels(self, xlabel, ylabel, title):
        self.title = title
        self.axes = self.figure.add_subplot(111)
        self.axes.set_xlabel(xlabel)
        self.axes.set_ylabel(ylabel)
        self.axes.set_title(title)
        self.axes.grid(True)

    def update_plot(self, values):
        """Update the plots with the given values.

        :param values: Values which should plot
        :type values: ndarray
        """
        self.values = values
        self.figure.canvas.mpl_connect("button_press_event", self._onclick)
        if len(values) > self.xmax:
            self.xmax += self.ticks
            self.xmin += self.ticks
            self.axes.set_xlim([self.xmin, self.xmax])
        self.axes.plot(values, marker="o", linestyle='-',
                       markerfacecolor=toolbar_background, linewidth=1)
        if not self.focus:
            self.axes.add_artist(self.focus_circel)
            self.focus = True
        self.figure.canvas.draw()

    def plot(self, x, y, color, label=""):
        max_x = amax(x)
        min_x = amin(x)
        self.axes.set_xlim([min_x - min_x * 0.1 - 0.1, max_x * 1.1])
        self.axes.plot(x, y, marker="o", markerfacecolor=toolbar_background,
                       label=label)
        
    def _onclick(self, event):
        # click event to select a point of the plot
        n = len(self.values)
        if n == 0:
            return
        x, y = event.xdata, event.ydata
        width, height = self.get_eps()
        self.focus_circel.width = width
        self.focus_circel.height = height
        for i in range(n):
            try:
                if x - width < i and i < x + width and \
                        y - height < self.values[i] and \
                        self.values[i] < y + height:
                    self.model._update_record_information(i)
            except TypeError:
                pass

    def get_eps(self):
        h = (amax(self.values) - amin(self.values))
        if h == 0:
            ymin, ymax = self.axes.get_ylim()
            h = (ymax - ymin)
        height = abs(h) / 100 * self.ellipse_size
        width = 20 / 100. * (self.ellipse_size - 1)
        return width, height

    def update_focus_point(self, index):
        width, height = self.get_eps()
        self.focus_circel.width = width
        self.focus_circel.height = height
        self.focus_circel.center = index, self.values[index]
        self.figure.canvas.draw()
        if not self.focus:
            self.axes.add_artist(self.focus_circel)
            self.focus = True
        self.figure.canvas.draw()

    def mpl_setup(self):
        pass

    view = View(
        UItem("figure", editor=MPLFigureEditor()),
        handler=MPLInitHandler,
        resizable=True
    )
