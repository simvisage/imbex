"""
You can pass a custom Figure constructor to figure if you want to derive from the default Figure.  This simple example creates a figure with a figure title
"""
from matplotlib.pyplot import figure, show
from matplotlib.figure import Figure


class MyFigure(Figure):
    def __init__(self, *args, **kwargs):
        """
        custom kwarg figtitle is a figure title
        """
        fig_title = kwargs.pop('figtitle')
        x_label = kwargs.pop('xlabel')
        Figure.__init__(self, *args, **kwargs)
        self.text(0.5, 0.95, fig_title, x_label, ha='center')


fig_kind = MyFigure
fig = figure(FigureClass=fig_kind, figtitle='', xlabel='time')
ax1 = fig.add_subplot(211)
ax2 = fig.add_subplot(212)
ax1.plot([1, 2, 3])
ax2.plot([3, 2, 1])

show()