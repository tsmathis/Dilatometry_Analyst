#
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from PyQt5.QtCore import pyqtSignal, QEvent
from PyQt5.QtWidgets import QWidget, QLabel, QComboBox, QLineEdit, QHBoxLayout


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=12, height=6, dpi=150):
        fig = Figure(figsize=(width, height), dpi=dpi, constrained_layout=True)
        self.axes = fig.add_subplot()
        super().__init__(fig)


class MultiMplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=12, height=6, dpi=150):
        fig = Figure(figsize=(width, height), dpi=dpi, constrained_layout=True)
        self.axes1 = fig.add_subplot(1, 3, 1)
        self.axes2 = fig.add_subplot(1, 3, 2)
        self.axes3 = fig.add_subplot(1, 3, 3)
        super().__init__(fig)


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
