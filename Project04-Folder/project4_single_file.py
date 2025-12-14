"""Project 4 – Single-file Budgeting System (domain + persistence + import/export + tests)

Run tests:
    python project4_single_file.py --test

Run demo:
    python project4_single_file.py

This file includes:
- Domain model: Budget, Account, BudgetCategory, polymorphic Transactions
- Save/load state to JSON (pathlib + context managers + error handling)
- Import transactions from CSV (validation)
- Export reports to CSV
- unittest suite: unit + integration (6) + system (4)
"""

from __future__ import annotations

import csv
import json
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional


# =========================
# Exceptions
# =========================

class BudgetAppError(Exception):
    """Base exception for the app."""

class StorageError(BudgetAppError):
    """Raised when save/load fails (I/O, corruption, etc.)."""

class ImportError(BudgetAppError):
    """Raised when import data is missing/invalid."""

class ExportError(BudgetAppError):
    """Raised when export fails."""

class ValidationError(BudgetAppError):
    """Raised when a domain object is invalid."""


# =========================
# Helpers
# =========================

def _clean_nonempty_str(value: Any, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string")
    cleaned = value.strip()
    if not cleaned:
        raise ValidationError(f"{field_name} must not be empty")
    return cleaned


# =========================
# Domain model
# =========================

@dataclass
class Account:
    """Represents a financial account."""
    name: str
    starting_balance: float = 0.0
    _balance: float = field(init=False, repr=False)
    _transactions: List[dict] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        self.name = _clean_nonempty_str(self.name, "name")
        if not isinstance(self.starting_balance, (int, float)):
            raise ValidationError("starting_balance must be numeric")
        if float(self.starting_balance) < 0:
            raise ValidationError("starting_balance cannot be negative")
        self._balance = float(self.starting_balance)

    @property
    def balance(self) -> float:
        return self._balance

    def apply_change(self, delta: float) -> None:
        if not isinstance(delta, (int, float)):
            raise ValidationError("delta must be numeric")
        self._balance += float(delta)

    def add_transaction_record(self, record: dict) -> None:
        if not isinstance(record, dict):
            raise ValidationError("record must be a dict")
        self._transactions.append(record)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "starting_balance": self.starting_balance,
            "balance": self._balance,
            "transactions": list(self._transactions),
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Account":
        acc = cls(name=d["name"], starting_balance=float(d.get("starting_balance", 0.0)))
        if "balance" in d:
            acc._balance = float(d["balance"])
        for rec in d.get("transactions", []):
            if isinstance(rec, dict):
                acc._transactions.append(rec)
        return acc


@dataclass
class BudgetCategory:
    """Tracks planned and actual spending for a category."""
    name: str
    planned_amount: float
    _spent: float = field(default=0.0, init=False, repr=False)

    def __post_init__(self) -> None:
        self.name = _clean_nonempty_str(self.name, "name")
        if not isinstance(self.planned_amount, (int, float)):
            raise ValidationError("planned_amount must be numeric")
        if float(self.planned_amount) < 0:
            raise ValidationError("planned_amount cannot be negative")
        self.planned_amount = float(self.planned_amount)

    @property
    def spent(self) -> float:
        return self._spent

    @property
    def remaining(self) -> float:
        return self.planned_amount - self._spent

    def add_spent(self, amount: float) -> None:
        if not isinstance(amount, (int, float)):
            raise ValidationError("amount must be numeric")
        if float(amount) < 0:
            raise ValidationError("amount must be non-negative for category spending")
        self._spent += float(amount)

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "planned_amount": self.planned_amount, "spent": self._spent}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "BudgetCategory":
        cat = cls(name=d["name"], planned_amount=float(d.get("planned_amount", 0.0)))
        cat._spent = float(d.get("spent", 0.0))
        return cat


class Transaction(ABC):
    """Abstract base for all transactions."""

    def __init__(self, amount: float, description: str, trans_date: Optional[date] = None):
        if not isinstance(amount, (int, float)):
            raise ValidationError("amount must be numeric")
        if float(amount) <= 0:
            raise ValidationError("amount must be positive")
        self._amount = float(amount)
        self._description = _clean_nonempty_str(description, "description")
        self._date = trans_date or date.today()
        if not isinstance(self._date, date):
            raise ValidationError("trans_date must be a datetime.date")

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
        raise NotImplementedError()

    @abstractmethod
    def signed_amount(self) -> float:
        raise NotImplementedError()

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError()

    @staticmethod
    def from_dict(d: dict[str, Any]) -> "Transaction":
        t = d.get("type")
        if t == "expense":
            return ExpenseTransaction(
                amount=float(d["amount"]),
                description=d["description"],
                account_name=d["account_name"],
                category_name=d["category_name"],
                trans_date=date.fromisoformat(d["date"]),
            )
        if t == "income":
            return IncomeTransaction(
                amount=float(d["amount"]),
                description=d["description"],
                account_name=d["account_name"],
                trans_date=date.fromisoformat(d["date"]),
            )
        if t == "transfer":
            return TransferTransaction(
                amount=float(d["amount"]),
                description=d["description"],
                from_account=d["from_account"],
                to_account=d["to_account"],
                trans_date=date.fromisoformat(d["date"]),
            )
        raise ValidationError(f"Unknown transaction type: {t!r}")


class ExpenseTransaction(Transaction):
    def __init__(
        self,
        amount: float,
        description: str,
        account_name: str,
        category_name: str,
        trans_date: Optional[date] = None,
    ):
        super().__init__(amount, description, trans_date)
        self._account_name = _clean_nonempty_str(account_name, "account_name")
        self._category_name = _clean_nonempty_str(category_name, "category_name")

    def signed_amount(self) -> float:
        return -self.amount

    def apply(self, budget: "Budget") -> None:
        account = budget.get_account(self._account_name)
        if self._category_name not in budget.categories:
            raise ValidationError(f"Unknown category: {self._category_name}")
        account.apply_change(self.signed_amount())
        budget.add_spent_to_category(self._category_name, self.amount)
        account.add_transaction_record({"date": self.date.isoformat(), "delta": self.signed_amount(), "desc": self.description})

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "expense",
            "amount": self.amount,
            "description": self.description,
            "date": self.date.isoformat(),
            "account_name": self._account_name,
            "category_name": self._category_name,
        }


class IncomeTransaction(Transaction):
    def __init__(self, amount: float, description: str, account_name: str, trans_date: Optional[date] = None):
        super().__init__(amount, description, trans_date)
        self._account_name = _clean_nonempty_str(account_name, "account_name")

    def signed_amount(self) -> float:
        return self.amount

    def apply(self, budget: "Budget") -> None:
        account = budget.get_account(self._account_name)
        account.apply_change(self.signed_amount())
        account.add_transaction_record({"date": self.date.isoformat(), "delta": self.signed_amount(), "desc": self.description})

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "income",
            "amount": self.amount,
            "description": self.description,
            "date": self.date.isoformat(),
            "account_name": self._account_name,
        }


class TransferTransaction(Transaction):
    def __init__(
        self,
        amount: float,
        description: str,
        from_account: str,
        to_account: str,
        trans_date: Optional[date] = None,
    ):
        super().__init__(amount, description, trans_date)
        self._from_account = _clean_nonempty_str(from_account, "from_account")
        self._to_account = _clean_nonempty_str(to_account, "to_account")
        if self._from_account == self._to_account:
            raise ValidationError("from_account and to_account must be different")

    def signed_amount(self) -> float:
        return 0.0

    def apply(self, budget: "Budget") -> None:
        from_acc = budget.get_account(self._from_account)
        to_acc = budget.get_account(self._to_account)
        from_acc.apply_change(-self.amount)
        to_acc.apply_change(self.amount)
        from_acc.add_transaction_record({"date": self.date.isoformat(), "delta": -self.amount, "desc": self.description})
        to_acc.add_transaction_record({"date": self.date.isoformat(), "delta": self.amount, "desc": self.description})

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "transfer",
            "amount": self.amount,
            "description": self.description,
            "date": self.date.isoformat(),
            "from_account": self._from_account,
            "to_account": self._to_account,
        }


@dataclass
class Budget:
    accounts: Dict[str, Account] = field(default_factory=dict)
    categories: Dict[str, BudgetCategory] = field(default_factory=dict)
    transactions: List[Transaction] = field(default_factory=list)

    def add_account(self, account: Account) -> None:
        if not isinstance(account, Account):
            raise ValidationError("account must be an Account")
        self.accounts[account.name] = account

    def get_account(self, name: str) -> Account:
        name = _clean_nonempty_str(name, "name")
        if name not in self.accounts:
            raise ValidationError(f"Unknown account: {name}")
        return self.accounts[name]

    def add_category(self, category: BudgetCategory) -> None:
        if not isinstance(category, BudgetCategory):
            raise ValidationError("category must be a BudgetCategory")
        self.categories[category.name] = category

    def add_spent_to_category(self, name: str, amount: float) -> None:
        name = _clean_nonempty_str(name, "name")
        if name not in self.categories:
            raise ValidationError(f"Unknown category: {name}")
        self.categories[name].add_spent(amount)

    def add_transaction(self, transaction: Transaction) -> None:
        if not isinstance(transaction, Transaction):
            raise ValidationError("transaction must be a Transaction")
        transaction.apply(self)
        self.transactions.append(transaction)

    def total_balance(self) -> float:
        return sum(a.balance for a in self.accounts.values())

    # Charter-question helpers (examples)
    def spending_by_category(self) -> dict[str, float]:
        return {name: cat.spent for name, cat in self.categories.items()}

    def top_spending_categories(self, n: int = 3) -> list[tuple[str, float]]:
        if not isinstance(n, int) or n <= 0:
            raise ValidationError("n must be a positive int")
        items = sorted(((name, cat.spent) for name, cat in self.categories.items()), key=lambda x: x[1], reverse=True)
        return items[:n]

    def category_status(self) -> list[dict[str, Any]]:
        status = []
        for cat in self.categories.values():
            status.append({
                "name": cat.name,
                "planned": cat.planned_amount,
                "spent": cat.spent,
                "remaining": cat.remaining,
                "over_budget": cat.remaining < 0,
            })
        return status

    def to_dict(self) -> dict[str, Any]:
        return {
            "accounts": {k: v.to_dict() for k, v in self.accounts.items()},
            "categories": {k: v.to_dict() for k, v in self.categories.items()},
            "transactions": [t.to_dict() for t in self.transactions],
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Budget":
        b = cls()
        for name, acc_d in d.get("accounts", {}).items():
            b.accounts[name] = Account.from_dict(acc_d)
        for name, cat_d in d.get("categories", {}).items():
            b.categories[name] = BudgetCategory.from_dict(cat_d)

        # recompute computed fields by reapplying transactions
        txs = [Transaction.from_dict(t) for t in d.get("transactions", [])]
        for acc in b.accounts.values():
            acc._balance = float(acc.starting_balance)
            acc._transactions = []
        for cat in b.categories.values():
            cat._spent = 0.0
        for t in txs:
            b.add_transaction(t)
        return b


# =========================
# Persistence (JSON)
# =========================

def save_budget(budget: Budget, path: Path) -> None:
    try:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(budget.to_dict(), f, indent=2)
    except OSError as e:
        raise StorageError(f"Could not save budget to {path}") from e


def load_budget(path: Path) -> Budget:
    path = Path(path)
    try:
        with path.open("r", encoding="utf-8") as f:
            data: Any = json.load(f)
        if not isinstance(data, dict):
            raise StorageError("Save file must be a JSON object")
        return Budget.from_dict(data)
    except FileNotFoundError:
        return Budget()
    except json.JSONDecodeError as e:
        raise StorageError("Save file is corrupted (invalid JSON)") from e
    except OSError as e:
        raise StorageError(f"Could not read budget from {path}") from e


# =========================
# Import (CSV)
# =========================

def _req(row: dict[str, Any], key: str, line_no: int) -> str:
    if key not in row or row[key] is None or str(row[key]).strip() == "":
        raise ImportError(f"Missing required field '{key}' on line {line_no}")
    return str(row[key]).strip()


def import_transactions_csv(path: Path) -> list[Transaction]:
    """Expected headers:
    type, amount, description, date, account_name, category_name, from_account, to_account
    """
    path = Path(path)
    txs: list[Transaction] = []
    try:
        with path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise ImportError("CSV must include a header row")
            for line_no, row in enumerate(reader, start=2):
                try:
                    t = _req(row, "type", line_no).lower()
                    amount = float(_req(row, "amount", line_no))
                    desc = _req(row, "description", line_no)
                    d = date.fromisoformat(_req(row, "date", line_no))

                    if t == "expense":
                        acc = _req(row, "account_name", line_no)
                        cat = _req(row, "category_name", line_no)
                        txs.append(ExpenseTransaction(amount, desc, acc, cat, d))
                    elif t == "income":
                        acc = _req(row, "account_name", line_no)
                        txs.append(IncomeTransaction(amount, desc, acc, d))
                    elif t == "transfer":
                        frm = _req(row, "from_account", line_no)
                        to = _req(row, "to_account", line_no)
                        txs.append(TransferTransaction(amount, desc, frm, to, d))
                    else:
                        raise ImportError(f"Unknown transaction type '{t}' on line {line_no}")
                except ValueError as e:
                    raise ImportError(f"Invalid value on line {line_no}: {row}") from e
        return txs
    except FileNotFoundError as e:
        raise ImportError(f"Import file not found: {path}") from e
    except OSError as e:
        raise ImportError(f"Could not read import file: {path}") from e


def import_into_budget(budget: Budget, csv_path: Path) -> int:
    txs = import_transactions_csv(csv_path)
    for t in txs:
        budget.add_transaction(t)
    return len(txs)


# =========================
# Export (CSV)
# =========================

def export_category_report_csv(budget: Budget, path: Path) -> None:
    path = Path(path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["category", "planned", "spent", "remaining", "over_budget"])
            for row in sorted(budget.category_status(), key=lambda r: r["name"]):
                w.writerow([
                    row["name"],
                    f"{row['planned']:.2f}",
                    f"{row['spent']:.2f}",
                    f"{row['remaining']:.2f}",
                    str(bool(row["over_budget"])),
                ])
    except OSError as e:
        raise ExportError(f"Could not export category report to {path}") from e


def export_account_report_csv(budget: Budget, path: Path) -> None:
    path = Path(path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["account", "balance"])
            for name, acc in sorted(budget.accounts.items()):
                w.writerow([name, f"{acc.balance:.2f}"])
    except OSError as e:
        raise ExportError(f"Could not export account report to {path}") from e


def export_transactions_csv(budget: Budget, path: Path) -> None:
    path = Path(path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["type", "amount", "description", "date", "account_name", "category_name", "from_account", "to_account"])
            for t in budget.transactions:
                d = t.to_dict()
                w.writerow([
                    d.get("type", ""),
                    f"{float(d.get('amount', 0.0)):.2f}",
                    d.get("description", ""),
                    d.get("date", ""),
                    d.get("account_name", ""),
                    d.get("category_name", ""),
                    d.get("from_account", ""),
                    d.get("to_account", ""),
                ])
    except OSError as e:
        raise ExportError(f"Could not export transactions to {path}") from e


# =========================
# Services / workflows (for system tests)
# =========================

def load_or_new(save_path: Path) -> Budget:
    return load_budget(save_path)


def setup_demo_budget() -> Budget:
    b = Budget()
    b.add_account(Account("Checking", 1000.0))
    b.add_account(Account("Savings", 500.0))
    b.add_category(BudgetCategory("Housing", 1200.0))
    b.add_category(BudgetCategory("Food", 400.0))
    b.add_category(BudgetCategory("Fun", 200.0))
    return b


def import_csv_workflow(budget: Budget, csv_path: Path) -> int:
    return import_into_budget(budget, csv_path)


def export_reports_workflow(budget: Budget, out_dir: Path) -> dict[str, Path]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    cat_path = out_dir / "category_report.csv"
    acc_path = out_dir / "account_report.csv"
    tx_path = out_dir / "transactions_export.csv"
    export_category_report_csv(budget, cat_path)
    export_account_report_csv(budget, acc_path)
    export_transactions_csv(budget, tx_path)
    return {"categories": cat_path, "accounts": acc_path, "transactions": tx_path}


def save_workflow(budget: Budget, save_path: Path) -> None:
    save_budget(budget, save_path)


# =========================
# Tests (unittest)
# =========================

import unittest
import tempfile


class TestUnitModels(unittest.TestCase):
    def test_account_validation(self):
        with self.assertRaises(ValidationError):
            Account("", 0)

    def test_category_remaining(self):
        c = BudgetCategory("Food", 100.0)
        self.assertEqual(c.remaining, 100.0)
        c.add_spent(30.0)
        self.assertEqual(c.spent, 30.0)
        self.assertEqual(c.remaining, 70.0)

    def test_expense_signed_amount(self):
        t = ExpenseTransaction(10, "Lunch", "Checking", "Food", date(2025, 12, 1))
        self.assertEqual(t.signed_amount(), -10.0)

    def test_transfer_requires_different_accounts(self):
        with self.assertRaises(ValidationError):
            TransferTransaction(10, "Bad", "A", "A", date(2025, 12, 1))


class TestUnitStorage(unittest.TestCase):
    def test_load_missing_file_returns_empty_budget(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "missing.json"
            b = load_budget(p)
            self.assertIsInstance(b, Budget)
            self.assertEqual(len(b.accounts), 0)

    def test_corrupted_json_raises(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "bad.json"
            p.write_text("{ not json", encoding="utf-8")
            with self.assertRaises(StorageError):
                load_budget(p)


class TestIntegration(unittest.TestCase):
    def _make_budget(self) -> Budget:
        b = Budget()
        b.add_account(Account("Checking", 100.0))
        b.add_account(Account("Savings", 0.0))
        b.add_category(BudgetCategory("Housing", 500.0))
        b.add_category(BudgetCategory("Food", 200.0))
        return b

    def test_transactions_update_accounts_and_categories(self):
        b = self._make_budget()
        b.add_transaction(ExpenseTransaction(40, "Rent", "Checking", "Housing", date(2025, 12, 1)))
        b.add_transaction(IncomeTransaction(50, "Pay", "Checking", date(2025, 12, 2)))
        self.assertAlmostEqual(b.get_account("Checking").balance, 110.0)
        self.assertAlmostEqual(b.categories["Housing"].spent, 40.0)

    def test_transfer_moves_money_between_accounts(self):
        b = self._make_budget()
        b.add_transaction(TransferTransaction(25, "move", "Checking", "Savings", date(2025, 12, 3)))
        self.assertAlmostEqual(b.get_account("Checking").balance, 75.0)
        self.assertAlmostEqual(b.get_account("Savings").balance, 25.0)

    def test_save_then_load_roundtrip(self):
        b = self._make_budget()
        b.add_transaction(ExpenseTransaction(10, "snack", "Checking", "Food", date(2025, 12, 1)))
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "state.json"
            save_budget(b, p)
            b2 = load_budget(p)
        self.assertEqual(set(b2.accounts.keys()), {"Checking", "Savings"})
        self.assertEqual(set(b2.categories.keys()), {"Housing", "Food"})
        self.assertEqual(len(b2.transactions), 1)
        self.assertAlmostEqual(b2.categories["Food"].spent, 10.0)

    def test_export_reports_create_files(self):
        b = self._make_budget()
        b.add_transaction(ExpenseTransaction(10, "snack", "Checking", "Food", date(2025, 12, 1)))
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            cat_p = d / "cats.csv"
            acc_p = d / "accs.csv"
            tx_p = d / "tx.csv"
            export_category_report_csv(b, cat_p)
            export_account_report_csv(b, acc_p)
            export_transactions_csv(b, tx_p)
            self.assertTrue(cat_p.exists())
            self.assertTrue(acc_p.exists())
            self.assertTrue(tx_p.exists())

    def test_import_transactions_csv_parses_rows(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "import.csv"
            p.write_text(
                "type,amount,description,date,account_name,category_name,from_account,to_account\n"
                "income,100,Pay,2025-12-01,Checking,,,\n"
                "expense,25,Lunch,2025-12-02,Checking,Food,,\n"
                "transfer,10,Move,2025-12-03,,,Checking,Savings\n",
                encoding="utf-8",
            )
            txs = import_transactions_csv(p)
            self.assertEqual(len(txs), 3)

    def test_import_into_budget_applies_transactions(self):
        b = Budget()
        b.add_account(Account("Checking", 0.0))
        b.add_account(Account("Savings", 0.0))
        b.add_category(BudgetCategory("Food", 200.0))

        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "import.csv"
            p.write_text(
                "type,amount,description,date,account_name,category_name,from_account,to_account\n"
                "income,100,Pay,2025-12-01,Checking,,,\n"
                "expense,25,Lunch,2025-12-02,Checking,Food,,\n"
                "transfer,10,Move,2025-12-03,,,Checking,Savings\n",
                encoding="utf-8",
            )
            n = import_into_budget(b, p)

        self.assertEqual(n, 3)
        self.assertAlmostEqual(b.get_account("Checking").balance, 65.0)
        self.assertAlmostEqual(b.get_account("Savings").balance, 10.0)
        self.assertAlmostEqual(b.categories["Food"].spent, 25.0)


class TestSystem(unittest.TestCase):
    def test_end_to_end_import_export_save_load(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            save_path = d / "state.json"
            csv_path = d / "import.csv"
            out_dir = d / "out"

            budget = setup_demo_budget()

            csv_path.write_text(
                "type,amount,description,date,account_name,category_name,from_account,to_account\n"
                "income,1000,Pay,2025-12-01,Checking,,,\n"
                "expense,50,Groceries,2025-12-02,Checking,Food,,\n"
                "transfer,100,Save,2025-12-03,,,Checking,Savings\n",
                encoding="utf-8",
            )
            n = import_csv_workflow(budget, csv_path)
            self.assertEqual(n, 3)

            paths = export_reports_workflow(budget, out_dir)
            for p in paths.values():
                self.assertTrue(p.exists())

            save_workflow(budget, save_path)
            self.assertTrue(save_path.exists())

            loaded = load_or_new(save_path)
            self.assertGreaterEqual(loaded.total_balance(), 0.0)
            tops = loaded.top_spending_categories(2)
            self.assertEqual(len(tops), 2)

    def test_missing_save_file_starts_new_budget(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "missing.json"
            b = load_or_new(p)
            self.assertEqual(len(b.accounts), 0)
            self.assertEqual(len(b.categories), 0)

    def test_corrupted_save_file_raises_storage_error(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "state.json"
            p.write_text("{ bad json", encoding="utf-8")
            with self.assertRaises(StorageError):
                load_budget(p)

    def test_invalid_import_file_raises(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "import.csv"
            p.write_text("x,y\n1,2\n", encoding="utf-8")
            with self.assertRaises(ImportError):
                import_transactions_csv(p)


# =========================
# Demo runner
# =========================

def demo() -> None:
    save_path = Path("data") / "budget_state.json"
    export_dir = Path("data") / "exports"

    budget = load_or_new(save_path)
    if not budget.accounts:
        budget = setup_demo_budget()

    budget.add_transaction(IncomeTransaction(2000, "Paycheck", "Checking", date.today()))
    budget.add_transaction(ExpenseTransaction(50, "Groceries", "Checking", "Food", date.today()))
    budget.add_transaction(TransferTransaction(200, "Move to savings", "Checking", "Savings", date.today()))

    exported = export_reports_workflow(budget, export_dir)
    save_workflow(budget, save_path)

    print("Total balance:", budget.total_balance())
    print("Top categories:", budget.top_spending_categories(3))
    print("Exports written:")
    for k, p in exported.items():
        print(f" - {k}: {p}")


if __name__ == "__main__":
    if "--test" in sys.argv:
        # Run unittests in this module
        unittest.main(argv=[sys.argv[0]])
    else:
        demo()
