import reflex as rx

def undo_banner_item(transaction, state_class) -> rx.Component:
    """A single undo banner item."""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon("trash-2", class_name="w-5 h-5 text-[#BF616A]"),
                        class_name="flex items-center justify-center w-11 h-11 rounded-xl bg-[#BF616A]/15 shadow-inner",
                    ),
                    rx.el.div(
                        rx.el.p(
                            "Transaction deleted",
                            class_name="text-xs font-bold uppercase tracking-wider text-[#D8DEE9]/70 leading-none mb-1",
                        ),
                        rx.el.p(
                            transaction["memo"],
                            class_name="text-sm font-semibold text-[#ECEFF4] leading-none",
                        ),
                        class_name="flex flex-col justify-center",
                    ),
                    class_name="flex items-center gap-4",
                ),
                rx.el.div(
                    rx.el.button(
                        rx.icon("undo-2", class_name="w-4 h-4 mr-1.5"),
                        "Undo",
                        on_click=lambda: state_class.undo_delete(transaction["id"]),
                        class_name="flex items-center px-4 py-2.5 text-sm font-bold text-[#88C0D0] hover:text-[#2E3440] transition-all border border-[#88C0D0]/30 rounded-xl bg-[#88C0D0]/10 hover:bg-gradient-to-r hover:from-[#88C0D0] hover:to-[#81A1C1] hover:border-[#88C0D0] shadow-sm",
                    ),
                    rx.el.button(
                        rx.icon("x", class_name="w-5 h-5"),
                        on_click=lambda: state_class.close_undo_banner(transaction["id"]),
                        class_name="p-2 text-[#D8DEE9] hover:text-[#ECEFF4] transition-colors rounded-xl hover:bg-[#434C5E]",
                    ),
                    class_name="flex items-center gap-2",
                ),
                class_name="flex items-center justify-between gap-12 px-5 py-4",
            ),
            class_name="bg-[#2E3440]/98 backdrop-blur-xl border border-[#434C5E] shadow-2xl rounded-2xl min-w-[360px]",
        ),
        class_name="animate-in fade-in slide-in-from-bottom-8 duration-500 cubic-bezier(0.16, 1, 0.3, 1)",
    )

def undo_banner(state_class) -> rx.Component:
    """A floating container for stacking undo banner items."""
    return rx.el.div(
        rx.foreach(
            state_class.deleted_history,
            lambda t: undo_banner_item(t, state_class)
        ),
        class_name="fixed bottom-10 left-1/2 -translate-x-1/2 z-[100] flex flex-col-reverse gap-3",
    )
