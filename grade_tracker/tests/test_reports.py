import pytest
from notenverwaltung.models.student import Student
from notenverwaltung.models.course import Course
from notenverwaltung.gradebook import GradeBook
from notenverwaltung.reports.base import TextReportGenerator, CsvReportGenerator

@pytest.fixture
def sample_gradebook():
    """Create a GradeBook with Testdatas for reports."""
    gb = GradeBook()
    s1 = Student("S1", "Daniel", "Mustermann", "daniel@example.com")
    c1 = Course("C1", "Python Basics", max_grade=100.0, passing_grade=50.0)
    gb.add_student(s1)
    gb.add_course(c1)
    gb.record_grade("S1", "C1", 90.0, "2026-07-13", "Sehr gut")
    return gb

def test_text_report_generator(sample_gradebook):
    """Verifies that the Text-Report contains the correct keywords."""
    generator = TextReportGenerator()
    report = generator.generate_student_report("S1", sample_gradebook)
    
    assert "Daniel Mustermann" in report
    assert "Python Basics" in report
    assert "90.0" in report
    assert "PASSED" in report

def test_csv_report_generator(sample_gradebook):
    """Verifies that the CSV-Report provides correct comma-separated values."""
    generator = CsvReportGenerator()
    report = generator.generate_student_report("S1", sample_gradebook)
    
    lines = report.strip().split("\n")
    assert lines[0] == "course_id,course_name,score,letter_grade,status"
    assert "C1,Python Basics,90.0,A,PASSED" in lines[1]