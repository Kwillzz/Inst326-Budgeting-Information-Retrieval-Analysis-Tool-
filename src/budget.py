def validate_month(month):
  months = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")
  if month not in months:
    return False
  else:
    return True
#This class is dependent on running the transaction class at least once so that there's something
# in the json file to 
class Budget:
    
    #Represents a monthly or yearly budget containing multiple categories.

    #Example:
      #>>> b = Budget(10, 2025, 4000)
      #>>> b.add_transaction(Transaction(1200, "Rent", "Monthly rent", 10, 2025))
      #>>> b.add_transaction(Transaction(300, "Groceries", "Weekly groceries", 10, 2025))
      #>>> print(b.summary())

    def __init__(self, month: int, year: int, income: float):
        validate_month()
        self._month = month
        self._year = year
        self._income = income
        self._categories = {}

    def add_transaction(self, transaction: Transaction):
        #Add a transaction to the appropriate category.
        if transaction.category not in self._categories:
            self._categories[transaction.category] = Category(transaction.category)
        self._categories[transaction.category].add_transaction(transaction)

    def total_expenses(self) -> float:
        return sum(cat.total_spent() for cat in self._categories.values())

    def remaining_balance(self) -> float:#after expenses
        return self._income - self.total_expenses()

    def summary(self) -> dict: #Returns a summary dictionary of spending by category
        return {name: cat.total_spent() for name, cat in self._categories.items()}

    def __str__(self):
        return f"Budget({self._month}/{self._year}) - Income: ${self._income:.2f}, Remaining: ${self.remaining_balance():.2f}"

    def __repr__(self):
        return f"Budget(month={self._month}, year={self._year})"