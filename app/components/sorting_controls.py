import reflex as rx
from app.states.transaction_state import TransactionState


def sorting_controls() -> rx.Component:
    """Component with dropdown for sorting field and button for order."""
    return rx.el.div(
        rx.el.select(
            rx.el.option("Date", value="date"),
            rx.el.option("Amount", value="amount"),
            rx.el.option("Type", value="type"),
            value=TransactionState.sort_by,
            on_change=TransactionState.set_sort_by,
            class_name="text-sm font-semibold text-[#ECEFF4] bg-[#3B4252] border border-[#434C5E] rounded-lg shadow-sm hover:bg-[#434C5E] transition-colors focus:outline-none focus:ring-1 focus:ring-[#88C0D0]",
            custom_attrs={"aria-label": "Sort by"},
        ),
        rx.el.button(
            rx.icon(
                rx.cond(
                    TransactionState.sort_order == "desc",
                    "arrow-down-wide-narrow",
                    "arrow-up-wide-narrow",
                ),
                class_name="w-4 h-4",
            ),
            on_click=TransactionState.toggle_sort_order,
            class_name="p-2 text-[#ECEFF4] bg-[#3B4252] border border-[#434C5E] rounded-lg shadow-sm hover:bg-[#434C5E] transition-colors",
            custom_attrs={"aria-label": "Toggle sort order"},
        ),
        class_name="flex items-center gap-2",
    )