import reflex as rx
from app.states.business_expense_state import BusinessTransaction, BusinessExpenseState
from app.states.transaction_state import TransactionState # For account names if needed, or we can use BusinessExpenseState if we duplicated it

def business_expense_row(transaction: BusinessTransaction) -> rx.Component:
    """A single row in the business expense list."""
    is_potential_duplicate = BusinessExpenseState.potential_duplicates.contains(
        transaction["id"]
    )
    
    return rx.el.tr(
        rx.el.td(
            rx.el.div(
                rx.icon(
                    "receipt",
                    class_name="w-5 h-5 text-[#88C0D0]",
                ),
                class_name="flex items-center justify-center w-10 h-10 rounded-full bg-[#88C0D0]/20 shadow-[0_0_10px_rgba(136,192,208,0.2)]",
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
                        class_name="text-[#81A1C1]/70 font-['Heebo'] text-xs",
                    ),
                    class_name="text-sm text-[#D8DEE9]/70 flex items-center",
                ),
                rx.cond(
                    transaction["account_id"],
                    rx.el.div(
                        rx.icon("landmark", class_name="w-3 h-3 mr-1 text-[#88C0D0]"),
                        rx.el.span(
                            transaction["account_name"],
                            class_name="text-xs text-[#D8DEE9] font-medium",
                        ),
                        class_name="flex items-center mt-1",
                    ),
                    rx.el.div(
                        rx.icon("wallet", class_name="w-3 h-3 mr-1 text-[#88C0D0]"),
                        rx.el.span(
                            "Cash / Personal", class_name="text-xs text-[#D8DEE9] font-medium"
                        ),
                        class_name="flex items-center mt-1",
                    ),
                ),
            ),
            class_name="p-4",
        ),
        rx.el.td(
            rx.el.p(
                f"${transaction['amount']:.2f}",
                class_name="font-semibold text-[#BF616A]",
            ),
            class_name="p-4 text-right",
        ),
        rx.el.td(
            rx.el.button(
                rx.cond(
                    transaction["status"] == "reimbursed",
                    rx.el.span(
                        rx.icon("circle-check", class_name="w-4 h-4 mr-1"),
                        "Reimbursed",
                        class_name="flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-[#A3BE8C]/20 text-[#A3BE8C] border border-[#A3BE8C]/30",
                    ),
                    rx.el.span(
                        rx.icon("clock", class_name="w-4 h-4 mr-1"),
                        "Pending",
                        class_name="flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-[#EBCB8B]/20 text-[#EBCB8B] border border-[#EBCB8B]/30",
                    ),
                ),
                on_click=lambda: BusinessExpenseState.toggle_status(transaction["id"]),
                class_name="hover:opacity-80 transition-opacity",
            ),
            class_name="p-4 text-center",
        ),
        rx.el.td(
            rx.el.div(
                rx.el.button(
                    rx.icon("pencil", class_name="w-4 h-4"),
                    on_click=lambda: BusinessExpenseState.open_edit_transaction_modal(
                        transaction
                    ),
                    class_name="p-2 text-[#D8DEE9] hover:text-[#88C0D0] hover:bg-[#88C0D0]/10 rounded-md transition-colors",
                ),
                rx.el.button(
                    rx.icon("trash-2", class_name="w-4 h-4"),
                    on_click=lambda: BusinessExpenseState.delete_transaction(
                        transaction["id"]
                    ),
                    class_name="p-2 text-[#D8DEE9] hover:text-[#BF616A] hover:bg-[#BF616A]/10 rounded-md transition-colors",
                ),
                class_name="flex items-center justify-end gap-2",
            ),
            class_name="p-4",
        ),
        class_name=rx.cond(
            is_potential_duplicate,
            "border-b border-[#434C5E] bg-[#EBCB8B]/10 border-l-4 border-l-[#EBCB8B]",
            "border-b border-[#434C5E] hover:bg-[#434C5E]/30 transition-colors",
        ),
    )


def business_expense_list_header() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                "Business Expenses", class_name="text-xl font-bold text-[#ECEFF4] tracking-tight"
            ),
            # Sorting controls could be added here similar to transaction_list
            class_name="flex items-center justify-between w-full",
        ),
        rx.el.div(
            rx.el.div(
                rx.icon("search", class_name="w-4 h-4 text-[#4C566A]"),
                rx.el.input(
                    id="search-input",
                    placeholder="Search expenses...",
                    on_change=BusinessExpenseState.set_search_query.debounce(300),
                    class_name="bg-transparent focus:outline-none w-full text-sm font-medium text-[#ECEFF4] placeholder:text-[#4C566A]",
                ),
                class_name="flex items-center gap-2 bg-[#3B4252] border border-[#434C5E] rounded-lg px-3 py-1.5 w-full max-w-xs focus-within:border-[#88C0D0] transition-all",
            ),
            rx.el.button(
                rx.icon("import", class_name="w-4 h-4 mr-2"),
                "Import",
                on_click=BusinessExpenseState.open_import_modal,
                class_name="flex items-center px-3 py-2 text-sm font-semibold text-[#D8DEE9] bg-[#3B4252] border border-[#434C5E] rounded-lg hover:bg-[#434C5E] transition-colors",
            ),
            rx.el.button(
                rx.icon("download", class_name="w-4 h-4 mr-2"),
                "Export CSV",
                on_click=BusinessExpenseState.export_to_csv,
                class_name="flex items-center px-3 py-2 text-sm font-semibold text-[#D8DEE9] bg-[#3B4252] border border-[#434C5E] rounded-lg hover:bg-[#434C5E] transition-colors",
            ),
            rx.el.button(
                rx.icon("plus", class_name="w-4 h-4 mr-2"),
                "Add Expense",
                on_click=BusinessExpenseState.open_new_transaction_modal,
                class_name="flex items-center px-4 py-2 text-sm font-semibold text-[#2E3440] bg-[#88C0D0] rounded-lg shadow-sm hover:bg-[#81A1C1] transition-all",
            ),
            class_name="flex items-center gap-2",
        ),
        class_name="flex flex-col md:flex-row justify-between items-center mb-4 gap-4",
    )


def business_expense_list() -> rx.Component:
    """The main component to display the list of business expenses."""
    return rx.el.div(
        business_expense_list_header(),
        rx.el.div(
            rx.cond(
                BusinessExpenseState.sorted_transactions.length() > 0,
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            rx.el.th("", class_name="p-4 text-left w-16"),
                            rx.el.th("Details", class_name="p-4 text-left"),
                            rx.el.th("Amount", class_name="p-4 text-right"),
                            rx.el.th("Status", class_name="p-4 text-center"),
                            rx.el.th("", class_name="p-4 text-right"),
                            class_name="border-b border-[#434C5E] bg-[#3B4252]/50 text-xs font-bold text-[#D8DEE9] uppercase tracking-widest",
                        )
                    ),
                    rx.el.tbody(
                        rx.foreach(
                            BusinessExpenseState.transactions_with_hebrew_dates, business_expense_row
                        )
                    ),
                    class_name="w-full",
                ),
                rx.el.div(
                    rx.icon("receipt", class_name="w-16 h-16 text-[#4C566A] mb-4"),
                    rx.el.h3(
                        "No expenses yet",
                        class_name="text-lg font-semibold text-[#D8DEE9]",
                    ),
                    rx.el.p(
                        "Click 'Add Expense' to track business spending.",
                        class_name="text-sm text-[#81A1C1]",
                    ),
                    class_name="flex flex-col items-center justify-center text-center p-12 border-2 border-dashed border-[#434C5E] rounded-lg",
                ),
            ),
            class_name="glass-panel rounded-xl overflow-hidden shadow-2xl",
        ),
    )
