import re # Handle date serialization and validation
from dataclasses import dataclass
from notenverwaltung.models.student import Student
from notenverwaltung.models.course import Course

@dataclass
class Grade:
    student: Student
    course: Course
    score: float
    date: str  # ISO Format (YYYY-MM-DD)
    notes: str = ""

    def __post_init__(self) -> None:
        """Validates the reached score against the course limits."""
        # Convert score to float for consistency
        self.score = float(self.score)
        
        # Validate the grade score
        if self.score < 0.0 or self.score > self.course.max_grade:
            raise ValueError("Score must be between 0.0 and course max grade")

        # Validate the date format (YYYY-MM-DD)
        iso_date_pattern = r"^\d{4}-\d{2}-\d{2}$"
        if not re.match(iso_date_pattern, self.date):
            raise ValueError("Date must be in valid ISO format (YYYY-MM-DD)")

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
        elif pct >= 80.0:
            return "B"
        elif pct >= 70.0:
            return "C"
        elif pct >= 60.0:
            return "D"
        return "F"
    
    def __str__(self) -> str:
        """Gives the required, readable string representation back."""
        status = "PASSED" if self.is_passing else "FAILED"
        return (
            f"Grade: {self.student.full_name} | "
            f"{self.course.name} | "
            f"Score: {self.score}/{self.course.max_grade} ({self.letter_grade}) | "
            f"[{status}]"
        )