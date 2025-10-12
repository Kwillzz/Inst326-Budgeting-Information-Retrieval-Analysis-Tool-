#Create User ID ---1
import os
import random

def username_creation():
    while True:
        username = input("Please make your username: ")
        print(f"You have entered: {username}")
        file_name = "users.txt"
        try:
            with open(file_name, 'w') as file:
                file.write(username)
            print(f"Your answer has been saved to '{file_name}' successfully.")
            break
        except IOError as e:
                print(f"Error writing to file: {e}")

username_creation()
    
def is_username_taken_from_file(username, filename="users.txt"):
    try:
        with open(filename, "r") as f:
            for line in f:
                # Assuming one username per line, or username is the first element in a CSV line
                stored_username = line.strip().split(",")[0] 
                if username.lower() == stored_username.lower():
                    return True
        return False
    except FileNotFoundError:
        return False # No file means no users, so username is available

new_username = input("Enter a desired username: ")
if is_username_taken_from_file(new_username):
    print("This username is already taken. Please choose another.")
else:
    print("Username is available!")
    # Optionally, add the new username to the file
    with open("users.txt", "a") as f:
        f.write(new_username + "\n")

def generate_unique_identifier():
    random_int = random.randint(100000, 999999)
    print(f"Random integer: {random_int}")
    
def get_numeric_input(prompt):
    while True:
        user_input = input(prompt)
        try:
            # Try to convert to a float first to handle decimals
            number = float(user_input)
            # If you specifically need an integer, you can add another check
            if number == int(number):
                return int(number)
            else:
                return number
        except ValueError:
            print("Invalid input. Please enter a valid number.")



#User input monthly income---2
income = input("Please enter your income for this month: ")
income = float(income)
#User input monthly spending
spending = input("Please enter your spending for this month: ")
spending = float(spending)
#How will the data be stored/saved?
with open("budget.txt", "a") as file:
  file.write(f"Income: {income}, Spending: {spending}\n")

#Categorize spendings into different groups (Ex. Food, Rent, entertainment)
print("\nEnter your spending for the following categories:")
categories = ["Rent & Utilities", "Groceries", "Transportation", "Entertainment", "Other"]
spending_by_category = {}

for category in categories:
    amount = float(input(f"How much did you spend on {category}? $"))
    spending_by_category[category] = amount

total_category_spending = sum(spending_by_category.values())
print(f"\n You have spent a total of ${total_category_spending:.2f} this month.")



#Arrange month and year ---3
#What month's budget are you trying to input? For logging purposes
def what_month():
    while True:
        try:
            month = int(input("What month is it? Format in MM format \n"))
            if 1 <= month <= 12:
                print("Valid month.")
                break
            else:
                print("Invalid month. Please enter a number between 1 and 12.")
        except ValueError:
            print("Invalid input. Please enter a number.")
#Year input for logging purposes. Should be run alongside month inside of one "session" or in a way that keeps months and years together.
def what_year():
    while True:
        try:
            year = int(input("What year is it? Format in YYYY format \n"))
            if len(str(year)) !=4:
                print("Invalid year. Please enter a 4-digit year.")
            else:
                print("Valid year.")
                break
        except ValueError:
            print ("Invalid input. Please enter a number.")

#Categorizing purchases(#2)
def purchase_category():
    categories = {1:"Utilities", 2: "Rent", 3:"Leisure"}
    while True:
        try:
            print("Please select a purchase category by entering the corresponding number:")
            for key, value in categories.items():
                print(f"{key}: {value}")
            choice = int(input("Enter category number: "))
            if choice in categories:
                print(f"You selected: {categories[choice]}")
                break
            else:
                print("Invalid category number. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")



#Input state to determine state taxes---4
#Ask for state that  the user lives in to deduct state taxes and log monthly budget.
states = ["Alabama", "Alaska", "Arizona" "Arkansas", "California", "Colorado",
"Connecticut", "Delaware", "Florida","Georgia", "Hawaii", "Idaho","Illinois","Indiana",
"Iowa","Kansas", "Kentucky", "Louisiana","Maine", "Maryland", "Massachusetts", "Michigan",
"Minnesota","Mississippi","Missouri","Montana", "Nebraska","Nevada","New Hampshire",
"New Jersey","New Mexico","New York","North Carolina",
"North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", 
"South Carolina", "South Dakota","Tennessee", "Texas", "Utah","Vermont","Virginia", 
"Washington", "West Virginia", "Wisconsin", "Wyoming",]
def what_state():
    state = input ("Enter which state you live in. \n")
    #
    if state not in states:
        print ("Invalid state. ")
    else:
        print ("Valid state.")



#Calculate tax + income after taxes---5
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

#gets user input for spending information (Categorization #3)
amount = float(input("Enter amount spent: "))
category = input("Enter spending category: ")
description = input("Enter a short description: ")
month = input("Enter the month: ")
track_monthly_spending(amount, category, description, month)
print("Spending record added")
