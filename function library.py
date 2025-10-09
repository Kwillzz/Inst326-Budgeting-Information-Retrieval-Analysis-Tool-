#Assign User ID

#User input monthly income
income = input("Please enter your income for this month: ")
income = float(income)
#User input monthly spending
spending = input("Please enter your spending for this month: ")
spending = float(spending)
#How will the data be stored/saved?
with open("budget.txt", "a") as file:
  file.write(f"Income: {income}, Spending: {spending}\n")


#Categorize spendings into different groups (Ex. Food, Rent, entertainment)

#How will the data be stored/saved?



