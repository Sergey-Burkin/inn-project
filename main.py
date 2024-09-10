from PyQt5.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QDialog, QApplication, QHBoxLayout, QPushButton
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import sys
from ui.registration_window import RegistrationWindow
from models.database import db_manager, hash_password, register_user

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
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
        
        button_layout = QHBoxLayout()
        register_button = QPushButton("Register")
        login_button = QPushButton("Login")
        
        register_button.clicked.connect(self.open_registration_window)
        # login_button.clicked.connect(self.open_login_window)
        
        button_layout.addWidget(register_button)
        button_layout.addWidget(login_button)
        
        layout.addLayout(button_layout)

    def open_registration_window(self):
        RegistrationWindow().show()

    # def open_login_window(self):
    #     LoginWindow().show()        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())