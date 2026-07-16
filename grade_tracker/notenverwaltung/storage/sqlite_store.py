import sqlite3
from notenverwaltung.storage.base import GradeStore
from notenverwaltung.models.student import Student
from notenverwaltung.models.course import Course
from notenverwaltung.models.grade import Grade

class SqliteGradeStore(GradeStore):
    """SQLite backend wrapping database operations according to Phase 4, Step 3."""
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.execute("PRAGMA foreign_keys = ON;")
        self._conn.row_factory = sqlite3.Row
        self.create_schema()

    def create_schema(self) -> None:
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL
            );
        """)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                course_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                max_grade REAL NOT NULL DEFAULT 100.0,
                passing_grade REAL NOT NULL DEFAULT 50.0
            );
        """)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS grades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                course_id TEXT NOT NULL,
                score REAL NOT NULL,
                date TEXT NOT NULL,
                notes TEXT DEFAULT '',
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                FOREIGN KEY (course_id) REFERENCES courses(course_id)
            );
        """)
        self._conn.commit()

    def add_student(self, student: Student) -> None:
        try:
            self._conn.execute(
                "INSERT INTO students (student_id, first_name, last_name, email) VALUES (?, ?, ?, ?);",
                (student.student_id, student.first_name, student.last_name, student.email)
            )
            self._conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError(f"Student with ID {student.student_id} already exists.")

    def get_student(self, student_id: str) -> Student | None:
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM students WHERE student_id = ?;", (student_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return Student(row["student_id"], row["first_name"], row["last_name"], row["email"])

    def add_course(self, course: Course) -> None:
        try:
            self._conn.execute(
                "INSERT INTO courses (course_id, name, max_grade, passing_grade) VALUES (?, ?, ?, ?);",
                (course.course_id, course.name, course.max_grade, course.passing_grade)
            )
            self._conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError(f"Course with ID {course.course_id} already exists.")

    def get_course(self, course_id: str) -> Course | None:
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM courses WHERE course_id = ?;", (course_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return Course(row["course_id"], row["name"], row["max_grade"], row["passing_grade"])

    def record_grade(self, grade: Grade) -> None:
        try:
            self._conn.execute(
                "INSERT INTO grades (student_id, course_id, score, date, notes) VALUES (?, ?, ?, ?, ?);",
                (grade.student.student_id, grade.course.course_id, grade.score, grade.date, grade.notes)
            )
            self._conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError("Student or Course does not exist in the database.")

    def get_student_grades(self, student_id: str) -> list[Grade]:
        cursor = self._conn.cursor()
        query = """
            SELECT g.id AS grade_id, g.score, g.date, g.notes,
                   s.student_id, s.first_name, s.last_name, s.email,
                   c.course_id, c.name AS course_name, c.max_grade, c.passing_grade
            FROM grades g
            JOIN students s ON g.student_id = s.student_id
            JOIN courses c ON g.course_id = c.course_id
            WHERE g.student_id = ?;
        """
        cursor.execute(query, (student_id,))
        rows = cursor.fetchall()
        
        grades_list = []
        for row in rows:
            student = Student(row["student_id"], row["first_name"], row["last_name"], row["email"])
            course = Course(row["course_id"], row["course_name"], row["max_grade"], row["passing_grade"])
            grade = Grade(student=student, course=course, score=row["score"], date=row["date"], notes=row["notes"])
            grades_list.append(grade)
        return grades_list

    def get_course_grades(self, course_id: str) -> list[Grade]:
        cursor = self._conn.cursor()
        query = """
            SELECT g.id AS grade_id, g.score, g.date, g.notes,
                   s.student_id, s.first_name, s.last_name, s.email,
                   c.course_id, c.name AS course_name, c.max_grade, c.passing_grade
            FROM grades g
            JOIN students s ON g.student_id = s.student_id
            JOIN courses c ON g.course_id = c.course_id
            WHERE g.course_id = ?;
        """
        cursor.execute(query, (course_id,))
        rows = cursor.fetchall()
        
        grades_list = []
        for row in rows:
            student = Student(row["student_id"], row["first_name"], row["last_name"], row["email"])
            course = Course(row["course_id"], row["course_name"], row["max_grade"], row["passing_grade"])
            grade = Grade(student=student, course=course, score=row["score"], date=row["date"], notes=row["notes"])
            grades_list.append(grade)
        return grades_list

    def close(self) -> None:
        self._conn.close()