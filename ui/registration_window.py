import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QCheckBox, QRadioButton
from PyQt5.QtCore import Qt
from ui.page_window import PageWindow

from models.database import DatabaseManager

class RegistrationWindow(PageWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Регистрация")
        self.setGeometry(300, 300, 400, 250)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)


 # Create radio buttons instead of checkboxes
        self.student_radio = QRadioButton("Студент")
        self.teacher_radio = QRadioButton("Учитель")
        
        # Make one button checked by default
        self.student_radio.setChecked(True)
        
        # Add radio buttons to the layout
        layout.addWidget(QLabel("Выберите роль:"))
        layout.addWidget(self.student_radio)
        layout.addWidget(self.teacher_radio)
        
        # Логин
        label_login = QLabel("Логин:")
        self.login_input = QLineEdit()
        layout.addWidget(label_login)
        layout.addWidget(self.login_input)
        
        # Email
        label_email = QLabel("Email:")
        self.email_input = QLineEdit()
        layout.addWidget(label_email)
        layout.addWidget(self.email_input)
        
        # Пароль
        label_password = QLabel("Пароль:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(label_password)
        layout.addWidget(self.password_input)
        
        # Подтвердение пароля
        label_confirm_password = QLabel("Подтвердить пароль:")
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(label_confirm_password)
        layout.addWidget(self.confirm_password_input)
        
        # Кнопка регистрации
        button_register = QPushButton("Зарегистрироваться")
        button_register.clicked.connect(self.register)
        layout.addWidget(button_register)
        
    
    def register(self):
        login = self.login_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        email = self.email_input.text()
        role = "student" if self.student_radio.isChecked() else "teacher"

        if not login or not password or not confirm_password or not email:
            QMessageBox.warning(self, "Ошибка", "Все поля обязательны!")
            return
        
        if password != confirm_password:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают!")
            return
        
        # Здесь можно добавить логику регистрации
        print(f"Попытка регистрации пользователя: {login}, email: {email}")
        
        # Показываем сообщение об успехе
        result = QMessageBox.information(self, "Успех", f"Пользователь {login} успешно зарегистрирован! Вы хотите войти в систему?")
        db_manager = DatabaseManager()
        db_manager.register_user(login, email, password, role)
        if result == QMessageBox.Ok:
            self.goto("course")
        else:
            self.close()
