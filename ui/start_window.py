from ui.page_window import PageWindow
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QDialog, QApplication, QPushButton, QHBoxLayout, QLineEdit
from PyQt5.QtGui import QFont
from PyQt5 import QtCore, QtGui, QtWidgets

class StartWindow(PageWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setWindowTitle("StartWindow")

    def initUI(self):
        self.UiComponents()

    def UiComponents(self):
        self.setWindowTitle("Main Window")
        self.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        label = QLabel("Welcome to the Main Window!")
        label.setFont(QFont("Arial", 24))
        layout.addWidget(label)
        
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        self.registration_window = None

        button_layout = QHBoxLayout()
        register_button = QPushButton("Register")
        login_button = QPushButton("Login")
        
        register_button.clicked.connect(self.goto_search)
        # login_button.clicked.connect(lambda: LoginWindow().show())
        
        button_layout.addWidget(register_button)
        button_layout.addWidget(login_button)
        
        layout.addLayout(button_layout)

    def goto_search(self):
            self.goto("reg")

    def make_handleButton(self, button):
        def handleButton():
            if button == "searchButton":
                self.goto("search")
        return handleButton
