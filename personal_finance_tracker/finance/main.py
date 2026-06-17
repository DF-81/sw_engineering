# Import all dependencies for testing
from finance.income import Income
from finance.expenses import Expense
from finance.analytics.budget import Budget
from finance.analytics.reporting import print_financial_report

def main():
    """Create the Test Driver"""
    # 1. Create lists of incomes and expenses
    incomes = [
        Income(amount=2500.0, source="Salary"),
        Income(amount=250.0, source="Freelancing"),
        Income(amount=50.0, source="ebay_sells")
    ]

    expenses = [
        Expense(amount=1000.0, category="Credit"),
        Expense(amount=500.0, category="Groceries"),
        Expense(amount=100.0, category="Entertainment")
    ]

    # 2. Create a budget and check it
    budget_limit = 2000.0
    my_budget = Budget(limit=budget_limit)

    print(f"Budget Limit: ${budget_limit:.2f}")
    if my_budget.is_limit(expenses):
        print("Success: You are within your budget")
    else:
        print("Warning: You have exceeded your budget")
    
    print() # Blank line

    # 3. Create financial report
    print_financial_report(incomes, expenses)

if __name__ == "__main__":
    main()