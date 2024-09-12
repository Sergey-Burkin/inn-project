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

        # Кнопка назад
        button_register = QPushButton("Назад")
        button_register.clicked.connect(lambda: self.goto("main"))
        layout.addWidget(button_register)
        
    
    def register(self):
        login = self.login_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        email = self.email_input.text()
        role = "student" if self.student_radio.isChecked() else "teacher"
        db_manager = DatabaseManager()
        
        # Username length limit
        max_username_length = 50
        if len(login) > max_username_length:
            QMessageBox.warning(self, "Ошибка", f"Имя пользователя должно быть не более {max_username_length} символов!")
            return

        # Email length limit
        max_email_length = 100
        if len(email) > max_email_length:
            QMessageBox.warning(self, "Ошибка", f"Адрес электронной почты должен быть не более {max_email_length} символов!")
            return

        # Password length limit
        min_password_length = 1
        max_password_length = 255
        if len(password) < min_password_length:
            QMessageBox.warning(self, "Ошибка", f"Пароль должен содержать не менее {min_password_length} символов!")
            return
        elif len(password) > max_password_length:
            QMessageBox.warning(self, "Ошибка", f"Пароль должен быть не длиннее {max_password_length} символов!")
            return

        # Check if username already exists
        existing_user = db_manager.get_user_by_username_or_email(login)
        if existing_user:
            QMessageBox.warning(self, "Ошибка", f"Пользователь с именем {login} уже существует!")
            return

        # Check if email already exists
        existing_email = db_manager.get_user_by_username_or_email(email)
        if existing_email:
            QMessageBox.warning(self, "Ошибка", f"Email {email} уже используется!")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают!")
            return

        # Здесь можно добавить логику регистрации
        print(f"Попытка регистрации пользователя: {login}, email: {email}")

        try:
            db_manager.register_user(login, email, password, role)
            result = QMessageBox.question(self, "Успех",
                                      f"Пользователь {login} успешно зарегистрирован!\n"
                                      "Вы хотите войти в систему?",
                                      QMessageBox.Yes | QMessageBox.No,
                                      QMessageBox.Yes)
            if result == QMessageBox.Yes:
                self.goto("login")
            else:
                self.goto("main")
        except Exception as e:
            print(f"Error registering user: {e}")
            QMessageBox.critical(self, "Ошибка при регистрации", str(e))
