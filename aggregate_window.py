from collections import deque
from ui_elements import MplCanvas, ClickableWidget
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QFont, QDesktopServices
from PyQt5.QtWidgets import (
    QAction,
    QLineEdit,
    QFileDialog,
    QMainWindow,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QStackedLayout,
    QWidget,
    QMessageBox,
)


class AggregateWindow(QMainWindow):
    def __init__(self, aggregate_data):
        super().__init__()

        menu = self.menuBar()
        documentation_action = QAction("Documentation", self)
        documentation_action.triggered.connect(self.open_documentation)
        help_menu = menu.addMenu("Help")
        help_menu.addAction(documentation_action)

        self.setWindowTitle("Dilatometry Analyst")
        self.resize(1200, 677)

        page_layout = QHBoxLayout()
        button_layout = QVBoxLayout()
        self.stack_layout = QStackedLayout()

        buttons = QWidget()
        stack = QWidget()
        stack.setMinimumSize(400, 400)
        stack.setLayout(self.stack_layout)
        buttons.setLayout(button_layout)
        buttons.setFixedWidth(350)

        window_queue = deque(maxlen=3)

        for i in range(3):
            fig = MplCanvas()
            fig_toolbar = NavigationToolbar(fig, self)
            window = QWidget()
            window_layout = QVBoxLayout()
            window.setLayout(window_layout)
            window_layout.addWidget(fig_toolbar)
            window_layout.addWidget(fig)
            self.stack_layout.addWidget(window)
            window_queue.append(fig)

        widget_slot_queue = deque(maxlen=3)

        page_layout.addWidget(stack)
        page_layout.addWidget(buttons)

        for i in range(3):
            button = ClickableWidget(idx=i)
            button.clicked.connect(self.change_active_view)
            button_layout.addWidget(button)
            widget_slot_queue.append(button)

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

    def get_export_location(self):
        pass
