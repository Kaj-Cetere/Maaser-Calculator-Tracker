import reflex as rx
from typing import TypedDict, Literal
import datetime
import uuid
import logging
import os
import shutil
import json
from app.states.transaction_state import BankAccount

DATA_FILE = "business_data.json"
BACKUP_FILE = "business_data_backup.json"


class BusinessTransaction(TypedDict):
    id: str
    amount: float
    date: str
    memo: str
    status: Literal["pending", "reimbursed"]
    account_id: str | None


class BusinessExpenseState(rx.State):
    """Manages all business expense related data and logic."""

    transactions: list[BusinessTransaction] = []
    accounts: list[BankAccount] = []  # We might need to load accounts here too or share them
    show_form_modal: bool = False
    is_editing: bool = False
    current_transaction_id: str | None = None
    form_error: str = ""
    form_amount: str = ""
    form_date: str = ""
    form_memo: str = ""
    form_status: Literal["pending", "reimbursed"] = "pending"
    form_account_id: str = "cash"
    memo_input_value: str = ""
    
    # Filters and Sorting
    search_query: str = ""
    sort_by: str = "date"
    sort_order: str = "desc"
    filter_status: Literal["all", "pending", "reimbursed"] = "all"

    # Import State
    show_import_modal: bool = False
    import_json_text: str = ""
    import_preview: list[BusinessTransaction] = []
    import_error: str = ""

    @rx.var
    def total_pending(self) -> float:
        """Calculates the total pending reimbursement amount."""
        return sum((t["amount"] for t in self.transactions if t["status"] == "pending"))

    @rx.var
    def filtered_transactions(self) -> list[BusinessTransaction]:
        """Applies search and filters to the transactions list."""
        transactions = self.transactions
        if self.search_query:
            search_lower = self.search_query.lower()
            transactions = [
                t
                for t in transactions
                if search_lower in t["memo"].lower() or search_lower in str(t["amount"])
            ]
        if self.filter_status != "all":
            transactions = [t for t in transactions if t["status"] == self.filter_status]
        
        return transactions

    @rx.var
    def sorted_transactions(self) -> list[BusinessTransaction]:
        """Transactions sorted based on selected field and order."""
        key_map = {
            "date": lambda t: t["date"],
            "amount": lambda t: t["amount"],
            "status": lambda t: t["status"],
        }
        sort_key = key_map.get(self.sort_by, key_map["date"])
        reverse = self.sort_order == "desc"
        return sorted(self.filtered_transactions, key=sort_key, reverse=reverse)

    @rx.var
    def potential_duplicates(self) -> list[str]:
        """Identifies potential duplicate transactions."""
        duplicates = set()
        # For business expenses, we might not have a 'verified' list yet, 
        # but we can check for identical amount/date/memo
        for i, t1 in enumerate(self.transactions):
            if t1["id"] in duplicates:
                continue
            for j in range(i + 1, len(self.transactions)):
                t2 = self.transactions[j]
                if t1["id"] == t2["id"]:
                    continue
                if t1["amount"] == t2["amount"] and t1["memo"] == t2["memo"]:
                    try:
                        date1 = datetime.date.fromisoformat(t1['date'])
                        date2 = datetime.date.fromisoformat(t2['date'])
                        if abs(date1 - date2) <= datetime.timedelta(days=1):
                            duplicates.add(t1["id"])
                            duplicates.add(t2["id"])
                    except ValueError:
                        pass
        return sorted(list(duplicates))

    @rx.var
    def transaction_patterns(self) -> list[dict]:
        """Analyzes historical data to identify transaction patterns for suggestions."""
        from collections import defaultdict, Counter
        from datetime import datetime

        patterns = defaultdict(list)
        for t in self.transactions:
            patterns[t["memo"].lower().strip()].append(t)
        
        ranked_patterns = []
        today = datetime.now()
        
        for memo, transactions in patterns.items():
            if not memo:
                continue
            frequency = len(transactions)
            last_used_date = max((datetime.fromisoformat(t["date"]) for t in transactions))
            recency_days = (today - last_used_date).days
            recency_score = 0.9 ** (recency_days / 7)
            
            amounts = [t["amount"] for t in transactions]
            avg_amount = sum(amounts) / len(amounts)
            
            score = frequency * 0.4 + recency_score * 0.6
            
            ranked_patterns.append({
                "memo": memo.capitalize(),
                "frequency": frequency,
                "avg_amount": avg_amount,
                "score": score
            })
            
        ranked_patterns.sort(key=lambda p: p["score"], reverse=True)
        return ranked_patterns

    @rx.var
    def contextual_suggestions(self) -> list[dict]:
        """Provides memo suggestions based on input."""
        patterns = self.transaction_patterns
        if not self.memo_input_value.strip():
            return patterns[:5]
        search_term = self.memo_input_value.lower()
        filtered = [p for p in patterns if search_term in p["memo"].lower()]
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
                except Exception as e:
                    logging.exception(f"Error loading business data: {e}")
            else:
                self.transactions = []
            
            # Load accounts from the main data file if needed, or just rely on TransactionState
            # For now, let's assume we might want to read accounts from the main data file 
            # to populate the dropdown, or we can just fetch them if we import TransactionState
            # But importing TransactionState here might cause circular imports if not careful.
            # Let's read the main data file just for accounts to be safe and independent.
            if os.path.exists("data.json"):
                 try:
                    with open("data.json", "r") as f:
                        main_data = json.load(f)
                        self.accounts = main_data.get("accounts", [])
                 except Exception:
                     pass

    def _save_data(self):
        """Saves all data to a local JSON file with backup."""
        data = {
            "transactions": self.transactions,
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

    @rx.event
    def open_new_transaction_modal(self):
        self._reset_form_fields()
        self.is_editing = False
        self.form_date = datetime.date.today().isoformat()
        self.show_form_modal = True

    @rx.event
    def open_edit_transaction_modal(self, transaction: BusinessTransaction):
        self.is_editing = True
        self.current_transaction_id = transaction["id"]
        self.form_amount = str(transaction["amount"])
        self.form_date = transaction["date"]
        self.form_memo = transaction["memo"]
        self.memo_input_value = transaction["memo"]
        self.form_status = transaction["status"]
        self.form_account_id = transaction.get("account_id") or "cash"
        self.show_form_modal = True

    @rx.event
    def close_form_modal(self):
        self.show_form_modal = False
        self._reset_form_fields()

    def _reset_form_fields(self):
        self.form_amount = ""
        self.form_date = ""
        self.form_memo = ""
        self.memo_input_value = ""
        self.form_status = "pending"
        self.form_account_id = "cash"
        self.current_transaction_id = None
        self.form_error = ""

    @rx.event
    def apply_suggestion(self, memo: str, amount: float):
        self.form_memo = memo
        self.memo_input_value = memo
        self.form_amount = str(amount)

    @rx.event
    def handle_form_submit(self):
        if not self.form_amount or not self.form_date:
            self.form_error = "Amount and Date are required."
            return
        try:
            amount = float(self.form_amount)
        except ValueError:
            self.form_error = "Amount must be a valid number."
            return

        transaction_data = {
            "amount": amount,
            "date": self.form_date,
            "memo": self.form_memo,
            "status": self.form_status,
            "account_id": self.form_account_id if self.form_account_id != "cash" else None,
        }

        if self.is_editing and self.current_transaction_id:
            for i, t in enumerate(self.transactions):
                if t["id"] == self.current_transaction_id:
                    self.transactions[i] = {
                        "id": self.current_transaction_id,
                        **transaction_data
                    }
                    break
        else:
            new_transaction: BusinessTransaction = {
                "id": str(uuid.uuid4()),
                **transaction_data
            }
            self.transactions.append(new_transaction)
        
        self.close_form_modal()
        self._save_data()

    @rx.event
    def delete_transaction(self, transaction_id: str):
        self.transactions = [t for t in self.transactions if t["id"] != transaction_id]
        self._save_data()

    @rx.event
    def toggle_status(self, transaction_id: str):
        for i, t in enumerate(self.transactions):
            if t["id"] == transaction_id:
                new_status = "reimbursed" if t["status"] == "pending" else "pending"
                self.transactions[i]["status"] = new_status
                break
        self._save_data()

    @rx.event
    def export_to_csv(self) -> rx.event.EventSpec:
        import csv
        from io import StringIO

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Date", "Memo", "Amount", "Status"])
        for t in self.sorted_transactions:
            writer.writerow(
                [t["id"], t["date"], t["memo"], t["amount"], t["status"]]
            )
        csv_data = output.getvalue()
        return rx.download(
            data=csv_data, filename=f"business_expenses_{datetime.date.today()}.csv"
        )

    def _reset_import_state(self):
        self.import_json_text = ""
        self.import_preview = []
        self.import_error = ""
        return rx.clear_selected_files("business_json_upload")

    @rx.event
    def open_import_modal(self):
        self.show_import_modal = True
        return self._reset_import_state()

    @rx.event
    def close_import_modal(self):
        self.show_import_modal = False
        return self._reset_import_state()

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
                # Required fields: amount, date. Optional: memo, status, account_id
                if not all((k in item for k in ["amount", "date"])):
                    continue
                
                try:
                    amount = float(item["amount"])
                except (ValueError, TypeError):
                    continue
                
                new_transaction: BusinessTransaction = {
                    "id": str(uuid.uuid4()),
                    "amount": amount,
                    "date": item.get("date", datetime.date.today().isoformat()),
                    "memo": item.get("memo", ""),
                    "status": item.get("status", "pending"),
                    "account_id": item.get("account_id"),
                }
                # Validate status
                if new_transaction["status"] not in ["pending", "reimbursed"]:
                    new_transaction["status"] = "pending"

                preview_list.append(new_transaction)
            
            if not preview_list:
                self.import_error = "No valid transactions found in the provided JSON."
            self.import_preview = preview_list
        except json.JSONDecodeError:
            self.import_error = "Invalid JSON. Please check the syntax."
        except Exception as e:
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
        self._save_data()
        self._reset_import_state()
        self.show_import_modal = False
        return rx.toast.success(
            f"Successfully imported {len(self.import_preview)} transactions."
        )
