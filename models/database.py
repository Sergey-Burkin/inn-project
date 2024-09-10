import psycopg2
from psycopg2 import pool
import bcrypt


class DatabaseManager:
    def __init__(self):
        self.connection_pool = pool.SimpleConnectionPool(
            1, 20,
            host="localhost",
            database="online_learning_db",
            user="postgres",
            password="admin"
        )
        self.create_tables()

    def get_connection(self):
        return self.connection_pool.getconn()

    def release_connection(self, connection):
        self.connection_pool.putconn(connection)

    def create_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # SQL-запросы для создания таблиц
        sql_create_users = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL CHECK (role IN ('student', 'teacher')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """

        sql_create_courses = """
        CREATE TABLE IF NOT EXISTS courses (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            teacher_id INTEGER REFERENCES users(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """

        sql_create_course_sections = """
        CREATE TABLE IF NOT EXISTS course_sections (
            id SERIAL PRIMARY KEY,
            course_id INTEGER REFERENCES courses(id),
            title VARCHAR(100) NOT NULL,
            order_num INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """

        sql_create_video_materials = """
        CREATE TABLE IF NOT EXISTS video_materials (
            id SERIAL PRIMARY KEY,
            course_section_id INTEGER REFERENCES course_sections(id),
            title VARCHAR(200) NOT NULL,
            file_path VARCHAR(255) NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """

        sql_create_tests = """
        CREATE TABLE IF NOT EXISTS tests (
            id SERIAL PRIMARY KEY,
            course_section_id INTEGER REFERENCES course_sections(id),
            title VARCHAR(100) NOT NULL,
            total_questions INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """

        sql_create_test_questions = """
        CREATE TABLE IF NOT EXISTS test_questions (
            id SERIAL PRIMARY KEY,
            test_id INTEGER REFERENCES tests(id),
            question_text TEXT NOT NULL,
            correct_answer VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """

        sql_create_user_answers = """
        CREATE TABLE IF NOT EXISTS user_answers (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            test_question_id INTEGER REFERENCES test_questions(id),
            answer_text VARCHAR(255),
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """

        sql_create_grades = """
        CREATE TABLE IF NOT EXISTS grades (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            course_id INTEGER REFERENCES courses(id),
            grade NUMERIC(5,2),
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """

        # Выполнение SQL-запросов
        cursor.execute(sql_create_users)
        cursor.execute(sql_create_courses)
        cursor.execute(sql_create_course_sections)
        cursor.execute(sql_create_video_materials)
        cursor.execute(sql_create_tests)
        cursor.execute(sql_create_test_questions)
        cursor.execute(sql_create_user_answers)
        cursor.execute(sql_create_grades)

        conn.commit()
        print("Таблицы успешно созданы")
        self.release_connection(conn)


    def hash_password(self, password):
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed_password.decode('utf-8')


    def register_user(self, username, email, password, role):
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("INSERT INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, %s)",
                        (username, email, self.hash_password(password), role))
            
            conn.commit()
            print(f"User {username} registered successfully")
        except Exception as e:
            print(f"Error registering user: {e}")
            conn.rollback()
        finally:
            db_manager.release_connection(conn)

    def create_course(self, title, teacher_id):
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("INSERT INTO courses (title, teacher_id) VALUES (%s, %s)", (title, teacher_id))
            course_id = cursor.fetchone()[0]
            conn.commit()
            print(f"Course '{title}' created successfully (ID: {course_id})")
        except Exception as e:
            print(f"Error creating course: {e}")
            conn.rollback()
        finally:
            db_manager.release_connection(conn)



    def get_user_by_username(self):
        pass




db_manager = DatabaseManager()
