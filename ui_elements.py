#
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from PyQt5.QtCore import pyqtSignal, QEvent
from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QComboBox,
    QLineEdit,
    QHBoxLayout,
    QVBoxLayout,
    QGraphicsOpacityEffect,
)


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=12, height=6, dpi=150):
        fig = Figure(figsize=(width, height), dpi=dpi, constrained_layout=True)
        self.axes = fig.add_subplot()
        super().__init__(fig)


class FigureWindow(QWidget):
    def __init__(self, fig):
        QWidget.__init__(self)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        self.fig = fig
        self.canvas = FigureCanvas(fig)
        self.canvas.draw()

        self.canvas.mpl_connect("resize_event", self.resize)
        self.canvas.draw()
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


class MultiMplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=12, height=6, dpi=150):
        fig = Figure(figsize=(width, height), dpi=dpi, constrained_layout=True)
        self.axes1 = fig.add_subplot(1, 3, 1)
        self.axes2 = fig.add_subplot(1, 3, 2)
        self.axes3 = fig.add_subplot(1, 3, 3)
        super().__init__(fig)


# class HideableNavBar(NavigationToolbar):
#     def __init__(self, fig, parent=None):
#         super().__init__(fig)
#         self.fig = fig
#         self.hidden = True
#         self.fig.mpl_connect("resize_event", self.resize)
#         self.installEventFilter(self)

#     def resize(self, event):
#         # on resize reposition the navigation toolbar to (0,0) of the axes.
#         x, y = self.fig.axes[0].transAxes.transform((0, 0))
#         figw, figh = self.fig.get_size_inches()
#         ynew = figh * self.fig.dpi - y - self.frameGeometry().height()
#         self.move(x, ynew)

#     def eventFilter(self, obj, event):
#         if isinstance(obj, NavigationToolbar) and event.type() == QEvent.Enter:
#             if self.hidden:
#                 self.show()
#                 self.hidden = False
#             return True
#         elif event.type() == QEvent.Leave:
#             self.hide()
#             self.hidden = True
#         return False


class ClickableWidget(MplCanvas):
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
        if isinstance(obj, MplCanvas) and event.type() == QEvent.MouseButtonPress:
            self.clicked.emit(self.index)
        return QWidget.eventFilter(self, obj, event)


class FileLabelCombo(QWidget):
    def __init__(self, parent=None, file_text=None):
        QWidget.__init__(self, parent=parent)
        self.file_text = file_text
        self.setMinimumHeight(50)

        disp_text = ""
        limit = 40
        if len(file_text) > limit:
            disp_text = "..." + file_text[limit:]
        else:
            disp_text = file_text

        self.file_display = QLabel(disp_text)
        self.file_label = QLineEdit("Enter a file label, e.g., '5 mV/s', '0.5 C', etc.")
        self.file_label.setFixedWidth(60)
        self.file_type = QComboBox()
        self.file_type.setFixedWidth(60)
        self.file_type.addItems(["CV", "CCCD"])

        layout = QHBoxLayout(self)

        layout.addWidget(self.file_display)
        layout.addWidget(self.file_label)
        layout.addWidget(self.file_type)
