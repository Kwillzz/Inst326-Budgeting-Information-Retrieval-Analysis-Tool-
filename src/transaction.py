def validate_month(month):
  months = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")
  if month not in months:
    return False
  else:
    return True

def validate_year(year):
    if isinstance(year, str) and year.isdigit() and len(year) == 4:
        print("Valid year")
        return int(year)
    else:
        print("Invalid year. Please enter a 4-digit year.")
        return None
    
class Transaction:
    #Represents a single financial transaction.

    def __init__(self, amount: float, category: str, description: str, month: int, year: int):
        validate_month(month)
        validate_year(year)
        self._amount = amount
        self._category = category
        self._description = description
        self._month = month
        self._year = year

    @property
    def amount(self): return self._amount
    @property
    def category(self): return self._category
    @property
    def description(self): return self._description
    @property
    def month(self): return self._month
    @property
    def year(self): return self._year

    def __repr__(self):
        return f"Transaction({self._amount}, '{self._category}', '{self._description}', {self._month}, {self._year})"

    def __str__(self):
        month_name = calendar.month_name[self._month]
        return f"{self._category}: {format_currency(self._amount)} ({month_name} {self._year})"

    def to_dict(self):
        """Return a dictionary representation suitable for JSON."""
        return {
            "category": self._category,
            "amount": self._amount
        }