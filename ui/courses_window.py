import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QCheckBox, QRadioButton
from PyQt5.QtCore import Qt
from ui.page_window import PageWindow

from models.database import DatabaseManager

class CourseWindow(PageWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Регистрация")
        self.setGeometry(300, 300, 400, 250)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)

                
        label = QLabel("Text")
        label.setStyleSheet("font-size: 48pt; font-weight: bold;")
        
        layout.addWidget(label)