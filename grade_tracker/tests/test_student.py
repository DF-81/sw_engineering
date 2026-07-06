import pytest
from notenverwaltung.student import Student

def test_student_creation_valid():
    """Validates if an regular student is created correctly."""
    student = Student(
        student_id="S123",
        first_name="Daniel",
        last_name="Mustermann",
        email="daniel@example.com"
    )
    assert student.student_id == "S123"
    assert student.first_name == "Daniel"
    assert student.last_name == "Mustermann"
    assert student.email == "daniel@example.com"

def test_student_full_name_property():
    """Validates the full_name property connects first and last names correctly."""
    student = Student("S123", "Daniel", "Mustermann", "daniel@example.com")
    assert student.full_name == "Daniel Mustermann"

def test_student_str_representation():
    """Validates the readable string representation."""
    student = Student("S123", "Daniel", "Mustermann", "daniel@example.com")
    assert "S123" in str(student)
    assert "Daniel Mustermann" in str(student)

def test_student_empty_first_name_raises_error():
    """Validates that an empty first name raises a ValueError."""
    with pytest.raises(ValueError, match="First name must not be empty"):
        Student("S123", "", "Mustermann", "daniel@example.com")

def test_student_empty_last_name_raises_error():
    """Validates that an empty last name raises a ValueError."""
    with pytest.raises(ValueError, match="Last name must not be empty"):
        Student("S123", "Daniel", "", "daniel@example.com")

def test_student_invalid_email_raises_error():
    """Validates that an invalid email raises a ValueError."""
    with pytest.raises(ValueError, match="Invalid email format"):
        Student("S123", "Daniel", "Mustermann", "daniel_at_example.com")
