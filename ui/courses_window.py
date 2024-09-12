import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QCheckBox, QRadioButton, QTextEdit, QListWidget, QListWidgetItem, QTabWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont
from ui.page_window import PageWindow
from models.database import DatabaseManager
import settings


class CourseWindow(PageWindow):
    def __init__(self):
        super().__init__()
        # self.initUI()

    def initUI(self):
        self.setWindowTitle("Список курсов")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Add welcome message
        welcome_label = QLabel("Welcome to Courses!")
        welcome_label.setFont(QFont("Arial", 24))
        layout.addWidget(welcome_label)

        # Create tab widget
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)

        # Courses Tab
        courses_tab = QWidget()
        tab_widget.addTab(courses_tab, "Courses")

        courses_layout = QVBoxLayout(courses_tab)

        # List of courses
        self.course_list = QListWidget()
        self.course_list.itemSelectionChanged.connect(self.on_course_selection_changed)
        courses_layout.addWidget(self.course_list)

        # Buttons
        button_layout = QHBoxLayout()
        go_to_button = QPushButton("Go To Course")
        logout_button = QPushButton("Logout")
        go_to_button.clicked.connect(self.on_go_to_course)
        logout_button.clicked.connect(self.on_logout)

        button_layout.addWidget(go_to_button)
        button_layout.addWidget(logout_button)
        print(settings.current_user["id"])
        if settings.current_user["role"] == "teacher":
            add_course_button = QPushButton("Add Course")
            delete_course_button = QPushButton("Delete Course")
            add_course_button.clicked.connect(self.on_add_course)
            delete_course_button.clicked.connect(self.on_delete_course)
            button_layout.addWidget(add_course_button)
            button_layout.addWidget(delete_course_button)

        courses_layout.addLayout(button_layout)

        if settings.current_user["role"] == "student":
            # Assign Course Tab
            assign_tab = QWidget()
            tab_widget.addTab(assign_tab, "Assign to a course using a code")

            assign_layout = QVBoxLayout(assign_tab)

            self.assign_code_line = QLineEdit()
            self.assign_code_line.setPlaceholderText("Enter course codename")
            assign_layout.addWidget(self.assign_code_line)

            assign_button = QPushButton("Assign")
            assign_button.clicked.connect(self.on_assign_course)
            assign_layout.addWidget(assign_button)


                
    def loadCoursesFromDatabase(self):
        self.course_list.clear()
        # Replace this with actual database loading logic
        courses = ["Course " + str(x) for x in range(1, 109)]
        for course in courses:
            item = QListWidgetItem(course)
            self.course_list.addItem(item)
        
    @pyqtSlot()
    def on_course_selection_changed(self):
        selected_item = self.course_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Warning", "Please select a course!")
            return
        
        go_to_button = self.findChild(QPushButton, "go_to_button")
        if go_to_button:
            go_to_button.clicked.emit()

    @pyqtSlot()
    def on_go_to_course(self):
        selected_item = self.course_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Warning", "Please select a course!")
            return
        
        # Navigate to the selected course
        # You'll need to implement this navigation logic
        pass

    @pyqtSlot()
    def on_logout(self):
        self.goto("main")

    @pyqtSlot()
    def on_add_course(self):
        # Implement add course logic here
        self.loadCoursesFromDatabase()
        pass

    @pyqtSlot()
    def on_delete_course(self):
        # Implement delete course logic here
        pass

    @pyqtSlot()
    def on_assign_course(self):
        course_codename = self.assign_code_line.text()
        if not course_codename:
            QMessageBox.warning(self, "Error", "Please enter a course codename!")
            return
        
        # Implement assignment logic here
        
        pass