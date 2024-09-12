from sqlalchemy import or_, create_engine, Column, Integer, String, Text, Numeric, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from psycopg2 import pool
import bcrypt
import settings
from datetime import datetime



Base = declarative_base()

user_courses = Table('user_courses',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('course_id', Integer, ForeignKey('courses.id'))
)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    courses = relationship("Course", secondary=user_courses, back_populates="students")

class Course(Base):
    __tablename__ = 'courses'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    teacher_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)

    students = relationship("User", secondary=user_courses, back_populates="courses")

class CourseSection(Base):
    __tablename__ = 'course_sections'
    
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'))
    title = Column(String(100), nullable=False)
    order_num = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class VideoMaterial(Base):
    __tablename__ = 'video_materials'
    
    id = Column(Integer, primary_key=True)
    course_section_id = Column(Integer, ForeignKey('course_sections.id'))
    title = Column(String(200), nullable=False)
    file_path = Column(String(255), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

class Test(Base):
    __tablename__ = 'tests'
    
    id = Column(Integer, primary_key=True)
    course_section_id = Column(Integer, ForeignKey('course_sections.id'))
    title = Column(String(100), nullable=False)
    total_questions = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class TestQuestion(Base):
    __tablename__ = 'test_questions'
    
    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey('tests.id'))
    question_text = Column(Text, nullable=False)
    correct_answer = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

class UserAnswer(Base):
    __tablename__ = 'user_answers'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    test_question_id = Column(Integer, ForeignKey('test_questions.id'))
    answer_text = Column(String(255))
    submitted_at = Column(DateTime, default=datetime.utcnow)

class Grade(Base):
    __tablename__ = 'grades'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    course_id = Column(Integer, ForeignKey('courses.id'))
    grade = Column(Numeric(5,2))
    submitted_at = Column(DateTime, default=datetime.utcnow)
class DatabaseManager:
    def __init__(self):
        self.engine = create_engine('postgresql://postgres:admin@localhost/online_learning_db', 
                                     pool_size=1, max_overflow=19, poolclass=QueuePool)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def hash_password(self, password):
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')


    def register_user(self, username, email, password, role):
        try:
            user = User(username=username, email=email, password_hash=self.hash_password(password), role=role)
            self.session.add(user)
            self.session.commit()
            print(f"User {username} registered successfully")
        except OperationalError as e:
            self.session.rollback()
            print(f"Error registering user: {e}")
        finally:
            self.session.close()

    def create_course(self, title, teacher_id):
        try:
            # Create the course
            course = Course(title=title, teacher_id=teacher_id)
            self.session.add(course)
            self.session.commit()
            
            # Get the newly created course ID
            new_course_id = course.id
            
            # Add the (teacher_id, course_id) tuple to user_courses
            self.session.execute(
                user_courses.insert().values(
                    user_id=teacher_id,
                    course_id=new_course_id
                )
            )
            
            self.session.commit()
            print(f"Course '{title}' created successfully")
        except OperationalError as e:
            self.session.rollback()
            print(f"Error creating course: {e}")
        finally:
            self.session.close()



    def get_user_by_username_or_email(self, username_or_email):
        try:
            query = self.session.query(User).filter(or_(User.username == username_or_email, 
                                                       User.email == username_or_email))
            user_data = query.first()
            
            if user_data:
                return {
                    "id": user_data.id,
                    "username": user_data.username,
                    "email": user_data.email,
                    "password_hash": user_data.password_hash,
                    "role": user_data.role
                }
            else:
                return None
        except OperationalError as e:
            print(f"Error fetching user data: {e}")
            return None
        finally:
            self.session.close()

    def authenticate_user(self, username, password):
        try:
            user = self.session.query(User).filter_by(username=username).first()
            
            if not user:
                return False, None, "User not found"

            hashed_password = user.password_hash
            
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                user_data = {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role
                }
                settings.current_user = user_data
                return True, user_data, "Authentication successful"
            else:
                return False, None, "Incorrect password"
        except OperationalError as e:
            print(f"Error authenticating user: {e}")
            return False, None, f"An error occurred: {str(e)}"
        finally:
            self.session.close()

    def get_courses_by_user_id(self, user_id):
        try:
            result = self.session.query(Course).join(user_courses).join(User).filter(User.id == user_id).all()
            return [course.__dict__ for course in result]
        except OperationalError as e:
            self.session.rollback()
            print(f"Error retrieving courses: {e}")
            return []
        finally:
            self.session.close()

    def delete_course_by_id(self, course_id):
        try:
            self.session.begin_nested()  # Start a nested transaction
            
            # First, remove associations from user_courses
            user_courses_deleted = self.session.query(user_courses).filter_by(course_id=course_id).delete()
            
            # Then delete the course
            course_deleted = self.session.query(Course).filter_by(id=course_id).delete()
            
            # Commit the nested transaction
            self.session.commit()
            
            return course_deleted > 0  # Return True if course was deleted
            
        except OperationalError as e:
            self.session.rollback()
            print(f"Error deleting course: {e}")
            return False
        finally:
            self.session.close()


db_manager = DatabaseManager()
