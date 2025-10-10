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


 


