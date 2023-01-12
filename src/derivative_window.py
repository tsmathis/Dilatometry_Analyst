from ui_elements import BaseWindow, FigureWindow

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QSizePolicy,
    QHBoxLayout,
    QVBoxLayout,
    QScrollArea,
    QWidget,
)


class DerivativeWindow(BaseWindow):
    def __init__(self, derivative_data, parent=None):
        super(DerivativeWindow, self).__init__(parent)

        self.data = derivative_data

        self.setWindowTitle("Dilatometry Analyst: Displacement Derivatives")
        self.resize(1400, 877)

        scrolling_widget = QWidget()
        scroll_layout = QHBoxLayout()
        scrolling_widget.setLayout(scroll_layout)

        for key in self.data:
            dDdt_vs_V = FigureWindow(
                width=3,
                height=3,
                x=self.data[key].averaged_data["Average Potential (V)"],
                y=self.data[key].averaged_data["dD/dt"],
                xlabel="Potential (V)",
                ylabel="dD/dt ($\mu$m/s)",
                curve_label=key,
                smoothing=True,
            )

            dDdt_vs_i = FigureWindow(
                width=3,
                height=3,
                x=self.data[key].averaged_data["Average Current (mA)"],
                y=self.data[key].averaged_data["dD/dt"] * -1,
                xlabel="Current (mA)",
                ylabel="-dD/dt ($\mu$m/s)",
                curve_label=key,
                smoothing=True,
            )

            container = QWidget()
            container_layout = QVBoxLayout()
            container.setLayout(container_layout)
            container.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

            container_layout.addWidget(dDdt_vs_V)
            container_layout.addWidget(dDdt_vs_i)
            scroll_layout.addWidget(container)

        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setWidgetResizable(True)
        scroll.setWidget(scrolling_widget)

        self.setCentralWidget(scroll)
