import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QDialog, QHBoxLayout
from PyQt5.QtCore import Qt
from ui.page_window import PageWindow
import settings
from models.database import DatabaseManager

class LoginWindow(PageWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Вход")
        self.setGeometry(300, 300, 300, 150)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        
        layout.addWidget(QLabel("Логин:"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Пароль:"))
        layout.addWidget(self.password_input)
        
        button_layout = QHBoxLayout()
        login_button = QPushButton("Войти")
        cancel_button = QPushButton("Отмена")
        
        login_button.clicked.connect(self.authenticate_user)
        cancel_button.clicked.connect(lambda x: self.goto("main"))
        
        button_layout.addWidget(login_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
    
    def authenticate_user(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Все поля обязательны!")
            return
        db_manager = DatabaseManager()
        if db_manager.authenticate_user(username, password):
            user = db_manager.get_user_by_username_or_email(username)
            if user:
                settings.current_user = user
                self.goto("course")
            else:
                QMessageBox.warning(self, "Ошибка", "Пользователь не найден или неправильный пароль.")
        else:
            QMessageBox.warning(self, "Ошибка", "Неправильный логин или пароль.")
