import os
import random
from datetime import date

# test test

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
                stored_username = line.strip().split(",")[0] 
                if username.lower() == stored_username.lower():
                    return True
        return False
    except FileNotFoundError:
        return False

new_username = input("Enter a desired username: ")
if is_username_taken_from_file(new_username):
    print("This username is already taken. Please choose another.")
else:
    print("Username is available!")
    with open("users.txt", "a") as f:
        f.write(new_username + "\n")

def generate_unique_identifier():
    random_int = random.randint(100000, 999999)
    print(f"Random integer: #{random_int}")
    
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

# Example usage:
age = get_numeric_input("Please enter your age: ")
print(f"You entered: {age}")

price = get_numeric_input("Enter the product price: ")
print(f"The price is: {price}")

# What is your monthly income?
# How much do you typically spend per month?

generate_unique_identifier()

class Category:
    def __init__(self, name, budget_limit=None):
        self.name = name
        self.budget_limit = budget_limit
        self.transactions = []

    def add_transaction(self, transaction):
        self.transactions.append(transaction)

    def total_spent(self):
        return sum(t.amount for t in self.transactions if t.t_type == "expense")

    def total_income(self):
        return sum(t.amount for t in self.transactions if t.t_type == "income")

    def remaining_budget(self):
        if self.budget_limit is None:
            return None
        return self.budget_limit - self.total_spent()
    
Category("People")

print(Category)