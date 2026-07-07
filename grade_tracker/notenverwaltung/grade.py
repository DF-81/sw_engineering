from dataclasses import dataclass
from notenverwaltung.student import Student
from notenverwaltung.course import Course

@dataclass
class Grade:
    student: Student
    course: Course
    score: float
    date: str  # ISO Format (YYYY-MM-DD)
    notes: str = ""

    def __post_init__(self) -> None:
        self.score = float(self.score)

        """Validates the reached score against the course limits."""
        if self.score < 0.0 or self.score > self.course.max_grade:
            raise ValueError("Score must be between 0.0 and course max grade")

    @property
    def is_passing(self) -> bool:
        """Returns True if the passing threshold has been reached."""
        return self.score >= self.course.passing_grade

    @property
    def percentage(self) -> float:
        """Calculates the percentage of the achieved points."""
        return (self.score / self.course.max_grade) * 100.0

    @property
    def letter_grade(self) -> str:
        """Determines the letter grade based on the percentage."""
        pct = self.percentage
        if pct >= 90.0:
            return "A"
        if pct >= 80.0:
            return "B"
        if pct >= 70.0:
            return "C"
        if pct >= 60.0:
            return "D"
        return "F"