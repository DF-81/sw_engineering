from abc import ABC, abstractmethod
from notenverwaltung.gradebook import GradeBook

class ReportGenerator(ABC):
    """Abstract class (ABC) for all report generators."""
    
    @abstractmethod
    def generate_student_report(self, student_id: str, gradebook: GradeBook) -> str:
        """Must be overridden in subclasses."""
        pass

    @abstractmethod
    def generate_course_report(self, course_id: str, gradebook: GradeBook) -> str:
        """Must be overridden in subclasses."""
        pass

    @abstractmethod
    def generate_summary_report(self, gradebook: GradeBook) -> str:
        """Must be overridden in subclasses."""
        pass


class TextReportGenerator(ReportGenerator):
    """Generate reports as formated and readable text."""
    
    def generate_student_report(self, student_id: str, gradebook: GradeBook) -> str:
        student = gradebook.students.get(student_id)
        if not student:
            return f"Student mit ID {student_id} nicht gefunden."
            
        grades = gradebook.get_student_grades(student_id)
        avg = gradebook.student_average(student_id)
        
        report = f"📄 NOTENBERICHT FÜR: {student.full_name} ({student_id})\n"
        report += "="*50 + "\n"
        for g in grades:
            status = "PASSED" if g.is_passing else "FAILED"
            report += f"• {g.course.name}: {g.score}/{g.course.max_grade} ({g.letter_grade}) -> [{status}]\n"
        report += "="*50 + "\n"
        report += f"📈 Gesamtdurchschnitt: {avg:.1f}%\n"
        return report

    def generate_course_report(self, course_id: str, gradebook: GradeBook) -> str:
        course = gradebook.courses.get(course_id)
        if not course:
            return f"Kurs mit ID {course_id} nicht gefunden."
        avg = gradebook.course_average(course_id)
        pass_rate = gradebook.course_pass_rate(course_id)
        
        return f"📘 KURSBERICHT: {course.name}\nDurchschnitt: {avg:.1f}\nBestehensquote: {pass_rate:.1f}%"

    def generate_summary_report(self, gradebook: GradeBook) -> str:
        return f"📊 SYSTEMÜBERSICHT\nAnzahl Studenten: {len(gradebook.students)}\nAnzahl Kurse: {len(gradebook.courses)}"


class CsvReportGenerator(ReportGenerator):
    """Generate reports in the standardized CSV format."""
    
    def generate_student_report(self, student_id: str, gradebook: GradeBook) -> str:
        grades = gradebook.get_student_grades(student_id)
        csv_output = "course_id,course_name,score,letter_grade,status\n"
        for g in grades:
            status = "PASSED" if g.is_passing else "FAILED"
            csv_output += f"{g.course.course_id},{g.course.name},{g.score},{g.letter_grade},{status}\n"
        return csv_output

    def generate_course_report(self, course_id: str, gradebook: GradeBook) -> str:
        grades = gradebook.get_course_grades(course_id)
        csv_output = "student_id,student_name,score,status\n"
        for g in grades:
            status = "PASSED" if g.is_passing else "FAILED"
            csv_output += f"{g.student.student_id},{g.student.full_name},{g.score},{status}\n"
        return csv_output

    def generate_summary_report(self, gradebook: GradeBook) -> str:
        csv_output = "metric,value\n"
        csv_output += f"total_students,{len(gradebook.students)}\n"
        csv_output += f"total_courses,{len(gradebook.courses)}\n"
        return csv_output