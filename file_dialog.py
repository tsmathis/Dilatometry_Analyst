from dilatometry import Dilatometry
from ui_elements import FileLabelCombo
from main_window import MainWindow

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
        mid = QWidget()
        bot = QWidget()

        layout.addWidget(top)
        layout.addWidget(mid)
        layout.addWidget(bot)

        top_layout = QHBoxLayout()
        self.mid_layout = QVBoxLayout()
        bottom_layout = QHBoxLayout()

        import_button = QPushButton("File Import")
        import_button.clicked.connect(self.get_files)

        baseline_label = QLabel("Baseline value:")
        self.baseline_input = QLineEdit("Enter a value in microns")

        top_layout.addWidget(import_button)
        top_layout.addWidget(baseline_label)
        top_layout.addWidget(self.baseline_input)

        mass = QLabel("Enter electrode mass:")
        volume = QLabel("Enter electrode volume:")
        area = QLabel("Enter electrode area:")
        process_btn = QPushButton("Process data")
        process_btn.clicked.connect(self.process_data)

        bottom_layout.addWidget(mass)
        bottom_layout.addWidget(volume)
        bottom_layout.addWidget(area)
        bottom_layout.addWidget(process_btn)

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
            disp = FileLabelCombo(file_text=path)
            self.file_params.append(disp)
            self.mid_layout.addWidget(disp)

    def process_data(self):
        ref_thickness = float(self.baseline_input.text())

        for idx in range(len(self.file_params)):
            file_key = self.file_params[idx].file_label.text()
            file_str = self.file_params[idx].file_text

            data = Dilatometry(ref_thickness=ref_thickness)
            data.load_data(file_str=file_str)
            data.normalize_data()
            data.subtract_baseline()
            data.average_data()
            data.calc_derivatives()

            self.processed_data[file_key] = data

            # print(self.file_params[key].file_type.currentText())

        self.main_window = MainWindow(processed_data_dict=self.processed_data)
        self.main_window.initialize_window()
        self.main_window.show()
