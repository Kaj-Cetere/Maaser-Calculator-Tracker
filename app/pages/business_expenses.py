import reflex as rx
from app.components.sidebar import sidebar
from app.components.business_expense_list import business_expense_list
from app.components.business_expense_form import business_expense_form_modal
from app.components.business_import_modal import business_import_modal


def business_expenses_page() -> rx.Component:
    return rx.el.div(
        sidebar(),
        rx.el.main(
            rx.el.div(
                rx.el.div(
                    rx.el.h1(
                        "Business Expenses",
                        class_name="text-3xl font-bold text-gray-800 tracking-tight",
                    ),
                    class_name="pb-6 border-b border-gray-200 mb-6",
                ),
                business_expense_list(),
                class_name="flex-1 p-6 md:p-8 lg:p-10",
            ),
            class_name="flex flex-col flex-1 min-h-screen bg-gray-50",
        ),
        business_expense_form_modal(),
        business_import_modal(),
        class_name="flex min-h-screen w-full font-['Open_Sans'] bg-white",
    )
