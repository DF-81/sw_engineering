import pytest
from notenverwaltung.models.student import Student
from notenverwaltung.models.course import Course
from notenverwaltung.gradebook import GradeBook

def test_json_round_trip():
    """Check if a GradeBook can export in a dict and import again without issues."""
    # 1. Setup with Testdatas
    gb = GradeBook()
    s1 = Student("S1", "Daniel", "Mustermann", "daniel@example.com")
    c1 = Course("C1", "Python Basics")
    gb.add_student(s1)
    gb.add_course(c1)
    gb.record_grade("S1", "C1", 85.0, "2026-07-08", "Gute Arbeit")
    
    # 2. Export to Dictionary
    data_dict = gb.to_dict()
    
    # Quick check if the structure in the dict is correct
    assert "students" in data_dict
    assert "courses" in data_dict
    assert "grades" in data_dict
    assert data_dict["students"]["S1"]["first_name"] == "Daniel"
    
    # 3. Import from the dictionary into a new GradeBook
    new_gb = GradeBook.from_dict(data_dict)
    
    # 4. Check if the new GradeBook contains exactly the same data
    assert "S1" in new_gb.students
    assert new_gb.students["S1"].full_name == "Daniel Mustermann"
    assert "C1" in new_gb.courses
    
    assert len(new_gb.grades) == 1
    assert new_gb.grades[0].score == 85.0
    # Wichtig: Prüfen, ob die Verknüpfung im Speicher wieder stimmt
    assert new_gb.grades[0].student == new_gb.students["S1"]

# Implement a test for the import_grades_from_csv method
def test_import_grades_from_csv(tmp_path):
    """Check the robust mass import of grades from a CSV file."""
    # 1. Setup GradeBooks with existing students and courses
    gb = GradeBook()
    gb.add_student(Student("S1", "Daniel", "Mustermann", "daniel@example.com"))
    gb.add_student(Student("S2", "Jane", "Doe", "jane@example.com"))
    gb.add_course(Course("C1", "Python Basics"))
    
    # 2. Creation of a simulated CSV file with errors
    csv_content = (
        "student_id,course_id,score,date\n"  # Header
        "S1,C1,90.0,2026-07-08\n"            # Valid
        "S2,C1,45.5,2026-07-08\n"            # Valid
        "S99,C1,80.0,2026-07-08\n"           # Invalid: Student does not exist
        "S1,C1,invalid_score,2026-07-08\n"   # Invalid: Not a number
        "S1,C1,85.0,08-07-2026\n"            # Invalid: Wrong date format (not ISO)
    )
    
    csv_file = tmp_path / "grades_import.csv"
    csv_file.write_text(csv_content, encoding="utf-8")
    
    # 3. Call Import
    report = gb.import_grades_from_csv(csv_file)
    
    # 4. Verification of the report and the state
    assert report["success_count"] == 2
    assert report["skipped_count"] == 3
    assert len(report["errors"]) == 3  # Must contain 3 error messages
    
    # Check if the valid grades have been added to the system
    assert len(gb.grades) == 2
    assert gb.grades[0].score == 90.0

# Add test for export_grades_to_csv method
def test_export_grades_to_csv(tmp_path):
    """Check if grades are correctly exported to a CSV file."""
    gb = GradeBook()
    s1 = Student("S1", "Daniel", "Mustermann", "daniel@example.com")
    c1 = Course("C1", "Python Basics")
    gb.add_student(s1)
    gb.add_course(c1)
    gb.record_grade("S1", "C1", 95.0, "2026-07-08", "Sehr gut")

    output_file = tmp_path / "grades_export.csv"
    
    # Call the export method
    gb.export_grades_to_csv(output_file)
    assert output_file.exists()

    # Verify the content of the file
    content = output_file.read_text(encoding="utf-8")
    lines = content.strip().split("\n")
    
    assert lines[0] == "student_id,course_id,score,date"  # Header
    assert lines[1] == "S1,C1,95.0,2026-07-08"            # Datenzeile

