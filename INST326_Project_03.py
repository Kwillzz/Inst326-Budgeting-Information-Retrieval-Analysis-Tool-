from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from typing import Optional, List, Dict


class Category:
    """Represents a budgeting category (e.g. 'Groceries', 'Rent', 'Salary')."""

    def __init__(self, name, category_type="expense", monthly_limit=None):
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

    @property
    def name(self):
        return self._name

    @property
    def category_type(self):
        return self._category_type

    @property
    def monthly_limit(self):
        return self._monthly_limit

    @monthly_limit.setter
    def monthly_limit(self, value):
        if value is not None:
            if not isinstance(value, (int, float)):
                raise ValueError("monthly_limit must be a number or None.")
            if value < 0:
                raise ValueError("monthly_limit cannot be negative.")
            self._monthly_limit = float(value)
        else:
            self._monthly_limit = None

    @property
    def is_expense(self):
        return self._category_type == "expense"

    @property
    def is_income(self):
        return self._category_type == "income"

    def remaining_budget(self, spent_amount):
        if self._monthly_limit is None:
            return None
        return self._monthly_limit - float(spent_amount)

    def is_over_limit(self, spent_amount):
        remaining = self.remaining_budget(spent_amount)
        return remaining is not None and remaining < 0

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


# -------------------------
# Project 3: ABC + Inheritance
# -------------------------

class Transaction(ABC):
    """
    Abstract base class for all transactions.

    Project 3 goals:
    - ABC: can't instantiate Transaction directly
    - Subclasses override signed_amount() and to_dict() (polymorphism)
    """

    def __init__(self, amount, category: Category, description="", trans_date=None, is_recurring=False):
        if not isinstance(amount, (int, float)):
            raise ValueError("amount must be a number.")
        if float(amount) <= 0:
            raise ValueError("amount must be positive (use transaction type to determine sign).")
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

    @property
    def amount(self):
        return self._amount

    @property
    def category(self):
        return self._category

    @property
    def description(self):
        return self._description

    @property
    def date(self):
        return self._date

    @property
    def is_recurring(self):
        return self._is_recurring

    def apply_conversion_rate(self, rate):
        if not isinstance(rate, (int, float)) or rate <= 0:
            raise ValueError("rate must be a positive number.")
        return self._amount * float(rate)

    def is_expense(self):
        # Uses category meaning, but subclass type is the real source of truth.
        return self._category.is_expense

    def is_income(self):
        return self._category.is_income

    @abstractmethod
    def signed_amount(self) -> float:
        """Return amount with sign appropriate for balance math."""
        raise NotImplementedError()

    @abstractmethod
    def to_dict(self):
        """Return serializable dictionary representation."""
        raise NotImplementedError()

    def __str__(self):
        sign = "-" if self.signed_amount() < 0 else "+"
        return (
            f"{self._date.isoformat()} {sign}${abs(self._amount):.2f} "
            f"[{self._category.name}] {self._description}"
        )

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"amount={self._amount!r}, category={self._category!r}, "
            f"description={self._description!r}, trans_date={self._date!r}, "
            f"is_recurring={self._is_recurring!r})"
        )


class ExpenseTransaction(Transaction):
    """Expense transaction: reduces balance."""

    def __init__(self, amount, category: Category, description="", trans_date=None, is_recurring=False):
        # enforce category type matches (optional but good validation)
        if not isinstance(category, Category) or not category.is_expense:
            raise ValueError("ExpenseTransaction requires a Category with category_type='expense'.")
        super().__init__(amount, category, description, trans_date, is_recurring)

    def signed_amount(self) -> float:
        return -abs(self._amount)

    def to_dict(self):
        return {
            "type": "expense",
            "amount": self._amount,
            "signed_amount": self.signed_amount(),
            "category": self._category.name,
            "category_type": self._category.category_type,
            "description": self._description,
            "date": self._date.isoformat(),
            "is_recurring": self._is_recurring,
        }


class IncomeTransaction(Transaction):
    """Income transaction: increases balance."""

    def __init__(self, amount, category: Category, description="", trans_date=None, is_recurring=False):
        if not isinstance(category, Category) or not category.is_income:
            raise ValueError("IncomeTransaction requires a Category with category_type='income'.")
        super().__init__(amount, category, description, trans_date, is_recurring)

    def signed_amount(self) -> float:
        return abs(self._amount)

    def to_dict(self):
        return {
            "type": "income",
            "amount": self._amount,
            "signed_amount": self.signed_amount(),
            "category": self._category.name,
            "category_type": self._category.category_type,
            "description": self._description,
            "date": self._date.isoformat(),
            "is_recurring": self._is_recurring,
        }


class SavingsTransaction(Transaction):
    """
    Savings transaction: treated as expense-like for an account balance,
    but categorized separately.
    """

    def __init__(self, amount, category: Category, description="", trans_date=None, is_recurring=False):
        if not isinstance(category, Category) or category.category_type != "savings":
            raise ValueError("SavingsTransaction requires a Category with category_type='savings'.")
        super().__init__(amount, category, description, trans_date, is_recurring)

    def signed_amount(self) -> float:
        # Most budgeting apps treat savings contributions as money leaving spendable balance.
        return -abs(self._amount)

    def to_dict(self):
        return {
            "type": "savings",
            "amount": self._amount,
            "signed_amount": self.signed_amount(),
            "category": self._category.name,
            "category_type": self._category.category_type,
            "description": self._description,
            "date": self._date.isoformat(),
            "is_recurring": self._is_recurring,
        }


# -------------------------
# Optional Project 3: Account inheritance hierarchy (2nd hierarchy)
# -------------------------

class Account:
    """Represents a financial account (bank, cash, credit card, etc.)."""

    def __init__(self, name, starting_balance=0.0, currency="USD"):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Account name must be a non-empty string.")
        if not isinstance(starting_balance, (int, float)):
            raise ValueError("starting_balance must be a number.")
        if not isinstance(currency, str) or not currency.strip():
            raise ValueError("currency must be a non-empty string.")

        self._name = name.strip()
        self._starting_balance = float(starting_balance)
        self._currency = currency.strip().upper()
        self._transactions: List[Transaction] = []

    @property
    def name(self):
        return self._name

    @property
    def currency(self):
        return self._currency

    @currency.setter
    def currency(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("currency must be a non-empty string.")
        self._currency = value.strip().upper()

    @property
    def transactions(self):
        return list(self._transactions)

    def add_transaction(self, transaction: Transaction):
        if not isinstance(transaction, Transaction):
            raise ValueError("transaction must be a Transaction object (subclass).")
        self._transactions.append(transaction)

    def remove_transaction(self, index):
        return self._transactions.pop(index)

    def current_balance(self):
        # Polymorphism: each transaction decides its signed effect
        total = sum(t.signed_amount() for t in self._transactions)
        return self._starting_balance + total

    def total_by_category(self, category_name):
        if not isinstance(category_name, str):
            raise ValueError("category_name must be a string.")
        category_name = category_name.strip()

        total = 0.0
        for t in self._transactions:
            if t.category.name == category_name:
                total += t.signed_amount()
        return total

    def get_transactions_for_month(self, year, month):
        if not isinstance(year, int) or not isinstance(month, int):
            raise ValueError("year and month must be integers.")
        return [t for t in self._transactions if t.date.year == year and t.date.month == month]

    def __str__(self):
        return f"Account '{self._name}' ({self._currency}), balance: {self.current_balance():.2f}"

    def __repr__(self):
        return (
            f"Account(name={self._name!r}, starting_balance={self._starting_balance!r}, "
            f"currency={self._currency!r}, transactions={len(self._transactions)} txns)"
        )


class CheckingAccount(Account):
    """Simple checking account (no special rules yet)."""
    pass


class CreditAccount(Account):
    """
    Credit account: allow negative balances; optionally enforce a credit limit.
    """

    def __init__(self, name, starting_balance=0.0, currency="USD", credit_limit=None):
        super().__init__(name, starting_balance, currency)
        if credit_limit is not None:
            if not isinstance(credit_limit, (int, float)) or credit_limit <= 0:
                raise ValueError("credit_limit must be a positive number or None.")
        self._credit_limit = float(credit_limit) if credit_limit is not None else None

    @property
    def credit_limit(self):
        return self._credit_limit

    def add_transaction(self, transaction: Transaction):
        super().add_transaction(transaction)
        if self._credit_limit is not None:
            # If balance drops below -limit, reject last transaction
            if self.current_balance() < -self._credit_limit:
                self._transactions.pop()
                raise ValueError("Transaction would exceed credit limit.")


class BudgetPeriod:
    """Represents a budgeting period (e.g., a specific month)."""

    def __init__(self, year, month, categories=None):
        if not isinstance(year, int) or not isinstance(month, int):
            raise ValueError("year and month must be integers.")
        if month < 1 or month > 12:
            raise ValueError("month must be between 1 and 12.")

        self._year = year
        self._month = month
        self._categories: Dict[str, Category] = {}
        if categories:
            for cat in categories:
                if not isinstance(cat, Category):
                    raise ValueError("All items in categories must be Category objects.")
                self._categories[cat.name] = cat

    @property
    def year(self):
        return self._year

    @property
    def month(self):
        return self._month

    @property
    def categories(self):
        return dict(self._categories)

    def add_category(self, category):
        if not isinstance(category, Category):
            raise ValueError("category must be a Category object.")
        self._categories[category.name] = category

    def remove_category(self, category_name):
        del self._categories[category_name]

    def summarize_account(self, account: Account):
        if not isinstance(account, Account):
            raise ValueError("account must be an Account object.")

        txns = account.get_transactions_for_month(self._year, self._month)

        by_category = {}
        total_expenses = 0.0
        total_income = 0.0

        for t in txns:
            name = t.category.name
            by_category.setdefault(name, 0.0)

            # Polymorphism again: signed_amount drives math
            by_category[name] += t.signed_amount()

            if isinstance(t, IncomeTransaction):
                total_income += t.amount
            elif isinstance(t, (ExpenseTransaction, SavingsTransaction)):
                total_expenses += t.amount

        return {
            "by_category": by_category,
            "total_expenses": total_expenses,
            "total_income": total_income,
        }

    def over_limit_categories(self, account: Account):
        summary = self.summarize_account(account)
        over = []

        for name, net in summary["by_category"].items():
            cat = self._categories.get(name)
            if cat and cat.is_expense:
                # net is negative for expenses; compare abs(net) to limit
                if cat.is_over_limit(abs(net)):
                    over.append(name)
        return over

    def __str__(self):
        return f"BudgetPeriod {self._year}-{self._month:02d} ({len(self._categories)} categories)"

    def __repr__(self):
        return (
            f"BudgetPeriod(year={self._year!r}, month={self._month!r}, "
            f"categories={list(self._categories.keys())!r})"
        )


# -------------------------
# Small demo
# -------------------------
if __name__ == "__main__":
    food = Category("Food", "expense", monthly_limit=300)
    salary = Category("Salary", "income")
    savings = Category("Emergency Fund", "savings")

    acc = CheckingAccount("Checking", starting_balance=1000)

    acc.add_transaction(IncomeTransaction(2000, salary, "Paycheck"))
    acc.add_transaction(ExpenseTransaction(50, food, "Groceries"))
    acc.add_transaction(SavingsTransaction(100, savings, "Transfer to savings bucket"))

    period = BudgetPeriod(2025, 10, [food, salary, savings])

    print(acc)
    print(period.summarize_account(acc))
    print("Over limit categories:", period.over_limit_categories(acc))
    assert budget.get_account("Checking").balance == pytest.approx(110.0)
    assert rent.signed_amount() == -40.0

    assert paycheck.signed_amount() == 50.0
