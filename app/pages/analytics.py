import reflex as rx
from app.states.transaction_state import TransactionState
from app.components.sidebar import sidebar
from app.components.transaction_form import transaction_form_modal


def kpi_card(title: str, value: rx.Var, icon: str, color: str, prefix: str = "$", suffix: str = "", subtext: rx.Var | str = "") -> rx.Component:
    """A card for displaying a key performance indicator."""
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name=f"w-6 h-6 {color}"),
            class_name="p-3 bg-white/5 rounded-lg border border-white/5",
        ),
        rx.el.div(
            rx.el.h3(title, class_name="text-sm font-medium text-[#D8DEE9]"),
            rx.el.div(
                rx.el.p(
                    rx.cond(
                        prefix == "$",
                        f"${value:.2f}",
                        f"{value:.1f}%" if suffix == "%" else f"{value}"
                    ),
                    class_name=f"text-2xl font-bold {color if prefix != '$' else 'text-[#ECEFF4]'}",
                ),
                rx.cond(
                    subtext != "",
                    rx.el.span(subtext, class_name="text-xs text-[#81A1C1] mt-1 block"),
                ),
            ),
        ),
        class_name="flex items-center gap-4 p-4 glass-card rounded-xl shadow-lg hover:bg-[#3B4252] transition-colors",
    )


def analytics_chart() -> rx.Component:
    """An area chart to show income vs maaser trends."""
    return rx.el.div(
        rx.el.h3("Monthly Trends", class_name="text-lg font-bold text-[#ECEFF4] mb-4 tracking-tight"),
        rx.recharts.area_chart(
            rx.recharts.cartesian_grid(
                horizontal=True, vertical=False, class_name="opacity-20 stroke-[#4C566A]"
            ),
            rx.recharts.graphing_tooltip(
                cursor=False,
                content_style={"backgroundColor": "#2E3440", "borderColor": "#434C5E", "borderRadius": "8px", "color": "#ECEFF4"},
                item_style={"color": "#ECEFF4"}
            ),
            rx.recharts.x_axis(
                data_key="month",
                tick_line=False,
                axis_line=False,
                custom_attrs={"fontSize": "12px", "stroke": "#81A1C1"},
            ),
            rx.recharts.y_axis(
                tick_line=False,
                axis_line=False,
                tick_prefix="$",
                custom_attrs={"fontSize": "12px", "stroke": "#81A1C1"},
            ),
            rx.recharts.area(
                data_key="income",
                type_="natural",
                fill="#A3BE8C", # nord14 Green
                stroke="#8FBCBB", # nord7 Teal
                stack_id="1",
                fill_opacity=0.3,
            ),
            rx.recharts.area(
                data_key="maaser",
                type_="natural",
                fill="#B48EAD", # nord15 Purple
                stroke="#D08770", # nord12 Orange (Accent)
                stack_id="1",
                fill_opacity=0.3,
            ),
            data=TransactionState.chart_data,
            height=300,
            margin={"left": -20, "top": 10},
        ),
        class_name="p-6 glass-panel rounded-xl shadow-lg",
    )


def analytics_page() -> rx.Component:
    """The analytics page component."""
    return rx.el.div(
        sidebar(),
        rx.el.main(
            rx.el.div(
                rx.el.h1(
                    "Analytics",
                    class_name="text-3xl font-bold text-[#ECEFF4] tracking-tight pb-6 border-b border-[#434C5E] mb-6",
                ),
                rx.el.div(
                    kpi_card(
                        "Total Income",
                        TransactionState.total_income,
                        "arrow_up",
                        "text-[#A3BE8C]", # nord14 given
                    ),
                    kpi_card(
                        "Maaser Given",
                        TransactionState.total_maaser,
                        "hand-coins",
                        "text-[#B48EAD]", # nord15
                        subtext=f"{TransactionState.maaser_percentage:.1f}% of income",
                    ),
                    kpi_card(
                        "Giving Progress",
                        TransactionState.maaser_percentage,
                        "percent",
                        TransactionState.maaser_status_color, # This needs updating in state potentially, but css handles hexes well
                        prefix="",
                        suffix="%",
                        subtext=TransactionState.maaser_status_label,
                    ),
                    class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6",
                ),
                analytics_chart(),
                class_name="flex-1 p-6 md:p-8 lg:p-10",
            ),
            class_name="flex flex-col flex-1 min-h-screen bg-[#2E3440] text-[#ECEFF4]",
        ),
        transaction_form_modal(),
        class_name="flex min-h-screen w-full bg-[#2E3440] text-slate-100 selection:bg-[#88C0D0] selection:text-[#2E3440]",
    )