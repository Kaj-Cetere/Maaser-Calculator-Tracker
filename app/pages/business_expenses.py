import reflex as rx
from app.components.sidebar import sidebar
from app.components.business_expense_list import business_expense_list
from app.components.business_expense_form import business_expense_form_modal
from app.components.business_import_modal import business_import_modal


from app.components.undo_banner import undo_banner
from app.states.business_expense_state import BusinessExpenseState

def business_expenses_page() -> rx.Component:
    return rx.el.div(
        sidebar(),
        rx.el.main(
            rx.el.div(
                rx.el.div(
                    rx.el.h1(
                        "Business Expenses",
                        class_name="text-3xl font-bold text-[#ECEFF4] tracking-tight",
                    ),
                    class_name="pb-6 border-b border-[#434C5E] mb-6",
                ),
                business_expense_list(),
                class_name="flex-1 p-6 md:p-8 lg:p-10",
            ),
            class_name="flex flex-col flex-1 min-h-screen bg-[#2E3440] text-[#ECEFF4]",
        ),
        business_expense_form_modal(),
        business_import_modal(),
        undo_banner(BusinessExpenseState),
        class_name="flex min-h-screen w-full bg-[#2E3440] text-slate-100 selection:bg-[#88C0D0] selection:text-[#2E3440]",
    )
