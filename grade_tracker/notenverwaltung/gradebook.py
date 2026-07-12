import json
from pathlib import Path
import re
from dataclasses import dataclass, field
from notenverwaltung.student import Student
from notenverwaltung.course import Course
from notenverwaltung.grade import Grade

@dataclass
class GradeBook:
    # field(default_factory=...) is resposible for that every GradeBook has its own, independent lists and dictionaries. 
    students: dict[str, Student] = field(default_factory=dict)
    courses: dict[str, Course] = field(default_factory=dict)
    grades: list[Grade] = field(default_factory=list)

    def add_student(self, student: Student) -> None:
        """Add an student. Raises ValueError if student ID already exists."""
        if student.student_id in self.students:
            raise ValueError("Student ID already exists")
        self.students[student.student_id] = student

    def add_course(self, course: Course) -> None:
        """Add a course. Raises ValueError if course ID already exists."""
        if course.course_id in self.courses:
            raise ValueError("Course ID already exists")
        self.courses[course.course_id] = course

    def record_grade(self, student_id: str, course_id: str, score: float, date: str, notes: str = "") -> Grade:
        """Create and save an grade if student and course exist."""
        if student_id not in self.students:
            raise ValueError("Student not found")
        if course_id not in self.courses:
            raise ValueError("Course not found")
            
        # Searching for the student and course objects
        student = self.students[student_id]
        course = self.courses[course_id]
        
        # Create new Grade-Object (Validation runs automatically in Grade.__post_init__)
        new_grade = Grade(student=student, course=course, score=score, date=date, notes=notes)
        
        # Save in the internal list
        self.grades.append(new_grade)
        return new_grade

    def get_student_grades(self, student_id: str) -> list[Grade]:
        """Return a defensive copy of all grades for a student."""
        return [g for g in self.grades if g.student.student_id == student_id]

    def get_course_grades(self, course_id: str) -> list[Grade]:
        """Return a defensive copy of all grades for a course."""
        return [g for g in self.grades if g.course.course_id == course_id]
    
    def student_average(self, student_id: str) -> float:
        """Calculates the average percentage of a student across all courses."""
        student_grades = self.get_student_grades(student_id)
        if not student_grades:
            return 0.0
        
        total_percentage = sum(g.percentage for g in student_grades)
        return total_percentage / len(student_grades)

    def course_average(self, course_id: str) -> float:
        """Calculates the average score of a course across all students."""
        course_grades = self.get_course_grades(course_id)
        if not course_grades:
            return 0.0
            
        total_score = sum(g.score for g in course_grades)
        return total_score / len(course_grades)
    
    def course_pass_rate(self, course_id: str) -> float:
        """Return the pass rate of a course in percentage."""
        course_grades = self.get_course_grades(course_id)
        if not course_grades:
            return 0.0
            
        passing_count = sum(1 for g in course_grades if g.is_passing)
        return (passing_count / len(course_grades)) * 100.0

    def top_students(self, n: int = 5) -> list[tuple[Student, float]]:
        """Return the top N students sorted by their average grade."""
        student_averages = []
        for student in self.students.values():
            avg = self.student_average(student.student_id)
            # Laut Aufgabe zählen wir nur Studenten, die auch mindestens eine Note haben
            if self.get_student_grades(student.student_id):
                student_averages.append((student, avg))
                
        # Sort: Highest Average (reverse=True) first
        sorted_students = sorted(student_averages, key=lambda x: x[1], reverse=True)
        return sorted_students[:n]

    def students_at_risk(self, threshold: float = 60.0) -> list[Student]:
        """Return a list of students whose average is below the threshold."""
        at_risk = []
        for student in self.students.values(): # Only for students with grades
            if self.get_student_grades(student.student_id):
                avg = self.student_average(student.student_id)
                if avg < threshold:
                    at_risk.append(student)
        return at_risk
    
    # Regex search methods
    def search_students(self, query: str) -> list[Student]:
        """Searches for students via regex in their full name or email."""
        pattern = re.compile(query, re.IGNORECASE)
        results = []
        for student in self.students.values():
            if (pattern.search(student.first_name) or 
                pattern.search(student.last_name) or 
                pattern.search(student.email)):
                results.append(student)
        return results

    def search_courses(self, query: str) -> list[Course]:
        """Searches for courses via regex in their name."""
        pattern = re.compile(query, re.IGNORECASE)
        return [c for c in self.courses.values() if pattern.search(c.name)]

        # Implementation of the to_dict and from_dict methods for JSON serialization and deserialization
    def to_dict(self) -> dict:
        """Convert the whole GradeBook to a JSON-compatible Dictionary."""
        return {
            "students": {
                s_id: {
                    "student_id": s.student_id,
                    "first_name": s.first_name,
                    "last_name": s.last_name,
                    "email": s.email
                } for s_id, s in self.students.items()
            },
            "courses": {
                c_id: {
                    "course_id": c.course_id,
                    "name": c.name,
                    "max_grade": c.max_grade,
                    "passing_grade": c.passing_grade
                } for c_id, c in self.courses.items()
            },
            "grades": [
                {
                    "student_id": g.student.student_id,
                    "course_id": g.course.course_id,
                    "score": g.score,
                    "date": g.date,
                    "notes": g.notes
                } for g in self.grades
            ]
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GradeBook":
        """Create a fully functional GradeBook object from a dictionary."""
        # 1. Frische GradeBook-Instanz erstellen
        gradebook = cls()
        
        # 2. Studenten wiederherstellen
        for s_data in data.get("students", {}).values():
            student = Student(
                student_id=s_data["student_id"],
                first_name=s_data["first_name"],
                last_name=s_data["last_name"],
                email=s_data["email"]
            )
            gradebook.add_student(student)
            
        # 3. Kurse wiederherstellen
        for c_data in data.get("courses", {}).values():
            course = Course(
                course_id=c_data["course_id"],
                name=c_data["name"],
                max_grade=c_data["max_grade"],
                passing_grade=c_data["passing_grade"]
            )
            gradebook.add_course(course)
            
        # 4. Noten wiederherstellen und sauber verknüpfen
        for g_data in data.get("grades", []):
            gradebook.record_grade(
                student_id=g_data["student_id"],
                course_id=g_data["course_id"],
                score=g_data["score"],
                date=g_data["date"],
                notes=g_data["notes"]
            )
            
        return gradebook

    # Implementation of the save_to_json and load_from_json methods for file persistence
    def save_to_json(self, filepath: str | Path) -> None:
        """Save the entire GradeBook as a formatted JSON text to the hard drive."""
        # Ensure we have a Path object
        path = Path(filepath)
        
        # Get data using our to_dict() method
        data = self.to_dict()
        
        # Datei schreiben (mit UTF-8 für deutsche Umlaute und indent=4 für Lesbarkeit)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    @classmethod
    def load_from_json(cls, filepath: str | Path) -> "GradeBook":
        """Load a JSON file from the hard drive and reconstruct the GradeBook."""
        path = Path(filepath)
        
        if not path.exists():
            raise FileNotFoundError(f"The file {path} does not exist.")
            
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        # Nutzen Sie unsere fertige from_dict() Methode für den Wiederaufbau
        return cls.from_dict(data)

    # Implementation of the import_grades_from_csv method for robust mass import of grades
    def import_grades_from_csv(self, filepath: str | Path) -> dict:
        """Import grades from an existing CSV file and return an error report."""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {path}")

        report = {"success_count": 0, "skipped_count": 0, "errors": []}

        # Regex for a rough structure check of the line (4 comma-separated values)
        # Expected: text,text,number,date(YYYY-MM-DD)
        csv_pattern = re.compile(r"^([^,]+),([^,]+),([^,]+),(\d{4}-\d{2}-\d{2})$")

        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for index, line in enumerate(lines):
            line = line.strip()
            if not line or "student_id" in line: # Skip Header-Row or empty lines
                continue

            match = csv_pattern.match(line)
            if not match:
                report["skipped_count"] += 1
                report["errors"].append(f"Zeile {index + 1}: Ungültiges CSV-Format oder Datumsformat.")
                continue

            s_id, c_id, score_str, date_str = match.groups() # Extract values from Regex-Match

            try:
                # Convert int to float
                score = float(score_str)
                
                # Registry grade (give ValueError, when s_id/c_id are missing od score is wrong)
                self.record_grade(student_id=s_id, course_id=c_id, score=score, date=date_str)
                report["success_count"] += 1
                
            except ValueError as e:
                report["skipped_count"] += 1
                report["errors"].append(f"Zeile {index + 1}: {str(e)}")

        return report
    
    # Implementation of the export_grades_to_csv method for exporting grades to a CSV file
    def export_grades_to_csv(self, filepath: str | Path) -> None:
        """Export all saved grades in a standard CSV file."""
        path = Path(filepath)
        
        with open(path, "w", encoding="utf-8") as f:
            # 1. write Column Headers (Header)
            f.write("student_id,course_id,score,date\n")
            
            # 2. write all grades line by line
            for g in self.grades:
                f.write(f"{g.student.student_id},{g.course.course_id},{g.score},{g.date}\n")

    # Implementation of the export_grades_to_csv method for exporting grades to a CSV file
    def export_grades_to_csv(self, filepath: str | Path) -> None:
        """Export all saved values in a standard CSV file."""
        path = Path(filepath)
        
        with open(path, "w", encoding="utf-8") as f:
            # 1. write Column Headers (Header)
            f.write("student_id,course_id,score,date\n")
            
            # 2. write All Grades Line by Line
            for g in self.grades:
                f.write(f"{g.student.student_id},{g.course.course_id},{g.score},{g.date}\n")
