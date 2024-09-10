from PyQt5.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QDialog, QApplication, QPushButton, QHBoxLayout, QLineEdit
from PyQt5 import QtCore, QtGui, QtWidgets

class PageWindow(QMainWindow):
    gotoSignal = QtCore.pyqtSignal(str)

    def goto(self, name):
        self.gotoSignal.emit(name)