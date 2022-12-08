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
    QVBoxLayout,
    QHBoxLayout,
    QStackedLayout,
    QWidget,
)

colorcet_cmaps = {
    "Linear Fire": cc.m_CET_L4,
    "Linear Cobalt": cc.m_CET_CBL3,
    "Linear Green": cc.m_kgy,
    "Linear Black-Blue": cc.m_kb,
    "Linear Black-Cyan": cc.m_CET_CBTL3,
    "Linear Black-Green": cc.m_kg,
    "Linear Black-Red": cc.m_kr,
    "Linear BGY": cc.m_bgy,
    "Linear BMY": cc.m_bmy,
    "Rainbow": cc.m_rainbow4,
}


class AggregateWindow(QMainWindow):
    def __init__(self, aggregate_data):
        super().__init__()

        self.data = aggregate_data

        menu = self.menuBar()
        documentation_action = QAction("Documentation", self)
        documentation_action.triggered.connect(self.open_documentation)
        help_menu = menu.addMenu("Help")
        help_menu.addAction(documentation_action)

        self.setWindowTitle("Dilatometry Analyst: Aggregate Data")
        self.resize(1200, 677)

        page_layout = QHBoxLayout()
        button_layout = QVBoxLayout()
        self.stack_layout = QStackedLayout()

        self.color_dropdown = QComboBox()
        self.color_dropdown.addItems(
            [
                "Linear Fire",
                "Linear Cobalt",
                "Linear Green",
                "Linear Black-Blue",
                "Linear Black-Cyan",
                "Linear Black-Green",
                "Linear Black-Red",
                "Linear BGY",
                "Linear BMY",
                "Rainbow",
                "tab10",
                "tab20",
                "tab20b",
                "tab20c",
                "Set1",
                "Set2",
                "Set3",
                "Pastel1",
                "Pastel2",
                "Paired",
                "Accent",
                "Dark2",
            ]
        )

        self.color_dropdown.setCurrentIndex(10)
        button_layout.addWidget(self.color_dropdown)

        self.color_dropdown.currentIndexChanged.connect(self.update_plots)

        buttons = QWidget()
        stack = QWidget()
        stack.setMinimumSize(400, 400)
        stack.setLayout(self.stack_layout)
        buttons.setLayout(button_layout)
        buttons.setFixedWidth(175)

        keys = ["CVs", "disp_V", "disp_Q"]
        self.main_displays = {}
        self.preview_widgets = {}

        button_labels = [
            QLabel("Voltammograms"),
            QLabel("Disp. vs. V"),
            QLabel("Disp. vs. Q"),
        ]

        for i, key in enumerate(keys):
            fig = MplCanvas()
            fig_toolbar = NavigationToolbar(fig, self)
            window = QWidget()
            window_layout = QVBoxLayout()
            window.setLayout(window_layout)
            window_layout.addWidget(fig_toolbar)
            window_layout.addWidget(fig)
            self.stack_layout.addWidget(window)
            self.main_displays[key] = fig

            button = ClickableWidget(idx=i)
            button.clicked.connect(self.change_active_view)
            button_layout.addWidget(button_labels[i])
            button_labels[i].setFont(QFont("Arial", 12))
            button_labels[i].setAlignment(Qt.AlignCenter)
            button_layout.addWidget(button)
            self.preview_widgets[key] = button

        page_layout.addWidget(stack)
        page_layout.addWidget(buttons)

        export = QPushButton("Export Data")
        export.setStyleSheet("background-color: #007AFF")
        export.clicked.connect(self.get_export_location)
        button_layout.addWidget(export)

        widget = QWidget()
        widget.setLayout(page_layout)
        self.setCentralWidget(widget)

    def open_documentation(self):
        QDesktopServices.openUrl(
            QUrl("https://github.com/tsmathis/dilatometry_analyst/blob/main/README.md")
        )

    def change_active_view(self, clicked):
        self.stack_layout.setCurrentIndex(clicked)

    def update_plots(self):
        color_cat = self.color_dropdown.currentText()
        if color_cat in colorcet_cmaps:
            color_cat = colorcet_cmaps[color_cat]

        plt.rcParams["axes.prop_cycle"] = get_color_cycle(color_cat, len(self.data))
        colors = [color for color in plt.rcParams["axes.prop_cycle"]]

        # Clear all current axes to allow for updates
        self.main_displays["CVs"].axes.clear()
        self.preview_widgets["CVs"].axes.clear()

        self.main_displays["disp_V"].axes.clear()
        self.preview_widgets["disp_V"].axes.clear()

        self.main_displays["disp_Q"].axes.clear()
        self.preview_widgets["disp_Q"].axes.clear()

        # Replot updated data
        for i, key in enumerate(self.data):
            self.main_displays["CVs"].axes.plot(
                self.data[key].averaged_data["Average Potential (V)"],
                self.data[key].averaged_data["Average Current (mA)"],
                color=colors[i]["color"],
                label=key,
            )
            self.main_displays["CVs"].axes.legend()
            self.main_displays["CVs"].axes.set_xlabel("Potential (V)")
            self.main_displays["CVs"].axes.set_ylabel("Average Current (mA)")

            self.preview_widgets["CVs"].axes.plot(
                self.data[key].averaged_data["Average Potential (V)"],
                self.data[key].averaged_data["Average Current (mA)"],
                color=colors[i]["color"],
            )

        for i, key in enumerate(self.data):
            self.main_displays["disp_V"].axes.plot(
                self.data[key].averaged_data["Average Potential (V)"],
                self.data[key].averaged_data["Average Displacement (%)"],
                color=colors[i]["color"],
                label=key,
            )
            self.main_displays["disp_V"].axes.legend()
            self.main_displays["disp_V"].axes.set_xlabel("Potential (V)")
            self.main_displays["disp_V"].axes.set_ylabel("Average Displacement (%)")

            self.preview_widgets["disp_V"].axes.plot(
                self.data[key].averaged_data["Average Potential (V)"],
                self.data[key].averaged_data["Average Displacement (%)"],
                color=colors[i]["color"],
            )

        for i, key in enumerate(self.data):
            self.main_displays["disp_Q"].axes.plot(
                self.data[key].averaged_data["Average Charge (C)"],
                self.data[key].averaged_data["Average Displacement (%)"],
                color=colors[i]["color"],
                label=key,
            )
            self.main_displays["disp_Q"].axes.legend()
            self.main_displays["disp_Q"].axes.set_xlabel("Charge (C)")
            self.main_displays["disp_Q"].axes.set_ylabel("Average Displacement (%)")

            self.preview_widgets["disp_Q"].axes.plot(
                self.data[key].averaged_data["Average Charge (C)"],
                self.data[key].averaged_data["Average Displacement (%)"],
                color=colors[i]["color"],
            )

        # Update displayed plots in GUI
        self.main_displays["CVs"].draw_idle()
        self.preview_widgets["CVs"].draw_idle()

        self.main_displays["disp_V"].draw_idle()
        self.preview_widgets["disp_V"].draw_idle()

        self.main_displays["disp_Q"].draw_idle()
        self.preview_widgets["disp_Q"].draw_idle()

    def get_export_location(self):
        pass
