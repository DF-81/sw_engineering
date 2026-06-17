class Expense:
    """Create class Expense with attributes amount and category"""
    def __init__(self, amount: float, category: str):
        self.amount = amount
        self.category = category
        
def summarize_expenses(expenses: list[Expense]) -> dict[str, float]:
    """Summarize all expenses for each category"""
    summary = {}
    for exp in expenses:
        if exp.category in summary: # Check if expense in dict
            summary[exp.category] += exp.amount # if yes add the amount to the summary
        else:
            summary[exp.category] = exp.amount # if not create a category and add the amount to the summary
    return summary

def total_expenses(expenses: list[Expense]) -> float:
    """Summarize the total amount for expenses"""
    return sum(exp.amount for exp in expenses)