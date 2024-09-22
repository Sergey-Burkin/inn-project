import sys
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QListWidget, QListWidgetItem, QPushButton, QVBoxLayout, QHBoxLayout, QInputDialog, QMessageBox, QLineEdit, QTextEdit
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont
from ui.page_window import PageWindow
import settings
from models.database import DatabaseManager
import json
import models.database


class TestViewer(PageWindow):
    def __init__(self):
        super().__init__()
        self.structure_items = []
        self.user_answers = []

    def initUI(self):
        print(settings.current_test["title"])
        self.setWindowTitle(settings.current_test["title"])
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        self.structure_view = QListWidget()
        self.load_structure_from_database()
        self.dislplay_structure()
        center_widget = QWidget()
        center_layout = QVBoxLayout()
        structure_label = QLabel("Questions")
        structure_label.setFont(QFont('Arial', 12))
        structure_label.setAlignment(Qt.AlignCenter)
        center_layout.addWidget(structure_label)
        center_layout.addWidget(self.structure_view)
        center_widget.setLayout(center_layout)

        # Right side: Buttons
        right_layout = QVBoxLayout()
        self.save_button = QPushButton("Save and exit")

        right_layout.addWidget(self.save_button)

        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(center_widget)
        main_splitter.addWidget(right_widget)

        layout.addWidget(main_splitter)

        # Connect double-click signals
        self.structure_view.itemDoubleClicked.connect(self.on_double_click_question)

        # Connect buttons
        self.connect_buttons()

    def connect_buttons(self):
        self.save_button.clicked.connect(self.on_save_and_exit)
    
    @pyqtSlot()
    def on_save_and_exit(self):
        confirm = QMessageBox.question(
            self,
            "Confirm Submission",
            "Are you sure you want to submit this?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            self.submit()
            self.goto("course_viewer")
        else:
            return
        
    def submit(self):
        db_manager = DatabaseManager()
        
        for item, answer in zip(self.structure_items, self.user_answers):
            try:
                # Add the answer to the database
                db_manager.submit_answer(
                    test_attempt_id=settings.current_attempt["id"],
                    test_question_id=item["id"],
                    given_answer=answer
                )
                
            except Exception as e:
                print(f"Error adding answer: {str(e)}")
    
        # Close the database connection
        db_manager.session.close()

    def on_double_click_question(self, item):
        self.current_item = self.structure_view.row(item)
        self.answer_window = self.AnswerGetWindow(parent_window=self)
        self.answer_window.show()

    def load_structure_from_database(self):
        db_manager = DatabaseManager()
        
        structure = db_manager.get(models.database.Test, settings.current_test["id"])
        
        if structure is None:
            self.structure_items = []
        else:
            if "structure" in structure and structure["structure"] is not None:
                self.structure_items = json.loads(structure["structure"])
            else:
                self.structure_items = []

        self.dislplay_structure()

    def dislplay_structure(self):
        self.structure_view.clear()
        self.user_answers = []

        db_manager = DatabaseManager()
        for item in self.structure_items:
            if item["type"] == "test":
                try:
                    test = db_manager.get(models.database.TestQuestion, item["id"])
                    new_item = QListWidgetItem(f"{test['title']}")
                except ValueError as e:
                    print(f"Test with ID {item['id']} not found")
                    continue
            self.user_answers.append('')
            self.structure_view.addItem(new_item)
        
        

    class AnswerGetWindow(QWidget):
        def __init__(self, parent_window):
            super().__init__()
            self.parent_window=parent_window
            db_manager = DatabaseManager()
            current_item = parent_window.current_item
            current_question_id = parent_window.structure_items[current_item]["id"]
            current_question = db_manager.get(models.database.TestQuestion, current_question_id)

            self.setWindowTitle(current_question["title"])
            self.setGeometry(100, 100, 400, 300)

            layout = QVBoxLayout()
            # Question text
            self.question_label = QLabel(current_question["question_text"])
            self.question_label.setWordWrap(True)
            layout.addWidget(self.question_label)
            
            # Answer text field
            self.answer_field = QTextEdit()
            self.answer_field.setPlaceholderText(parent_window.user_answers[current_item])
            layout.addWidget(self.answer_field)
            save_button = QPushButton("Save Changes")
            cancel_button = QPushButton("Cancel")

            layout.addWidget(save_button)
            layout.addWidget(cancel_button)

            self.setLayout(layout)

            save_button.clicked.connect(self.save_changes)
            cancel_button.clicked.connect(self.close)

        def save_changes(self):
            given_answer = self.answer_field.toPlainText().strip()

            self.parent_window.user_answers[self.parent_window.current_item] = given_answer

            self.close()


