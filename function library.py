#####Function Library here###
#Kurt Wills
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

#Categorizing purchases
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
###############

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



