import reflex as rx
from app.states.transaction_state import TransactionState, BankAccount
from app.components.sidebar import sidebar


def account_row(account: BankAccount) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            rx.el.div(
                rx.icon("landmark", class_name="w-5 h-5 text-gray-500"),
                class_name="flex items-center justify-center w-10 h-10 rounded-full bg-gray-100",
            ),
            class_name="p-4",
        ),
        rx.el.td(
            rx.el.p(account["name"], class_name="font-medium text-gray-800"),
            class_name="p-4",
        ),
        rx.el.td(
            rx.el.div(
                rx.el.button(
                    rx.icon("trash-2", class_name="w-4 h-4"),
                    on_click=lambda: TransactionState.delete_account(account["id"]),
                    class_name="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-md",
                ),
                class_name="flex items-center justify-end gap-2",
            ),
            class_name="p-4",
        ),
        class_name="border-b border-gray-100 hover:bg-gray-50/50",
    )


def add_account_form() -> rx.Component:
    return rx.el.form(
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    "Add New Account", class_name="text-lg font-bold text-gray-800"
                ),
                rx.el.p(
                    "Add a new bank account to track transactions from.",
                    class_name="text-sm text-gray-500",
                ),
                class_name="mb-4",
            ),
            rx.el.div(
                rx.el.label(
                    "Account Name",
                    class_name="block text-sm font-medium text-gray-700 mb-1",
                ),
                rx.el.input(
                    name="name",
                    placeholder="e.g., Chase Checking",
                    class_name="w-full px-3 py-2 rounded-md border border-gray-300 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 shadow-sm transition-colors",
                ),
                class_name="mb-4",
            ),
            rx.el.button(
                "Add Account",
                type="submit",
                class_name="px-4 py-2 text-sm font-medium text-white bg-emerald-600 border border-transparent rounded-md shadow-sm hover:bg-emerald-700",
            ),
            class_name="p-6 bg-white border border-gray-200 rounded-lg shadow-sm",
        ),
        on_submit=TransactionState.add_account,
        reset_on_submit=True,
    )


def settings_page() -> rx.Component:
    """The settings page for managing accounts."""
    return rx.el.div(
        sidebar(),
        rx.el.main(
            rx.el.div(
                rx.el.h1(
                    "Settings",
                    class_name="text-3xl font-bold text-gray-800 tracking-tight pb-6 border-b border-gray-200 mb-6",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.h2(
                            "Bank Accounts",
                            class_name="text-xl font-bold text-gray-800 mb-4",
                        ),
                        rx.el.div(
                            rx.cond(
                                TransactionState.accounts.length() > 0,
                                rx.el.table(
                                    rx.el.tbody(
                                        rx.foreach(
                                            TransactionState.accounts, account_row
                                        )
                                    ),
                                    class_name="w-full",
                                ),
                                rx.el.div(
                                    rx.icon(
                                        "landmark",
                                        class_name="w-16 h-16 text-gray-300 mb-4",
                                    ),
                                    rx.el.h3(
                                        "No accounts yet",
                                        class_name="text-lg font-semibold text-gray-600",
                                    ),
                                    rx.el.p(
                                        "Add an account using the form below.",
                                        class_name="text-sm text-gray-500",
                                    ),
                                    class_name="flex flex-col items-center justify-center text-center p-12 border-2 border-dashed border-gray-200 rounded-lg",
                                ),
                            ),
                            class_name="bg-white border border-gray-200 rounded-lg overflow-hidden",
                        ),
                        class_name="flex-1",
                    ),
                    add_account_form(),
                    class_name="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start",
                ),
                class_name="flex-1 p-6 md:p-8 lg:p-10",
            ),
            class_name="flex flex-col flex-1 min-h-screen bg-gray-50",
        ),
        class_name="flex min-h-screen w-full font-['Open_Sans'] bg-white",
    )