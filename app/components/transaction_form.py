import reflex as rx
from app.states.transaction_state import TransactionState


def suggestion_row(suggestion: dict) -> rx.Component:
    """A single suggestion row with memo and amount."""
    return rx.el.button(
        rx.el.div(
            rx.el.div(
                rx.el.span(suggestion["memo"], class_name="font-semibold text-[#ECEFF4]"),
                rx.cond(
                    suggestion["is_recurring"],
                    rx.el.div(
                        rx.icon("star", class_name="w-3 h-3 text-[#EBCB8B]"),
                        rx.el.span("Recurring", class_name="text-xs font-medium"),
                        class_name="flex items-center gap-1 px-2 py-0.5 rounded-full bg-[#EBCB8B]/10 text-[#EBCB8B]",
                    ),
                    None,
                ),
                class_name="flex items-center gap-2",
            ),
            rx.el.span(
                f"${suggestion['common_amount']:.2f}",
                class_name="text-sm text-[#81A1C1] font-medium",
            ),
            class_name="flex items-center justify-between w-full",
        ),
        on_click=lambda: TransactionState.apply_suggestion(
            suggestion["memo"], suggestion["common_amount"]
        ),
        class_name="w-full text-left px-3 py-2 rounded-lg hover:bg-[#434C5E] transition-colors",
    )


def form_input(
    label: str,
    name: str,
    type: str,
    value: rx.Var,
    on_change: rx.event.EventHandler,
    placeholder: str = "",
) -> rx.Component:
    """A reusable form input component."""
    return rx.el.div(
        rx.el.label(label, class_name="block text-sm font-medium text-[#D8DEE9] mb-1"),
        rx.el.input(
            name=name,
            type=type,
            on_change=on_change,
            placeholder=placeholder,
            class_name="w-full px-3 py-2 rounded-md border border-[#434C5E] bg-[#3B4252] text-[#ECEFF4] focus:border-[#88C0D0] focus:ring-1 focus:ring-[#88C0D0] shadow-sm transition-colors placeholder-[#4C566A]",
            default_value=value,
        ),
        class_name="w-full",
    )


def transaction_form_modal() -> rx.Component:
    """A modal form for adding or editing transactions."""
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.portal(
            rx.radix.primitives.dialog.overlay(
                class_name="fixed inset-0 z-50 bg-black/60"
            ),
            rx.radix.primitives.dialog.content(
                rx.radix.primitives.dialog.title(
                    rx.cond(
                        TransactionState.is_editing,
                        "Edit Transaction",
                        "New Transaction",
                    ),
                    class_name="text-xl font-bold text-[#ECEFF4]",
                ),
                rx.radix.primitives.dialog.close(
                    rx.el.button(
                        rx.icon("x", class_name="w-5 h-5"),
                        class_name="absolute top-4 right-4 p-1 rounded-full text-[#D8DEE9] hover:bg-[#434C5E] hover:text-[#ECEFF4]",
                    )
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.label(
                            "Type",
                            class_name="block text-sm font-medium text-[#D8DEE9] mb-2",
                        ),
                        rx.el.div(
                            rx.el.button(
                                "Income",
                                on_click=lambda: TransactionState.set_form_type(
                                    "income"
                                ),
                                class_name=rx.cond(
                                    TransactionState.form_type == "income",
                                    "flex-1 py-2 px-4 text-sm font-semibold rounded-l-md bg-[#A3BE8C] text-[#2E3440] border border-[#A3BE8C]",
                                    "flex-1 py-2 px-4 text-sm font-semibold rounded-l-md bg-[#3B4252] text-[#D8DEE9] border border-[#434C5E] hover:bg-[#434C5E]",
                                ),
                            ),
                            rx.el.button(
                                "Maaser",
                                on_click=lambda: TransactionState.set_form_type(
                                    "maaser"
                                ),
                                class_name=rx.cond(
                                    TransactionState.form_type == "maaser",
                                    "flex-1 py-2 px-4 text-sm font-semibold rounded-r-md bg-[#B48EAD] text-[#ECEFF4] border border-[#B48EAD]",
                                    "flex-1 py-2 px-4 text-sm font-semibold rounded-r-md bg-[#3B4252] text-[#D8DEE9] border border-[#434C5E] hover:bg-[#434C5E]",
                                ),
                            ),
                            class_name="flex w-full",
                        ),
                        class_name="w-full mb-4",
                    ),
                    rx.el.div(
                        form_input(
                            label="Amount",
                            name="amount",
                            type="text",
                            placeholder="0.00",
                            value=TransactionState.form_amount,
                            on_change=TransactionState.set_form_amount,
                        ),
                        class_name="w-full mb-4",
                    ),
                    rx.el.div(
                        form_input(
                            label="Date",
                            name="date",
                            type="date",
                            value=TransactionState.form_date,
                            on_change=TransactionState.set_form_date,
                        ),
                        rx.cond(
                            TransactionState.form_hebrew_date != "",
                            rx.el.p(
                                TransactionState.form_hebrew_date,
                                class_name="text-sm font-['Heebo'] mt-1 text-[#88C0D0] font-medium",
                            ),
                            None,
                        ),
                        class_name="w-full mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Memo",
                            class_name="block text-sm font-medium text-[#D8DEE9] mb-1",
                        ),
                        rx.el.textarea(
                            name="memo",
                            placeholder="e.g., Paycheck, Tzedakah box...",
                            on_change=[
                                TransactionState.set_form_memo,
                                TransactionState.set_memo_input_value,
                            ],
                            class_name="w-full px-3 py-2 rounded-md border border-[#434C5E] bg-[#3B4252] text-[#ECEFF4] focus:border-[#88C0D0] focus:ring-1 focus:ring-[#88C0D0] shadow-sm transition-colors min-h-[80px] placeholder-[#4C566A]",
                            default_value=TransactionState.form_memo,
                        ),
                        class_name="w-full mb-4",
                    ),
                    rx.el.div(
                        rx.cond(
                            TransactionState.contextual_suggestions.length() > 0,
                            rx.el.div(
                                rx.el.h4(
                                    "Suggestions",
                                    class_name="text-xs font-bold text-[#81A1C1] uppercase tracking-wider mb-2 px-3",
                                ),
                                rx.foreach(
                                    TransactionState.contextual_suggestions,
                                    suggestion_row,
                                ),
                                class_name="bg-[#2E3440] border border-dashed border-[#434C5E] rounded-lg p-2",
                            ),
                            None,
                        ),
                        class_name="w-full mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Account",
                            class_name="block text-sm font-medium text-[#D8DEE9] mb-1",
                        ),
                        rx.el.select(
                            rx.el.option("Cash", value="cash"),
                            rx.foreach(
                                TransactionState.accounts,
                                lambda acc: rx.el.option(acc["name"], value=acc["id"]),
                            ),
                            value=TransactionState.form_account_id,
                            on_change=TransactionState.set_form_account_id,
                            class_name="w-full px-3 py-2 rounded-md border border-[#434C5E] bg-[#3B4252] text-[#ECEFF4] focus:border-[#88C0D0] focus:ring-1 focus:ring-[#88C0D0] shadow-sm transition-colors",
                        ),
                        class_name="w-full mb-4",
                    ),
                    rx.cond(
                        TransactionState.form_error != "",
                        rx.el.div(
                            rx.icon("badge_alert", class_name="w-4 h-4 mr-2"),
                            TransactionState.form_error,
                            class_name="flex items-center text-sm text-[#BF616A] bg-[#BF616A]/10 p-3 rounded-md mb-4",
                        ),
                        None,
                    ),
                    class_name="py-6",
                ),
                rx.el.div(
                    rx.radix.primitives.dialog.close(
                        rx.el.button(
                            "Cancel",
                            class_name="px-4 py-2 text-sm font-medium text-[#D8DEE9] bg-[#3B4252] border border-[#434C5E] rounded-md shadow-sm hover:bg-[#434C5E]/80",
                        )
                    ),
                    rx.el.button(
                        rx.cond(
                            TransactionState.is_editing,
                            "Save Changes",
                            "Add Transaction",
                        ),
                        on_click=TransactionState.handle_form_submit,
                        class_name="px-4 py-2 text-sm font-medium text-[#2E3440] bg-[#88C0D0] border border-transparent rounded-md shadow-sm hover:bg-[#81A1C1]",
                    ),
                    class_name="flex justify-end gap-3 pt-4 border-t border-[#434C5E]",
                ),
                class_name="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 glass-card rounded-xl shadow-xl w-full max-w-lg p-6 z-50 max-h-[85vh] overflow-y-auto",
            ),
        ),
        open=TransactionState.show_form_modal,
        on_open_change=lambda open: TransactionState.close_form_modal(),
    )