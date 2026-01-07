import reflex as rx
from app.states.business_expense_state import BusinessExpenseState


def suggestion_row(suggestion: dict) -> rx.Component:
    """A single suggestion row with memo and amount."""
    return rx.el.button(
        rx.el.div(
            rx.el.div(
                rx.el.span(suggestion["memo"], class_name="font-semibold"),
                class_name="flex items-center gap-2",
            ),
            rx.el.span(
                f"${suggestion['avg_amount']:.2f}",
                class_name="text-sm text-gray-500 font-medium",
            ),
            class_name="flex items-center justify-between w-full",
        ),
        on_click=lambda: BusinessExpenseState.apply_suggestion(
            suggestion["memo"], suggestion["avg_amount"]
        ),
        class_name="w-full text-left px-3 py-2 rounded-lg hover:bg-[#434C5E] transition-colors text-[#D8DEE9]",
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


def business_expense_form_modal() -> rx.Component:
    """A modal form for adding or editing business expenses."""
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.portal(
            rx.radix.primitives.dialog.overlay(
                class_name="fixed inset-0 z-50 bg-black/60"
            ),
            rx.radix.primitives.dialog.content(
                rx.radix.primitives.dialog.title(
                    rx.cond(
                        BusinessExpenseState.is_editing,
                        "Edit Business Expense",
                        "New Business Expense",
                    ),
                    class_name="text-xl font-bold text-[#ECEFF4]",
                ),
                rx.radix.primitives.dialog.close(
                    rx.el.button(
                        rx.icon("x", class_name="w-5 h-5"),
                        class_name="absolute top-4 right-4 p-1 rounded-full text-[#D8DEE9] hover:bg-[#434C5E] hover:text-[#ECEFF4] transition-colors",
                    )
                ),
                rx.el.div(
                    rx.el.div(
                        form_input(
                            label="Amount",
                            name="amount",
                            type="text",
                            placeholder="0.00",
                            value=BusinessExpenseState.form_amount,
                            on_change=BusinessExpenseState.set_form_amount,
                        ),
                        class_name="w-full mb-4",
                    ),
                    rx.el.div(
                        form_input(
                            label="Date",
                            name="date",
                            type="date",
                            value=BusinessExpenseState.form_date,
                            on_change=BusinessExpenseState.set_form_date,
                        ),
                        rx.cond(
                            BusinessExpenseState.form_hebrew_date != "",
                            rx.el.p(
                                BusinessExpenseState.form_hebrew_date,
                                class_name="text-sm text-[#81A1C1] mt-1 font-['Heebo']",
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
                            placeholder="e.g., Client Lunch, Office Supplies...",
                            on_change=[
                                BusinessExpenseState.set_form_memo,
                                BusinessExpenseState.set_memo_input_value,
                            ],
                            class_name="w-full px-3 py-2 rounded-md border border-[#434C5E] bg-[#3B4252] text-[#ECEFF4] focus:border-[#88C0D0] focus:ring-1 focus:ring-[#88C0D0] shadow-sm transition-colors min-h-[80px] placeholder-[#4C566A]",
                            default_value=BusinessExpenseState.form_memo,
                        ),
                        class_name="w-full mb-4",
                    ),
                    rx.el.div(
                        rx.cond(
                            BusinessExpenseState.contextual_suggestions.length() > 0,
                            rx.el.div(
                                rx.el.h4(
                                    "Suggestions",
                                    class_name="text-xs font-bold text-[#81A1C1] uppercase tracking-wider mb-2 px-3",
                                ),
                                rx.foreach(
                                    BusinessExpenseState.contextual_suggestions,
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
                            "Paid From Account",
                            class_name="block text-sm font-medium text-[#D8DEE9] mb-1",
                        ),
                        rx.el.select(
                            rx.el.option("Cash / Personal", value="cash"),
                            rx.foreach(
                                BusinessExpenseState.accounts,
                                lambda acc: rx.el.option(acc["name"], value=acc["id"]),
                            ),
                            value=BusinessExpenseState.form_account_id,
                            on_change=BusinessExpenseState.set_form_account_id,
                            class_name="w-full px-3 py-2 rounded-md border border-[#434C5E] bg-[#3B4252] text-[#ECEFF4] focus:border-[#88C0D0] focus:ring-1 focus:ring-[#88C0D0] shadow-sm transition-colors",
                        ),
                        class_name="w-full mb-4",
                    ),
                    rx.cond(
                        BusinessExpenseState.form_error != "",
                        rx.el.div(
                            rx.icon("circle-alert", class_name="w-4 h-4 mr-2"),
                            BusinessExpenseState.form_error,
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
                            class_name="px-4 py-2 text-sm font-medium text-[#D8DEE9] bg-[#3B4252] border border-[#434C5E] rounded-md shadow-sm hover:bg-[#434C5E]/80 transition-colors",
                        )
                    ),
                    rx.el.button(
                        rx.cond(
                            BusinessExpenseState.is_editing,
                            "Save Changes",
                            "Add Expense",
                        ),
                        on_click=BusinessExpenseState.handle_form_submit,
                        class_name="px-4 py-2 text-sm font-medium text-[#2E3440] bg-[#88C0D0] border border-transparent rounded-md shadow-sm hover:bg-[#81A1C1] transition-all",
                    ),
                    class_name="flex justify-end gap-3 pt-4 border-t border-[#434C5E]",
                ),
                class_name="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 glass-card rounded-xl shadow-xl w-full max-w-lg p-6 z-50 max-h-[85vh] overflow-y-auto text-[#ECEFF4]",
            ),
        ),
        open=BusinessExpenseState.show_form_modal,
        on_open_change=lambda open: BusinessExpenseState.close_form_modal(),
    )
