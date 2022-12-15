import matplotlib

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from PyQt5.QtCore import pyqtSignal, QEvent, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import (
    QAction,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QGraphicsOpacityEffect,
)

matplotlib.use("Qt5Agg")


class BaseWindow(QMainWindow):
    def __init__(self, parent=None):
        super(QMainWindow, self).__init__(parent)

        menu = self.menuBar()
        documentation_action = QAction("Documentation", self)
        documentation_action.triggered.connect(self.open_documentation)
        help_menu = menu.addMenu("Help")
        help_menu.addAction(documentation_action)

    def open_documentation(self):
        QDesktopServices.openUrl(
            QUrl("https://github.com/tsmathis/dilatometry_analyst/blob/main/README.md")
        )


class FigureWindow(QWidget):
    def __init__(
        self,
        width=12,
        height=6,
        dpi=150,
        x=None,
        y=None,
        xlabel=None,
        ylabel=None,
        curve_label=None,
        subplots=1,
    ):
        QWidget.__init__(self)

        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        self.fig = Figure(figsize=(width, height), dpi=dpi, constrained_layout=True)
        self.axes = self.fig.add_subplot(1, subplots, 1)
        if x is not None and y is not None:
            self.axes.plot(x, y, label=curve_label)
        if xlabel and ylabel:
            self.axes.set_xlabel(xlabel)
            self.axes.set_ylabel(ylabel)
        if curve_label:
            self.axes.legend()

        self.canvas = FigureCanvas(self.fig)
        self.canvas.mpl_connect("resize_event", self.resize)
        self.layout().addWidget(self.canvas)

        self.nav = NavigationToolbar(self.canvas, self, coordinates=False)
        self.nav.setMinimumWidth(300)
        self.nav.setStyleSheet("QToolBar { border: 0px }")
        self.nav.installEventFilter(self)

        self.opac = QGraphicsOpacityEffect()
        self.opac.setOpacity(0.3)
        self.nav.setGraphicsEffect(self.opac)

    def resize(self, event):
        # on resize reposition the navigation toolbar to (0,0) of the axes.
        x, y = self.fig.axes[0].transAxes.transform((0, 0))
        figw, figh = self.fig.get_size_inches()
        ynew = figh * self.fig.dpi - y - self.nav.frameGeometry().height()
        self.nav.move(int(x), int(ynew))

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Enter:
            self.opac.setOpacity(1.0)
            self.nav.setGraphicsEffect(self.opac)
            return True
        elif event.type() == QEvent.Leave:
            self.opac.setOpacity(0.3)
            self.nav.setGraphicsEffect(self.opac)
        return False


class ClickableWidget(FigureCanvas):
    clicked = pyqtSignal(int)

    def __init__(self, idx=None, parent=None):
        self.fig = Figure(dpi=100)
        self.axes = self.fig.add_subplot()
        super().__init__(self.fig)
        self.setMaximumSize(150, 150)
        self.setMinimumSize(50, 50)
        self.axes.get_xaxis().set_visible(False)
        self.axes.get_yaxis().set_visible(False)
        self.index = idx
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if isinstance(obj, FigureCanvas) and event.type() == QEvent.MouseButtonPress:
            self.clicked.emit(self.index)
        return QWidget.eventFilter(self, obj, event)
