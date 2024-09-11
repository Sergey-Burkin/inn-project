from ui.page_window import PageWindow
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QDialog, QApplication, QPushButton, QHBoxLayout, QLineEdit
from PyQt5.QtGui import QFont
from PyQt5 import QtCore, QtGui, QtWidgets

class StartWindow(PageWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.UiComponents()

    def UiComponents(self):
        self.setWindowTitle("Welcome")
        self.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        label = QLabel("Welcome to the Main Window!")
        label.setFont(QFont("Arial", 24))
        layout.addWidget(label)
        
        
        button_layout = QVBoxLayout()
        register_button = QPushButton("Register")
        login_button = QPushButton("Login")
        
        register_button.clicked.connect(lambda: self.goto("registration"))
        login_button.clicked.connect(lambda: self.goto("login"))
        
        button_layout.addWidget(register_button)
        button_layout.addWidget(login_button)
        
        layout.addLayout(button_layout)