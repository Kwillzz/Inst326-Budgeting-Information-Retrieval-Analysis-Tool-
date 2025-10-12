#Calculates the money available after tax and validates inputs
def calculate_money_available_after_tax(salary, tax_rate):
    if salary < 0: 
        raise ValueError("Salary cannot be negative.")
    if not 0 <= tax_rate <= 1:
        raise ValueError("Tax rate must be between 0 and 1")
    #Calculate tax and subtracts from salary to get available amount
    tax_amount = salary * tax_rate
    available = salary - tax_amount
    return available
#Get user input for salary and tax rate
salary = float(input("Enter your salary: "))
tax_rate = float(input("Enter your tax rate (0-1): "))
available = calculate_money_available_after_tax(salary, tax_rate)
print(f"Money available after tax: ${available:,.2f}")

#Tracks and stores user monthly spending
def track_monthly_spending(amount, category, description, month):
    with open("monthly_spending.txt", "a") as file:
        file.write(f"{month},{amount},{category},{description}\n")
#gets user input for spending information
amount = float(input("Enter amount spent: "))
category = input("Enter spending category: ")
description = input("Enter a short description: ")
month = input("Enter the month: ")
track_monthly_spending(amount, category, description, month)
print("Spending record added")

#Retrieves most frequent transaction category
from collections import Counter
def get_most_frequent_transaction_category():
    categories = []
    try:
        with open("monthly_spending.txt", "r") as file:
            for line in file:
                parts = line.strip().split(",", 3)
                if len(parts) >= 3:
                    categories.append(parts[2]) 
    except FileNotFoundError:
        return None
    if not categories:
        return None
    counter = Counter(categories)
    most_common = counter.most_common(1)
    return most_common[0][0] if most_common else None

most_frequent = get_most_frequent_transaction_category()
if most_frequent:
    print(f"Most frequent transaction category: {most_frequent}")
else:
    print("No transactions found.")

 


