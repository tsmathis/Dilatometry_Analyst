from dilatometry import Dilatometry
from main_window import MainWindow

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QFont, QDesktopServices
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QAction,
    QLineEdit,
    QComboBox,
    QFileDialog,
    QTreeWidget,
    QHeaderView,
    QTreeWidgetItem,
    QMainWindow,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QMessageBox,
)


class FileDialog(QMainWindow):
    def __init__(self, parent=None):
        super(FileDialog, self).__init__(parent)

        self.setWindowTitle("Dilatometry Analyst: Data Import")
        self.setMinimumSize(600, 400)

        self.file_params = []
        self.processed_data = {}

        menu = self.menuBar()
        documentation_action = QAction("Documentation", self)
        documentation_action.triggered.connect(self.open_documentation)
        help_menu = menu.addMenu("Help")
        help_menu.addAction(documentation_action)

        layout = QVBoxLayout()

        top = QWidget()
        top.setFixedHeight(50)
        mid = QWidget()
        bot = QWidget()
        bot.setFixedHeight(50)

        layout.addWidget(top)
        layout.addWidget(mid)
        layout.addWidget(bot)

        top_layout = QHBoxLayout()
        self.mid_layout = QVBoxLayout()
        bottom_layout = QHBoxLayout()

        self.file_tree = QTreeWidget()
        self.file_tree.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.file_tree.setColumnCount(3)
        self.file_tree.setAlternatingRowColors(True)
        self.file_tree.setHeaderLabels(["Files", "File Label", "File Type"])
        self.file_tree.setColumnWidth(1, 80)
        self.file_tree.setColumnWidth(2, 120)
        header = self.file_tree.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setStretchLastSection(False)
        self.mid_layout.addWidget(self.file_tree)

        import_button = QPushButton("Add Files")
        import_button.setFixedWidth(100)
        import_button.clicked.connect(self.get_files)

        baseline_label = QLabel("Electrode Reference Thickness (<span>&mu;</span>m):")
        baseline_label.setFixedWidth(180)
        self.baseline_input = QLineEdit()
        self.baseline_input.setPlaceholderText("Electrode thickness")
        self.baseline_input.setFixedWidth(110)

        top_layout.addWidget(import_button)
        top_layout.addWidget(QWidget())
        top_layout.addWidget(baseline_label)
        top_layout.addWidget(self.baseline_input)

        mass = QLabel("Enter electrode mass:")
        volume = QLabel("Enter electrode volume:")
        area = QLabel("Enter electrode area:")
        self.process_btn = QPushButton("Process data")
        self.process_btn.setFixedWidth(120)
        self.process_btn.setStyleSheet("background-color: #007AFF")
        self.process_btn.setEnabled(False)
        self.process_btn.clicked.connect(self.process_data)

        bottom_layout.addWidget(mass)
        bottom_layout.addWidget(volume)
        bottom_layout.addWidget(area)
        bottom_layout.addWidget(self.process_btn)

        top.setLayout(top_layout)
        mid.setLayout(self.mid_layout)
        bot.setLayout(bottom_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def open_documentation(self):
        QDesktopServices.openUrl(
            QUrl("https://github.com/tsmathis/dilatometry_analyst/blob/main/README.md")
        )

    def get_files(self):
        files, _ = QFileDialog.getOpenFileNames(self)
        for idx, path in enumerate(files):
            item = QTreeWidgetItem(self.file_tree, [path, "Label"])
            item.setFlags(item.flags() | Qt.ItemIsEditable)

            file_type = QComboBox()
            file_type.addItems(
                ["CV - SuperCap", "CCCD - SuperCap", "CV - Battery", "CCCD - Battery"]
            )
            self.file_tree.setItemWidget(item, 2, file_type)

            self.file_params.append(item)

        self.process_btn.setEnabled(True)

    def process_data(self):
        ref_thickness = float(self.baseline_input.text())

        for idx in range(len(self.file_params)):
            file_key = self.file_params[idx].text(1)
            file_str = self.file_params[idx].text(0)

            data = Dilatometry(ref_thickness=ref_thickness)
            data.load_data(file_str=file_str)
            data.normalize_data()
            data.subtract_baseline()
            data.average_data()
            data.calc_derivatives()

            self.processed_data[file_key] = data

        self.main_window = MainWindow(processed_data_dict=self.processed_data)
        self.main_window.initialize_window()
        self.main_window.show()
