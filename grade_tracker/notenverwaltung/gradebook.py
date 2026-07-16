import json # after refactoring no longer needed, but kept for backward compatibility
from pathlib import Path
import re
from notenverwaltung.storage.base import GradeStore
from notenverwaltung.storage.memory_store import InMemoryGradeStore
from notenverwaltung.models.student import Student
from notenverwaltung.models.course import Course
from notenverwaltung.models.grade import Grade

class GradeBook:
    """Refactored GradeBook that utilizes the GradeStore abstraction (Phase 4, Step 4)."""
    
    def __init__(self, store: GradeStore = None) -> None:
        # Wenn kein Store übergeben wird, nutzen wir als Standard den InMemoryStore
        self.store = store if store is not None else InMemoryGradeStore()

    # Properties für die Kompatibilität mit Phase 2/3 (greift direkt auf den Store zu)
    @property
    def students(self) -> dict:
        if hasattr(self.store, 'students'):
            return self.store.students
        return {}

    @property
    def courses(self) -> dict:
        if hasattr(self.store, 'courses'):
            return self.store.courses
        return {}

    @property
    def grades(self) -> list:
        if hasattr(self.store, 'grades'):
            return self.store.grades
        return []

    # --- CRUD-DELEGATION to the store ---
    def add_student(self, student: Student) -> None:
        self.store.add_student(student)

    def add_course(self, course: Course) -> None:
        self.store.add_course(course)

    def record_grade(self, student_id: str, course_id: str, score: float, date: str, notes: str = "") -> Grade:
        student = self.store.get_student(student_id)
        course = self.store.get_course(course_id)
        
        if not student:
            raise ValueError("Student not found")
        if not course:
            raise ValueError("Course not found")
            
        new_grade = Grade(student=student, course=course, score=score, date=date, notes=notes)
        self.store.record_grade(new_grade)
        return new_grade

    def get_student_grades(self, student_id: str) -> list[Grade]:
        return self.store.get_student_grades(student_id)

    def get_course_grades(self, course_id: str) -> list[Grade]:
        return self.store.get_course_grades(course_id)

    # --- Statistic calculations (stay at the GradeBook) ---
    def student_average(self, student_id: str) -> float:
        student_grades = self.get_student_grades(student_id)
        if not student_grades:
            return 0.0
        return sum(g.percentage for g in student_grades) / len(student_grades)

    def course_average(self, course_id: str) -> float:
        course_grades = self.get_course_grades(course_id)
        if not course_grades:
            return 0.0
        return sum(g.score for g in course_grades) / len(course_grades)

    def course_pass_rate(self, course_id: str) -> float:
        course_grades = self.get_course_grades(course_id)
        if not course_grades:
            return 0.0
        passing_count = sum(1 for g in course_grades if g.is_passing)
        return (passing_count / len(course_grades)) * 100.0

    def top_students(self, n: int = 5) -> list[tuple[Student, float]]:
        # Funktioniert nur vollumfänglich im InMemory-Modus via Dict-Iteration
        if not hasattr(self.store, 'students'):
            return []
        student_averages = []
        for student in self.store.students.values():
            if self.get_student_grades(student.student_id):
                avg = self.student_average(student.student_id)
                student_averages.append((student, avg))
        return sorted(student_averages, key=lambda x: x[1], reverse=True)[:n]

    def students_at_risk(self, threshold: float = 60.0) -> list[Student]:
        if not hasattr(self.store, 'students'):
            return []
        return [
            s for s in self.store.students.values()
            if self.get_student_grades(s.student_id) and self.student_average(s.student_id) < threshold
        ]

    # --- REGEX Searchfunction ---
    def search_students(self, query: str) -> list[Student]:
        if not hasattr(self.store, 'students'):
            return []
        pattern = re.compile(query, re.IGNORECASE)
        return [
            s for s in self.store.students.values()
            if pattern.search(s.first_name) or pattern.search(s.last_name) or pattern.search(s.email)
        ]

    def search_courses(self, query: str) -> list[Course]:
        if not hasattr(self.store, 'courses'):
            return []
        pattern = re.compile(query, re.IGNORECASE)
        return [c for c in self.store.courses.values() if pattern.search(c.name)]

    # --- PERSISTENZ (FÜR JSON ROUND-TRIP IN PHASE 3) ---
    def to_dict(self) -> dict:
        return {
            "students": {
                s_id: {"student_id": s.student_id, "first_name": s.first_name, "last_name": s.last_name, "email": s.email}
                for s_id, s in self.students.items()
            },
            "courses": {
                c_id: {"course_id": c.course_id, "name": c.name, "max_grade": c.max_grade, "passing_grade": c.passing_grade}
                for c_id, c in self.courses.items()
            },
            "grades": [
                {"student_id": g.student.student_id, "course_id": g.course.course_id, "score": g.score, "date": g.date, "notes": g.notes}
                for g in self.grades
            ]
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GradeBook":
        gradebook = cls()
        for s_data in data.get("students", {}).values():
            gradebook.add_student(Student(s_data["student_id"], s_data["first_name"], s_data["last_name"], s_data["email"]))
        for c_data in data.get("courses", {}).values():
            gradebook.add_course(Course(c_data["course_id"], c_data["name"], c_data["max_grade"], c_data["passing_grade"]))
        for g_data in data.get("grades", []):
            gradebook.record_grade(g_data["student_id"], g_data["course_id"], g_data["score"], g_data["date"], g_data["notes"])
        return gradebook
    
        # --- CSV IMPORT & EXPORT (PHASE 3) ---
    def import_grades_from_csv(self, filepath) -> dict:
        """Import grades from a CSV file and return a error report."""
        from pathlib import Path
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {path}")

        report = {"success_count": 0, "skipped_count": 0, "errors": []}
        csv_pattern = re.compile(r"^([^,]+),([^,]+),([^,]+),(\d{4}-\d{2}-\d{2})$")

        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for index, line in enumerate(lines):
            line = line.strip()
            if not line or "student_id" in line:
                continue

            match = csv_pattern.match(line)
            if not match:
                report["skipped_count"] += 1
                report["errors"].append(f"Zeile {index + 1}: Ungültiges CSV-Format oder Datumsformat.")
                continue

            s_id, c_id, score_str, date_str = match.groups()

            try:
                score = float(score_str)
                # Using the store logic via record_grade
                self.record_grade(s_id, c_id, score, date_str)
                report["success_count"] += 1
            except ValueError as e:
                report["skipped_count"] += 1
                report["errors"].append(f"Zeile {index + 1}: {str(e)}")

        return report

    def export_grades_to_csv(self, filepath) -> None:
        """Exportiert alle gespeicherten Noten in eine Standard-CSV-Datei."""
        from pathlib import Path
        path = Path(filepath)
        
        with open(path, "w", encoding="utf-8") as f:
            f.write("student_id,course_id,score,date\n")
            for g in self.grades:
                f.write(f"{g.student.student_id},{g.course.course_id},{g.score},{g.date}\n")