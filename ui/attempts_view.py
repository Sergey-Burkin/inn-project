import sys
from PyQt5.QtWidgets import QLabel, QDoubleSpinBox , QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QListWidget, QListWidgetItem, QPushButton, QVBoxLayout, QHBoxLayout, QInputDialog, QMessageBox
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont
from ui.page_window import PageWindow
import settings
from models.database import DatabaseManager
import models.database
import json
import json  # Add this line

class AttemptViewer(PageWindow):
    def __init__(self):
        super().__init__()
        self.attempts = []

    def initUI(self):
        self.setWindowTitle(f"Attempts for {settings.current_test['title']}")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # List widget for attempts
        self.attempts_list = QListWidget()
        self.load_attempts_from_database()
        layout.addWidget(self.attempts_list)

        # Go Back button
        go_back_button = QPushButton("Go Back")
        go_back_button.clicked.connect(self.on_go_back)
        layout.addWidget(go_back_button)

        self.attempts_list.itemDoubleClicked.connect(self.on_attempt_double_clicked)

    def load_attempts_from_database(self):
        db_manager = DatabaseManager()
        self.attempts = db_manager.get_test_results(settings.current_test["id"])
        
        self.attempts_list.clear()
        
        if self.attempts:
            for attempt in self.attempts:
                item_text = f"Attempt {attempt['attempt_id']}, User ID: {attempt['user_id']}"
                item = QListWidgetItem(item_text)
                self.attempts_list.addItem(item)
        else:
            QMessageBox.warning(self, "No Attempts", "There are no attempts for this test.")

    @pyqtSlot()
    def on_go_back(self):
        self.goto("course_editor")

    @pyqtSlot(QListWidgetItem)
    def on_attempt_double_clicked(self, item):
        selected_index = self.attempts_list.row(item)
        attempt_id = self.attempts[selected_index]["attempt_id"]
        print(attempt_id)
        
        # Create a new window to display attempt details
        self.attempt_details_window = AttemptDetailsWindow(attempt_id)
        self.attempt_details_window.show()

class AttemptDetailsWindow(QWidget):
    def __init__(self, attempt_id):
        super().__init__()
        self.setWindowTitle(f"Attempt {attempt_id} Details")
        self.setGeometry(100, 100, 400, 300)
        self.grades = []
        self.grades_widgets = []
        layout = QVBoxLayout()

        # Load attempt details from database
        db_manager = DatabaseManager()
        attempt = db_manager.get(models.database.TestAttempt, attempt_id)

        if attempt:
            user = db_manager.get(models.database.User, attempt["user_id"])
            test = db_manager.get(models.database.Test, attempt["test_id"])

            layout.addWidget(QLabel(f"User: {user["username"]}"))
            layout.addWidget(QLabel(f"Test: {test["title"]}"))
            layout.addWidget(QLabel(f"Submitted at: {attempt["submitted_at"]}"))

            answers_layout = QVBoxLayout()
            layout.addLayout(answers_layout)
            self.answers = db_manager.get_related_objects("test_attempt_id", models.database.Answer, attempt["id"])
            print(self.answers)
            for answer in self.answers:
                question = db_manager.get(models.database.TestQuestion, answer["test_question_id"])
                answers_layout.addWidget(QLabel(f"{question["title"]}:"))
                answers_layout.addWidget(QLabel(f"Question: {question["question_text"]}"))
                answers_layout.addWidget(QLabel(f"Given Answer: {answer["given_answer"]}"))
                self.grades.append(answer["score"])
                spin = QDoubleSpinBox(self)
                spin.setMaximum(1)
                spin.setSingleStep(0.1)
                spin.setValue(self.grades[-1])
                self.grades_widgets.append(spin)
                answers_layout.addWidget(spin)


        else:
            layout.addWidget(QLabel("Attempt not found."))

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.on_close)
        layout.addWidget(close_button)
        self.setLayout(layout)

    @pyqtSlot()
    def on_close(self):
        for spin, answer in zip(self.grades_widgets ,self.answers):
            new_value = spin.value()
            DatabaseManager().edit(models.database.Answer, answer["id"], "score", new_value)
        self.close()
