class User:
    def __init__(self, username=None, email=None, role=None):
        self.username = username
        self.email = email
        self.role = role
        self.id = None  # ID пользователя будет установлено при регистрации

    def __str__(self):
        return f"User(username='{self.username}', email='{self.email}', role='{self.role}')"