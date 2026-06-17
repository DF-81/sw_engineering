class Income:
    """Create class Income with attributes amount and source"""
    def __init__(self, amount: float, source: str):
        self.amount = amount
        self.source = source
    
def summarize_incomes(incomes: list[Income]) -> dict[str, float]:
    """Summarize the income for each source"""
    summary = {}
    for inc in incomes: 
        if inc.source in summary: # Check if income in dict
            summary[inc.source] += inc.amount # if yes add the amount to the summary
        else:
            summary[inc.source] = inc.amount # if not create a source and add the amount to the summary
    return summary

def total_income(incomes: list[Income]) -> float:
    """Sumarize the total amount for Incomes"""
    return sum(inc.amount for inc in incomes)