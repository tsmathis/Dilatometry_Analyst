from ui_elements import BaseWindow, FigureWindow

from PyQt5.QtWidgets import (
    QGridLayout,
    QWidget,
)


class DerivativeWindow(BaseWindow):
    def __init__(self, derivative_data, parent=None):
        super(DerivativeWindow, self).__init__(parent)

        self.data = derivative_data

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
                outlier_mode=True,
            )

            dDdt_vs_i = FigureWindow(
                x=self.data[key].averaged_data["Average Current (mA)"],
                y=self.data[key].averaged_data["dD/dt"] * -1,
                xlabel="Current (mA)",
                ylabel="-dD/dt ($\mu$m/s)",
                curve_label=key,
                outlier_mode=True,
            )

            page_layout.addWidget(dDdt_vs_V, 0, i)
            page_layout.addWidget(dDdt_vs_i, 1, i)

        widget = QWidget()
        widget.setLayout(page_layout)
        self.setCentralWidget(widget)
