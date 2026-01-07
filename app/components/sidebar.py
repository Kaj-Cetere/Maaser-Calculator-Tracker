import reflex as rx
from app.states.transaction_state import TransactionState


def nav_item(icon: str, text: str, href: str, is_active: bool) -> rx.Component:
    """A single navigation item in the sidebar."""
    return rx.el.a(
        rx.icon(
            icon,
            class_name=rx.cond(
                is_active,
                "w-5 h-5 text-[#88C0D0]",
                "w-5 h-5 text-[#D8DEE9]",
            ),
        ),
        rx.el.span(text, class_name="font-medium"),
        href=href,
        class_name=rx.cond(
            is_active,
            "flex items-center gap-3 rounded-lg bg-[#4C566A] px-3 py-2 text-[#ECEFF4] shadow-md transition-all border border-[#88C0D0]/20",
            "flex items-center gap-3 rounded-lg px-3 py-2 text-[#D8DEE9] transition-all hover:bg-[#434C5E] hover:text-white",
        ),
    )


def sidebar() -> rx.Component:
    """The main sidebar component for navigation."""
    return rx.el.aside(
        rx.el.div(
            rx.el.div(
                rx.el.a(
                    rx.icon("sprout", class_name="h-6 w-6 text-[#A3BE8C]"),
                    rx.el.span(
                        "Maaser Tracker",
                        class_name="text-lg font-semibold text-[#ECEFF4] tracking-wide",
                    ),
                    href="/",
                    class_name="flex items-center gap-2",
                ),
                class_name="flex h-16 items-center border-b border-[#434C5E] px-6",
            ),
            rx.el.nav(
                nav_item(
                    "layout-dashboard",
                    "Dashboard",
                    "/",
                    rx.State.router.page.path == "/",
                ),
                nav_item(
                    "area-chart",
                    "Analytics",
                    "/analytics",
                    rx.State.router.page.path == "/analytics",
                ),
                nav_item(
                    "settings",
                    "Settings",
                    "/settings",
                    rx.State.router.page.path == "/settings",
                ),
                nav_item(
                    "briefcase",
                    "Business Expenses",
                    "/business-expenses",
                    rx.State.router.page.path == "/business-expenses",
                ),
                class_name="flex-1 overflow-auto py-4 px-4 grid items-start gap-1 text-sm",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.span(
                            "Giving Progress",
                            class_name="text-xs font-semibold text-[#81A1C1] uppercase tracking-wider mb-1 block",
                        ),
                        rx.el.div(
                            rx.el.span(
                                f"{TransactionState.maaser_percentage:.1f}%",
                                class_name=f"text-3xl font-black {TransactionState.maaser_status_color} tabular-nums tracking-tight",
                            ),
                            rx.el.span(
                                " given",
                                class_name="text-sm font-medium text-[#D8DEE9]/60 ml-1",
                            ),
                            class_name="flex items-baseline mb-2",
                        ),
                        rx.el.div(
                            rx.el.div(
                                class_name=rx.cond(
                                    TransactionState.maaser_percentage >= 20,
                                    "h-full bg-purple-400 rounded-full transition-all duration-1000",
                                    rx.cond(
                                        TransactionState.maaser_percentage >= 10,
                                        "h-full bg-emerald-400 rounded-full transition-all duration-1000",
                                        "h-full bg-amber-400 rounded-full transition-all duration-1000",
                                    ),
                                ),
                                style={
                                    "width": rx.cond(
                                        TransactionState.maaser_percentage > 100,
                                        "100%",
                                        f"{TransactionState.maaser_percentage}%",
                                    )
                                },
                            ),
                            class_name="w-full h-1.5 bg-[#434C5E] rounded-full mb-3 overflow-hidden",
                        ),
                        rx.el.p(
                            TransactionState.maaser_status_label,
                            class_name="text-sm font-medium text-[#ECEFF4] mb-3",
                        ),
                        rx.el.div(
                            rx.el.div(
                                rx.el.span(
                                    "Remaining Due", class_name="text-xs text-[#D8DEE9]/60"
                                ),
                                rx.el.span(
                                    f"${TransactionState.maaser_due:.2f}",
                                    class_name="text-sm font-mono text-[#ECEFF4]/80",
                                ),
                                class_name="flex justify-between items-center",
                            ),
                            class_name="pt-3 border-t border-[#434C5E]/30",
                        ),
                    ),
                    class_name="p-5 bg-gradient-to-b from-[#2E3440] to-[#2E3440]/50 rounded-xl border border-[#434C5E] m-4 shadow-lg backdrop-blur-sm",
                ),
                class_name="mt-auto border-t border-[#434C5E]",
            ),
            class_name="flex h-full max-h-screen flex-col gap-2",
        ),
        class_name="hidden border-r border-[#434C5E] bg-[#3B4252] md:block w-64 shadow-xl",
    )