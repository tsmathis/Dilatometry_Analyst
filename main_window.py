from ui_elements import BaseWindow, FigureWindow
from aggregate_window import AggregateWindow
from derivative_window import DerivativeWindow
from file_export import export_data

from PyQt5.QtCore import Qt
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


class MainWindow(BaseWindow):
    def __init__(self, processed_data_dict, parent=None):
        super(MainWindow, self).__init__(parent)

        self.processed_data = processed_data_dict
        self.tab_stacks = {}

        self.setWindowTitle("Dilatometry Analyst")

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
        self.setCentralWidget(container)

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
            )

            stack.addWidget(norm_widget)

            baseline_widget = FigureWindow(
                x=self.processed_data[key].data_minus_baseline["time/s"],
                y=self.processed_data[key].data_minus_baseline[
                    "Percent change minus baseline"
                ],
                xlabel="Time (s)",
                ylabel="Relative Displacement (%)",
            )
            stack.addWidget(baseline_widget)

            avg_widget = FigureWindow(
                x=self.processed_data[key].averaged_data["Average Potential (V)"],
                y=self.processed_data[key].averaged_data["Average Current (mA)"],
                xlabel="Potential (V)",
                ylabel="Averaged Current (mA)",
                subplots=3,
            )

            axes2 = avg_widget.fig.add_subplot(1, 3, 2)

            axes2.plot(
                self.processed_data[key].averaged_data["Average Time (s)"],
                self.processed_data[key].averaged_data["Average Displacement (%)"],
            )
            axes2.set_xlabel("Time (s)")
            axes2.set_ylabel("Averaged Relative Displacement (%)")

            axes3 = avg_widget.fig.add_subplot(1, 3, 3)
            axes3.plot(
                self.processed_data[key].averaged_data["Average Potential (V)"],
                self.processed_data[key].averaged_data["Average Displacement (%)"],
            )

            axes3.set_xlabel("Potential (V)")
            axes3.set_ylabel("Averaged Relative Displacement (%)")

            stack.addWidget(avg_widget)
            self.tabs.addTab(preview, key)

            # avg_preview.axes1.fill_between(
            #     self.processed_data[key].averaged_data["Average Potential (V)"],
            #     (
            #         self.processed_data[key].averaged_data["Average Current (mA)"]
            #         + self.processed_data[key].averaged_data["Current Stand Dev (mA)"]
            #     ),
            #     (
            #         self.processed_data[key].averaged_data["Average Current (mA)"]
            #         - self.processed_data[key].averaged_data["Current Stand Dev (mA)"]
            #     ),
            #     alpha=0.4,
            # )

            # avg_preview.axes2.fill_between(
            #     self.processed_data[key].averaged_data["Average Time (s)"],
            #     (
            #         self.processed_data[key].averaged_data["Average Displacement (%)"]
            #         + self.processed_data[key].averaged_data[
            #             "Displacement Stand Dev (%)"
            #         ]
            #     ),
            #     (
            #         self.processed_data[key].averaged_data["Average Displacement (%)"]
            #         - self.processed_data[key].averaged_data[
            #             "Displacement Stand Dev (%)"
            #         ]
            #     ),
            #     alpha=0.4,
            # )

            # x = self.processed_data[key].averaged_data["Average Potential (V)"]
            # y = self.processed_data[key].averaged_data["Average Displacement (%)"]
            # err = self.processed_data[key].averaged_data["Displacement Stand Dev (%)"]
            # self.draw_error_band(
            #     ax=avg_preview.axes3, x=x, y=y, err=err, edgecolor="none", alpha=0.4
            # )

            # # avg_layout.addWidget(avg_toolbar)
            # avg_layout.addWidget(avg_preview)

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
        export_data(
            norm_file=f"{file_name}_Normalized_data",
            baseline_file=f"{file_name}_Data_minus_baseline",
            average_file=f"{file_name}_Averaged_data",
            processed_data=self.processed_data,
        )
