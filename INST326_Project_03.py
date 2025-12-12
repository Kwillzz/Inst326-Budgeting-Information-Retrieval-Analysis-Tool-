from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import date
from typing import Optional
from typing import Dict, List
import pytest


class Transaction(ABC):

    def __init__(self,
                 amount: float,
                 description: str,
                 trans_date: Optional[date] = None):
        if amount <= 0:
            raise ValueError("amount must be positive")
        self._amount = float(amount)
        self._description = description.strip()
        self._date = trans_date or date.today()

    @property
    def amount(self) -> float:
        return self._amount

    @property
    def description(self) -> str:
        return self._description

    @property
    def date(self) -> date:
        return self._date

    @abstractmethod
    def apply(self, budget: "Budget") -> None:
        """
        Apply this transaction to the appropriate account(s) in the budget.
        Must be implemented by subclasses.
        """
        raise NotImplementedError()

    @abstractmethod
    def signed_amount(self) -> float:
        """
        Return the amount with a sign indicating its effect on the account.
        Expense: negative, Income: positive, etc.
        """
        raise NotImplementedError()
    
class ExpenseTransaction(Transaction):
    """
    Money leaving an account, usually tied to a budget category.
    """

    def __init__(self,
                 amount: float,
                 description: str,
                 account_name: str,
                 category_name: str,
                 trans_date: Optional[date] = None):
        super().__init__(amount, description, trans_date)
        self._account_name = account_name
        self._category_name = category_name

    @property
    def account_name(self) -> str:
        return self._account_name

    @property
    def category_name(self) -> str:
        return self._category_name

    def signed_amount(self) -> float:
        return -self.amount

    def apply(self, budget: "Budget") -> None:
        account = budget.get_account(self._account_name)
        account.apply_change(self.signed_amount())
        budget.add_spent_to_category(self._category_name, self.amount)


class IncomeTransaction(Transaction):
    """
    Money coming into an account.
    """

    def __init__(self,
                 amount: float,
                 description: str,
                 account_name: str,
                 trans_date: Optional[date] = None):
        super().__init__(amount, description, trans_date)
        self._account_name = account_name

    @property
    def account_name(self) -> str:
        return self._account_name

    def signed_amount(self) -> float:
        return self.amount

    def apply(self, budget: "Budget") -> None:
        account = budget.get_account(self._account_name)
        account.apply_change(self.signed_amount())


class TransferTransaction(Transaction):
    """
    Move money from one account to another (no net change to total).
    """

    def __init__(self,
                 amount: float,
                 description: str,
                 from_account: str,
                 to_account: str,
                 trans_date: Optional[date] = None):
        super().__init__(amount, description, trans_date)
        if from_account == to_account:
            raise ValueError("from_account and to_account must be different")
        self._from_account = from_account
        self._to_account = to_account

    @property
    def from_account(self) -> str:
        return self._from_account

    @property
    def to_account(self) -> str:
        return self._to_account

    def signed_amount(self) -> float:
        return 0.0

    def apply(self, budget: "Budget") -> None:
        from_acc = budget.get_account(self._from_account)
        to_acc = budget.get_account(self._to_account)
        from_acc.apply_change(-self.amount)
        to_acc.apply_change(self.amount)


class Account:
    """
    Represents a financial account in the budgeting system.
    """

    def __init__(self, name: str, starting_balance: float = 0.0):
        if starting_balance < 0:
            raise ValueError("starting_balance cannot be negative")
        self._name = name.strip()
        self._balance = float(starting_balance)
        self._transactions: List[Transaction] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def balance(self) -> float:
        return self._balance

    @property
    def transactions(self) -> List[Transaction]:
        return list(self._transactions) 

    def apply_change(self, delta: float) -> None:
        """
        Change the account balance by delta and record that change.
        (The actual Transaction object gets stored in Budget, but
        we track raw delta here.)
        """
        self._balance += delta

    def add_transaction(self, transaction: Transaction) -> None:
        self._transactions.append(transaction)

class BudgetCategory:
    """
    Tracks planned and actual spending for a category (e.g., Groceries).
    """

    def __init__(self, name: str, planned_amount: float):
        self._name = name.strip()
        self._planned = float(planned_amount)
        self._spent = 0.0

    @property
    def name(self) -> str:
        return self._name

    @property
    def planned(self) -> float:
        return self._planned

    @property
    def spent(self) -> float:
        return self._spent

    @property
    def remaining(self) -> float:
        return self._planned - self._spent

    def add_spent(self, amount: float) -> None:
        self._spent += amount

class Budget:
    """
    Main composition class: has accounts, categories, and transactions.
    """

    def __init__(self):
        self._accounts: Dict[str, Account] = {}
        self._categories: Dict[str, BudgetCategory] = {}
        self._transactions: List[Transaction] = []

    # --- composition helpers ---

    def add_account(self, account: Account) -> None:
        self._accounts[account.name] = account

    def get_account(self, name: str) -> Account:
        return self._accounts[name]

    def add_category(self, category: BudgetCategory) -> None:
        self._categories[category.name] = category

    def add_spent_to_category(self, name: str, amount: float) -> None:
        self._categories[name].add_spent(amount)

    # --- transaction handling (polymorphism here) ---

    def add_transaction(self, transaction: Transaction) -> None:
        transaction.apply(self)           
        self._transactions.append(transaction)

        if isinstance(transaction, ExpenseTransaction):
            self._accounts[transaction.account_name].add_transaction(transaction)
        elif isinstance(transaction, IncomeTransaction):
            self._accounts[transaction.account_name].add_transaction(transaction)

    def total_balance(self) -> float:
        return sum(acc.balance for acc in self._accounts.values())
    
def apply_all_transactions(budget: Budget,
                           transactions: List[Transaction]) -> None:
    """
    Example function that treats all transactions the same (as Transaction),
    but each subclass behaves differently when apply() is called.
    """
    for t in transactions:
        t.apply(budget)


def test_expense_and_income_affect_balance_differently():
    budget = Budget()
    budget.add_account(Account("Checking", starting_balance=100.0))

    rent = ExpenseTransaction(
        amount=40.0,
        description="Rent",
        account_name="Checking",
        category_name="Housing",
        trans_date=date(2025, 10, 1),
    )
    paycheck = IncomeTransaction(
        amount=50.0,
        description="Paycheck",
        account_name="Checking",
        trans_date=date(2025, 10, 2),
    )

    budget.add_category(BudgetCategory("Housing", planned_amount=500.0))

    budget.add_transaction(rent)
    budget.add_transaction(paycheck)

    assert budget.get_account("Checking").balance == pytest.approx(110.0)
    assert rent.signed_amount() == -40.0
    assert paycheck.signed_amount() == 50.0