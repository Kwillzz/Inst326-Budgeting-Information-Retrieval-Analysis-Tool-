# This is a more to-date version of our Project 02. The classes have been changed or added, and here are two for our project.
# This is constructing a category class, and a user class. We will also be trying to work on an UI class.

class Category:
    """
    Represents a budget category such as Food, Rent, or Travel.

    Example:
        >>> groceries = Category("Food", limit=300)
        >>> groceries.add_transaction(Transaction("Groceries", 45.22))
        >>> groceries.total_spent()
        45.22
    """

    def __init__(self, name, limit=0):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Category name must be a non-empty string.")
        if limit < 0:
            raise ValueError("Limit must be non-negative.")

        self._name = name
        self._limit = limit
        self._transactions = []  # list of Transaction objects

        # BREAK

    def name(self):
        return self._name

    
    def limit(self):
        return self._limit

    
    def limit(self, amount):
        if amount < 0:
            raise ValueError("Limit cannot be negative.")
        self._limit = amount

    
    def transactions(self):
        """Return a copy of the transactions list."""
        return list(self._transactions)

    # BREAK

    def add_transaction(self, transaction):
        """Add a Transaction object to the category."""
        if not isinstance(transaction, Transaction):
            raise TypeError("Must add a Transaction object.")
        self._transactions.append(transaction)

    def total_spent(self):
        """Return total spending in this category."""
        return sum(t.amount for t in self._transactions)

    def remaining(self):
        """Return budget remaining for this category."""
        return self._limit - self.total_spent()

    def over_budget(self):
        """Return True if the category is overspent."""
        return self.total_spent() > self._limit

    # BREAK

    def __str__(self):
        return f"{self._name}: Spent ${self.total_spent():.2f} / ${self._limit:.2f}"

    def __repr__(self):
        return f"Category(name={self._name!r}, limit={self._limit!r})"
    
class User:
    """
    Represents a user of the budgeting app.

    Example:
        >>> u = User("Alex")
        >>> u.add_budget(Budget("2025 Budget"))
    """

    def __init__(self, username):
        if not isinstance(username, str) or not username.strip():
            raise ValueError("Username required.")

        self._username = username
        self._budgets = []

    # BREAK

    
    def username(self):
        return self._username

    
    def budgets(self):
        return list(self._budgets)

    # BREAK

    def add_budget(self, budget):
        if not isinstance(budget, Budget):
            raise TypeError("Must add a Budget object.")
        self._budgets.append(budget)

    def get_budget(self, name):
        """Return a budget by name."""
        for b in self._budgets:
            if b.name == name:
                return b
        return None

    def total_net_worth(self):
        """
        Could integrate a Project 1 function for net worth calculations
        across budgets.
        """
        return sum(b.remaining() for b in self._budgets)

    # BREAK

    def __str__(self):
        return f"User: {self._username} — {len(self._budgets)} budgets"

    def __repr__(self):
        return f"User(username={self._username!r})"