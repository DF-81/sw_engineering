from abc import ABC, abstractmethod
from notenverwaltung.models.student import Student
from notenverwaltung.models.course import Course
from notenverwaltung.models.grade import Grade

class GradeStore(ABC):
    """Abstract storage interface according to Phase 4 requirements."""

    @abstractmethod
    def add_student(self, student: Student) -> None:
        pass

    @abstractmethod
    def get_student(self, student_id: str) -> Student | None:
        pass

    @abstractmethod
    def add_course(self, course: Course) -> None:
        pass

    @abstractmethod
    def get_course(self, course_id: str) -> Course | None:
        pass

    @abstractmethod
    def record_grade(self, grade: Grade) -> None:
        pass

    @abstractmethod
    def get_student_grades(self, student_id: str) -> list[Grade]:
        pass

    @abstractmethod
    def get_course_grades(self, course_id: str) -> list[Grade]:
        pass