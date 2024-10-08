from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import or_, create_engine, Column, Integer, Float, String, Text, Numeric, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from psycopg2 import pool
import bcrypt
import settings
from datetime import datetime

from sqlalchemy import text
from sqlalchemy import func


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
    test_attempts = relationship("TestAttempt", back_populates="user")


class Course(Base):
    __tablename__ = 'courses'

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    codename = Column(String(50))
    teacher_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    created_at = Column(DateTime, default=datetime.utcnow)

    tests = relationship("Test", back_populates="course")
    video_materials = relationship("VideoMaterial", back_populates="course")

    students = relationship("User", secondary=user_courses, back_populates="courses")
    structure = Column(JSONB())

    def __repr__(self):
        return f'Course(id={self.id}, title={self.title})'

class VideoMaterial(Base):
    __tablename__ = 'video_materials'
    
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'))
    title = Column(String(200), nullable=False)
    file_path = Column(String(255), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    course = relationship("Course", back_populates="video_materials")


class Test(Base):
    __tablename__ = 'tests'
    
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id', ondelete='CASCADE'))
    title = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    questions = relationship("TestQuestion", back_populates="test")
    attempts = relationship("TestAttempt", back_populates="test")
    structure = Column(JSONB) 

    def __repr__(self):
        return f'Test(id={self.id}, title={self.title})'
    course = relationship("Course", back_populates="tests")

class TestQuestion(Base):
    __tablename__ = 'test_questions'
    
    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey('tests.id', ondelete='CASCADE'))
    question_text = Column(Text, nullable=True)
    correct_answer = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    title = Column(String(255), nullable=False)
    test = relationship("Test", back_populates="questions")
    answers = relationship("Answer", back_populates="question")

    def __repr__(self):
        return f'TestQuestion(id={self.id}, test_id={self.test_id}, title={self.title}, question_text={self.question_text})'

class TestAttempt(Base):
    __tablename__ = 'test_attempts'
    
    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey('tests.id', ondelete='CASCADE'))
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    submitted_at = Column(DateTime, default=datetime.utcnow)

    test = relationship("Test", back_populates="attempts")
    user = relationship("User", back_populates="test_attempts")
    answers = relationship("Answer", back_populates="attempt")

    def __repr__(self):
        return f'TestAttempt(id={self.id}, test_id={self.test_id}, user_id={self.user_id}, submitted_at={self.submitted_at})'


class Answer(Base):
    __tablename__ = 'answers'
    
    id = Column(Integer, primary_key=True)
    test_attempt_id = Column(Integer, ForeignKey('test_attempts.id', ondelete='CASCADE'))
    test_question_id = Column(Integer, ForeignKey('test_questions.id', ondelete='CASCADE'))
    given_answer = Column(Text)
    score = Column(Float, default=0.0)


    attempt = relationship("TestAttempt", back_populates="answers")
    question = relationship("TestQuestion", back_populates="answers")

    def __repr__(self):
        return f'Answer(id={self.id}, test_attempt_id={self.test_attempt_id}, test_question_id={self.test_question_id}, given_answer={self.given_answer})'

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
            course_id = self.add(Course, {"title": title, "teacher_id": teacher_id})
            
            if course_id is None:
                raise ValueError("Failed to create course")
            
            self.assign_user_to_course(teacher_id, course_id)
            print(f"Course '{title}' created successfully")
        except OperationalError as e:
            self.session.rollback()
            print(f"Error creating course: {e}")
        finally:
            self.session.close()

    def assign_user_to_course(self, user_id, course_id):
        try:
            # Check if the assignment already exists
            existing_assignment = self.session.query(user_courses).\
                filter(user_courses.c.user_id == user_id,
                       user_courses.c.course_id == course_id).\
                first()
            
            if existing_assignment:
                print(f"Assignment between user {user_id} and course {course_id} already exists.")
                return
            
            # If no existing assignment, create a new one
            self.session.execute(
                user_courses.insert().values(
                    user_id=user_id,
                    course_id=course_id
                )
            )
            self.session.commit()
            print(f"User {user_id} assigned to course {course_id}.")
        
        except OperationalError as e:
            self.session.rollback()
            print(f"Error assigning user to course: {e}")
        
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


    def add(self, entity_class, params):
        try:
            instance = entity_class(**params)
            self.session.add(instance)
            self.session.commit()
            return instance.id
        except OperationalError as e:
            self.session.rollback()
            print(f"Error adding {entity_class.__name__}: {e}")
            return None
        finally:
            self.session.close()

    def edit(self, entity_class, id, feature, new_value):
        try:
            instance = self.session.query(entity_class).filter_by(id=id).first()
            if instance:
                setattr(instance, feature, new_value)
                self.session.commit()
            else:
                raise ValueError(f"{entity_class.__name__} with id {id} not found")
        except OperationalError as e:
            self.session.rollback()
            print(f"Error editing {entity_class.__name__}: {e}")
        finally:
            self.session.close()

    def delete(self, entity_class, id):
        try:
            instance = self.session.query(entity_class).filter_by(id=id).first()
            if instance:
                self.session.delete(instance)
                self.session.commit()
                return True
            else:
                raise ValueError(f"{entity_class.__name__} with id {id} not found")
        except OperationalError as e:
            self.session.rollback()
            print(f"Error deleting {entity_class.__name__}: {e}")
            return False
        finally:
            self.session.close()

    def delete_with_cascade(self, entity_class, id):
        try:
            instance = self.session.query(entity_class).filter_by(id=id).first()
            if not instance:
                self._recursive_delete(instance)
                
                self.session.delete(instance)

                # Start with the main entity
                
                # Recursively delete related entities
                
                self.session.commit()
                return True
            else:
                raise ValueError(f"{entity_class.__name__} with id {id} not found")
        except OperationalError as e:
            self.session.rollback()
            print(f"Error deleting {entity_class.__name__}: {e}")
            return False
        finally:
            self.session.close()

    def _recursive_delete(self, instance):
        for relationship in instance.__mapper__.relationships.values():
            related_entities = self.session.query(relationship.entity).filter(
                relationship.column == instance.id
            )
            
            for related_entity in related_entities:
                self.session.delete(related_entity)
                
                # Recursively delete nested relationships
                self._recursive_delete(related_entity)
    def get(self, entity_class, id):
        try:
            instance = self.session.query(entity_class).filter_by(id=id).first()
            if instance:
                return instance.__dict__
            else:
                raise ValueError(f"{entity_class.__name__} with id {id} not found")
        except OperationalError as e:
            self.session.rollback()
            print(f"Error getting {entity_class.__name__}: {e}")
            return None
        finally:
            self.session.close()
    

    def get_related_objects(self, feature, class_name, feature_value):
        """
        Get related objects of type class_name associated with the given feature and feature_value.
        
        :param feature: The feature to filter by (e.g., "course_id")
        :param class_name: The class of the objects to retrieve (e.g., Test)
        :param feature_value: The value of the feature to filter by (e.g., course_id)
        :return: List of dictionaries representing the related objects
        """
        try:
            with self.session.begin():
                query = self.session.query(class_name).filter(getattr(class_name, feature) == feature_value)
                related_objects = query.all()
                
                # Convert the objects to dictionaries, excluding internal SQLAlchemy attributes
                result = []
                for obj in related_objects:
                    obj_dict = {k: v for k, v in obj.__dict__.items() if not k.startswith('_sa_')}
                    result.append(obj_dict)
                return result
        except Exception as e:
            print(f"Error fetching related objects: {str(e)}")
            return []
        

    def find_course_by_codename(self, codename):
        try:
            course = self.session.query(Course).filter_by(codename=codename).first()
            if course:
                return course.__dict__
            else:
                return None
        except OperationalError as e:
            self.session.rollback()
            print(f"Error finding course: {e}")
            return None
        finally:
            self.session.close()

    def create_test_attempt(self, test_id, user_id):
        try:
            attempt = TestAttempt(test_id=test_id, user_id=user_id)
            self.session.add(attempt)
            self.session.commit()
            print(f"Test attempt created successfully")
            return attempt.id
        except OperationalError as e:
            self.session.rollback()
            print(f"Error creating test attempt: {e}")
            return None
        finally:
            self.session.close()

    def submit_answer(self, test_attempt_id, test_question_id, given_answer):
        try:
            answer = Answer(
                test_attempt_id=test_attempt_id,
                test_question_id=test_question_id,
                given_answer=given_answer
            )
            self.session.add(answer)
            self.session.commit()
            print(f"Answer submitted successfully")
            return answer.id
        except OperationalError as e:
            self.session.rollback()
            print(f"Error submitting answer: {e}")
            return None
        finally:
            self.session.close()

    def drop_attempts(self, test_id):
        try:
            # Delete all TestAttempt records associated with the given test_id
            self.session.query(TestAttempt).filter_by(test_id=test_id).delete()
            self.session.commit()
            print(f"All test attempts for test {test_id} have been deleted.")
            return True
        except OperationalError as e:
            self.session.rollback()
            print(f"Error dropping test attempts: {e}")
            return False
        finally:
            self.session.close()

    def count_attempts(self, user_id, test_id):
        try:
            result = self.session.query(func.count()).\
                filter(TestAttempt.user_id == user_id).\
                filter(TestAttempt.test_id == test_id).\
                scalar()
            return result
        except OperationalError as e:
            self.session.rollback()
            print(f"Error counting attempts: {e}")
            return None
        finally:
            self.session.close()

    def get_test_results(self, test_id):
        try:
            attempts = self.session.query(TestAttempt).filter_by(test_id=test_id).all()
            results = []
            for attempt in attempts:
                attempt_results = {
                    "attempt_id": attempt.id,
                    "user_id": attempt.user_id,
                    "submitted_at": attempt.submitted_at,
                    "answers": []
                }
                for answer in attempt.answers:
                    attempt_results["answers"].append({
                        "question_title": answer.question.title,
                        "correct_answer": answer.question.correct_answer,
                        "given_answer": answer.given_answer
                    })
                results.append(attempt_results)
            return results
        except OperationalError as e:
            print(f"Error fetching test results: {e}")
            return None
        finally:
            self.session.close()
    
    def calculate_progress(self, user_id, course_id):
        try:
            # Query all tests for the given course
            tests_query = self.session.query(Test).filter_by(course_id=course_id)
            
            # Initialize total score and count of tests
            total_score = 0
            num_tests = 0
            
            # Iterate through each test
            for test in tests_query.all():
                num_tests += 1
                
                # Find all attempts for this test
                attempts_query = self.session.query(TestAttempt).filter_by(
                    test_id=test.id,
                    user_id=user_id
                )
                
                best_score = 0
                
                # Calculate average score for each attempt and find the best
                for attempt in attempts_query.all():
                    avg_score = self.calculate_average_score(attempt.id)
                    
                    if avg_score is not None and avg_score > best_score:
                        best_score = avg_score
                
                # Add the best score to the total
                total_score += best_score
            
            # Calculate overall progress
            if num_tests > 0:
                progress = total_score / num_tests
            else:
                progress = 0
            
            return progress
        
        except Exception as e:
            print(f"Error calculating progress: {str(e)}")
            return None
    
    def calculate_average_score(self, attempt_id):
        try:
            query = self.session.query(
                func.sum(Answer.score).label('total_score'),
                func.count(Answer.id).label('num_answers')
            ).join(TestAttempt).filter(TestAttempt.id == attempt_id)

            result = query.first()

            if result is None or result.total_score is None or result.num_answers == 0:
                return 0  # No answers or invalid attempt ID

            avg_score = result.total_score / result.num_answers
            return avg_score

        except Exception as e:
            print(f"Error calculating average score: {str(e)}")
            return None
# Usage example:
db_manager = DatabaseManager()

