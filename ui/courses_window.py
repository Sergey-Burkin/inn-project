import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QCheckBox, QRadioButton, QTextEdit, QListWidget, QListWidgetItem, QTabWidget, QVBoxLayout, QHBoxLayout, QInputDialog
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont
from ui.page_window import PageWindow
from models.database import DatabaseManager
import models.database 
import settings


class CourseWindow(PageWindow):
    def __init__(self):
        super().__init__()

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
        self.loadCoursesFromDatabase()
        # Buttons
        button_layout = QHBoxLayout()
        if settings.current_user["role"] == "student":
        
            go_to_button = QPushButton("Go To Course")
            go_to_button.clicked.connect(self.on_go_to_course)
            button_layout.addWidget(go_to_button)

        logout_button = QPushButton("Logout")
        logout_button.clicked.connect(self.on_logout)
        button_layout.addWidget(logout_button)

        if settings.current_user["role"] == "teacher":
            add_course_button = QPushButton("Add Course")
            delete_course_button = QPushButton("Delete Course")
            add_course_button.clicked.connect(self.on_add_course)
            delete_course_button.clicked.connect(self.on_delete_course)
            button_layout.addWidget(add_course_button)
            button_layout.addWidget(delete_course_button)
            edit_course_button = QPushButton("Edit Course")
            edit_course_button.clicked.connect(self.on_edit_course)
            button_layout.addWidget(edit_course_button)

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
        db_manager = DatabaseManager()
        self.courses = db_manager.get_courses_by_user_id(settings.current_user["id"])
        for course in self.courses:
            item = QListWidgetItem(course["title"])
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

        settings.current_course = self.courses[self.course_list.row(selected_item)]
        
        self.goto("course_viewer")

    @pyqtSlot()
    def on_logout(self):
        self.goto("main")

    @pyqtSlot()
    def on_add_course(self):
        # Implement add course logic here
        course_name, ok = QInputDialog.getText(self, "Add Course", "Enter course name:")
        
        
        if ok and course_name:
            if len(course_name) > 200:
                QMessageBox.warning(self, "Warning", f"The course name '{course_name}' is too long. It has {len(course_name)} characters, but the maximum allowed is 200.")
                return
            if len(course_name.strip()) == 0:
                QMessageBox.warning(self, "Error", "Course name cannot be empty.")
                return
            db_manager = DatabaseManager()
            db_manager.create_course(course_name, settings.current_user["id"])

        self.loadCoursesFromDatabase()
        pass

    @pyqtSlot()
    def on_delete_course(self):
        selected_item = self.course_list.currentItem()
        if not selected_item:
            return
        item_text = selected_item.text()
        item_index = self.course_list.row(selected_item)
        confirm_delete = QMessageBox.question(self, "Confirm Deletion", f"Are you sure you want to delete course '{item_text}'?")
    
        if confirm_delete == QMessageBox.Yes:
            db_manager = DatabaseManager()
            db_manager.delete(models.database.Course, self.courses[item_index]["id"])
            self.loadCoursesFromDatabase()
        pass

    @pyqtSlot()
    def on_assign_course(self):
        course_codename = self.assign_code_line.text()
        if not course_codename:
            QMessageBox.warning(self, "Error", "Please enter a course codename!")
            return
    
        db_manager = DatabaseManager()
        new_course = db_manager.find_course_by_codename(course_codename)
        
        if new_course:
            try:
                db_manager.assign_user_to_course(settings.current_user["id"], new_course["id"])
                self.loadCoursesFromDatabase()
                
                QMessageBox.information(self, "Success", f"You have been successfully assigned to course '{new_course['title']}'")
            
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(e)}")
        else:
            QMessageBox.warning(self, "Error", f"No course found with codename '{course_codename}'. Please check the codename and try again.")


    @pyqtSlot()
    def on_edit_course(self):
        selected_item = self.course_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Warning", "Please select a course!")
            return
        
        settings.current_course = self.courses[self.course_list.row(selected_item)]
        self.goto("course_editor")
