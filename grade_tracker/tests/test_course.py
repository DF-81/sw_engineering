import pytest
from notenverwaltung.course import Course

def test_course_creation_valid_with_defaults():
    """Validates if course object is created with default values correctly."""
    course = Course(course_id="SE101", name="Software Engineering")
    assert course.course_id == "SE101"
    assert course.name == "Software Engineering"
    assert course.max_grade == 100.0
    assert course.passing_grade == 50.0

def test_course_creation_custom_grades():
    """Validates if course object is created with custom grades correctly."""
    course = Course(course_id="KI1", name="Künstliche Intelligenz", max_grade=6.0, passing_grade=4.0)
    assert course.max_grade == 6.0
    assert course.passing_grade == 4.0

def test_course_invalid_max_grade_raises_error():
    """Validates if course object raises error for invalid max grade."""
    with pytest.raises(ValueError, match="Max grade must be greater than 0"):
        Course(course_id="CS101", name="Test", max_grade=0.0)
        
    with pytest.raises(ValueError, match="Max grade must be greater than 0"):
        Course(course_id="CS101", name="Test", max_grade=-10.0)

def test_course_invalid_passing_grade_raises_error():
    """Validates if course object raises error for invalid passing grade."""
    with pytest.raises(ValueError, match="Passing grade must be between 0.0 and max grade"):
        Course(course_id="CS101", name="Test", max_grade=100.0, passing_grade=0.0)
        
def test_course_invalid_passing_grade_raises_error():
    """Validates if course object raises error for invalid passing grade."""
    with pytest.raises(ValueError, match="Passing grade must be between 0.0 and max grade"):
        Course(course_id="CS101", name="Test", max_grade=100.0, passing_grade=101.0)