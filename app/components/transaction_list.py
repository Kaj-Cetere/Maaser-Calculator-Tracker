import reflex as rx
from app.states.transaction_state import Transaction, TransactionState
from app.components.filter_popover import filter_popover
from app.components.sorting_controls import sorting_controls


def transaction_row(transaction: Transaction) -> rx.Component:
    """A single row in the transaction list."""
    is_potential_duplicate = TransactionState.potential_duplicates.contains(
        transaction["id"]
    )
    is_verified = TransactionState.verified_transactions.contains(transaction["id"])
    return rx.el.tr(
        rx.el.td(
            rx.cond(
                is_potential_duplicate,
                rx.el.div(
                    rx.el.input(
                        type="checkbox",
                        checked=is_verified,
                        on_change=lambda _: TransactionState.toggle_verified(
                            transaction["id"]
                        ),
                        class_name="w-4 h-4 text-emerald-600 bg-gray-100 border-gray-300 rounded focus:ring-emerald-500",
                        custom_attrs={"aria-label": "Mark as verified"},
                    ),
                    class_name="flex items-center justify-center w-10 h-10",
                ),
                rx.el.div(class_name="w-10"),
            ),
            class_name="p-4",
        ),
        rx.el.td(
            rx.el.div(
                rx.icon(
                    rx.cond(
                        transaction["type"] == "income", "trending-up", "hand-coins"
                    ),
                    class_name=rx.cond(
                        transaction["type"] == "income",
                        "w-5 h-5 text-[#A3BE8C]", # nord14 Green
                        "w-5 h-5 text-[#B48EAD]", # nord15 Purple
                    ),
                ),
                class_name=rx.cond(
                    transaction["type"] == "income",
                    "flex items-center justify-center w-10 h-10 rounded-full bg-[#A3BE8C]/20",
                    "flex items-center justify-center w-10 h-10 rounded-full bg-[#B48EAD]/20",
                ),
            ),
            class_name="p-4",
        ),
        rx.el.td(
            rx.el.div(
                rx.el.p(transaction["memo"], class_name="font-medium text-[#ECEFF4]"),
                rx.el.p(
                    rx.el.span(f"{transaction['date']}", class_name="mr-2"),
                    rx.el.span(
                        transaction["hebrew_date"],
                        class_name="text-[#88C0D0] font-['Heebo'] text-xs font-semibold",
                    ),
                    class_name="text-sm text-[#81A1C1] flex items-center",
                ),
                rx.cond(
                    transaction["account_id"],
                    rx.el.div(
                        rx.icon("landmark", class_name="w-3 h-3 mr-1 text-[#88C0D0]"), # nord8
                        rx.el.span(
                            transaction["account_name"],
                            class_name="text-xs text-[#D8DEE9] font-medium",
                        ),
                        class_name="flex items-center mt-1",
                    ),
                    rx.el.div(
                        rx.icon("wallet", class_name="w-3 h-3 mr-1 text-[#88C0D0]"),
                        rx.el.span(
                            "Cash", class_name="text-xs text-[#D8DEE9] font-medium"
                        ),
                        class_name="flex items-center mt-1",
                    ),
                ),
            ),
            class_name="p-4",
        ),
        rx.el.td(
            rx.el.p(
                rx.cond(
                    transaction["type"] == "income",
                    f"+${transaction['amount']:.2f}",
                    f"${transaction['amount']:.2f}",
                ),
                class_name=rx.cond(
                    transaction["type"] == "income",
                    "font-semibold text-[#A3BE8C]",
                    "font-semibold text-[#B48EAD]",
                ),
            ),
            class_name="p-4 text-right",
        ),
        rx.el.td(
            rx.el.div(
                rx.el.button(
                    rx.icon("pencil", class_name="w-4 h-4"),
                    on_click=lambda: TransactionState.open_edit_transaction_modal(
                        transaction
                    ),
                    class_name="p-2 text-[#D8DEE9] hover:text-[#88C0D0] hover:bg-[#88C0D0]/10 rounded-md transition-colors",
                ),
                rx.el.button(
                    rx.icon("trash-2", class_name="w-4 h-4"),
                    on_click=lambda: TransactionState.delete_transaction(
                        transaction["id"]
                    ),
                    class_name="p-2 text-[#D8DEE9] hover:text-[#BF616A] hover:bg-[#BF616A]/10 rounded-md transition-colors",
                ),
                class_name="flex items-center justify-end gap-2",
            ),
            class_name="p-4",
        ),
        class_name=rx.cond(
            is_potential_duplicate & ~is_verified,
            "border-b border-[#434C5E] bg-[#EBCB8B]/10 border-l-4 border-[#EBCB8B]", # nord13 Warning
            "border-b border-[#434C5E] hover:bg-[#434C5E]/30 transition-colors",
        ),
    )


def transaction_list_header() -> rx.Component:
    return rx.el.div(
        # Row 1: Title and Main Actions
        rx.el.div(
            rx.el.h2(
                "Recent Transactions", class_name="text-xl font-bold text-[#ECEFF4]"
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon("import", class_name="w-4 h-4 mr-2"),
                    "Import",
                    on_click=TransactionState.open_import_modal,
                    class_name="flex items-center px-3 py-2 text-sm font-medium text-[#D8DEE9] bg-[#3B4252] border border-[#434C5E] rounded-lg hover:bg-[#434C5E] hover:border-[#88C0D0]/50 transition-all",
                ),
                rx.el.button(
                    rx.icon("download", class_name="w-4 h-4 mr-2"),
                    "Export CSV",
                    on_click=TransactionState.export_to_csv,
                    class_name="flex items-center px-3 py-2 text-sm font-medium text-[#D8DEE9] bg-[#3B4252] border border-[#434C5E] rounded-lg hover:bg-[#434C5E] hover:border-[#88C0D0]/50 transition-all",
                ),
                rx.el.button(
                    rx.icon("plus", class_name="w-4 h-4 mr-2"),
                    "Add Transaction",
                    on_click=TransactionState.open_new_transaction_modal,
                    class_name="flex items-center px-4 py-2 text-sm font-bold text-[#2E3440] bg-[#88C0D0] rounded-lg shadow-lg shadow-[#88C0D0]/20 hover:bg-[#81A1C1] hover:shadow-[#81A1C1]/30 transition-all transform hover:-translate-y-0.5",
                ),
                class_name="flex items-center gap-3",
            ),
            class_name="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 w-full",
        ),
        
        # Row 2: Search and View Controls
        rx.el.div(
            rx.el.div(
                rx.icon("search", class_name="w-4 h-4 text-[#81A1C1]"),
                rx.el.input(
                    id="search-input",
                    placeholder="Search query, amount, or date...",
                    on_change=TransactionState.set_search_query.debounce(300),
                    class_name="bg-transparent focus:outline-none w-full text-sm font-medium placeholder:text-[#4C566A] text-[#ECEFF4]",
                ),
                class_name="flex flex-1 items-center gap-3 bg-[#3B4252] border border-[#434C5E] rounded-lg px-4 py-2.5 focus-within:border-[#88C0D0] focus-within:ring-1 focus-within:ring-[#88C0D0] transition-all shadow-sm",
            ),
            rx.el.div(
                sorting_controls(),
                filter_popover(),
                class_name="flex items-center gap-3",
            ),
            class_name="flex flex-col md:flex-row items-stretch md:items-center gap-4 w-full",
        ),
        class_name="flex flex-col gap-5 mb-6",
    )


def transaction_list() -> rx.Component:
    """The main component to display the list of transactions."""
    return rx.el.div(
        transaction_list_header(),
        rx.el.div(
            rx.cond(
                TransactionState.sorted_transactions.length() > 0,
                rx.el.table(
                    rx.el.tbody(
                        rx.foreach(
                            TransactionState.transactions_with_hebrew_dates, transaction_row
                        )
                    ),
                    class_name="w-full",
                ),
                rx.el.div(
                    rx.icon("archive", class_name="w-16 h-16 text-[#4C566A] mb-4"),
                    rx.el.h3(
                        "No transactions yet",
                        class_name="text-lg font-semibold text-[#D8DEE9]",
                    ),
                    rx.el.p(
                        "Click 'Add Transaction' to get started.",
                        class_name="text-sm text-[#81A1C1]",
                    ),
                    class_name="flex flex-col items-center justify-center text-center p-12 border-2 border-dashed border-[#434C5E] rounded-lg",
                ),
            ),
            class_name="glass-panel rounded-lg overflow-hidden",
        ),
    )