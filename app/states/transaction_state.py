import reflex as rx
from typing import TypedDict, Literal
import datetime
import uuid
import logging


class BankAccount(TypedDict):
    id: str
    name: str


class Transaction(TypedDict):
    id: str
    type: Literal["income", "maaser"]
    amount: float
    date: str
    time: str
    memo: str
    account_id: str | None


class TransactionState(rx.State):
    """Manages all transaction-related data and logic."""

    _transactions_json: str = rx.LocalStorage("[]", name="transactions")
    _accounts_json: str = rx.LocalStorage("[]", name="accounts")
    _verified_json: str = rx.LocalStorage("[]", name="verified_transactions")
    transactions: list[Transaction] = []
    verified_transactions: list[str] = []
    accounts: list[BankAccount] = []
    show_form_modal: bool = False
    is_editing: bool = False
    current_transaction_id: str | None = None
    form_error: str = ""
    form_type: Literal["income", "maaser"] = "income"
    form_amount: str = ""
    form_date: str = ""
    form_time: str = ""
    form_memo: str = ""
    form_account_id: str = "cash"
    memo_input_value: str = ""
    search_query: str = ""
    show_filters: bool = False
    filter_type: Literal["all", "income", "maaser"] = "all"
    filter_start_date: str = ""
    filter_end_date: str = ""
    filter_min_amount: str = ""
    filter_max_amount: str = ""
    filter_account_id: str = "all"
    sort_by: str = "date"
    sort_order: str = "desc"

    @rx.var
    def potential_duplicates(self) -> list[str]:
        """Identifies potential duplicate transactions."""
        duplicates = set()
        verified_set = set(self.verified_transactions)
        transactions_to_check = [
            t for t in self.transactions if t["id"] not in verified_set
        ]
        for i, t1 in enumerate(transactions_to_check):
            if t1["id"] in duplicates:
                continue
            for j in range(i + 1, len(transactions_to_check)):
                t2 = transactions_to_check[j]
                if t1["id"] == t2["id"]:
                    continue
                if t1["amount"] == t2["amount"]:
                    try:
                        date1 = datetime.datetime.fromisoformat(
                            f"{t1['date']}T{t1['time']}"
                        )
                        date2 = datetime.datetime.fromisoformat(
                            f"{t2['date']}T{t2['time']}"
                        )
                        if abs(date1 - date2) <= datetime.timedelta(days=1):
                            duplicates.add(t1["id"])
                            duplicates.add(t2["id"])
                    except ValueError as e:
                        logging.exception(
                            f"Error parsing dates for duplicate check: {e}"
                        )
        return sorted(list(duplicates))

    @rx.var
    def filtered_transactions(self) -> list[Transaction]:
        """Applies search and filters to the transactions list."""
        transactions = self.transactions
        if self.search_query:
            search_lower = self.search_query.lower()
            transactions = [
                t
                for t in transactions
                if search_lower in t["memo"].lower() or search_lower in str(t["amount"])
            ]
        if self.filter_type != "all":
            transactions = [t for t in transactions if t["type"] == self.filter_type]
        if self.filter_start_date:
            transactions = [
                t for t in transactions if t["date"] >= self.filter_start_date
            ]
        if self.filter_end_date:
            transactions = [
                t for t in transactions if t["date"] <= self.filter_end_date
            ]
        if self.filter_min_amount:
            try:
                min_amount = float(self.filter_min_amount)
                transactions = [t for t in transactions if t["amount"] >= min_amount]
            except ValueError as e:
                logging.exception(f"Error: {e}")
        if self.filter_max_amount:
            try:
                max_amount = float(self.filter_max_amount)
                transactions = [t for t in transactions if t["amount"] <= max_amount]
            except ValueError as e:
                logging.exception(f"Error: {e}")
        if self.filter_account_id != "all":
            if self.filter_account_id == "cash":
                transactions = [t for t in transactions if t["account_id"] is None]
            else:
                transactions = [
                    t for t in transactions if t["account_id"] == self.filter_account_id
                ]
        return transactions

    @rx.var
    def sorted_transactions(self) -> list[Transaction]:
        """Transactions sorted based on selected field and order."""
        key_map = {
            "date": lambda t: (t["date"], t["time"]),
            "amount": lambda t: t["amount"],
            "type": lambda t: t["type"],
        }
        sort_key = key_map.get(self.sort_by, key_map["date"])
        reverse = self.sort_order == "desc"
        return sorted(self.filtered_transactions, key=sort_key, reverse=reverse)

    @rx.var
    def total_income(self) -> float:
        """Calculates the total income from all transactions."""
        return sum((t["amount"] for t in self.transactions if t["type"] == "income"))

    @rx.var
    def total_maaser(self) -> float:
        """Calculates the total maaser given from all transactions."""
        return sum((t["amount"] for t in self.transactions if t["type"] == "maaser"))

    @rx.var
    def maaser_due(self) -> float:
        """Calculates the maaser due (10% of income minus maaser given)."""
        return self.total_income * 0.1 - self.total_maaser

    @rx.var
    def account_names_by_id(self) -> dict[str, str]:
        """Returns a dictionary mapping account IDs to their names."""
        return {acc["id"]: acc["name"] for acc in self.accounts}

    @rx.var
    def chart_data(self) -> list[dict[str, float | str]]:
        """Prepares data for the analytics chart."""
        from collections import defaultdict

        monthly_data = defaultdict(lambda: {"income": 0.0, "maaser": 0.0})
        for t in self.transactions:
            month = datetime.datetime.strptime(t["date"], "%Y-%m-%d").strftime("%b %Y")
            monthly_data[month][t["type"]] += t["amount"]
        sorted_months = sorted(
            monthly_data.keys(), key=lambda m: datetime.datetime.strptime(m, "%b %Y")
        )
        return [
            {
                "month": month,
                "income": monthly_data[month]["income"],
                "maaser": monthly_data[month]["maaser"],
            }
            for month in sorted_months
        ]

    @rx.var
    def transaction_patterns(self) -> dict[Literal["income", "maaser"], list[dict]]:
        """Analyzes historical data to identify transaction patterns."""
        from collections import defaultdict, Counter
        from datetime import datetime, timedelta

        patterns = {"income": defaultdict(list), "maaser": defaultdict(list)}
        for t in self.transactions:
            patterns[t["type"]][t["memo"].lower().strip()].append(
                {
                    "amount": t["amount"],
                    "date": datetime.fromisoformat(f"{t['date']}T{t['time']}"),
                }
            )
        ranked_patterns = {"income": [], "maaser": []}
        today = datetime.now()
        for type, memo_groups in patterns.items():
            for memo, transactions in memo_groups.items():
                if not memo:
                    continue
                frequency = len(transactions)
                last_used_date = max((t["date"] for t in transactions))
                recency_days = (today - last_used_date).days
                recency_score = 0.9 ** (recency_days / 7)
                amounts = [t["amount"] for t in transactions]
                avg_amount = sum(amounts) / len(amounts)
                common_amount = Counter(amounts).most_common(1)[0][0]
                is_recurring = False
                if len(transactions) > 2:
                    dates = sorted([t["date"] for t in transactions])
                    intervals = [
                        (dates[i] - dates[i - 1]).days for i in range(1, len(dates))
                    ]
                    avg_interval = sum(intervals) / len(intervals)
                    if avg_interval > 5:
                        variance = sum(
                            ((i - avg_interval) ** 2 for i in intervals)
                        ) / len(intervals)
                        if variance < 5:
                            is_recurring = True
                score = (
                    frequency * 0.4 + recency_score * 0.35 + int(is_recurring) * 0.25
                )
                ranked_patterns[type].append(
                    {
                        "memo": memo.capitalize(),
                        "frequency": frequency,
                        "avg_amount": avg_amount,
                        "common_amount": common_amount,
                        "score": score,
                        "is_recurring": is_recurring,
                    }
                )
        ranked_patterns["income"].sort(key=lambda p: p["score"], reverse=True)
        ranked_patterns["maaser"].sort(key=lambda p: p["score"], reverse=True)
        return ranked_patterns

    @rx.var
    def contextual_suggestions(self) -> list[dict]:
        """Provides memo suggestions based on current form type and input."""
        patterns = self.transaction_patterns.get(self.form_type, [])
        if not self.memo_input_value.strip():
            return patterns[:5]
        search_term = self.memo_input_value.lower()
        filtered = [p for p in patterns if search_term in p["memo"].lower()]
        for p in filtered:
            p["score"] += len(search_term) / len(p["memo"]) * 0.2
        return sorted(filtered, key=lambda p: p["score"], reverse=True)[:5]

    @rx.event(background=True)
    async def on_load(self):
        """Load transactions and accounts from local storage on app startup."""
        async with self:
            import json

            try:
                self.transactions = json.loads(self._transactions_json)
            except json.JSONDecodeError as e:
                logging.exception(f"Error: {e}")
                self.transactions = []
            try:
                self.accounts = json.loads(self._accounts_json)
            except json.JSONDecodeError as e:
                logging.exception(f"Error: {e}")
                self.accounts = []
            try:
                self.verified_transactions = json.loads(self._verified_json)
            except json.JSONDecodeError as e:
                logging.exception(f"Error loading verified transactions: {e}")
                self.verified_transactions = []

    def _save_transactions(self):
        """Helper to save transactions to local storage."""
        import json

        self._transactions_json = json.dumps(self.transactions)

    def _save_verified_transactions(self):
        """Helper to save verified transactions to local storage."""
        import json

        self._verified_json = json.dumps(self.verified_transactions)

    def _save_accounts(self):
        """Helper to save accounts to local storage."""
        import json

        self._accounts_json = json.dumps(self.accounts)

    def _validate_form(self) -> bool:
        """Helper to validate form fields."""
        if not self.form_amount or not self.form_date or (not self.form_time):
            self.form_error = "Amount, Date, and Time are required."
            return False
        try:
            float(self.form_amount)
        except ValueError as e:
            logging.exception(f"Error: {e}")
            self.form_error = "Amount must be a valid number."
            return False
        self.form_error = ""
        return True

    def _reset_form_fields(self):
        """Helper to clear all form fields."""
        self.form_type = "income"
        self.form_amount = ""
        self.form_date = ""
        self.form_time = ""
        self.form_memo = ""
        self.memo_input_value = ""
        self.form_account_id = "cash"
        self.current_transaction_id = None
        self.form_error = ""

    @rx.event
    def open_new_transaction_modal(self):
        """Opens the modal to add a new transaction."""
        self._reset_form_fields()
        self.is_editing = False
        self.form_date = datetime.date.today().isoformat()
        self.form_time = datetime.datetime.now().strftime("%H:%M")
        self.show_form_modal = True

    @rx.event
    def open_edit_transaction_modal(self, transaction: Transaction):
        """Opens the modal to edit an existing transaction."""
        self.is_editing = True
        self.current_transaction_id = transaction["id"]
        self.form_type = transaction["type"]
        self.form_amount = str(transaction["amount"])
        self.form_date = transaction["date"]
        self.form_time = transaction["time"]
        self.form_memo = transaction["memo"]
        self.memo_input_value = transaction["memo"]
        self.form_account_id = transaction.get("account_id") or "cash"
        self.form_error = ""
        self.show_form_modal = True

    @rx.event
    def close_form_modal(self):
        """Closes the transaction form modal."""
        self.show_form_modal = False
        self._reset_form_fields()

    @rx.event
    def apply_suggestion(self, memo: str, amount: float):
        """Applies a memo and amount from a suggestion."""
        self.form_memo = memo
        self.memo_input_value = memo
        self.form_amount = str(amount)

    @rx.event
    def handle_form_submit(self):
        """Adds or updates a transaction."""
        if not self._validate_form():
            return
        transaction_data = {
            "type": self.form_type,
            "amount": float(self.form_amount),
            "date": self.form_date,
            "time": self.form_time,
            "memo": self.form_memo,
            "account_id": self.form_account_id
            if self.form_account_id != "cash"
            else None,
        }
        if self.is_editing and self.current_transaction_id:
            index_to_update = -1
            for i, t in enumerate(self.transactions):
                if t["id"] == self.current_transaction_id:
                    index_to_update = i
                    break
            if index_to_update != -1:
                self.transactions[index_to_update] = {
                    "id": self.current_transaction_id,
                    **transaction_data,
                }
        else:
            new_transaction: Transaction = {"id": str(uuid.uuid4()), **transaction_data}
            self.transactions.append(new_transaction)
        self.close_form_modal()
        self._save_transactions()

    @rx.event
    def delete_transaction(self, transaction_id: str):
        """Deletes a transaction by its ID."""
        self.transactions = [t for t in self.transactions if t["id"] != transaction_id]
        self.verified_transactions = [
            vid for vid in self.verified_transactions if vid != transaction_id
        ]
        self._save_transactions()
        self._save_verified_transactions()

    @rx.event
    def toggle_verified(self, transaction_id: str):
        """Toggles the verified status of a transaction."""
        if transaction_id in self.verified_transactions:
            self.verified_transactions = [
                vid for vid in self.verified_transactions if vid != transaction_id
            ]
        else:
            self.verified_transactions.append(transaction_id)
        self._save_verified_transactions()

    @rx.event
    def export_to_csv(self) -> rx.event.EventSpec:
        """Exports current transactions to a CSV file."""
        import csv
        from io import StringIO

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Type", "Amount", "Date", "Time", "Memo"])
        for t in self.sorted_transactions:
            writer.writerow(
                [t["id"], t["type"], t["amount"], t["date"], t["time"], t["memo"]]
            )
        csv_data = output.getvalue()
        return rx.download(
            data=csv_data, filename=f"maaser_transactions_{datetime.date.today()}.csv"
        )

    @rx.event
    def reset_filters(self):
        """Resets all filter fields to their default values."""
        self.filter_type = "all"
        self.filter_start_date = ""
        self.filter_end_date = ""
        self.filter_min_amount = ""
        self.filter_max_amount = ""
        self.filter_account_id = "all"

    @rx.event
    def add_account(self, form_data: dict):
        """Adds a new bank account."""
        name = form_data.get("name")
        if not name:
            return
        new_account: BankAccount = {"id": str(uuid.uuid4()), "name": name}
        self.accounts.append(new_account)
        self._save_accounts()

    @rx.event
    def delete_account(self, account_id: str):
        """Deletes a bank account by its ID."""
        self.accounts = [acc for acc in self.accounts if acc["id"] != account_id]
        self._save_accounts()

    @rx.event
    def toggle_sort_order(self):
        """Toggles the sort order between ascending and descending."""
        self.sort_order = "asc" if self.sort_order == "desc" else "desc"