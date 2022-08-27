import sys, os, subprocess
import matplotlib
import numpy as np
import textwrap

from dilatometry_methods import Dilatometry
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QFont, QIcon, QDesktopServices
from PyQt5.QtWidgets import (
    QApplication,
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

FILEPATH = os.path.abspath(__file__)
basedir = os.path.dirname(__file__)

try:
    from ctypes import windll

    myappid = "diltometry_analyst.tylersmathis"
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass


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


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        menu = self.menuBar()
        documentation_action = QAction("Documentaion", self)
        documentation_action.triggered.connect(self.open_documentation)
        help_menu = menu.addMenu("Help")
        help_menu.addAction(documentation_action)

        self.dilatometry_data = Dilatometry()
        self.tab_stacks = {}
        self.norm_data = None
        self.data_minus_base = None
        self.avg_data = None

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
                left: 210px
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
        self.norm_button.setEnabled(False)
        bottom_buttons.addWidget(self.norm_button)

        self.baseline_button = QPushButton("Baseline Subtracted")
        self.baseline_button.setFixedHeight(41)
        self.baseline_button.setFont(QFont("Arial", 9))
        self.baseline_button.pressed.connect(self.show_base_data)
        self.baseline_button.setEnabled(False)
        bottom_buttons.addWidget(self.baseline_button)

        self.averages_button = QPushButton("Averaged Data Preview")
        self.averages_button.setFixedHeight(41)
        self.averages_button.setFont(QFont("Arial", 9))
        self.averages_button.pressed.connect(self.show_avg_data)
        self.averages_button.setEnabled(False)
        bottom_buttons.addWidget(self.averages_button)

        spacer_1 = QWidget()
        bottom_buttons.addWidget(spacer_1)

        reset_button = QPushButton("Reset")
        reset_button.setFixedHeight(41)
        reset_button.setMaximumWidth(151)
        reset_button.setFont(QFont("Arial", 9))
        reset_button.clicked.connect(self.reset_workspace)
        bottom_buttons.addWidget(reset_button)

        self.export_data = QPushButton("Export Data")
        self.export_data.setFixedHeight(41)
        self.export_data.setMaximumWidth(151)
        self.export_data.setFont(QFont("Arial", 11))
        self.export_data.clicked.connect(self.get_export_location)
        self.export_data.setEnabled(False)
        bottom_buttons.addWidget(self.export_data)

        container = QWidget()
        container.setLayout(self.page_layout)
        self.setCentralWidget(container)

        self.import_data = QPushButton(parent=container, text="Import Data")
        self.import_data.setFixedHeight(41)
        self.import_data.setFixedWidth(151)
        self.import_data.move(10, 10)
        self.import_data.setFont(QFont("Arial", 11))
        self.import_data.clicked.connect(self.load_data)

        file_label = QLabel(parent=container, text="Files:")
        file_label.setFixedHeight(41)
        file_label.setFixedWidth(49)
        file_label.move(165, 10)
        file_label.setFont(QFont("Arial", 10))
        file_label.setAlignment(Qt.AlignCenter)

    def open_documentation(self):
        QDesktopServices.openUrl(
            QUrl("https://github.com/tsmathis/dilatometry_analyst/blob/main/README.md")
        )

    def load_data(self):
        dialog = QFileDialog()
        self.import_path = dialog.getExistingDirectory(
            None, "", directory=os.path.expanduser("~")
        )
        if not self.import_path:
            return
        try:
            dila_files = self.dilatometry_data.load_files(file_path=self.import_path)
            if len(dila_files) == 0:
                raise Exception
            self.dilatometry_data.process_data(dila_files)
        except KeyError as e:
            dlg2 = QMessageBox(self)
            dlg2.setWindowTitle("File Content Error")
            dlg2.setText(
                textwrap.dedent(
                    """\
                    The imported files do not contain the required data or the column headers are not recognized. 

                    Check the Documentiation link in the "Help" menu for more information about the expected file contents."""
                )
            )
            dlg2.setIcon(QMessageBox.Warning)
            dlg2.setStandardButtons(QMessageBox.Ok)
            button = dlg2.exec_()
        except Exception as e:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("File Import Error")
            dlg.setText("No .txt files found to load!")
            dlg.setIcon(QMessageBox.Warning)
            dlg.setStandardButtons(QMessageBox.Ok)
            button = dlg.exec_()
        else:
            self.import_data.setEnabled(False)
            self.norm_button.setEnabled(True)
            self.baseline_button.setEnabled(True)
            self.averages_button.setEnabled(True)
            self.export_data.setEnabled(True)

            self.norm_data = self.dilatometry_data.normalized_data
            self.data_minus_base = self.dilatometry_data.data_minus_baseline
            self.avg_data = self.dilatometry_data.averaged_data

            for key in self.norm_data:
                preview = QWidget()
                stack = QStackedLayout()
                preview.setLayout(stack)

                self.tab_stacks[key] = stack

                norm_widget = QWidget()
                norm_layout = QVBoxLayout()
                norm_widget.setLayout(norm_layout)
                norm_preview = MplCanvas()
                norm_toolbar = NavigationToolbar(norm_preview, self)
                norm_preview.axes.plot(
                    self.norm_data[key]["time/s"],
                    self.norm_data[key]["normalized displacement"],
                )
                norm_preview.axes.set_xlabel("Time (s)")
                norm_preview.axes.set_ylabel("Displacement ($\mu$m)")
                norm_layout.addWidget(norm_toolbar)
                norm_layout.addWidget(norm_preview)
                stack.addWidget(norm_widget)

                baseline_widget = QWidget()
                baseline_layout = QVBoxLayout()
                baseline_widget.setLayout(baseline_layout)
                baseline_preview = MplCanvas()
                baseline_toolbar = NavigationToolbar(baseline_preview, self)
                baseline_preview.axes.plot(
                    self.data_minus_base[key]["time/s"],
                    self.data_minus_base[key]["disp minus baseline"],
                )
                baseline_preview.axes.set_xlabel("Time (s)")
                baseline_preview.axes.set_ylabel("Displacement ($\mu$m)")
                baseline_layout.addWidget(baseline_toolbar)
                baseline_layout.addWidget(baseline_preview)
                stack.addWidget(baseline_widget)

                avg_widget = QWidget()
                avg_layout = QVBoxLayout()
                avg_widget.setLayout(avg_layout)
                avg_preview = MultiMplCanvas()
                avg_toolbar = NavigationToolbar(avg_preview, self)

                avg_preview.axes1.plot(
                    self.avg_data[key]["Average Potential (V)"],
                    self.avg_data[key]["Average Current (mA)"],
                )
                avg_preview.axes1.fill_between(
                    self.avg_data[key]["Average Potential (V)"],
                    (
                        self.avg_data[key]["Average Current (mA)"]
                        + self.avg_data[key]["Current Stand Dev (mA)"]
                    ),
                    (
                        self.avg_data[key]["Average Current (mA)"]
                        - self.avg_data[key]["Current Stand Dev (mA)"]
                    ),
                    alpha=0.4,
                )
                avg_preview.axes1.set_xlabel("Potential (V)")
                avg_preview.axes1.set_ylabel("Averaged Current (mA)")

                avg_preview.axes2.plot(
                    self.avg_data[key]["Average Time (s)"],
                    self.avg_data[key]["Average Displacement (um)"],
                )
                avg_preview.axes2.fill_between(
                    self.avg_data[key]["Average Time (s)"],
                    (
                        self.avg_data[key]["Average Displacement (um)"]
                        + self.avg_data[key]["Displacement Stand Dev (um)"]
                    ),
                    (
                        self.avg_data[key]["Average Displacement (um)"]
                        - self.avg_data[key]["Displacement Stand Dev (um)"]
                    ),
                    alpha=0.4,
                )
                avg_preview.axes2.set_xlabel("Time (s)")
                avg_preview.axes2.set_ylabel("Averaged Displacement ($\mu$m)")

                avg_preview.axes3.plot(
                    self.avg_data[key]["Average Potential (V)"],
                    self.avg_data[key]["Average Displacement (um)"],
                )
                x = self.avg_data[key]["Average Potential (V)"]
                y = self.avg_data[key]["Average Displacement (um)"]
                err = self.avg_data[key]["Displacement Stand Dev (um)"]
                self.draw_error_band(
                    ax=avg_preview.axes3, x=x, y=y, err=err, edgecolor="none", alpha=0.4
                )
                avg_preview.axes3.set_xlabel("Potential (V)")
                avg_preview.axes3.set_ylabel("Averaged Displacement ($\mu$m)")
                avg_layout.addWidget(avg_toolbar)
                avg_layout.addWidget(avg_preview)
                stack.addWidget(avg_widget)

                self.tabs.addTab(preview, f"File {key + 1}")

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

    def reset_workspace(self):
        confirm_reset = QMessageBox.warning(
            self,
            "Reset Application?",
            textwrap.dedent(
                """\
                This operation will restart the application.
                All current data will be lost.
                
                Continue?
                """
            ),
            QMessageBox.Ok | QMessageBox.Cancel,
        )
        if confirm_reset == QMessageBox.Cancel:
            return
        else:
            subprocess.Popen([sys.executable, FILEPATH])
            sys.exit()

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


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setWindowIcon(QIcon(os.path.join(basedir, "dilatometry_icon.ico")))

    window = MainWindow()
    window.show()

    app.exec_()


if __name__ == "__main__":
    main()
