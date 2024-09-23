from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QDialog, QApplication, QPushButton, QHBoxLayout, QLineEdit
from PyQt5.QtGui import QFont
from ui.page_window import PageWindow
from ui.start_window import StartWindow
from ui.registration_window import RegistrationWindow
from ui.courses_window import CourseWindow
from ui.login_window import LoginWindow
from ui.course_editor import CourseEditor
from ui.test_editor import TestEditor
from ui.course_viewer import CourseViewer
from ui.test_viewer import TestViewer
from ui.attempts_view import AttemptViewer
from models.database import DatabaseManager


class Window(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.stacked_widget = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.m_pages = {}

        self.register(RegistrationWindow(), "registration")
        self.register(StartWindow(), "main")
        self.register(CourseWindow(), "course")
        self.register(LoginWindow(), "login")
        self.register(CourseEditor(), "course_editor")
        self.register(TestEditor(), "test_editor")
        self.register(CourseViewer(), "course_viewer")
        self.register(TestViewer(), "test_viewer")
        self.register(AttemptViewer(), "attempt_viewer")
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
            widget.initUI()
            self.stacked_widget.setCurrentWidget(widget)
            self.setWindowTitle(widget.windowTitle())
