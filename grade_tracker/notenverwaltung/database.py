import sqlite3
from notenverwaltung.student import Student
from notenverwaltung.course import Course
from notenverwaltung.grade import Grade

class GradeDatabase:
    def __init__(self, db_path: str) -> None:
        """Initialization database connection with the specified path."""
        self.db_path = db_path
        # Hold a permanent connection for the lifetime of this object
        self._conn = sqlite3.connect(self.db_path)
        self._conn.execute("PRAGMA foreign_keys = ON;")
        self._conn.row_factory = sqlite3.Row

    def create_schema(self) -> None:
        """Creates the database schema."""
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL
            );
        """)

        # 2. Table for courses
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                course_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                max_grade REAL NOT NULL DEFAULT 100.0,
                passing_grade REAL NOT NULL DEFAULT 50.0
            );
        """)
        
        # Table for grades
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
        """Adds a new student to the database."""
        try:
            self._conn.execute(
                "INSERT INTO students (student_id, first_name, last_name, email) VALUES (?, ?, ?, ?);",
                (student.student_id, student.first_name, student.last_name, student.email)
            )
            self._conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError(f"Student with ID {student.student_id} already exists.")

    def get_student(self, student_id: str) -> Student | None:
        """Fetches a student by their ID and returns a Student object."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM students WHERE student_id = ?;", (student_id,))
        row = cursor.fetchone()
            
        if row is None:
            return None
                
        return Student(
            student_id=row["student_id"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            email=row["email"]
        )
    
    # Add methods for courses and grades here, similar to the student methods
    def add_course(self, course: Course) -> None:
        """Add a new course to the database."""
        try:
            self._conn.execute(
                "INSERT INTO courses (course_id, name, max_grade, passing_grade) VALUES (?, ?, ?, ?);",
                (course.course_id, course.name, course.max_grade, course.passing_grade)
            )
            self._conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError(f"Course with ID {course.course_id} already exists.")

    def get_course(self, course_id: str) -> Course | None:
        """Fetches a course by its ID and returns a Course object."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM courses WHERE course_id = ?;", (course_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return Course(
            course_id=row["course_id"],
            name=row["name"],
            max_grade=row["max_grade"],
            passing_grade=row["passing_grade"]
        )

    def record_grade(self, grade: Grade) -> None:
        """Save a grade in the database. Checks Foreign Keys via SQLite."""
        try:
            self._conn.execute(
                "INSERT INTO grades (student_id, course_id, score, date, notes) VALUES (?, ?, ?, ?, ?);",
                (grade.student.student_id, grade.course.course_id, grade.score, grade.date, grade.notes)
            )
            self._conn.commit()
        except sqlite3.IntegrityError:
            # Wird geworfen, wenn die foreign key Einschränkung verletzt wird
            raise ValueError("Student or Course does not exist in the database.")

    def get_student_grades(self, student_id: str) -> list[Grade]:
        """Get all grades of a student and link them with the objects (SQL JOIN)."""
        cursor = self._conn.cursor()
        # SQL-JOIN to get all infos about Student, Course and Grade at once
        query = """
            SELECT g.score, g.date, g.notes,
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
            # re-build Objects
            student = Student(row["student_id"], row["first_name"], row["last_name"], row["email"])
            course = Course(row["course_id"], row["course_name"], row["max_grade"], row["passing_grade"])
            # build grade
            grade = Grade(student=student, course=course, score=row["score"], date=row["date"], notes=row["notes"])
            grades_list.append(grade)
            
        return grades_list
    
    def close(self) -> None:
        """Closes the database connection."""
        self._conn.close()
