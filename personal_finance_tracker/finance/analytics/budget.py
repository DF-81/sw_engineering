# Importing from the sibling package level
from finance.expenses import Expense, total_expenses
"""This model needs to know what an Expense ist and how to calculate total expenses"""
class Budget:
    """Create a class Budget with attribute limit"""
    def __init__(self, limit: float):
        self.limit = limit
    
    def is_limit(self, expenses: list[Expense]) -> bool:
        """Check if total expenses lower equal than limit"""
        return total_expenses(expenses) <= self.limit