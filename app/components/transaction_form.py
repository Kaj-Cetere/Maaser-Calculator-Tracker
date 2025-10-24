import reflex as rx
from app.states.transaction_state import TransactionState


def suggestion_row(suggestion: dict) -> rx.Component:
    """A single suggestion row with memo and amount."""
    return rx.el.button(
        rx.el.div(
            rx.el.div(
                rx.el.span(suggestion["memo"], class_name="font-semibold"),
                rx.cond(
                    suggestion["is_recurring"],
                    rx.el.div(
                        rx.icon("star", class_name="w-3 h-3 text-amber-500"),
                        rx.el.span("Recurring", class_name="text-xs font-medium"),
                        class_name="flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-100 text-amber-700",
                    ),
                    None,
                ),
                class_name="flex items-center gap-2",
            ),
            rx.el.span(
                f"${suggestion['common_amount']:.2f}",
                class_name="text-sm text-gray-500 font-medium",
            ),
            class_name="flex items-center justify-between w-full",
        ),
        on_click=lambda: TransactionState.apply_suggestion(
            suggestion["memo"], suggestion["common_amount"]
        ),
        class_name="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors",
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
        rx.el.label(label, class_name="block text-sm font-medium text-gray-700 mb-1"),
        rx.el.input(
            name=name,
            type=type,
            on_change=on_change,
            placeholder=placeholder,
            class_name="w-full px-3 py-2 rounded-md border border-gray-300 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 shadow-sm transition-colors",
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
                    class_name="text-xl font-bold text-gray-900",
                ),
                rx.radix.primitives.dialog.close(
                    rx.el.button(
                        rx.icon("x", class_name="w-5 h-5"),
                        class_name="absolute top-4 right-4 p-1 rounded-full text-gray-400 hover:bg-gray-100 hover:text-gray-600",
                    )
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.label(
                            "Type",
                            class_name="block text-sm font-medium text-gray-700 mb-2",
                        ),
                        rx.el.div(
                            rx.el.button(
                                "Income",
                                on_click=lambda: TransactionState.set_form_type(
                                    "income"
                                ),
                                class_name=rx.cond(
                                    TransactionState.form_type == "income",
                                    "flex-1 py-2 px-4 text-sm font-semibold rounded-l-md bg-emerald-600 text-white border border-emerald-600",
                                    "flex-1 py-2 px-4 text-sm font-semibold rounded-l-md bg-white text-gray-700 border border-gray-300 hover:bg-gray-50",
                                ),
                            ),
                            rx.el.button(
                                "Maaser",
                                on_click=lambda: TransactionState.set_form_type(
                                    "maaser"
                                ),
                                class_name=rx.cond(
                                    TransactionState.form_type == "maaser",
                                    "flex-1 py-2 px-4 text-sm font-semibold rounded-r-md bg-red-500 text-white border border-red-500",
                                    "flex-1 py-2 px-4 text-sm font-semibold rounded-r-md bg-white text-gray-700 border border-gray-300 hover:bg-gray-50",
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
                            type="number",
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
                        form_input(
                            label="Time",
                            name="time",
                            type="time",
                            value=TransactionState.form_time,
                            on_change=TransactionState.set_form_time,
                        ),
                        class_name="flex gap-4 mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Memo",
                            class_name="block text-sm font-medium text-gray-700 mb-1",
                        ),
                        rx.el.textarea(
                            name="memo",
                            placeholder="e.g., Paycheck, Tzedakah box...",
                            on_change=[
                                TransactionState.set_form_memo,
                                TransactionState.set_memo_input_value,
                            ],
                            class_name="w-full px-3 py-2 rounded-md border border-gray-300 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 shadow-sm transition-colors min-h-[80px]",
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
                                    class_name="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2 px-3",
                                ),
                                rx.foreach(
                                    TransactionState.contextual_suggestions,
                                    suggestion_row,
                                ),
                                class_name="bg-gray-50/70 border border-dashed rounded-lg p-2",
                            ),
                            None,
                        ),
                        class_name="w-full mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Account",
                            class_name="block text-sm font-medium text-gray-700 mb-1",
                        ),
                        rx.el.select(
                            rx.el.option("Cash", value="cash"),
                            rx.foreach(
                                TransactionState.accounts,
                                lambda acc: rx.el.option(acc["name"], value=acc["id"]),
                            ),
                            value=TransactionState.form_account_id,
                            on_change=TransactionState.set_form_account_id,
                            class_name="w-full px-3 py-2 rounded-md border border-gray-300 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 shadow-sm transition-colors bg-white",
                        ),
                        class_name="w-full mb-4",
                    ),
                    rx.cond(
                        TransactionState.form_error != "",
                        rx.el.div(
                            rx.icon("badge_alert", class_name="w-4 h-4 mr-2"),
                            TransactionState.form_error,
                            class_name="flex items-center text-sm text-red-600 bg-red-50 p-3 rounded-md mb-4",
                        ),
                        None,
                    ),
                    class_name="py-6",
                ),
                rx.el.div(
                    rx.radix.primitives.dialog.close(
                        rx.el.button(
                            "Cancel",
                            class_name="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50",
                        )
                    ),
                    rx.el.button(
                        rx.cond(
                            TransactionState.is_editing,
                            "Save Changes",
                            "Add Transaction",
                        ),
                        on_click=TransactionState.handle_form_submit,
                        class_name="px-4 py-2 text-sm font-medium text-white bg-emerald-600 border border-transparent rounded-md shadow-sm hover:bg-emerald-700",
                    ),
                    class_name="flex justify-end gap-3 pt-4 border-t",
                ),
                class_name="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white rounded-xl shadow-xl w-full max-w-lg p-6 z-50",
            ),
        ),
        open=TransactionState.show_form_modal,
        on_open_change=lambda open: TransactionState.close_form_modal(),
    )