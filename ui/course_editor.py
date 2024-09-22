import sys
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QListWidget, QListWidgetItem, QPushButton, QVBoxLayout, QHBoxLayout, QInputDialog, QMessageBox
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont
from ui.page_window import PageWindow
import settings
from models.database import DatabaseManager
import models.database
import json
import json  # Add this line

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

            # Add label for Tests
        tests_label = QLabel("Tests")
        tests_label.setFont(QFont('Arial', 12))
        tests_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(tests_label)

        self.tests_list = QListWidget()
        self.load_tests_from_database()
        left_layout.addWidget(self.tests_list)
        
        # Add label for Videos
        videos_label = QLabel("Videos")
        videos_label.setFont(QFont('Arial', 12))
        videos_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(videos_label)

        self.videos_list = QListWidget()
        self.load_videos_from_database()
        left_layout.addWidget(self.videos_list)
        left_widget = QWidget()
        left_widget.setLayout(left_layout)

        # Center: Structure view
        self.structure_view = QListWidget()
        self.load_structure_from_database()
        self.dislplay_structure()
        center_widget = QWidget()

        center_layout = QVBoxLayout()

        # Add label for Course Structure
        structure_label = QLabel("Course Structure")
        structure_label.setFont(QFont('Arial', 12))
        structure_label.setAlignment(Qt.AlignCenter)
        center_layout.addWidget(structure_label)
        center_layout.addWidget(self.structure_view)
        center_widget.setLayout(center_layout)

        # Right side: Buttons
        right_layout = QVBoxLayout()
        self.new_test_button = QPushButton("New Test")
        self.edit_test_button = QPushButton("Edit Test")
        self.delete_test_button = QPushButton("Delete Test")
        self.attempt_button = QPushButton("Show Attempts")
        self.new_video_button = QPushButton("New Video")
        self.delete_video_button = QPushButton("Delete Video")
        self.clear_structure_button = QPushButton("Clear Structure")
        self.save_structure_button = QPushButton("Save Structure")
        self.configure_course_button = QPushButton("Configure Course")
        self.go_back_button = QPushButton("Go Back")

        right_layout.addWidget(self.new_test_button)
        right_layout.addWidget(self.edit_test_button)
        right_layout.addWidget(self.delete_test_button)
        right_layout.addWidget(self.attempt_button)
        right_layout.addWidget(self.new_video_button)
        right_layout.addWidget(self.delete_video_button)
        right_layout.addWidget(self.clear_structure_button)
        right_layout.addWidget(self.save_structure_button)
        right_layout.addWidget(self.configure_course_button)
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
        self.attempt_button.clicked.connect(self.on_attempt)
        self.new_video_button.clicked.connect(self.on_new_video)
        self.delete_video_button.clicked.connect(self.on_delete_video)
        self.clear_structure_button.clicked.connect(self.on_clear_structure)
        self.save_structure_button.clicked.connect(self.on_save_structure)
        self.go_back_button.clicked.connect(self.on_go_back)
        self.configure_course_button.clicked.connect(self.on_configure_course)



    
    @pyqtSlot()
    def on_new_test(self):
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
        selected_item = self.tests_list.currentItem()
        if selected_item:
            settings.current_test = self.tests[self.tests_list.row(selected_item)]
                
            db_manager = DatabaseManager()
            attempts_count = db_manager.session.query(models.database.TestAttempt).filter_by(test_id=settings.current_test["id"]).count()
            
            if attempts_count > 0:
                confirm_message = QMessageBox.question(self, "Confirm Test Edit", 
                    f"Editing test '{selected_item.text()}' will drop {attempts_count} existing attempts. Are you sure?")
                    
                if confirm_message == QMessageBox.Yes:
                    # Drop attempts
                    db_manager.drop_attempts(settings.current_test["id"])
                    
            self.goto("test_editor")

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
    def on_attempt(self):
        selected_item = self.tests_list.currentItem()
        if not selected_item:
            return
        settings.current_test = self.tests[self.tests_list.row(selected_item)]
        item_index = self.tests_list.row(selected_item)
        self.goto("attempt_viewer")



    @pyqtSlot()
    def on_new_video(self):
        video_name, ok = QInputDialog.getText(self, "Add Video", "Enter Video name:")
        if ok and video_name:
            if len(video_name) > 200:
                QMessageBox.warning(self, "Warning", f"The video name '{video_name}' is too long. It has {len(video_name)} characters, but the maximum allowed is 200.")
                return
            if len(video_name.strip()) == 0:
                QMessageBox.warning(self, "Error", "Video name cannot be empty.")
                return

            db_manager = DatabaseManager()
            db_manager.add(models.database.VideoMaterial, {
                "title": video_name,
                "course_id": settings.current_course["id"],
                "file_path": ""  # Initially set to empty string, can be updated later
            })

        self.load_videos_from_database()


    @pyqtSlot()
    def on_delete_video(self):
        selected_item = self.videos_list.currentItem()
        if not selected_item:
            return

        item_text = selected_item.text()
        item_index = self.videos_list.row(selected_item)

        confirm_delete = QMessageBox.question(self, "Confirm Deletion", f"Are you sure you want to delete video '{item_text}'?")

        if confirm_delete == QMessageBox.Yes:
            db_manager = DatabaseManager()
            video_id = self.videos[item_index]["id"]
            db_manager.delete(models.database.VideoMaterial, video_id)
            self.load_videos_from_database()

    @pyqtSlot()
    def on_clear_structure(self):
        self.structure_items = []
        self.dislplay_structure()

    @pyqtSlot()
    def on_save_structure(self):
        # Convert self.structure_items to JSON
        structure_json = json.dumps(self.structure_items)

        # Edit the current course structure
        db_manager = DatabaseManager()
        db_manager.edit(
            models.database.Course,
            settings.current_course["id"],
            "structure",
            structure_json
        )

        # Update the current course settings
        settings.current_course["structure"] = structure_json

        # Show a success message
        QMessageBox.information(self, "Success", "Course structure saved successfully!")

        # Optionally, reload the structure display
        self.dislplay_structure()

    @pyqtSlot()
    def on_go_back(self):
        self.goto("course")
        pass


    def on_double_click_test(self, item):
        row = self.tests_list.row(item)
        self.structure_items.append({"type": "test", "id": self.tests[row]["id"]})
        self.dislplay_structure()
        
    def on_double_click_video(self, item):
        row = self.videos_list.row(item)
        self.structure_items.append({"type": "video", "id": self.videos[row]["id"]})
        self.dislplay_structure()


    def load_tests_from_database(self):
        self.tests_list.clear()
        db_manager = DatabaseManager()
        self.tests = db_manager.get_related_objects("course_id", models.database.Test, settings.current_course["id"])
        for test in self.tests:
            if test:
                item = QListWidgetItem(test["title"])
                self.tests_list.addItem(item)
            else:
                print(f"Warning: Test with ID {test['id']} not found")


    def load_videos_from_database(self):
        self.videos_list.clear()
        db_manager = DatabaseManager()
        self.videos = db_manager.get_related_objects("course_id", models.database.VideoMaterial, settings.current_course["id"])

        for video in self.videos:
            if video:
                item = QListWidgetItem(video["title"])
                self.videos_list.addItem(item)
            else:
                print(f"Warning: Video with ID {video['id']} not found")

    def load_structure_from_database(self):
        db_manager = DatabaseManager()
        
        # First, check if the structure exists in the database
        structure = db_manager.get(models.database.Course, settings.current_course["id"])
        
        if structure is None:
            # If no structure exists, initialize self.structure_items as an empty list
            self.structure_items = []
        else:
            # Check if the structure field exists and is not None
            # Unserialize the JSON string stored in the database
            if "structure" in structure and structure["structure"] is not None:
                # Unserialize the JSON string stored in the database
                self.structure_items = json.loads(structure["structure"])
            else:
                # If structure doesn't exist or is None, initialize as an empty list
                self.structure_items = []
        
        # Call display_structure to update the UI
        self.dislplay_structure()
        
    def dislplay_structure(self):
        self.structure_view.clear()
        db_manager = DatabaseManager()
        for item in self.structure_items:
            if item["type"] == "test":
                try:
                    test = db_manager.get(models.database.Test, item["id"])
                    new_item = QListWidgetItem(f"{item["type"]}: {test['title']}")
                except ValueError as e:
                    print(f"Test with ID {item['id']} not found")
                    continue
            if item["type"] == "video":
                try:
                    video = db_manager.get(models.database.VideoMaterial, item["id"])
                    new_item = QListWidgetItem(f"{item["type"]}: {video['title']}")
                except ValueError as e:
                    print(f"Video with ID {item['id']} not found")
                    continue
            self.structure_view.addItem(new_item)


    # Add new function
    @pyqtSlot()
    def on_configure_course(self):
        self.course_settings_window = self.CourseSettingsWindow()
        self.course_settings_window.show()

    class CourseSettingsWindow(QWidget):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Course Settings")
            self.setGeometry(100, 100, 400, 200)
            
            layout = QVBoxLayout()
            
            # Add fields for course settings (e.g., codename, description, etc.)
            self.course_codename = QLineEdit()
            self.course_codename.setText(settings.current_course["codename"])
            
            self.course_description = QTextEdit()

            self.course_description.setPlainText(settings.current_course["description"])
            

            layout.addWidget(QLabel("Course Description:"))
            layout.addWidget(self.course_description)
            layout.addWidget(QLabel("Course Codename:"))
            layout.addWidget(self.course_codename)

            
            save_button = QPushButton("Save Changes")
            cancel_button = QPushButton("Cancel")
            
            layout.addWidget(save_button)
            layout.addWidget(cancel_button)
            
            self.setLayout(layout)
            
            # Connect save and cancel actions
            save_button.clicked.connect(self.save_changes)
            cancel_button.clicked.connect(self.close)
        
        def save_changes(self):
            # Get the new codename
            new_codename = self.course_codename.text().strip()

            # Check if the codename exceeds the limit
            if len(new_codename) > 50 or len(new_codename) == 0:
                if len(new_codename) > 50:
                    QMessageBox.warning(self, "Warning", f"The codename '{new_codename}' is too long. Maximum allowed length is 50 characters.")
                    return
                elif settings.current_course["codename"]:
                    QMessageBox.warning(self, "Error", "The codename cannot be empty.")
                    return
                else:
                    new_codename = None

            # Check if the codename is being changed
            if new_codename != settings.current_course["codename"]:
                # Check if the new codename is already in use
                db_manager = DatabaseManager()
                existing_course = db_manager.find_course_by_codename(new_codename)
                
                if existing_course and existing_course["id"] != settings.current_course["id"]:
                    # Codename is already in use by another course
                    QMessageBox.warning(self, "Warning", f"The codename '{new_codename}' is already in use.")
                    return
            
            # Save course settings to database
            db_manager = DatabaseManager()
            db_manager.edit(models.database.Course, settings.current_course["id"], "codename", new_codename)
            db_manager.edit(models.database.Course, settings.current_course["id"], "description", self.course_description.toPlainText())
            
            # Update current course settings
            settings.current_course["codename"] = new_codename
            settings.current_course["description"] = self.course_description.toPlainText()
            
            print("Course settings saved successfully!")
            self.close()

# Add import statement at the top of the file
from PyQt5.QtWidgets import QLineEdit, QTextEdit
