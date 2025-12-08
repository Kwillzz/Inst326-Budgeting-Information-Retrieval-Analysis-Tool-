class Category:
    """Represents a budgeting category (e.g. 'Groceries', 'Rent', 'Salary').

    Attributes are mostly read-only and validated on creation.

    Examples:
        >>> groceries = Category("Groceries", category_type="expense", monthly_limit=400.0)
        >>> str(groceries)
        'Groceries (expense, limit: 400.00)'
        >>> groceries.is_expense
        True
        >>> groceries.remaining_budget(250.0)
        150.0
    """

    def __init__(self, name, category_type="expense", monthly_limit=None):
        """
        Args:
            name (str): Display name of the category.
            category_type (str): 'expense', 'income', or 'savings'.
            monthly_limit (float | None): Optional monthly spending cap (for expenses).

        Raises:
            ValueError: If name is empty or category_type/limit is invalid.
        """
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Category name must be a non-empty string.")

        category_type = category_type.lower().strip()
        if category_type not in {"expense", "income", "savings"}:
            raise ValueError("category_type must be 'expense', 'income', or 'savings'.")

        if monthly_limit is not None:
            if not isinstance(monthly_limit, (int, float)):
                raise ValueError("monthly_limit must be a number or None.")
            if monthly_limit < 0:
                raise ValueError("monthly_limit cannot be negative.")

        self._name = name.strip()
        self._category_type = category_type
        self._monthly_limit = float(monthly_limit) if monthly_limit is not None else None

    # ---- Properties ----
    @property
    def name(self):
        """str: Name of the category (read-only)."""
        return self._name

    @property
    def category_type(self):
        """str: 'expense', 'income', or 'savings' (read-only)."""
        return self._category_type

    @property
    def monthly_limit(self):
        """float | None: Monthly spending limit for this category."""
        return self._monthly_limit

    @monthly_limit.setter
    def monthly_limit(self, value):
        """Update the monthly limit (or set to None for no limit)."""
        if value is not None:
            if not isinstance(value, (int, float)):
                raise ValueError("monthly_limit must be a number or None.")
            if value < 0:
                raise ValueError("monthly_limit cannot be negative.")
            self._monthly_limit = float(value)
        else:
            self._monthly_limit = None

    # ---- Methods ----
    @property
    def is_expense(self):
        """bool: True if this category represents an expense."""
        return self._category_type == "expense"

    @property
    def is_income(self):
        """bool: True if this category represents income."""
        return self._category_type == "income"

    def remaining_budget(self, spent_amount):
        """Calculate how much budget remains for this category.

        Args:
            spent_amount (float): Amount already spent in this category
                                  (e.g., from a Project 1 function).

        Returns:
            float | None: Remaining amount or None if no limit is set.
        """
        if self._monthly_limit is None:
            return None
        return self._monthly_limit - float(spent_amount)

    def is_over_limit(self, spent_amount):
        """Check if the spending exceeds the monthly limit.

        Args:
            spent_amount (float): Amount spent in this category.

        Returns:
            bool: True if over limit, False otherwise or if no limit.
        """
        remaining = self.remaining_budget(spent_amount)
        return remaining is not None and remaining < 0

    # ---- String Representations ----
    def __str__(self):
        if self._monthly_limit is None:
            return f"{self._name} ({self._category_type}, no limit)"
        return f"{self._name} ({self._category_type}, limit: {self._monthly_limit:.2f})"

    def __repr__(self):
        return (
            f"Category(name={self._name!r}, "
            f"category_type={self._category_type!r}, "
            f"monthly_limit={self._monthly_limit!r})"
        )

from datetime import date

class Transaction:
    """Represents a single financial transaction in the budgeting app.

    Examples:
        >>> food = Category("Food", "expense")
        >>> t = Transaction(25.50, food, description="Lunch", trans_date=date(2025, 10, 5))
        >>> t.is_expense()
        True
        >>> t.amount
        25.5
    """

    def __init__(self, amount, category, description="", trans_date=None, is_recurring=False):
        """
        Args:
            amount (float): Positive for income, positive for expense
                            (or you can enforce expense as positive and handle sign elsewhere).
            category (Category): Category instance for this transaction.
            description (str): Human-readable description.
            trans_date (datetime.date | None): Date of the transaction. Defaults to today.
            is_recurring (bool): Whether this repeats regularly.

        Raises:
            ValueError: If inputs are invalid.
        """
        if not isinstance(amount, (int, float)):
            raise ValueError("amount must be a number.")
        if amount == 0:
            raise ValueError("amount cannot be zero.")
        if not isinstance(category, Category):
            raise ValueError("category must be a Category object.")
        if not isinstance(description, str):
            raise ValueError("description must be a string.")
        if trans_date is None:
            trans_date = date.today()
        if not isinstance(trans_date, date):
            raise ValueError("trans_date must be a datetime.date object.")
        if not isinstance(is_recurring, bool):
            raise ValueError("is_recurring must be a bool.")

        self._amount = float(amount)
        self._category = category
        self._description = description.strip()
        self._date = trans_date
        self._is_recurring = is_recurring

    # ---- Properties ----
    @property
    def amount(self):
        """float: Transaction amount."""
        return self._amount

    @amount.setter
    def amount(self, value):
        if not isinstance(value, (int, float)):
            raise ValueError("amount must be a number.")
        if value == 0:
            raise ValueError("amount cannot be zero.")
        self._amount = float(value)

    @property
    def category(self):
        """Category: Category assigned to this transaction."""
        return self._category

    @category.setter
    def category(self, value):
        if not isinstance(value, Category):
            raise ValueError("category must be a Category object.")
        self._category = value

    @property
    def description(self):
        """str: Description of the transaction."""
        return self._description

    @description.setter
    def description(self, value):
        if not isinstance(value, str):
            raise ValueError("description must be a string.")
        self._description = value.strip()

    @property
    def date(self):
        """datetime.date: Date of the transaction."""
        return self._date

    @property
    def is_recurring(self):
        """bool: Whether this transaction is recurring."""
        return self._is_recurring

    @is_recurring.setter
    def is_recurring(self, value):
        if not isinstance(value, bool):
            raise ValueError("is_recurring must be a bool.")
        self._is_recurring = value

    # ---- Methods ----
    def is_expense(self):
        """bool: True if this is an expense transaction."""
        return self._category.is_expense

    def is_income(self):
        """bool: True if this is an income transaction."""
        return self._category.is_income

    def to_dict(self):
        """Return a serializable dictionary of this transaction.

        This is a natural place to integrate Project 1 functions that
        exported or formatted transaction data.
        """
        return {
            "amount": self._amount,
            "category": self._category.name,
            "category_type": self._category.category_type,
            "description": self._description,
            "date": self._date.isoformat(),
            "is_recurring": self._is_recurring,
        }

    def apply_conversion_rate(self, rate):
        """Convert the amount using a given exchange or scaling rate.

        Example integration with a Project 1 function that handled currency conversion.

        Args:
            rate (float): Multiplicative conversion rate.

        Returns:
            float: Converted amount (does not modify the transaction).
        """
        if not isinstance(rate, (int, float)) or rate <= 0:
            raise ValueError("rate must be a positive number.")
        return self._amount * float(rate)

    # ---- String Representations ----
    def __str__(self):
        sign = "-" if self.is_expense() else "+"
        return (
            f"{self._date.isoformat()} {sign}${abs(self._amount):.2f} "
            f"[{self._category.name}] {self._description}"
        )

    def __repr__(self):
        return (
            "Transaction("
            f"amount={self._amount!r}, category={self._category!r}, "
            f"description={self._description!r}, trans_date={self._date!r}, "
            f"is_recurring={self._is_recurring!r})"
        )

class Account:
    """Represents a financial account (bank, cash, credit card, etc.).

    Holds a collection of Transaction objects.

    Examples:
        >>> food = Category("Food", "expense")
        >>> acc = Account("Checking", starting_balance=1000.0)
        >>> acc.add_transaction(Transaction(50, food, "Groceries"))
        >>> acc.current_balance()
        950.0
    """

    def __init__(self, name, starting_balance=0.0, currency="USD"):
        """
        Args:
            name (str): Name of the account (e.g., 'Checking', 'Savings').
            starting_balance (float): Initial balance.
            currency (str): Currency code for display.

        Raises:
            ValueError: If inputs are invalid.
        """
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Account name must be a non-empty string.")
        if not isinstance(starting_balance, (int, float)):
            raise ValueError("starting_balance must be a number.")
        if not isinstance(currency, str) or not currency.strip():
            raise ValueError("currency must be a non-empty string.")

        self._name = name.strip()
        self._starting_balance = float(starting_balance)
        self._currency = currency.strip().upper()
        self._transactions = []

    # ---- Properties ----
    @property
    def name(self):
        """str: Name of the account (read-only)."""
        return self._name

    @property
    def currency(self):
        """str: Currency code (e.g., 'USD')."""
        return self._currency

    @currency.setter
    def currency(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("currency must be a non-empty string.")
        self._currency = value.strip().upper()

    @property
    def transactions(self):
        """list[Transaction]: Copy of the transactions list (read-only)."""
        return list(self._transactions)

    # ---- Methods ----
    def add_transaction(self, transaction):
        """Add a new Transaction to this account.

        Args:
            transaction (Transaction): Transaction instance to add.

        Raises:
            ValueError: If transaction is not a Transaction instance.
        """
        if not isinstance(transaction, Transaction):
            raise ValueError("transaction must be a Transaction object.")
        self._transactions.append(transaction)

    def remove_transaction(self, index):
        """Remove a transaction by index.

        Args:
            index (int): Index in the internal transaction list.

        Returns:
            Transaction: The removed transaction.

        Raises:
            IndexError: If index is out of range.
        """
        return self._transactions.pop(index)

    def current_balance(self):
        """Calculate the current balance.

        Returns:
            float: starting_balance plus the sum of all transaction amounts.

        This is a natural place to integrate a Project 1 function that
        computed a running total.
        """
        total = sum(t.amount if t.is_income() else -abs(t.amount)
                    if t.is_expense() else t.amount
                    for t in self._transactions)

        # If you used positive for income and negative for expenses in P1,
        # you could simply do:
        # total = project1_sum_function(self._transactions)

        return self._starting_balance + total

    def total_by_category(self, category_name):
        """Calculate net amount for a given category.

        Args:
            category_name (str): Category name to filter by.

        Returns:
            float: Sum of amounts for that category (income positive, expenses negative).
        """
        if not isinstance(category_name, str):
            raise ValueError("category_name must be a string.")
        category_name = category_name.strip()

        total = 0.0
        for t in self._transactions:
            if t.category.name == category_name:
                if t.is_expense():
                    total -= abs(t.amount)
                else:
                    total += t.amount
        return total

    def get_transactions_for_month(self, year, month):
        """Return a list of transactions for a given year and month.

        Args:
            year (int): Year value.
            month (int): Month (1–12).

        Returns:
            list[Transaction]: Matching transactions.
        """
        if not isinstance(year, int) or not isinstance(month, int):
            raise ValueError("year and month must be integers.")

        return [
            t for t in self._transactions
            if t.date.year == year and t.date.month == month
        ]

    # ---- String Representations ----
    def __str__(self):
        return f"Account '{self._name}' ({self._currency}), balance: {self.current_balance():.2f}"

    def __repr__(self):
        return (
            f"Account(name={self._name!r}, starting_balance={self._starting_balance!r}, "
            f"currency={self._currency!r}, transactions={len(self._transactions)} txns)"
        )

class BudgetPeriod:
    """Represents a budgeting period (e.g., a specific month).

    Tracks which categories are in the budget and summarizes spending.

    Examples:
        >>> food = Category("Food", "expense", monthly_limit=300)
        >>> rent = Category("Rent", "expense", monthly_limit=800)
        >>> period = BudgetPeriod(2025, 10, [food, rent])
        >>> period.year, period.month
        (2025, 10)
    """

    def __init__(self, year, month, categories=None):
        """
        Args:
            year (int): Year for the budget period.
            month (int): Month (1–12) for the budget period.
            categories (list[Category] | None): Categories tracked in this period.

        Raises:
            ValueError: If inputs are invalid.
        """
        if not isinstance(year, int) or not isinstance(month, int):
            raise ValueError("year and month must be integers.")
        if month < 1 or month > 12:
            raise ValueError("month must be between 1 and 12.")

        self._year = year
        self._month = month
        self._categories = {}
        if categories:
            for cat in categories:
                if not isinstance(cat, Category):
                    raise ValueError("All items in categories must be Category objects.")
                self._categories[cat.name] = cat

    # ---- Properties ----
    @property
    def year(self):
        """int: Year of this budget period."""
        return self._year

    @property
    def month(self):
        """int: Month (1–12) of this budget period."""
        return self._month

    @property
    def categories(self):
        """dict[str, Category]: Mapping of category name to Category."""
        return dict(self._categories)

    # ---- Methods ----
    def add_category(self, category):
        """Add a Category to this budget period.

        Args:
            category (Category): Category to include or update.
        """
        if not isinstance(category, Category):
            raise ValueError("category must be a Category object.")
        self._categories[category.name] = category

    def remove_category(self, category_name):
        """Remove a Category from this period by name.

        Args:
            category_name (str): Name of category to remove.

        Raises:
            KeyError: If category does not exist.
        """
        del self._categories[category_name]

    def summarize_account(self, account):
        """Summarize spending for this period from a given Account.

        This method is a good place to integrate Project 1 functions
        that summarized transactions for a month.

        Args:
            account (Account): Account to analyze.

        Returns:
            dict: {
                "by_category": {category_name: spent_amount, ...},
                "total_expenses": float,
                "total_income": float,
            }
        """
        if not isinstance(account, Account):
            raise ValueError("account must be an Account object.")

        # Filter account transactions to just this month/year
        txns = account.get_transactions_for_month(self._year, self._month)

        by_category = {}
        total_expenses = 0.0
        total_income = 0.0

        for t in txns:
            name = t.category.name
            if name not in by_category:
                by_category[name] = 0.0

            if t.is_expense():
                by_category[name] -= abs(t.amount)
                total_expenses -= abs(t.amount)
            elif t.is_income():
                by_category[name] += t.amount
                total_income += t.amount
            else:
                by_category[name] += t.amount

        return {
            "by_category": by_category,
            "total_expenses": total_expenses,
            "total_income": total_income,
        }

    def over_limit_categories(self, account):
        """Return a list of category names that are over their monthly limits.

        Args:
            account (Account): Account to analyze.

        Returns:
            list[str]: Category names over their limit.
        """
        summary = self.summarize_account(account)
        over = []

        for name, spent in summary["by_category"].items():
            cat = self._categories.get(name)
            if cat and cat.is_expense:
                # spent will be negative for expenses; use absolute for comparison
                if cat.is_over_limit(abs(spent)):
                    over.append(name)

        return over

    # ---- String Representations ----
    def __str__(self):
        return f"BudgetPeriod {self._year}-{self._month:02d} ({len(self._categories)} categories)"

    def __repr__(self):
        return (
            f"BudgetPeriod(year={self._year!r}, month={self._month!r}, "
            f"categories={list(self._categories.keys())!r})"
        )
