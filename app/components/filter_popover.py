import reflex as rx
from app.states.transaction_state import TransactionState


def filter_input(
    label: str, name: str, type: str, value: rx.Var, on_change: rx.event.EventHandler
) -> rx.Component:
    return rx.el.div(
        rx.el.label(label, class_name="text-sm font-medium text-[#D8DEE9]"),
        rx.el.input(
            name=name,
            type=type,
            on_change=on_change,
            class_name="w-full mt-1 px-2 py-1.5 text-sm rounded-md border border-[#434C5E] bg-[#3B4252] text-[#ECEFF4] focus:border-[#88C0D0] focus:ring-1 focus:ring-[#88C0D0] shadow-sm",
            default_value=value,
        ),
        class_name="w-full",
    )


def filter_popover() -> rx.Component:
    """A popover component for filtering transactions."""
    return rx.radix.popover.root(
        rx.radix.popover.trigger(
            rx.el.button(
                rx.icon("filter", class_name="w-4 h-4 mr-2"),
                "Filters",
                class_name="flex items-center px-3 py-2 text-sm font-semibold text-[#D8DEE9] bg-[#3B4252] border border-[#434C5E] rounded-lg shadow-sm hover:bg-[#434C5E] transition-colors",
            )
        ),
        rx.radix.popover.content(
            rx.el.div(
                rx.el.h3(
                    "Filter Transactions",
                    class_name="text-base font-bold text-[#ECEFF4] mb-4",
                ),
                rx.el.div(
                    rx.el.label(
                        "Type", class_name="text-sm font-medium text-[#D8DEE9] mb-1"
                    ),
                    rx.el.div(
                        rx.el.button(
                            "All",
                            on_click=lambda: TransactionState.set_filter_type("all"),
                            class_name=rx.cond(
                                TransactionState.filter_type == "all",
                                "flex-1 py-1.5 px-3 text-xs font-semibold rounded-l-md bg-[#88C0D0] text-[#2E3440] border border-[#88C0D0]",
                                "flex-1 py-1.5 px-3 text-xs font-semibold rounded-l-md bg-[#3B4252] text-[#D8DEE9] border border-[#434C5E] hover:bg-[#434C5E]",
                            ),
                        ),
                        rx.el.button(
                            "Income",
                            on_click=lambda: TransactionState.set_filter_type("income"),
                            class_name=rx.cond(
                                TransactionState.filter_type == "income",
                                "flex-1 py-1.5 px-3 text-xs font-semibold bg-[#A3BE8C] text-[#2E3440] border-t border-b border-[#A3BE8C]",
                                "flex-1 py-1.5 px-3 text-xs font-semibold bg-[#3B4252] text-[#D8DEE9] border-t border-b border-[#434C5E] hover:bg-[#434C5E]",
                            ),
                        ),
                        rx.el.button(
                            "Maaser",
                            on_click=lambda: TransactionState.set_filter_type("maaser"),
                            class_name=rx.cond(
                                TransactionState.filter_type == "maaser",
                                "flex-1 py-1.5 px-3 text-xs font-semibold rounded-r-md bg-[#BF616A] text-[#ECEFF4] border border-[#BF616A]",
                                "flex-1 py-1.5 px-3 text-xs font-semibold rounded-r-md bg-[#3B4252] text-[#D8DEE9] border border-[#434C5E] hover:bg-[#434C5E]",
                            ),
                        ),
                        class_name="flex w-full",
                    ),
                    class_name="mb-4",
                ),
                rx.el.div(
                    rx.el.label(
                        "Date Range",
                        class_name="text-sm font-medium text-[#D8DEE9] mb-2",
                    ),
                    rx.el.div(
                        filter_input(
                            "Start Date",
                            "start_date",
                            "date",
                            TransactionState.filter_start_date,
                            TransactionState.set_filter_start_date,
                        ),
                        filter_input(
                            "End Date",
                            "end_date",
                            "date",
                            TransactionState.filter_end_date,
                            TransactionState.set_filter_end_date,
                        ),
                        class_name="flex gap-2",
                    ),
                    class_name="mb-4",
                ),
                rx.el.div(
                    rx.el.label(
                        "Amount Range",
                        class_name="text-sm font-medium text-[#D8DEE9] mb-2",
                    ),
                    rx.el.div(
                        filter_input(
                            "Min Amount",
                            "min_amount",
                            "text",
                            TransactionState.filter_min_amount,
                            TransactionState.set_filter_min_amount,
                        ),
                        filter_input(
                            "Max Amount",
                            "max_amount",
                            "text",
                            TransactionState.filter_max_amount,
                            TransactionState.set_filter_max_amount,
                        ),
                        class_name="flex gap-2",
                    ),
                    class_name="mb-4",
                ),
                rx.el.div(
                    rx.el.label(
                        "Account", class_name="text-sm font-medium text-[#D8DEE9] mb-2"
                    ),
                    rx.el.select(
                        rx.el.option("All Accounts", value="all"),
                        rx.el.option("Cash", value="cash"),
                        rx.foreach(
                            TransactionState.accounts,
                            lambda acc: rx.el.option(acc["name"], value=acc["id"]),
                        ),
                        value=TransactionState.filter_account_id,
                        on_change=TransactionState.set_filter_account_id,
                        class_name="w-full mt-1 px-2 py-1.5 text-sm rounded-md border border-[#434C5E] bg-[#3B4252] text-[#ECEFF4] focus:border-[#88C0D0] focus:ring-1 focus:ring-[#88C0D0] shadow-sm",
                    ),
                    class_name="mb-4",
                ),
                rx.el.div(
                    rx.el.button(
                        "Reset Filters",
                        on_click=TransactionState.reset_filters,
                        class_name="w-full px-4 py-2 text-sm font-medium text-[#D8DEE9] bg-[#3B4252] border border-[#434C5E] rounded-md shadow-sm hover:bg-[#434C5E]/80",
                    ),
                    class_name="pt-4 border-t border-[#434C5E]",
                ),
                class_name="space-y-4",
            ),
            class_name="bg-[#2E3440] p-4 rounded-lg shadow-lg border border-[#434C5E] w-80",
            side_offset=5,
        ),
    )