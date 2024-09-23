import sys
from PyQt5.QtWidgets import QLabel, QTextBrowser, QProgressBar, QTextEdit, QDialogButtonBox, QDialog, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QListWidget, QListWidgetItem, QPushButton, QVBoxLayout, QHBoxLayout, QInputDialog, QMessageBox
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont
import models.video_manager
from ui.page_window import PageWindow
import settings
from models.database import DatabaseManager
import models.database
import json
from models.video_manager import VideoManager

class CourseViewer(PageWindow):
    def __init__(self):
        super().__init__()
        self.structure_items = []
    def initUI(self):
        self.setWindowTitle(f"Просмотр курса")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

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
        self.open_button = QPushButton("Open")
        self.show_description_button = QPushButton("Show Description")
        self.go_back_button = QPushButton("Go Back")

        right_layout.addWidget(self.open_button)
        right_layout.addWidget(self.show_description_button) 
        right_layout.addWidget(self.go_back_button)
        
        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        # Progress Bar
        progress = DatabaseManager().calculate_progress(settings.current_user["id"], settings.current_course["id"])
        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(int(progress * 100))
        progress_layout.addWidget(QLabel("Прогресс по курсу:"))
        progress_layout.addWidget(self.progress_bar)
        progress_widget = QWidget()
        progress_widget.setLayout(progress_layout)

        # Main layout
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(center_widget)
        main_splitter.addWidget(right_widget)
        turbo_splitter = QSplitter(Qt.Vertical)
        turbo_splitter.addWidget(main_splitter)
        turbo_splitter.addWidget(progress_widget)
        layout.addWidget(turbo_splitter)

        # Connect buttons
        self.connect_buttons()

    def connect_buttons(self):
        self.open_button.clicked.connect(self.on_open)
        self.show_description_button.clicked.connect(self.show_course_description)
        self.go_back_button.clicked.connect(self.on_go_back)

    def show_course_description(self):
        description_dialog = QDialog(self)
        description_dialog.setWindowTitle("Course Description")
        description_dialog.setModal(True)

        layout = QVBoxLayout()
        description_text = QTextEdit()
        description_text.setReadOnly(True)
        description_text.setText(settings.current_course["description"])
        layout.addWidget(description_text)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(description_dialog.accept)
        layout.addWidget(button_box)

        description_dialog.setLayout(layout)
        description_dialog.exec_()

    @pyqtSlot()
    def on_go_back(self):
        self.goto("course")

        
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


    def parse_row(self, row):
        selected_item = self.structure_items[row]
        if selected_item["type"] == "test":
            self.open_test(selected_item["id"])
        elif selected_item["type"] == "video":
            self.open_video(selected_item["id"])

    def open_test(self, test_id):
        db_manager = DatabaseManager()
        attempts = db_manager.count_attempts(settings.current_user["id"], test_id)

        if attempts is None or attempts <= 3:
            response = QMessageBox.question(
                self,
                "Confirm",
                "Are you sure you want to start this test?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if response == QMessageBox.Yes:
                # Proceed with opening the test
                self.start_test(test_id)
            else:
                print("Test opening cancelled")
        else:
            QMessageBox.warning(
                self,
                "Warning",
                "You already have attempts for this test.",
                QMessageBox.Ok
            )

    def start_test(self, test_id):
        # Create a new test attempt
        db_manager = DatabaseManager()
        attempt_id = db_manager.create_test_attempt(test_id, settings.current_user["id"])
        
        # Fetch the current test details
        settings.current_test = db_manager.get(models.database.Test, test_id)
        
        # Fetch the newly created attempt details
        settings.current_attempt = db_manager.get(models.database.TestAttempt, attempt_id)
        
        # Go to the test view
        self.goto("test_viewer")

    def open_video(self, video_id):
        db_manager = DatabaseManager()
        video = db_manager.get(models.database.VideoMaterial, video_id)
        self.micro = self.MicroWindow(video=video)
        self.micro.show()

    @pyqtSlot()
    def on_open(self):
        selected_item = self.structure_view.currentItem()
        if selected_item:
            row = self.structure_view.row(selected_item)
            self.parse_row(row=row)

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


    class MicroWindow(QWidget):
        def __init__(self, video):
            super().__init__()

            self.setGeometry(300, 300, 400, 200)
            self.setWindowTitle('Hyperlink Example')
            
            label = QTextBrowser(self)
            label.setGeometry(20, 20, 360, 160)
            link = video["file_path"]
            # Set HTML formatting
            html = f"<html><body><center><h1><a href=\"{link}\">Download your video</a></h1></body></html>"
            
            # Apply HTML formatting
            label.setOpenExternalLinks(True)
            label.setHtml(html)