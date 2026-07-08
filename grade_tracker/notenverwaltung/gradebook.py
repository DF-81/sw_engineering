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
