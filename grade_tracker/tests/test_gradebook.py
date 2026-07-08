import pytest
from notenverwaltung.student import Student
from notenverwaltung.course import Course
from notenverwaltung.gradebook import GradeBook

@pytest.fixture
def fresh_gradebook():
    """Create an empty GradeBook for testing."""
    return GradeBook()

# Implementation of tests for add_student method
def test_add_student_valid(fresh_gradebook):
    """Test that a student is added successfully."""
    student = Student("S123", "Daniel", "Mustermann", "daniel@example.com")
    fresh_gradebook.add_student(student)
    
    assert "S123" in fresh_gradebook.students
    assert fresh_gradebook.students["S123"] == student

# Implementation of tests for add_student method
def test_add_duplicate_student_raises_error(fresh_gradebook):
    """Test that adding a duplicate student raises an error."""
    student1 = Student("S123", "Daniel", "Mustermann", "daniel@example.com")
    student2 = Student("S123", "Jane", "Doe", "jane@example.com")
    
    fresh_gradebook.add_student(student1)
    with pytest.raises(ValueError, match="Student ID already exists"):
        fresh_gradebook.add_student(student2)

# Implementation of tests for add_course method
def test_add_course_valid(fresh_gradebook):
    """Test that a course is added successfully."""
    course = Course("CS101", "Python Basics")
    fresh_gradebook.add_course(course)
    
    assert "CS101" in fresh_gradebook.courses
    assert fresh_gradebook.courses["CS101"] == course

# Implementation of tests for add_course method
def test_add_duplicate_course_raises_error(fresh_gradebook):
    """Test that adding a duplicate course raises an error."""
    course1 = Course("CS101", "Python Basics")
    course2 = Course("CS101", "Advanced Python")
    
    fresh_gradebook.add_course(course1)
    with pytest.raises(ValueError, match="Course ID already exists"):
        fresh_gradebook.add_course(course2)

# Implemntation of tests for record_grade method
def test_record_grade_valid(fresh_gradebook):
    """Prüft, ob eine Note für existierende Studenten/Kurse korrekt eingetragen wird."""
    student = Student("S123", "Daniel", "Mustermann", "daniel@example.com")
    course = Course("CS101", "Python Basics")
    fresh_gradebook.add_student(student)
    fresh_gradebook.add_course(course)
    
    # Note eintragen
    grade = fresh_gradebook.record_grade(
        student_id="S123",
        course_id="CS101",
        score=95.0,
        date="2026-07-08",
        notes="Hervorragende Leistung"
    )
    
    assert len(fresh_gradebook.grades) == 1
    assert fresh_gradebook.grades[0] == grade
    assert grade.student == student
    assert grade.course == course

def test_record_grade_student_not_found_raises_error(fresh_gradebook):
    """Prüft, ob ein Fehler fliegt, wenn der Student nicht existiert."""
    course = Course("CS101", "Python Basics")
    fresh_gradebook.add_course(course)
    
    with pytest.raises(ValueError, match="Student not found"):
        fresh_gradebook.record_grade("UNKNOWN_S", "CS101", 90.0, "2026-07-08")

def test_record_grade_course_not_found_raises_error(fresh_gradebook):
    """Prüft, ob ein Fehler fliegt, wenn der Kurs nicht existiert."""
    student = Student("S123", "Daniel", "Mustermann", "daniel@example.com")
    fresh_gradebook.add_student(student)
    
    with pytest.raises(ValueError, match="Course not found"):
        fresh_gradebook.record_grade("S123", "UNKNOWN_C", 90.0, "2026-07-08")

# Implementation of tests for get_student_grades and get_course_grades methods
@pytest.fixture
def populated_gradebook(fresh_gradebook):
    """Create a populated GradeBook with sample data for filtering and statistics."""
    s1 = Student("S1", "Daniel", "Mustermann", "daniel@example.com")
    s2 = Student("S2", "Jane", "Doe", "jane@example.com")
    c1 = Course("C1", "Python", max_grade=100.0, passing_grade=50.0)
    c2 = Course("C2", "Web", max_grade=100.0, passing_grade=50.0)
    
    fresh_gradebook.add_student(s1)
    fresh_gradebook.add_student(s2)
    fresh_gradebook.add_course(c1)
    fresh_gradebook.add_course(c2)
    
    # Grades
    fresh_gradebook.record_grade("S1", "C1", 90.0, "2026-07-08")
    fresh_gradebook.record_grade("S1", "C2", 80.0, "2026-07-08")
    fresh_gradebook.record_grade("S2", "C1", 45.0, "2026-07-08") # Durchgefallen
    
    return fresh_gradebook

def test_get_student_grades(populated_gradebook):
    """Prüft, ob Noten korrekt nach Student gefiltert werden."""
    s1_grades = populated_gradebook.get_student_grades("S1")
    assert len(s1_grades) == 2
    
    s2_grades = populated_gradebook.get_student_grades("S2")
    assert len(s2_grades) == 1
    assert s2_grades[0].score == 45.0

def test_get_course_grades(populated_gradebook):
    """Prüft, ob Noten korrekt nach Kurs gefiltert werden."""
    c1_grades = populated_gradebook.get_course_grades("C1")
    assert len(c1_grades) == 2
    
    c2_grades = populated_gradebook.get_course_grades("C2")
    assert len(c2_grades) == 1

def test_course_pass_rate(populated_gradebook):
    """Course C1 has two notes: 90 (pass) und 45 (fail) -> 50.0%."""
    assert populated_gradebook.course_pass_rate("C1") == 50.0
    
    # Course C2 has one note: 80 (pass) -> 100.0%
    assert populated_gradebook.course_pass_rate("C2") == 100.0

def test_course_pass_rate_no_grades(fresh_gradebook):
    """A course without grades returns a pass rate of 0.0%."""
    assert fresh_gradebook.course_pass_rate("C99") == 0.0

def test_top_students(populated_gradebook):
    """S1 has average 85.0, S2 has 45.0. S1 must be in place 1."""
    top = populated_gradebook.top_students(n=1)
    assert len(top) == 1
    assert top[0][0].student_id == "S1"
    assert top[0][1] == 85.0

def test_students_at_risk(populated_gradebook):
    """With a threshold of 60.0, S2 (45.0) is at risk, S1 (85.0) is not."""
    at_risk = populated_gradebook.students_at_risk(threshold=60.0)
    assert len(at_risk) == 1
    assert at_risk[0].student_id == "S2"

# Regex search tests
def test_search_students_regex(populated_gradebook):
    """Prüft die flexible Regex-Suche nach Studenten."""
    # Suche nach 'dan' liefert genau 1 Ergebnis (Daniel Mustermann)
    results = populated_gradebook.search_students(r"dan")
    assert len(results) == 1
    assert results[0].first_name == "Daniel"

    # Suche nach 'jane' liefert genau 1 Ergebnis (Jane Doe über ihre E-Mail)
    results_jane = populated_gradebook.search_students(r"jane")
    assert len(results_jane) == 1
    assert results_jane[0].last_name == "Doe"
