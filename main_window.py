import os
import matplotlib
import numpy as np
import textwrap

from ui_elements import MplCanvas, MultiMplCanvas
from aggregate_window import AggregateWindow
from derivative_window import DerivativeWindow

from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QFont, QDesktopServices
from PyQt5.QtWidgets import (
    QAction,
    QFileDialog,
    QMainWindow,
    QPushButton,
    QLabel,
    QTabWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedLayout,
    QWidget,
    QMessageBox,
)

matplotlib.use("Qt5Agg")


class MainWindow(QMainWindow):
    def __init__(self, processed_data_dict):
        super().__init__()

        self.processed_data = processed_data_dict
        self.tab_stacks = {}

        menu = self.menuBar()
        documentation_action = QAction("Documentation", self)
        documentation_action.triggered.connect(self.open_documentation)
        help_menu = menu.addMenu("Help")
        help_menu.addAction(documentation_action)

        self.setWindowTitle("Dilatometry Analyst")
        self.resize(1200, 677)

        self.page_layout = QVBoxLayout()
        bottom_buttons = QHBoxLayout()
        self.tabs = QTabWidget()
        self.page_layout.setContentsMargins(10, 10, 10, 10)
        self.page_layout.addWidget(self.tabs)
        self.page_layout.addLayout(bottom_buttons)

        self.tabs.setStyleSheet(
            """
            QTabWidget::tab-bar{
                left: 55px
                }
                
            QTabBar::tab{
                height: 51px;
                width: 100px;
                font-size: 10pt
                }
        """
        )

        self.norm_button = QPushButton("Normalized Data")
        self.norm_button.setFixedHeight(41)
        self.norm_button.setFont(QFont("Arial", 9))
        self.norm_button.pressed.connect(self.show_norm_data)
        bottom_buttons.addWidget(self.norm_button)

        self.baseline_button = QPushButton("Baseline Subtracted")
        self.baseline_button.setFixedHeight(41)
        self.baseline_button.setFont(QFont("Arial", 9))
        self.baseline_button.pressed.connect(self.show_base_data)
        bottom_buttons.addWidget(self.baseline_button)

        self.averages_button = QPushButton("Averaged Data Preview")
        self.averages_button.setFixedHeight(41)
        self.averages_button.setFont(QFont("Arial", 9))
        self.averages_button.pressed.connect(self.show_avg_data)
        bottom_buttons.addWidget(self.averages_button)

        spacer_1 = QWidget()
        bottom_buttons.addWidget(spacer_1)

        self.aggregate_button = QPushButton("Aggregate Data")
        self.aggregate_button.setFixedHeight(41)
        self.aggregate_button.setMaximumWidth(151)
        self.aggregate_button.setFont(QFont("Arial", 11))
        self.aggregate_button.clicked.connect(self.show_aggregate_data)
        bottom_buttons.addWidget(self.aggregate_button)

        self.derivative_button = QPushButton("Displacement Derivatives")
        self.derivative_button.setFixedHeight(41)
        self.derivative_button.setFont(QFont("Arial", 11))
        self.derivative_button.clicked.connect(self.show_derivative_data)
        bottom_buttons.addWidget(self.derivative_button)

        container = QWidget()
        container.setLayout(self.page_layout)
        self.setCentralWidget(container)

        file_label = QLabel(parent=container, text="Data:")
        file_label.setFixedHeight(41)
        file_label.setFixedWidth(49)
        file_label.move(10, 15)
        file_label.setFont(QFont("Arial", 10))
        file_label.setAlignment(Qt.AlignCenter)

    def open_documentation(self):
        QDesktopServices.openUrl(
            QUrl("https://github.com/tsmathis/dilatometry_analyst/blob/main/README.md")
        )

    def initialize_window(self):
        idx = 0
        for key in self.processed_data:
            preview = QWidget()
            stack = QStackedLayout()
            preview.setLayout(stack)

            self.tab_stacks[idx] = stack
            idx += 1

            norm_widget = QWidget()
            norm_layout = QVBoxLayout()
            norm_widget.setLayout(norm_layout)
            norm_preview = MplCanvas()
            norm_toolbar = NavigationToolbar(norm_preview, self)
            norm_preview.axes.plot(
                self.processed_data[key].data["time/s"],
                self.processed_data[key].data["Percent change displacement (total)"],
            )
            norm_preview.axes.set_xlabel("Time (s)")
            norm_preview.axes.set_ylabel("Relative Displacement (%)")
            norm_layout.addWidget(norm_toolbar)
            norm_layout.addWidget(norm_preview)
            stack.addWidget(norm_widget)

            baseline_widget = QWidget()
            baseline_layout = QVBoxLayout()
            baseline_widget.setLayout(baseline_layout)
            baseline_preview = MplCanvas()
            baseline_toolbar = NavigationToolbar(baseline_preview, self)
            baseline_preview.axes.plot(
                self.processed_data[key].data_minus_baseline["time/s"],
                self.processed_data[key].data_minus_baseline[
                    "Percent change minus baseline"
                ],
            )
            baseline_preview.axes.set_xlabel("Time (s)")
            baseline_preview.axes.set_ylabel("Relative Displacement (%)")
            baseline_layout.addWidget(baseline_toolbar)
            baseline_layout.addWidget(baseline_preview)
            stack.addWidget(baseline_widget)

            avg_widget = QWidget()
            avg_layout = QVBoxLayout()
            avg_widget.setLayout(avg_layout)
            avg_preview = MultiMplCanvas()
            avg_toolbar = NavigationToolbar(avg_preview, self)

            avg_preview.axes1.plot(
                self.processed_data[key].averaged_data["Average Potential (V)"],
                self.processed_data[key].averaged_data["Average Current (mA)"],
            )
            avg_preview.axes1.fill_between(
                self.processed_data[key].averaged_data["Average Potential (V)"],
                (
                    self.processed_data[key].averaged_data["Average Current (mA)"]
                    + self.processed_data[key].averaged_data["Current Stand Dev (mA)"]
                ),
                (
                    self.processed_data[key].averaged_data["Average Current (mA)"]
                    - self.processed_data[key].averaged_data["Current Stand Dev (mA)"]
                ),
                alpha=0.4,
            )
            avg_preview.axes1.set_xlabel("Potential (V)")
            avg_preview.axes1.set_ylabel("Averaged Current (mA)")

            avg_preview.axes2.plot(
                self.processed_data[key].averaged_data["Average Time (s)"],
                self.processed_data[key].averaged_data["Average Displacement (%)"],
            )
            avg_preview.axes2.fill_between(
                self.processed_data[key].averaged_data["Average Time (s)"],
                (
                    self.processed_data[key].averaged_data["Average Displacement (%)"]
                    + self.processed_data[key].averaged_data[
                        "Displacement Stand Dev (%)"
                    ]
                ),
                (
                    self.processed_data[key].averaged_data["Average Displacement (%)"]
                    - self.processed_data[key].averaged_data[
                        "Displacement Stand Dev (%)"
                    ]
                ),
                alpha=0.4,
            )
            avg_preview.axes2.set_xlabel("Time (s)")
            avg_preview.axes2.set_ylabel("Averaged Relative Displacement (%)")

            avg_preview.axes3.plot(
                self.processed_data[key].averaged_data["Average Potential (V)"],
                self.processed_data[key].averaged_data["Average Displacement (%)"],
            )
            x = self.processed_data[key].averaged_data["Average Potential (V)"]
            y = self.processed_data[key].averaged_data["Average Displacement (%)"]
            err = self.processed_data[key].averaged_data["Displacement Stand Dev (%)"]
            self.draw_error_band(
                ax=avg_preview.axes3, x=x, y=y, err=err, edgecolor="none", alpha=0.4
            )
            avg_preview.axes3.set_xlabel("Potential (V)")
            avg_preview.axes3.set_ylabel("Averaged Relative Displacement (%)")
            avg_layout.addWidget(avg_toolbar)
            avg_layout.addWidget(avg_preview)
            stack.addWidget(avg_widget)

            self.tabs.addTab(preview, key)

    def draw_error_band(self, ax, x, y, err, **kwargs):
        # Calculate normals via centered finite differences (except the first point
        # which uses a forward difference and the last point which uses a backward
        # difference).
        x = np.array(x)
        y = np.array(y)
        dx = np.concatenate([[x[1] - x[0]], x[2:] - x[:-2], [x[-1] - x[-2]]])
        dy = np.concatenate([[y[1] - y[0]], y[2:] - y[:-2], [y[-1] - y[-2]]])
        l = np.hypot(dx, dy)
        ny = -dx / l

        # end points of errors
        yp = y + ny * err
        yn = y - ny * err

        vertices = np.block([[x, x[::-1]], [yp, yn[::-1]]]).T
        codes = np.full(len(vertices), Path.LINETO)
        codes[0] = codes[len(x)] = Path.MOVETO
        path = Path(vertices, codes)
        ax.add_patch(PathPatch(path, **kwargs))

    def show_norm_data(self):
        idx = self.tabs.currentIndex()
        self.tab_stacks[idx].setCurrentIndex(0)

    def show_base_data(self):
        idx = self.tabs.currentIndex()
        self.tab_stacks[idx].setCurrentIndex(1)

    def show_avg_data(self):
        idx = self.tabs.currentIndex()
        self.tab_stacks[idx].setCurrentIndex(2)

    def show_aggregate_data(self):
        self.aggregate_window = AggregateWindow(aggregate_data=self.processed_data)
        self.aggregate_window.update_plots()
        self.aggregate_window.show()

    def show_derivative_data(self):
        self.derivative_window = DerivativeWindow(derivative_data=self.processed_data)
        self.derivative_window.show()

    def get_export_location(self):
        dialog = QFileDialog()
        folder_path = dialog.getExistingDirectory(None, "", directory=self.import_path)
        if not folder_path:
            return
        if folder_path:
            if os.path.exists(folder_path + "/Normalized dilatometry data.xlsx"):
                write_confirmed = QMessageBox.question(
                    self,
                    "Overwrite file?",
                    (
                        textwrap.dedent(
                            f"""\
                            The files: 
                            '{folder_path + '/Normalized dilatometry data.xlsx'}', 
                            '{folder_path + '/Dilatometry data minus baseline.xlsx'}',
                            and '{folder_path + '/Averaged dilatometry data.xlsx'}' already exist. 
                            Are you sure you want to overwrite them?"""
                        )
                    ),
                )
                if write_confirmed == QMessageBox.No:
                    return
            else:
                write_confirmed = True

        if write_confirmed:
            self.dilatometry_data.export_data(destination=folder_path + "/")
