import reflex as rx
from app.states.transaction_state import TransactionState, BankAccount
from app.components.sidebar import sidebar


def account_row(account: BankAccount) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            rx.el.div(
                rx.icon("landmark", class_name="w-5 h-5 text-[#81A1C1]"), # nord9
                class_name="flex items-center justify-center w-10 h-10 rounded-full bg-[#3B4252]", # nord1
            ),
            class_name="p-4",
        ),
        rx.el.td(
            rx.el.p(account["name"], class_name="font-medium text-[#ECEFF4]"),
            class_name="p-4",
        ),
        rx.el.td(
            rx.el.div(
                rx.el.button(
                    rx.icon("trash-2", class_name="w-4 h-4"),
                    on_click=lambda: TransactionState.delete_account(account["id"]),
                    class_name="p-2 text-[#D8DEE9] hover:text-[#BF616A] hover:bg-[#BF616A]/10 rounded-md transition-colors",
                ),
                class_name="flex items-center justify-end gap-2",
            ),
            class_name="p-4",
        ),
        class_name="border-b border-[#434C5E] hover:bg-[#3B4252]/50 transition-colors",
    )


def add_account_form() -> rx.Component:
    return rx.el.form(
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    "Add New Account", class_name="text-lg font-bold text-[#ECEFF4] tracking-tight"
                ),
                rx.el.p(
                    "Add a new bank account to track transactions from.",
                    class_name="text-sm text-[#D8DEE9]",
                ),
                class_name="mb-4",
            ),
            rx.el.div(
                rx.el.label(
                    "Account Name",
                    class_name="block text-sm font-medium text-[#D8DEE9] mb-1",
                ),
                rx.el.input(
                    name="name",
                    placeholder="e.g., Chase Checking",
                    class_name="w-full px-3 py-2 rounded-md border border-[#434C5E] bg-[#3B4252] text-[#ECEFF4] focus:border-[#88C0D0] focus:ring-1 focus:ring-[#88C0D0] shadow-sm transition-colors placeholder-[#4C566A]",
                ),
                class_name="mb-4",
            ),
            rx.el.button(
                "Add Account",
                type="submit",
                class_name="px-4 py-2 text-sm font-medium text-[#2E3440] bg-gradient-to-r from-[#88C0D0] to-[#81A1C1] rounded-md shadow-lg hover:from-[#81A1C1] hover:to-[#5E81AC] transition-all",
            ),
            class_name="p-6 glass-panel rounded-xl",
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
                    class_name="text-3xl font-bold text-[#ECEFF4] tracking-tight pb-6 border-b border-[#434C5E] mb-6",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.h2(
                            "Bank Accounts",
                            class_name="text-xl font-bold text-[#ECEFF4] mb-4 tracking-tight",
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
                                        class_name="w-16 h-16 text-[#4C566A] mb-4",
                                    ),
                                    rx.el.h3(
                                        "No accounts yet",
                                        class_name="text-lg font-semibold text-[#D8DEE9]",
                                    ),
                                    rx.el.p(
                                        "Add an account using the form below.",
                                        class_name="text-sm text-[#81A1C1]",
                                    ),
                                    class_name="flex flex-col items-center justify-center text-center p-12 border-2 border-dashed border-[#434C5E] rounded-lg",
                                ),
                            ),
                            class_name="glass-panel rounded-xl overflow-hidden",
                        ),
                        class_name="flex-1",
                    ),
                    add_account_form(),
                    class_name="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start",
                ),
                class_name="flex-1 p-6 md:p-8 lg:p-10",
            ),
            class_name="flex flex-col flex-1 min-h-screen bg-[#2E3440] text-[#ECEFF4]",
        ),
        class_name="flex min-h-screen w-full bg-[#2E3440] text-slate-100 selection:bg-[#88C0D0] selection:text-[#2E3440]",
    )