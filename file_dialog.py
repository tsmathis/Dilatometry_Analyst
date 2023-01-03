from dilatometry import Dilatometry
from ui_elements import BaseWindow, ModifableTable
from main_window import MainWindow
from spinner_widget import QtWaitingSpinner

from PyQt5.QtCore import Qt, QThreadPool, QRunnable, QObject, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QLineEdit,
    QComboBox,
    QFileDialog,
    QTreeWidget,
    QHeaderView,
    QTreeWidgetItem,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QStackedLayout,
    QWidget,
    QMessageBox,
)


class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str, str)
    result = pyqtSignal(object)


class Worker(QRunnable):
    def __init__(self, dialog, file_params, ref_thickness):
        super(Worker, self).__init__()
        self.signals = WorkerSignals()
        self.w = dialog
        self.file_params = file_params
        self.ref_thickness = ref_thickness

    def run(self):
        try:
            processed_data = {}
            for idx in range(len(self.file_params)):
                file_key = self.file_params[idx].text(1)
                file_str = self.file_params[idx].text(0)

                data = Dilatometry(ref_thickness=self.ref_thickness)
                data.load_data(file_str=file_str)
                data.normalize_data()
                data.subtract_baseline()
                data.average_data()
                data.calc_derivatives()

                processed_data[file_key] = data

        except:
            pass

        else:
            self.signals.result.emit(processed_data)
            self.signals.finished.emit()


class FileDialog(BaseWindow):
    def __init__(self, parent=None):
        super(FileDialog, self).__init__(parent)

        self.setWindowTitle("Dilatometry Analyst: Data Import")
        self.setMinimumSize(600, 400)

        text_font = QFont("Arial", 9)

        self.file_params = []

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

        self.file_tree = ModifableTable()
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
        import_button.setFont(text_font)
        import_button.setFixedWidth(100)
        import_button.clicked.connect(self.get_files)

        baseline_label = QLabel("Electrode Reference Thickness (<span>&mu;</span>m):")
        baseline_label.setFont(text_font)
        baseline_label.setFixedWidth(200)
        self.baseline_input = QLineEdit()
        self.baseline_input.setPlaceholderText("Electrode thickness")
        self.baseline_input.setFont(text_font)
        self.baseline_input.setFixedWidth(120)

        top_layout.addWidget(import_button)
        top_layout.addWidget(QWidget())
        top_layout.addWidget(baseline_label)
        top_layout.addWidget(self.baseline_input)

        mass = QLabel("Enter electrode mass:")
        volume = QLabel("Enter electrode volume:")
        area = QLabel("Enter electrode area:")

        mass.setFont(text_font)
        volume.setFont(text_font)
        area.setFont(text_font)

        self.process_btn = QPushButton("Process data")
        self.process_btn.setFixedWidth(120)
        self.process_btn.setFont(text_font)
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

        stack = QWidget()
        self.stack_layout = QStackedLayout()
        self.stack_layout.setStackingMode(QStackedLayout.StackAll)
        stack.setLayout(self.stack_layout)

        self.stack_layout.addWidget(container)
        self.spinner = QtWaitingSpinner(self, True, True, Qt.ApplicationModal)
        self.stack_layout.addWidget(self.spinner)

        self.setCentralWidget(stack)
        self.threadpool = QThreadPool()

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

        self.process_btn.setEnabled(True)

    def process_data(self):
        self.stack_layout.setCurrentIndex(1)
        self.spinner.start()

        root = self.file_tree.invisibleRootItem()
        child_count = root.childCount()
        for i in range(child_count):
            item = root.child(i)
            self.file_params.append(item)

        worker = Worker(
            dialog=self,
            file_params=self.file_params,
            ref_thickness=float(self.baseline_input.text()),
        )
        worker.signals.result.connect(self.set_data)
        worker.signals.finished.connect(self.finish_processing)
        worker.signals.error.connect(self.process_error)
        self.threadpool.start(worker)

    def set_data(self, processed_data):
        self.main_window = MainWindow(processed_data_dict=processed_data)
        self.main_window.initialize_window()
        self.main_window.show()

    def finish_processing(self):
        self.close()
        self.spinner.stop()

    def process_error(self, error, title):
        self.spinner.stop()
        # exception_handler(
        #     error=error,
        #     window_title=title,
        # )
