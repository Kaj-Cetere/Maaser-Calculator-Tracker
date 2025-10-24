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
                        transaction["type"] == "income", "trending-up", "trending-down"
                    ),
                    class_name=rx.cond(
                        transaction["type"] == "income",
                        "w-5 h-5 text-emerald-500",
                        "w-5 h-5 text-red-500",
                    ),
                ),
                class_name=rx.cond(
                    transaction["type"] == "income",
                    "flex items-center justify-center w-10 h-10 rounded-full bg-emerald-50",
                    "flex items-center justify-center w-10 h-10 rounded-full bg-red-50",
                ),
            ),
            class_name="p-4",
        ),
        rx.el.td(
            rx.el.div(
                rx.el.p(transaction["memo"], class_name="font-medium text-gray-800"),
                rx.el.p(
                    f"{transaction['date']} at {transaction['time']}",
                    class_name="text-sm text-gray-500",
                ),
                rx.cond(
                    transaction["account_id"],
                    rx.el.div(
                        rx.icon("landmark", class_name="w-3 h-3 mr-1 text-gray-400"),
                        rx.el.span(
                            TransactionState.account_names_by_id.get(
                                transaction["account_id"], ""
                            ),
                            class_name="text-xs text-gray-500 font-medium",
                        ),
                        class_name="flex items-center mt-1",
                    ),
                    rx.el.div(
                        rx.icon("wallet", class_name="w-3 h-3 mr-1 text-gray-400"),
                        rx.el.span(
                            "Cash", class_name="text-xs text-gray-500 font-medium"
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
                    f"-${transaction['amount']:.2f}",
                ),
                class_name=rx.cond(
                    transaction["type"] == "income",
                    "font-semibold text-emerald-600",
                    "font-semibold text-red-600",
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
                    class_name="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-md",
                ),
                rx.el.button(
                    rx.icon("trash-2", class_name="w-4 h-4"),
                    on_click=lambda: TransactionState.delete_transaction(
                        transaction["id"]
                    ),
                    class_name="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-md",
                ),
                class_name="flex items-center justify-end gap-2",
            ),
            class_name="p-4",
        ),
        class_name=rx.cond(
            is_potential_duplicate & ~is_verified,
            "border-b border-gray-100 bg-amber-50 border-l-4 border-amber-400",
            "border-b border-gray-100 hover:bg-gray-50/50 transition-colors",
        ),
    )


def transaction_list_header() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                "Recent Transactions", class_name="text-xl font-bold text-gray-800"
            ),
            sorting_controls(),
            class_name="flex items-center justify-between w-full",
        ),
        rx.el.div(
            rx.el.div(
                rx.icon("search", class_name="w-4 h-4 text-gray-400"),
                rx.el.input(
                    id="search-input",
                    placeholder="Search transactions...",
                    on_change=TransactionState.set_search_query.debounce(300),
                    class_name="bg-transparent focus:outline-none w-full text-sm font-medium placeholder:text-gray-400",
                ),
                class_name="flex items-center gap-2 bg-white border border-gray-200 rounded-lg px-3 py-1.5 w-full max-w-xs",
            ),
            filter_popover(),
            rx.el.button(
                rx.icon("download", class_name="w-4 h-4 mr-2"),
                "Export CSV",
                on_click=TransactionState.export_to_csv,
                class_name="flex items-center px-3 py-2 text-sm font-semibold text-gray-700 bg-white border border-gray-200 rounded-lg shadow-sm hover:bg-gray-50 transition-colors",
            ),
            rx.el.button(
                rx.icon("plus", class_name="w-4 h-4 mr-2"),
                "Add Transaction",
                on_click=TransactionState.open_new_transaction_modal,
                class_name="flex items-center px-4 py-2 text-sm font-semibold text-white bg-emerald-600 rounded-lg shadow-sm hover:bg-emerald-700 transition-colors",
            ),
            class_name="flex items-center gap-2",
        ),
        class_name="flex flex-col md:flex-row justify-between items-center mb-4 gap-4",
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
                            TransactionState.sorted_transactions, transaction_row
                        )
                    ),
                    class_name="w-full",
                ),
                rx.el.div(
                    rx.icon("archive", class_name="w-16 h-16 text-gray-300 mb-4"),
                    rx.el.h3(
                        "No transactions yet",
                        class_name="text-lg font-semibold text-gray-600",
                    ),
                    rx.el.p(
                        "Click 'Add Transaction' to get started.",
                        class_name="text-sm text-gray-500",
                    ),
                    class_name="flex flex-col items-center justify-center text-center p-12 border-2 border-dashed border-gray-200 rounded-lg",
                ),
            ),
            class_name="bg-white border border-gray-200 rounded-lg overflow-hidden",
        ),
    )