# Needs to import two dependencies from the sibling package
from finance.income import Income, summarize_incomes, total_income
from finance.expenses import Expense, summarize_expenses, total_expenses

def print_financial_report(incomes: list[Income], expenses: list[Expense]) -> None:
    """Create an overview to all incomes and expenses by source and total"""
    print("--- FINANCIAL REPORT ---")

    # 1. Income per source
    print("\nIncome by Source:")
    inc_summary = summarize_incomes(incomes)
    for source, amount in inc_summary.items():
        print(f" - {source}: ${amount:.2f}")
    
    # 2. Expense per category
    print("\nExpense by Category:")
    exp_summary = summarize_expenses(expenses)
    for category, amount in exp_summary.items():
        print(f" - {category}: ${amount:.2f}")

    # 3. Totals
    t_income = total_income(incomes)
    t_expenses = total_expenses(expenses)
    print("\nTotals")
    print(f" Total Income: ${t_income:.2f}")
    print(f" Total Expense: ${t_expenses:.2f}")

    # 4. Surplus or Deficit
    balance = t_income - t_expenses
    if balance >= 0:
        print(f" Surplus: ${balance:.2f}")
    else:
        print(f" Deficit: §{balance:.2f}")
    print("-----------------------")