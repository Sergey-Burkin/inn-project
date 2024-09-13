import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QListWidget, QListWidgetItem, QPushButton, QVBoxLayout, QHBoxLayout, QInputDialog, QMessageBox
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont
from ui.page_window import PageWindow
import settings
from models.database import DatabaseManager
import models.database

class CourseEditor(PageWindow):
    def __init__(self):
        super().__init__()
        self.structure_items = []
    def initUI(self):
        print(settings.current_course["title"])
        self.setWindowTitle(f"Редактор курса")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Left side: Tests and Videos lists
        left_layout = QVBoxLayout()
        self.tests_list = QListWidget()
        self.load_tests_from_database()
        self.videos_list = QListWidget()
        left_layout.addWidget(self.tests_list)
        left_layout.addWidget(self.videos_list)
        left_widget = QWidget()
        left_widget.setLayout(left_layout)

        # Center: Structure view
        self.structure_view = QListWidget()
        center_widget = QWidget()

        center_layout = QVBoxLayout()
        center_layout.addWidget(self.structure_view)
        center_widget.setLayout(center_layout)

        # Right side: Buttons
        right_layout = QVBoxLayout()
        self.new_test_button = QPushButton("New Test")
        self.edit_test_button = QPushButton("Edit Test")
        self.delete_test_button = QPushButton("Delete Test")
        self.new_video_button = QPushButton("New Video")
        self.delete_video_button = QPushButton("Delete Video")
        self.clear_structure_button = QPushButton("Clear Structure")
        self.save_structure_button = QPushButton("Save Structure")
        self.go_back_button = QPushButton("Go Back")

        right_layout.addWidget(self.new_test_button)
        right_layout.addWidget(self.edit_test_button)
        right_layout.addWidget(self.delete_test_button)
        right_layout.addWidget(self.new_video_button)
        right_layout.addWidget(self.delete_video_button)
        right_layout.addWidget(self.clear_structure_button)
        right_layout.addWidget(self.save_structure_button)
        right_layout.addWidget(self.go_back_button)

        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        # Main layout
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(center_widget)
        main_splitter.addWidget(right_widget)

        layout.addWidget(main_splitter)

        # Connect double-click signals
        self.tests_list.itemDoubleClicked.connect(self.on_double_click_test)
        self.videos_list.itemDoubleClicked.connect(self.on_double_click_video)

        # Connect buttons
        self.connect_buttons()

    def connect_buttons(self):
        self.new_test_button.clicked.connect(self.on_new_test)
        self.edit_test_button.clicked.connect(self.on_edit_test)
        self.delete_test_button.clicked.connect(self.on_delete_test)
        self.new_video_button.clicked.connect(self.on_new_video)
        self.delete_video_button.clicked.connect(self.on_delete_video)
        self.clear_structure_button.clicked.connect(self.on_clear_structure)
        self.save_structure_button.clicked.connect(self.on_save_structure)
        self.go_back_button.clicked.connect(self.on_go_back)


    
    @pyqtSlot()
    def on_new_test(self):
        # Implement add course logic here
        test_name, ok = QInputDialog.getText(self, "Add Test", "Enter Test name:")
        if ok and test_name:
            if len(test_name) > 200:
                QMessageBox.warning(self, "Warning", f"The test name '{test_name}' is too long. It has {len(test_name)} characters, but the maximum allowed is 200.")
                return
            if len(test_name.strip()) == 0:
                QMessageBox.warning(self, "Error", "Test name cannot be empty.")
                return
            db_manager = DatabaseManager()
            db_manager.add(models.database.Test, {"title": test_name, "course_id": settings.current_course["id"]})

        self.load_tests_from_database()
        pass



    @pyqtSlot()
    def on_edit_test(self):
        ## TODO
        selected_item = self.tests_list.currentItem()
        if selected_item:
            new_name, ok = QInputDialog.getText(self, "Edit Test", f"Enter new name for '{selected_item.text()}':")
            if ok and new_name:
                selected_item.setText(new_name)

    @pyqtSlot()
    def on_delete_test(self):
        selected_item = self.tests_list.currentItem()
        if not selected_item:
            return

        item_text = selected_item.text()
        item_index = self.tests_list.row(selected_item)

        confirm_delete = QMessageBox.question(self, "Confirm Deletion", f"Are you sure you want to delete test '{item_text}'?")

        if confirm_delete == QMessageBox.Yes:
            db_manager = DatabaseManager()
            test_id = self.tests[item_index]["id"]
            db_manager.delete(models.database.Test, test_id)
            self.load_tests_from_database()

    @pyqtSlot()
    def on_new_video(self):
        video_name, ok = QInputDialog.getText(self, "New Video", "Enter video name:")
        if ok and video_name:
            item = QListWidgetItem(video_name)
            self.videos_list.addItem(item)

    @pyqtSlot()
    def on_delete_video(self):
        selected_item = self.videos_list.currentItem()
        if selected_item:
            self.videos_list.takeItem(self.videos_list.row(selected_item))

    @pyqtSlot()
    def on_clear_structure(self):
        self.structure_view.clear()

    @pyqtSlot()
    def on_save_structure(self):
        # Implement save structure logic here
        pass

    @pyqtSlot()
    def on_go_back(self):
        self.goto("course")
        pass


    def on_double_click_test(self, item):
        test_name = item.text()
        self.add_to_structure(test_name)

    def on_double_click_video(self, item):
        video_name = item.text()
        self.add_to_structure(video_name)

    def add_to_structure(self, name):
        type_name = "Test" if self.tests_list.currentRow() != self.videos_list.currentRow() else "Video"
        new_item = QListWidgetItem(f"{type_name}: {name}")
        self.structure_view.addItem(new_item)
        self.structure_items.append((type_name, name))


    def load_tests_from_database(self):
        self.tests_list.clear()
        db_manager = DatabaseManager()
        print(settings.current_course["id"])
        self.tests = db_manager.get_related_objects(models.database.Course, models.database.Test, settings.current_course["id"])

        for test in self.tests:
            if test:
                item = QListWidgetItem(test["title"])
                self.tests_list.addItem(item)
            else:
                print(f"Warning: Test with ID {test['id']} not found")
