import reflex as rx
from typing import TypedDict, Literal
import datetime
import uuid
import logging
import os
import shutil
import json

DATA_FILE = "data.json"
BACKUP_FILE = "data_backup.json"


class BankAccount(TypedDict):
    id: str
    name: str


class Transaction(TypedDict):
    id: str
    type: Literal["income", "maaser"]
    amount: float
    date: str
    memo: str
    account_id: str | None


class TransactionState(rx.State):
    """Manages all transaction-related data and logic."""

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
    show_import_modal: bool = False
    import_json_text: str = ""
    import_preview: list[Transaction] = []
    import_error: str = ""

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
                        date1 = datetime.date.fromisoformat(t1['date'])
                        date2 = datetime.date.fromisoformat(t2['date'])
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
            "date": lambda t: t["date"],
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
                    "date": datetime.fromisoformat(t['date']),
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
        """Load data from local JSON file on app startup."""
        async with self:
            if os.path.exists(DATA_FILE):
                try:
                    with open(DATA_FILE, "r") as f:
                        data = json.load(f)
                        self.transactions = data.get("transactions", [])
                        self.accounts = data.get("accounts", [])
                        self.verified_transactions = data.get("verified_transactions", [])
                except Exception as e:
                    logging.exception(f"Error loading data: {e}")
            else:
                self.transactions = []
                self.accounts = []
                self.verified_transactions = []

    def _save_data(self):
        """Saves all data to a local JSON file with backup."""
        data = {
            "transactions": self.transactions,
            "accounts": self.accounts,
            "verified_transactions": self.verified_transactions,
        }
        
        if os.path.exists(DATA_FILE):
            try:
                shutil.copy2(DATA_FILE, BACKUP_FILE)
            except Exception as e:
                logging.error(f"Error creating backup: {e}")
            
        try:
            with open(DATA_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving data: {e}")

    def _save_transactions(self):
        """Helper to save transactions to local storage."""
        self._save_data()

    def _save_verified_transactions(self):
        """Helper to save verified transactions to local storage."""
        self._save_data()

    def _save_accounts(self):
        """Helper to save accounts to local storage."""
        self._save_data()

    def _validate_form(self) -> bool:
        """Helper to validate form fields."""
        if not self.form_amount or not self.form_date:
            self.form_error = "Amount and Date are required."
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
        self.form_memo = ""
        self.memo_input_value = ""
        self.form_account_id = "cash"
        self.current_transaction_id = None
        self.form_error = ""

    def _reset_import_state(self):
        self.import_json_text = ""
        self.import_preview = []
        self.import_error = ""
        return rx.clear_selected_files("json_upload")

    @rx.event
    def open_import_modal(self):
        self.show_import_modal = True
        return self._reset_import_state()

    @rx.event
    def close_import_modal(self):
        self.show_import_modal = False
        return self._reset_import_state()

    @rx.event
    def open_new_transaction_modal(self):
        """Opens the modal to add a new transaction."""
        self._reset_form_fields()
        self.is_editing = False
        self.form_date = datetime.date.today().isoformat()
        self.show_form_modal = True

    @rx.event
    def open_edit_transaction_modal(self, transaction: Transaction):
        """Opens the modal to edit an existing transaction."""
        self.is_editing = True
        self.current_transaction_id = transaction["id"]
        self.form_type = transaction["type"]
        self.form_amount = str(transaction["amount"])
        self.form_date = transaction["date"]
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

    def _validate_and_parse_json(self, json_content: str):
        import json

        self.import_preview = []
        self.import_error = ""
        try:
            data = json.loads(json_content)
            if not isinstance(data, list):
                self.import_error = "Invalid JSON format: must be an array of objects."
                return
            preview_list = []
            for item in data:
                if not isinstance(item, dict):
                    continue
                if not all((k in item for k in ["type", "amount", "date"])):
                    continue
                if item["type"] not in ["income", "maaser"]:
                    continue
                try:
                    amount = float(item["amount"])
                except (ValueError, TypeError) as e:
                    logging.exception(f"Error parsing amount during import: {e}")
                    continue
                new_transaction: Transaction = {
                    "id": str(uuid.uuid4()),
                    "type": item["type"],
                    "amount": amount,
                    "date": item.get("date", datetime.date.today().isoformat()),
                    "memo": item.get("memo", ""),
                    "account_id": item.get("account_id"),
                }
                preview_list.append(new_transaction)
            if not preview_list:
                self.import_error = "No valid transactions found in the provided JSON."
            self.import_preview = preview_list
        except json.JSONDecodeError as e:
            logging.exception(f"JSON Decode Error: {e}")
            self.import_error = "Invalid JSON. Please check the syntax."
        except Exception as e:
            logging.exception(f"Unexpected error during JSON validation: {e}")
            self.import_error = f"An unexpected error occurred: {e}"

    @rx.event
    async def handle_uploaded_file(self, files: list[rx.UploadFile]):
        if not files:
            self.import_error = "No file selected."
            return
        try:
            file_content = await files[0].read()
            self._validate_and_parse_json(file_content.decode("utf-8"))
        except Exception as e:
            logging.exception(f"Error reading uploaded file: {e}")
            self.import_error = f"Error reading file: {e}"

    @rx.event
    def validate_and_preview_json(self):
        if not self.import_json_text.strip():
            self.import_error = "Pasted JSON content is empty."
            return
        self._validate_and_parse_json(self.import_json_text)

    @rx.event
    def confirm_import(self):
        if not self.import_preview:
            return
        self.transactions.extend(self.import_preview)
        self._save_transactions()
        self._reset_import_state()
        self.show_import_modal = False
        return rx.toast.success(
            f"Successfully imported {len(self.import_preview)} transactions."
        )

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
        writer.writerow(["ID", "Type", "Amount", "Date", "Memo"])
        for t in self.sorted_transactions:
            writer.writerow(
                [t["id"], t["type"], t["amount"], t["date"], t["memo"]]
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