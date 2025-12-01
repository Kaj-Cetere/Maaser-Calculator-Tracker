import reflex as rx
from app.components.sidebar import sidebar
from app.components.transaction_list import transaction_list
from app.components.transaction_form import transaction_form_modal
from app.components.import_modal import import_modal
from app.pages.analytics import analytics_page
from app.pages.settings import settings_page


def index() -> rx.Component:
    return rx.el.div(
        sidebar(),
        rx.el.main(
            rx.el.div(
                rx.el.div(
                    rx.el.h1(
                        "Dashboard",
                        class_name="text-3xl font-bold text-gray-800 tracking-tight",
                    ),
                    class_name="pb-6 border-b border-gray-200 mb-6",
                ),
                transaction_list(),
                class_name="flex-1 p-6 md:p-8 lg:p-10",
            ),
            class_name="flex flex-col flex-1 min-h-screen bg-gray-50",
        ),
        transaction_form_modal(),
        import_modal(),
        rx.window_event_listener(
            on_key_down=rx.call_script("""
                if (event.ctrlKey || event.metaKey) {
                    if (event.key === 'n') {
                        event.preventDefault();
                        _reflex.event_handlers.transaction_state_open_new_transaction_modal();
                    }
                    if (event.key === 'k') {
                        event.preventDefault();
                        document.getElementById('search-input')?.focus();
                    }
                }
                """)
        ),
        class_name="flex min-h-screen w-full font-['Open_Sans'] bg-white",
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
from app.states.transaction_state import TransactionState

app.add_page(index, on_load=TransactionState.on_load)
app.add_page(analytics_page, route="/analytics", on_load=TransactionState.on_load)
app.add_page(settings_page, route="/settings", on_load=TransactionState.on_load)

from app.pages.business_expenses import business_expenses_page
from app.states.business_expense_state import BusinessExpenseState
app.add_page(business_expenses_page, route="/business-expenses", on_load=[TransactionState.on_load, BusinessExpenseState.on_load])