from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QDialog, QApplication, QPushButton, QHBoxLayout, QLineEdit
from PyQt5.QtGui import QFont
from ui.page_window import PageWindow
from ui.search_window import SearchWindow
from ui.start_window import StartWindow
from ui.registration_window import RegistrationWindow
from ui.courses_window import CourseWindow

class Window(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.stacked_widget = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.m_pages = {}

        self.register(RegistrationWindow(), "reg")
        self.register(StartWindow(), "main")
        self.register(SearchWindow(), "search")
        self.register(CourseWindow(), "course")

        self.goto("main")

    def register(self, widget, name):
        self.m_pages[name] = widget
        self.stacked_widget.addWidget(widget)
        if isinstance(widget, PageWindow):
            widget.gotoSignal.connect(self.goto)

    @QtCore.pyqtSlot(str)
    def goto(self, name):
        if name in self.m_pages:
            widget = self.m_pages[name]
            self.stacked_widget.setCurrentWidget(widget)
            self.setWindowTitle(widget.windowTitle())


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec_())
