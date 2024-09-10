from ui.page_window import PageWindow
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QDialog, QApplication, QPushButton, QHBoxLayout, QLineEdit
from PyQt5.QtGui import QFont
from PyQt5 import QtCore, QtGui, QtWidgets

class SearchWindow(PageWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Search for something")
        self.UiComponents()

    def goToMain(self):
        self.goto("main")

    def UiComponents(self):
        self.backButton = QtWidgets.QPushButton("BackButton", self)
        self.backButton.setGeometry(QtCore.QRect(5, 5, 100, 20))
        self.backButton.clicked.connect(self.goToMain)