from dataclasses import dataclass, field
from notenverwaltung.storage.base import GradeStore
from notenverwaltung.models.student import Student
from notenverwaltung.models.course import Course
from notenverwaltung.models.grade import Grade

@dataclass
class InMemoryGradeStore(GradeStore):
    """InMemory backend wrapping dicts according to Phase 4, Step 3."""
    students: dict[str, Student] = field(default_factory=dict)
    courses: dict[str, Course] = field(default_factory=dict)
    grades: list[Grade] = field(default_factory=list)

    def add_student(self, student: Student) -> None:
        if student.student_id in self.students:
            raise ValueError("Student ID already exists")
        self.students[student.student_id] = student

    def get_student(self, student_id: str) -> Student | None:
        return self.students.get(student_id)

    def add_course(self, course: Course) -> None:
        if course.course_id in self.courses:
            raise ValueError("Course ID already exists")
        self.courses[course.course_id] = course

    def get_course(self, course_id: str) -> Course | None:
        return self.courses.get(course_id)

    def record_grade(self, grade: Grade) -> None:
        self.grades.append(grade)

    def get_student_grades(self, student_id: str) -> list[Grade]:
        return [g for g in self.grades if g.student.student_id == student_id]

    def get_course_grades(self, course_id: str) -> list[Grade]:
        return [g for g in self.grades if g.course.course_id == course_id]