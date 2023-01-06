import matplotlib

from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from PyQt5.QtCore import Qt, pyqtSignal, QEvent, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import (
    QAction,
    QMainWindow,
    QTreeWidget,
    QWidget,
    QVBoxLayout,
    QGraphicsOpacityEffect,
)

matplotlib.use("Qt5Agg")


class NoCoordsNavBar(NavigationToolbar):
    # Prevents the pop-up cursor coordinates from resizing the
    # main window canvas when the nav bar is placed on the
    # right-side of the canvas as a QtMenubar
    def set_message(self, s):
        pass


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


class ModifableTable(QTreeWidget):
    def __init__(self, parent=None):
        super(QTreeWidget, self).__init__(parent)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            item = self.currentItem()
            item_to_delete = self.takeTopLevelItem(self.indexOfTopLevelItem(item))
            item_to_delete.takeChildren()
        else:
            super().keyPressEvent(event)


class FigureWindow(QMainWindow):
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
        parent=None,
        outlier_mode=False,
    ):
        super(QMainWindow, self).__init__(parent)

        layout = QVBoxLayout()
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.fig = Figure(figsize=(width, height), dpi=dpi, constrained_layout=True)
        self.axes = self.fig.add_subplot(1, subplots, 1)

        if x is not None and y is not None:
            self.axes.plot(x, y, label=curve_label, picker=True, pickradius=5)

        if xlabel and ylabel:
            self.axes.set_xlabel(xlabel)
            self.axes.set_ylabel(ylabel)

        if curve_label:
            self.axes.legend()

        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        self.nav = NoCoordsNavBar(self.canvas, self)
        self.nav.setStyleSheet("QToolBar { border: 0px }")
        self.nav.installEventFilter(self)

        self.addToolBar(Qt.RightToolBarArea, self.nav)
        self.insertToolBarBreak(self.nav)

        self.opac = QGraphicsOpacityEffect()
        self.opac.setOpacity(0.3)
        self.nav.setGraphicsEffect(self.opac)

        if outlier_mode:
            self.fig.canvas.setFocusPolicy(Qt.ClickFocus)
            self.fig.canvas.setFocus()
            self.x_annot, self.y_annot = 0.0, 0.0
            self.xoffset, self.yoffset = -20, 20
            self.text_template = "x: %0.2f\ny: %0.2f"

            self.outlier = None
            self.line = self.axes.lines[0]
            self.x_data = list(self.line.get_xdata())
            self.y_data = list(self.line.get_ydata())

            self.annotation = self.axes.annotate(
                self.text_template,
                xy=(self.x_annot, self.y_annot),
                xytext=(self.xoffset, self.yoffset),
                textcoords="offset points",
                ha="right",
                va="bottom",
                bbox=dict(boxstyle="round,pad=0.5", fc="yellow", alpha=0.8),
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"),
            )
            self.annotation.set_visible(False)

            self.fig.canvas.mpl_connect("pick_event", self.point_pick)
            self.fig.canvas.mpl_connect("key_press_event", self.delete_outlier)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Enter:
            self.opac.setOpacity(1.0)
            self.nav.setGraphicsEffect(self.opac)
            return True
        elif event.type() == QEvent.Leave:
            self.opac.setOpacity(0.3)
            self.nav.setGraphicsEffect(self.opac)
        return False

    def point_pick(self, event):
        if isinstance(event.artist, Line2D):
            self.artist = event.artist
            self.outlier = event.ind[0]
            self.x_annot, self.y_annot = (
                self.artist.get_xdata()[event.ind[0]],
                self.artist.get_ydata()[event.ind[0]],
            )
            self.annotation.xy = (self.x_annot, self.y_annot)
            self.annotation.set_text(self.text_template % (self.x_annot, self.y_annot))
            self.annotation.set_visible(True)
            event.canvas.draw_idle()

    def delete_outlier(self, event):
        if event.key == "delete" and self.outlier is not None:
            self.x_data.pop(self.outlier)
            self.y_data.pop(self.outlier)
            self.line.set_data(self.x_data, self.y_data)
            self.outlier = None
            self.annotation.set_visible(False)
            self.axes.relim()
            self.axes.autoscale_view()
            event.canvas.draw_idle()


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
