from dataclasses import dataclass

@dataclass
class Student:
    student_id: str
    first_name: str
    last_name: str
    email: str

    def __post_init__(self) -> None:
        """Validates fields after initialization."""
        if not self.first_name.strip():
            raise ValueError("First name must not be empty")
        
        if not self.last_name.strip():
            raise ValueError("Last name must not be empty")
            
        if "@" not in self.email:
            raise ValueError("Invalid email format")

    @property
    def full_name(self) -> str:
        """Gives the combined name."""
        return f"{self.first_name} {self.last_name}"

    def __str__(self) -> str:
        """Gives a readable string representation."""
        return f"Student {self.student_id}: {self.full_name} ({self.email})"