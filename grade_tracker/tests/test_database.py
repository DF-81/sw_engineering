import pytest
import sqlite3
from notenverwaltung.student import Student
from notenverwaltung.course import Course
from notenverwaltung.grade import Grade
from notenverwaltung.database import GradeDatabase

@pytest.fixture
def db():
    """Creates a fresh in-memory database for each test."""
    database = GradeDatabase(":memory:")
    database.create_schema()
    yield database
    # Close the database connection after the test
    database.close()

def test_create_schema(db):
    """Checks if the tables are successfully created in the database."""
    cursor = db._conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    # with row[0] get the string from the tuple
    tables = [row[0] for row in cursor.fetchall()]
        
    assert "students" in tables
    assert "courses" in tables
    assert "grades" in tables

def test_add_and_get_student(db):
    """Checks if a student can be written to the database and read back."""
    student = Student("S99", "Daniel", "Datenbank", "daniel@db.com")
    db.add_student(student)
    
    fetched_student = db.get_student("S99")
    assert fetched_student is not None
    assert fetched_student.student_id == "S99"
    assert fetched_student.first_name == "Daniel"
    assert fetched_student.email == "daniel@db.com"

def test_get_non_existent_student_returns_none(db):
    """If a student does not exist, None should be returned."""
    assert db.get_student("UNKNOWN") is None

# Insert tests for courses and grades below 
def test_add_and_get_course(db):
    """Check if a course can be written to the database and read back."""
    course = Course("C99", "Datenbanken 1", max_grade=100.0, passing_grade=50.0)
    db.add_course(course)
    
    fetched = db.get_course("C99")
    assert fetched is not None
    assert fetched.course_id == "C99"
    assert fetched.name == "Datenbanken 1"
    assert fetched.max_grade == 100.0

def test_add_and_get_grade(db):
    """Check if a grade can be written to the database and read back."""
    # For a grade, student and course must exist in the DB (Foreign Keys!)
    student = Student("S1", "Daniel", "Mustermann", "daniel@example.com")
    course = Course("C1", "Python Basics", max_grade=100.0, passing_grade=50.0)
    db.add_student(student)
    db.add_course(course)
    
    grade = Grade(student, course, score=90.0, date="2026-07-12", notes="Klasse Arbeit")
    db.record_grade(grade)
    
    # Get grades of the student
    grades = db.get_student_grades("S1")
    assert len(grades) == 1
    assert grades[0].score == 90.0
    assert grades[0].student.student_id == "S1"
    assert grades[0].course.course_id == "C1"

def test_record_grade_missing_student_raises_error(db):
    """ForeignKey Test: Grade without existing student must fail."""
    course = Course("C1", "Python Basics")
    db.add_course(course)
    
    student = Student("MISSING", "Ghost", "User", "ghost@example.com")
    grade = Grade(student, course, score=90.0, date="2026-07-12")
    
    # SQLite covers that due to PRAGMA foreign_keys = ON and throws an error
    with pytest.raises(ValueError, match="Student or Course does not exist"):
        db.record_grade(grade)
