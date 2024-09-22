import sys
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QListWidget, QListWidgetItem, QPushButton, QVBoxLayout, QHBoxLayout, QInputDialog, QMessageBox, QLineEdit, QTextEdit
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont
from ui.page_window import PageWindow
import settings
from models.database import DatabaseManager
import json
import models.database


class TestEditor(PageWindow):
    def __init__(self):
        super().__init__()
        self.structure_items = []

    def initUI(self):
        print(settings.current_test["title"])
        self.setWindowTitle(f"Редактор теста")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Left side: Tests list
        left_layout = QVBoxLayout()

        questions_label = QLabel("Questions")
        questions_label.setFont(QFont('Arial', 12))
        questions_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(questions_label)

        self.questions_list = QListWidget()
        self.load_questions_from_database()
        left_layout.addWidget(self.questions_list)
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        # Center: Structure view
        self.structure_view = QListWidget()
        self.load_structure_from_database()
        self.dislplay_structure()

        center_widget = QWidget()
        center_layout = QVBoxLayout()
        structure_label = QLabel("Test Structure")
        structure_label.setFont(QFont('Arial', 12))
        structure_label.setAlignment(Qt.AlignCenter)
        center_layout.addWidget(structure_label)
        center_layout.addWidget(self.structure_view)
        center_widget.setLayout(center_layout)

        # Right side: Buttons
        right_layout = QVBoxLayout()
        self.new_queston_button = QPushButton("New Question")
        self.edit_question_button = QPushButton("Edit Question")
        self.delete_question_button = QPushButton("Delete Question")
        self.clear_structure_button = QPushButton("Clear Structure")
        self.save_structure_button = QPushButton("Save Structure")
        self.go_back_button = QPushButton("Go Back")

        right_layout.addWidget(self.new_queston_button)
        right_layout.addWidget(self.edit_question_button)
        right_layout.addWidget(self.delete_question_button)
        right_layout.addWidget(self.clear_structure_button)
        right_layout.addWidget(self.save_structure_button)
        right_layout.addWidget(self.go_back_button)

        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(center_widget)
        main_splitter.addWidget(right_widget)

        layout.addWidget(main_splitter)

        # Connect double-click signals
        self.questions_list.itemDoubleClicked.connect(self.on_double_click_question)

        # Connect buttons
        self.connect_buttons()

    def connect_buttons(self):
        self.new_queston_button.clicked.connect(self.on_new_question)
        self.edit_question_button.clicked.connect(self.on_edit_question)
        self.delete_question_button.clicked.connect(self.on_delete_question)
        self.clear_structure_button.clicked.connect(self.on_clear_structure)
        self.save_structure_button.clicked.connect(self.on_save_structure)
        self.go_back_button.clicked.connect(self.on_go_back)

    @pyqtSlot()
    def on_new_question(self):
        test_name, ok = QInputDialog.getText(self, "Add Test", "Enter Test name:")
        if ok and test_name:
            if len(test_name) > 200:
                QMessageBox.warning(self, "Warning", f"The test name '{test_name}' is too long. It has {len(test_name)} characters, but the maximum allowed is 200.")
                return
            if len(test_name.strip()) == 0:
                QMessageBox.warning(self, "Error", "Test name cannot be empty.")
                return

            db_manager = DatabaseManager()
            db_manager.add(models.database.TestQuestion, {"title": test_name, "test_id": settings.current_test["id"]})

        self.load_questions_from_database()

    @pyqtSlot()
    def on_edit_question(self):
        selected_item = self.questions_list.currentItem()
        if selected_item:
            question_index = self.questions_list.row(selected_item)
            settings.current_question = self.questions[question_index]
            
            # Open QuestioneSettingsWindow
            self.QuestioneSettingsWindowInstance = self.QuestioneSettingsWindow()
            self.QuestioneSettingsWindowInstance.show()

        

    @pyqtSlot()
    def on_delete_question(self):
        selected_item = self.questions_list.currentItem()
        if not selected_item:
            return

        item_text = selected_item.text()
        item_index = self.questions_list.row(selected_item)

        confirm_delete = QMessageBox.question(self, "Confirm Deletion", f"Are you sure you want to delete test '{item_text}'?")
        
        if confirm_delete == QMessageBox.Yes:
            db_manager = DatabaseManager()
            question_id = self.questions[item_index]["id"]
            db_manager.delete(models.database.TestQuestion, question_id)
            self.load_questions_from_database()

    @pyqtSlot()
    def on_clear_structure(self):
        self.structure_items = []
        self.dislplay_structure()

    @pyqtSlot()
    def on_save_structure(self):
        structure_json = json.dumps(self.structure_items)

        db_manager = DatabaseManager()
        db_manager.edit(
            models.database.Test,
            settings.current_test["id"],
            "structure",
            structure_json
        )

        settings.current_test["structure"] = structure_json

        QMessageBox.information(self, "Success", "Course structure saved successfully!")

        self.dislplay_structure()

    @pyqtSlot()
    def on_go_back(self):
        self.goto("course_editor")

    def on_double_click_question(self, item):
        row = self.questions_list.row(item)
        self.structure_items.append({"type": "test", "id": self.questions[row]["id"]})
        self.dislplay_structure()

    def add_to_structure(self, name):
        new_item = QListWidgetItem(f"Question: {name}")
        self.structure_view.addItem(new_item)
        self.structure_items.append(("test", name))

    def load_questions_from_database(self):
        self.questions_list.clear()
        db_manager = DatabaseManager()
        self.questions = db_manager.get_related_objects("test_id", models.database.TestQuestion, settings.current_test["id"])
        for question in self.questions:
            if question:
                item = QListWidgetItem(question["title"])
                self.questions_list.addItem(item)
            else:
                print(f"Warning: Test with ID {question['id']} not found")

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
        db_manager = DatabaseManager()
        for item in self.structure_items:
            if item["type"] == "test":
                try:
                    test = db_manager.get(models.database.TestQuestion, item["id"])
                    new_item = QListWidgetItem(f"{test['title']}")
                except ValueError as e:
                    print(f"Test with ID {item['id']} not found")
                    continue
            self.structure_view.addItem(new_item)


    class QuestioneSettingsWindow(QWidget):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Edit Question")
            self.setGeometry(100, 100, 400, 300)

            layout = QVBoxLayout()

            self.question_title = QLineEdit()
            self.question_title.setText(settings.current_question["title"])
            self.question_title.setPlaceholderText("Enter question title")

            self.question_text = QTextEdit()
            self.question_text.setPlainText(settings.current_question["question_text"])
            self.question_text.setPlaceholderText("Enter question text")

            layout.addWidget(QLabel("Title:"))
            layout.addWidget(self.question_title)
            layout.addWidget(QLabel("Question Text:"))
            layout.addWidget(self.question_text)

            save_button = QPushButton("Save Changes")
            cancel_button = QPushButton("Cancel")

            layout.addWidget(save_button)
            layout.addWidget(cancel_button)

            self.setLayout(layout)

            save_button.clicked.connect(self.save_changes)
            cancel_button.clicked.connect(self.close)

        def save_changes(self):
            new_title = self.question_title.text().strip()
            new_text = self.question_text.toPlainText().strip()

            if not new_title:
                QMessageBox.warning(self, "Error", "Title cannot be empty.")
                return

            db_manager = DatabaseManager()
            db_manager.edit(models.database.TestQuestion, settings.current_question["id"], 
                            "title", new_title)
            db_manager.edit(models.database.TestQuestion, settings.current_question["id"], 
                            "question_text", new_text)

            settings.current_question["title"] = new_title
            settings.current_question["question_text"] = new_text

            QMessageBox.information(self, "Success", "Question updated successfully!")
            self.close()


