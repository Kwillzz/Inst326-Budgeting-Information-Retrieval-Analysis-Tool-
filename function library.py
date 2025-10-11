#####Function Library here###
#Kurt Wills
#What month's budget are you trying to input?
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
#Ask for state that the user lives in to deduct federal taxes
