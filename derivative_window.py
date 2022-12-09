import colorcet as cc
import matplotlib.pyplot as plt

from ui_elements import MplCanvas, ClickableWidget
from plotting_utils import get_color_cycle
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QFont, QDesktopServices
from PyQt5.QtWidgets import (
    QAction,
    QMainWindow,
    QPushButton,
    QComboBox,
    QLabel,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
    QStackedLayout,
    QWidget,
)


class DerivativeWindow(QMainWindow):
    def __init__(self, derivative_data):
        super().__init__()

        self.data = derivative_data

        menu = self.menuBar()
        documentation_action = QAction("Documentation", self)
        documentation_action.triggered.connect(self.open_documentation)
        help_menu = menu.addMenu("Help")
        help_menu.addAction(documentation_action)

        self.setWindowTitle("Dilatometry Analys: Displacement Derivatives")
        self.resize(1200, 677)

        page_layout = QGridLayout()

        for i, key in enumerate(self.data):
            dDdt_vs_V = MplCanvas()
            dDdt_V_toolbar = NavigationToolbar(dDdt_vs_V, self)
            window = QWidget()
            window_layout = QVBoxLayout()
            window.setLayout(window_layout)
            window_layout.addWidget(dDdt_V_toolbar)
            window_layout.addWidget(dDdt_vs_V)

            dDdt_vs_V.axes.plot(
                self.data[key].averaged_data["Average Potential (V)"],
                self.data[key].averaged_data["dD/dt"],
            )
            page_layout.addWidget(window, 0, i)

            dDdt_vs_i = MplCanvas()
            dDdt_i_toolbar = NavigationToolbar(dDdt_vs_i, self)
            window2 = QWidget()
            window_2_layout = QVBoxLayout()
            window2.setLayout(window_2_layout)
            window_2_layout.addWidget(dDdt_i_toolbar)
            window_2_layout.addWidget(dDdt_vs_i)

            dDdt_vs_i.axes.plot(
                self.data[key].averaged_data["Average Current (mA)"],
                self.data[key].averaged_data["dD/dt"] * -1,
            )
            page_layout.addWidget(window2, 1, i)

        widget = QWidget()
        widget.setLayout(page_layout)
        self.setCentralWidget(widget)

    def open_documentation(self):
        QDesktopServices.openUrl(
            QUrl("https://github.com/tsmathis/dilatometry_analyst/blob/main/README.md")
        )
