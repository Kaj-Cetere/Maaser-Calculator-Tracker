import reflex as rx
from app.states.transaction_state import TransactionState


def nav_item(icon: str, text: str, href: str, is_active: bool) -> rx.Component:
    """A single navigation item in the sidebar."""
    return rx.el.a(
        rx.icon(icon, class_name="w-5 h-5"),
        rx.el.span(text, class_name="font-medium"),
        href=href,
        class_name=rx.cond(
            is_active,
            "flex items-center gap-3 rounded-lg bg-emerald-100 px-3 py-2 text-emerald-700 transition-all hover:text-emerald-800",
            "flex items-center gap-3 rounded-lg px-3 py-2 text-gray-500 transition-all hover:text-gray-900",
        ),
    )


def sidebar() -> rx.Component:
    """The main sidebar component for navigation."""
    return rx.el.aside(
        rx.el.div(
            rx.el.div(
                rx.el.a(
                    rx.icon("sprout", class_name="h-6 w-6 text-emerald-600"),
                    rx.el.span(
                        "Maaser Tracker",
                        class_name="text-lg font-semibold text-gray-800",
                    ),
                    href="/",
                    class_name="flex items-center gap-2",
                ),
                class_name="flex h-16 items-center border-b px-6",
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
                class_name="flex-1 overflow-auto py-4 px-4 grid items-start gap-1 text-sm",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.h3(
                        "Maaser Due", class_name="text-sm font-semibold text-gray-500"
                    ),
                    rx.el.p(
                        f"${TransactionState.maaser_due:.2f}",
                        class_name="text-lg font-bold text-emerald-600",
                    ),
                    class_name="p-4",
                ),
                class_name="mt-auto border-t",
            ),
            class_name="flex h-full max-h-screen flex-col gap-2",
        ),
        class_name="hidden border-r bg-gray-50/40 md:block w-64",
    )