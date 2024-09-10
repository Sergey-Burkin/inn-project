class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Вход")
        self.setGeometry(300, 300, 300, 150)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
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
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(login_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def authenticate_user(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if db_manager.authenticate_user(username, password):
            user = get_user_by_username(username)
            if user:
                # Open main window with authenticated user
                self.close()
                MainWindow().show()
            else:
                QMessageBox.warning(self, "Ошибка", "Пользователь не найден или неправильный пароль.")
        else:
            QMessageBox.warning(self, "Ошибка", "Неправильный логин или пароль.")
