import sys, os

from file_dialog import FileDialog

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

FILEPATH = os.path.abspath(__file__)
basedir = os.path.dirname(__file__)

if hasattr(Qt, "AA_EnableHighDpiScaling"):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
if hasattr(Qt, "AA_UseHighDpiPixmaps"):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

try:
    from ctypes import windll

    myappid = "diltometry_analyst.tylersmathis"
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setWindowIcon(QIcon(os.path.join(basedir, "dilatometry_icon.ico")))

    window = FileDialog()
    window.show()

    app.exec_()


if __name__ == "__main__":
    main()
