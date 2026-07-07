from dataclasses import dataclass

@dataclass
class Course:
    course_id: str
    name: str
    max_grade: float = 100.0
    passing_grade: float = 50.0

    def __post_init__(self) -> None:
        """Validates fields after initialization."""
        
        # Convert to float in case int is given
        self.max_grade = float(self.max_grade)
        self.passing_grade = float(self.passing_grade)

        if self.max_grade <= 0.0:
            raise ValueError("Max grade must be greater than 0")
        
        if self.passing_grade < 0.0 or self.passing_grade > self.max_grade:
            raise ValueError("Passing grade must be between 0.0 and max grade")
    
    def __str__(self) -> str:
        """Gives a readable string representation."""
        return f"Course {self.course_id}: {self.name} (Max Grade: {self.max_grade}, Passing Grade: {self.passing_grade})"