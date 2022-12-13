from ui_elements import FigureWindow

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import (
    QAction,
    QMainWindow,
    QGridLayout,
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
        self.resize(1400, 877)

        page_layout = QGridLayout()

        for i, key in enumerate(self.data):
            dDdt_vs_V = FigureWindow(
                x=self.data[key].averaged_data["Average Potential (V)"],
                y=self.data[key].averaged_data["dD/dt"],
                xlabel="Potential (V)",
                ylabel="dD/dt ($\mu$m/s)",
                curve_label=key,
            )

            dDdt_vs_i = FigureWindow(
                x=self.data[key].averaged_data["Average Current (mA)"],
                y=self.data[key].averaged_data["dD/dt"] * -1,
                xlabel="Current (mA)",
                ylabel="-dD/dt ($\mu$m/s)",
                curve_label=key,
            )

            page_layout.addWidget(dDdt_vs_V, 0, i)
            page_layout.addWidget(dDdt_vs_i, 1, i)

        widget = QWidget()
        widget.setLayout(page_layout)
        self.setCentralWidget(widget)

    def open_documentation(self):
        QDesktopServices.openUrl(
            QUrl("https://github.com/tsmathis/dilatometry_analyst/blob/main/README.md")
        )
