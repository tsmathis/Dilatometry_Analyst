import colorcet as cc
import matplotlib.pyplot as plt

from ui_elements import BaseWindow, FigureWindow, ClickableWidget
from plotting_utils import get_color_cycle

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
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


class AggregateWindow(BaseWindow):
    def __init__(self, aggregate_data, parent=None):
        super(AggregateWindow, self).__init__(parent)

        self.data = aggregate_data

        self.setWindowTitle("Dilatometry Analyst: Aggregate Data")
        self.resize(960, 677)

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

        keys = ["CVs", "disp_V", "disp_Q", "disp_t"]
        self.main_displays = {}
        self.preview_widgets = {}

        button_labels = [
            QLabel("Voltammograms"),
            QLabel("Disp. vs. V"),
            QLabel("Disp. vs. Q"),
            QLabel("Disp. vs. t"),
        ]

        for i, key in enumerate(keys):
            window = QWidget()
            window_layout = QVBoxLayout()
            window.setLayout(window_layout)

            fig = FigureWindow()

            window_layout.addWidget(fig)
            self.stack_layout.addWidget(window)
            self.main_displays[key] = fig

            button = ClickableWidget(idx=i)
            button.clicked.connect(self.change_active_view)
            self.preview_widgets[key] = button
            button_layout.addWidget(button)
            button_layout.addWidget(button_labels[i])
            button_labels[i].setFont(QFont("Arial", 12))
            button_labels[i].setAlignment(Qt.AlignCenter)

        page_layout.addWidget(stack)
        page_layout.addWidget(buttons)

        widget = QWidget()
        widget.setLayout(page_layout)
        self.setCentralWidget(widget)

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

        self.main_displays["disp_t"].axes.clear()
        self.preview_widgets["disp_t"].axes.clear()

        # Replot updated data
        for i, key in enumerate(self.data):
            self.main_displays["CVs"].axes.plot(
                self.data[key].averaged_data["Average Potential (V)"],
                self.data[key].averaged_data["Average Current (mA)"],
                color=colors[i]["color"],
                label=key,
            )
            self.main_displays["CVs"].axes.errorbar(
                self.data[key].averaged_data["Average Potential (V)"],
                self.data[key].averaged_data["Average Current (mA)"],
                yerr=self.data[key].averaged_data["Current Stand Dev (mA)"],
                alpha=0.2,
                color=colors[i]["color"],
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
            self.main_displays["disp_V"].axes.errorbar(
                self.data[key].averaged_data["Average Potential (V)"],
                self.data[key].averaged_data["Average Displacement (%)"],
                yerr=self.data[key].averaged_data["Displacement Stand Dev (%)"],
                errorevery=2,
                color=colors[i]["color"],
                alpha=0.05,
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
            self.main_displays["disp_Q"].axes.errorbar(
                self.data[key].averaged_data["Average Charge (C)"],
                self.data[key].averaged_data["Average Displacement (%)"],
                yerr=self.data[key].averaged_data["Displacement Stand Dev (%)"],
                errorevery=2,
                color=colors[i]["color"],
                alpha=0.05,
            )
            self.main_displays["disp_Q"].axes.legend()
            self.main_displays["disp_Q"].axes.set_xlabel("Charge (C)")
            self.main_displays["disp_Q"].axes.set_ylabel("Average Displacement (%)")

            self.preview_widgets["disp_Q"].axes.plot(
                self.data[key].averaged_data["Average Charge (C)"],
                self.data[key].averaged_data["Average Displacement (%)"],
                color=colors[i]["color"],
            )

        for i, key in enumerate(self.data):
            self.main_displays["disp_t"].axes.plot(
                self.data[key].averaged_data["Average Time (s)"],
                self.data[key].averaged_data["Average Displacement (%)"],
                color=colors[i]["color"],
                label=key,
            )
            self.main_displays["disp_t"].axes.errorbar(
                self.data[key].averaged_data["Average Time (s)"],
                self.data[key].averaged_data["Average Displacement (%)"],
                yerr=self.data[key].averaged_data["Displacement Stand Dev (%)"],
                errorevery=2,
                color=colors[i]["color"],
                alpha=0.05,
            )
            self.main_displays["disp_t"].axes.legend()
            self.main_displays["disp_t"].axes.set_xlabel("Time (s)")
            self.main_displays["disp_t"].axes.set_ylabel("Average Displacement (%)")

            self.preview_widgets["disp_t"].axes.plot(
                self.data[key].averaged_data["Average Time (s)"],
                self.data[key].averaged_data["Average Displacement (%)"],
                color=colors[i]["color"],
            )

        # Update displayed plots in GUI
        self.main_displays["CVs"].canvas.draw_idle()
        self.preview_widgets["CVs"].draw_idle()

        self.main_displays["disp_V"].canvas.draw_idle()
        self.preview_widgets["disp_V"].draw_idle()

        self.main_displays["disp_Q"].canvas.draw_idle()
        self.preview_widgets["disp_Q"].draw_idle()

        self.main_displays["disp_t"].canvas.draw_idle()
        self.preview_widgets["disp_t"].draw_idle()
