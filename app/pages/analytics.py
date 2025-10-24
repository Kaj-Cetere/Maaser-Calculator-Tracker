import reflex as rx
from app.states.transaction_state import TransactionState
from app.components.sidebar import sidebar
from app.components.transaction_form import transaction_form_modal


def kpi_card(title: str, value: rx.Var, icon: str, color: str) -> rx.Component:
    """A card for displaying a key performance indicator."""
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name=f"w-6 h-6 {color}"),
            class_name="p-3 bg-gray-100 rounded-lg",
        ),
        rx.el.div(
            rx.el.h3(title, class_name="text-sm font-medium text-gray-500"),
            rx.el.p(f"${value:.2f}", class_name="text-2xl font-bold text-gray-800"),
        ),
        class_name="flex items-center gap-4 p-4 bg-white border border-gray-200 rounded-lg shadow-sm",
    )


def analytics_chart() -> rx.Component:
    """An area chart to show income vs maaser trends."""
    return rx.el.div(
        rx.el.h3("Monthly Trends", class_name="text-lg font-bold text-gray-800 mb-4"),
        rx.recharts.area_chart(
            rx.recharts.cartesian_grid(
                horizontal=True, vertical=False, class_name="opacity-20"
            ),
            rx.recharts.graphing_tooltip(cursor=False),
            rx.recharts.x_axis(
                data_key="month",
                tick_line=False,
                axis_line=False,
                custom_attrs={"fontSize": "12px"},
            ),
            rx.recharts.y_axis(
                tick_line=False,
                axis_line=False,
                tick_prefix="$",
                custom_attrs={"fontSize": "12px"},
            ),
            rx.recharts.area(
                data_key="income",
                type_="natural",
                fill="#10B981",
                stroke="#059669",
                stack_id="1",
            ),
            rx.recharts.area(
                data_key="maaser",
                type_="natural",
                fill="#EF4444",
                stroke="#DC2626",
                stack_id="1",
            ),
            data=TransactionState.chart_data,
            height=300,
            margin={"left": -20, "top": 10},
        ),
        class_name="p-6 bg-white border border-gray-200 rounded-lg shadow-sm",
    )


def analytics_page() -> rx.Component:
    """The analytics page component."""
    return rx.el.div(
        sidebar(),
        rx.el.main(
            rx.el.div(
                rx.el.h1(
                    "Analytics",
                    class_name="text-3xl font-bold text-gray-800 tracking-tight pb-6 border-b border-gray-200 mb-6",
                ),
                rx.el.div(
                    kpi_card(
                        "Total Income",
                        TransactionState.total_income,
                        "arrow_up",
                        "text-emerald-500",
                    ),
                    kpi_card(
                        "Total Maaser",
                        TransactionState.total_maaser,
                        "arrow_down",
                        "text-red-500",
                    ),
                    kpi_card(
                        "Maaser Due",
                        TransactionState.maaser_due,
                        "dollar-sign",
                        "text-blue-500",
                    ),
                    class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6",
                ),
                analytics_chart(),
                class_name="flex-1 p-6 md:p-8 lg:p-10",
            ),
            class_name="flex flex-col flex-1 min-h-screen bg-gray-50",
        ),
        transaction_form_modal(),
        class_name="flex min-h-screen w-full font-['Open_Sans'] bg-white",
    )