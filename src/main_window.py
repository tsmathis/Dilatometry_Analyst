from ui_elements import BaseWindow, FigureWindow
from aggregate_window import AggregateWindow
from derivative_window import DerivativeWindow
from file_export import export_data
from spinner_widget import QtWaitingSpinner

from PyQt5.QtCore import Qt, QThreadPool, QRunnable, QObject, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QFileDialog,
    QPushButton,
    QLabel,
    QTabWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedLayout,
    QWidget,
)


class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str, str)


class Worker(QRunnable):
    def __init__(self, dialog, file_name, export_data):
        super(Worker, self).__init__()
        self.signals = WorkerSignals()
        self.w = dialog
        self.file_name = file_name
        self.data_to_export = export_data

    def run(self):
        try:
            export_data(
                norm_file=f"{self.file_name}_Normalized_data",
                baseline_file=f"{self.file_name}_Data_minus_baseline",
                average_file=f"{self.file_name}_Averaged_data",
                processed_data=self.data_to_export,
            )

        except:
            pass

        else:
            self.signals.finished.emit()


class MainWindow(BaseWindow):
    def __init__(self, processed_data_dict, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setWindowTitle("Dilatometry Analyst")
        self.setMinimumSize(1200, 677)

        self.processed_data = processed_data_dict
        self.tab_stacks = {}

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

        self.export_button = QPushButton("Export Data")
        self.export_button.setFixedHeight(41)
        self.export_button.setFont(QFont("Arial", 11))
        self.export_button.setStyleSheet("background-color: #007AFF")
        self.export_button.clicked.connect(self.get_export_location)
        bottom_buttons.addWidget(self.export_button)

        container = QWidget()
        container.setLayout(self.page_layout)

        stack = QWidget()
        self.stack_layout = QStackedLayout()
        self.stack_layout.setStackingMode(QStackedLayout.StackAll)
        stack.setLayout(self.stack_layout)

        self.stack_layout.addWidget(container)
        self.spinner = QtWaitingSpinner(self, True, True, Qt.ApplicationModal)
        self.stack_layout.addWidget(self.spinner)

        self.setCentralWidget(stack)
        self.threadpool = QThreadPool()

        file_label = QLabel(parent=container, text="Data:")
        file_label.setFixedHeight(41)
        file_label.setFixedWidth(49)
        file_label.move(10, 15)
        file_label.setFont(QFont("Arial", 10))
        file_label.setAlignment(Qt.AlignCenter)

    def initialize_window(self):
        idx = 0
        for key in self.processed_data:
            preview = QWidget()
            stack = QStackedLayout()
            preview.setLayout(stack)

            self.tab_stacks[idx] = stack
            idx += 1

            norm_widget = FigureWindow(
                x=self.processed_data[key].data["time/s"],
                y=self.processed_data[key].data["Percent change displacement (total)"],
                xlabel="Time (s)",
                ylabel="Relative Displacement (%)",
                title=key,
            )

            stack.addWidget(norm_widget)

            baseline_widget = FigureWindow(
                x=self.processed_data[key].data_minus_baseline["time/s"],
                y=self.processed_data[key].data_minus_baseline[
                    "Percent change minus baseline"
                ],
                xlabel="Time (s)",
                ylabel="Relative Displacement (%)",
                title=key,
            )
            stack.addWidget(baseline_widget)

            avg_widget = FigureWindow(
                x=self.processed_data[key].averaged_data["Average Potential (V)"],
                y=self.processed_data[key].averaged_data["Average Current (mA)"],
                xlabel="Potential (V)",
                ylabel="Averaged Current (mA)",
                subplots=3,
            )

            avg_plot_midpoint = (
                avg_widget.fig.subplotpars.right + avg_widget.fig.subplotpars.left
            ) / 2

            avg_widget.fig.suptitle(key, x=avg_plot_midpoint)

            avg_widget.axes.errorbar(
                self.processed_data[key].averaged_data["Average Potential (V)"],
                self.processed_data[key].averaged_data["Average Current (mA)"],
                yerr=self.processed_data[key].averaged_data["Current Stand Dev (mA)"],
                color="tab:blue",
                alpha=0.2,
            )

            axes2 = avg_widget.fig.add_subplot(1, 3, 2)

            axes2.plot(
                self.processed_data[key].averaged_data["Average Time (s)"],
                self.processed_data[key].averaged_data["Average Displacement (%)"],
            )
            axes2.errorbar(
                self.processed_data[key].averaged_data["Average Time (s)"],
                self.processed_data[key].averaged_data["Average Displacement (%)"],
                yerr=self.processed_data[key].averaged_data[
                    "Displacement Stand Dev (%)"
                ],
                errorevery=2,
                color="tab:blue",
                alpha=0.05,
            )
            axes2.set_xlabel("Time (s)")
            axes2.set_ylabel("Averaged Relative Displacement (%)")

            axes3 = avg_widget.fig.add_subplot(1, 3, 3)
            axes3.plot(
                self.processed_data[key].averaged_data["Average Potential (V)"],
                self.processed_data[key].averaged_data["Average Displacement (%)"],
            )
            axes3.errorbar(
                self.processed_data[key].averaged_data["Average Potential (V)"],
                self.processed_data[key].averaged_data["Average Displacement (%)"],
                yerr=self.processed_data[key].averaged_data[
                    "Displacement Stand Dev (%)"
                ],
                errorevery=2,
                color="tab:blue",
                alpha=0.05,
            )

            axes3.set_xlabel("Potential (V)")
            axes3.set_ylabel("Averaged Relative Displacement (%)")

            stack.addWidget(avg_widget)
            self.tabs.addTab(preview, key)

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
        file_name, filters = QFileDialog.getSaveFileName(self, filter="Excel (*.xlsx)")
        if not file_name:
            return
        file_name = file_name.strip(".xlsx")

        self.stack_layout.setCurrentIndex(1)
        self.spinner.start()
        worker = Worker(
            dialog=self, file_name=file_name, export_data=self.processed_data
        )

        worker.signals.finished.connect(self.finish_processing)
        worker.signals.error.connect(self.process_error)
        self.threadpool.start(worker)

    def finish_processing(self):
        self.spinner.stop()

    def process_error(self, error, title):
        self.spinner.stop()
        # exception_handler(
        #     error=error,
        #     window_title=title,
        # )
