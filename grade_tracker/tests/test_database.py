import pytest
import sqlite3
from notenverwaltung.models.student import Student
from notenverwaltung.models.course import Course
from notenverwaltung.models.grade import Grade
from notenverwaltung.storage.sqlite_store import SqliteGradeStore

@pytest.fixture
def store():
    """Creates a fresh in-memory SqliteGradeStore for each test."""
    database_store = SqliteGradeStore(":memory:")
    yield database_store
    database_store.close()

def test_create_schema(store):
    """Checks if the tables are successfully created in the database."""
    cursor = store._conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row["name"] for row in cursor.fetchall()]
        
    assert "students" in tables
    assert "courses" in tables
    assert "grades" in tables

def test_add_and_get_student(store):
    """Checks if a student can be written to the database and read back."""
    student = Student("S99", "Daniel", "Datenbank", "daniel@db.com")
    store.add_student(student)
    
    fetched_student = store.get_student("S99")
    assert fetched_student is not None
    assert fetched_student.student_id == "S99"

def test_get_non_existent_student_returns_none(store):
    """If a student does not exist, None should be returned."""
    assert store.get_student("UNKNOWN") is None