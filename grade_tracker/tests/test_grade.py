import pytest
from notenverwaltung.models.student import Student
from notenverwaltung.models.course import Course
from notenverwaltung.models.grade import Grade

@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    student = Student("S1", "Daniel", "Mustermann", "daniel@example.com")
    course = Course("CS101", "Python", max_grade=100.0, passing_grade=50.0)
    return student, course

def test_grade_creation_valid(sample_data):
    student, course = sample_data
    grade = Grade(student=student, course=course, score=85.0, date="2026-07-07")
    
    assert grade.student == student
    assert grade.course == course
    assert grade.score == 85.0
    assert grade.date == "2026-07-07"
    assert grade.notes == ""

def test_grade_properties(sample_data):
    student, course = sample_data
    grade = Grade(student, course, score=75.0, date="2026-07-07")
    
    assert grade.is_passing is True
    assert grade.percentage == 75.0

def test_grade_failing(sample_data):
    student, course = sample_data
    grade = Grade(student, course, score=45.0, date="2026-07-07")
    
    assert grade.is_passing is False

def test_grade_invalid_score_raises_error(sample_data):
    student, course = sample_data
    with pytest.raises(ValueError, match="Score must be between 0.0 and course max grade"):
        Grade(student, course, score=-5.0, date="2026-07-07")
        
    with pytest.raises(ValueError, match="Score must be between 0.0 and course max grade"):
        Grade(student, course, score=105.0, date="2026-07-07")

# Parameterized test for the grade levels
@pytest.mark.parametrize("score,expected_letter", [
    (90.0, "A"),  # gte 90 --> A
    (89.9, "B"),  # lt 90 --> go for grade B
    (80.0, "B"),  # gte 80 --> B
    (79.9, "C"),  # lt 80 --> go for grade C
    (70.0, "C"),  # gte 70 --> C
    (69.9, "D"),  # lt 70 --> go for grade D
    (60.0, "D"),  # gte 60% --> D
    (59.9, "F"),  # lt 60% --> go for grade F
])
def test_grade_letter_boundaries(sample_data, score, expected_letter):
    student, course = sample_data
    grade = Grade(student, course, score=score, date="2026-07-07")
    assert grade.letter_grade == expected_letter
