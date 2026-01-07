import reflex as rx
from app.states.transaction_state import Transaction, TransactionState


def import_modal() -> rx.Component:
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.portal(
            rx.radix.primitives.dialog.overlay(
                class_name="fixed inset-0 z-50 bg-black/60"
            ),
            rx.radix.primitives.dialog.content(
                rx.radix.primitives.dialog.title(
                    "Import Transactions", class_name="text-xl font-bold text-[#ECEFF4]"
                ),
                rx.radix.primitives.dialog.description(
                    "Upload a JSON file or paste JSON content to import transactions.",
                    class_name="text-sm text-[#D8DEE9] mt-1 mb-4",
                ),
                rx.radix.primitives.dialog.close(
                    rx.el.button(
                        rx.icon("x", class_name="w-5 h-5"),
                        class_name="absolute top-4 right-4 p-1 rounded-full text-[#D8DEE9] hover:bg-[#434C5E] hover:text-[#ECEFF4]",
                    )
                ),
                rx.el.div(
                    rx.el.h3(
                        "Upload JSON File",
                        class_name="text-md font-semibold text-[#ECEFF4] mb-2",
                    ),
                    rx.upload.root(
                        rx.el.div(
                            rx.icon(
                                tag="cloud_upload", class_name="w-8 h-8 text-[#81A1C1]"
                            ),
                            rx.el.p("Drag & drop a JSON file here, or click to select", class_name="text-[#D8DEE9]"),
                            class_name="flex flex-col items-center justify-center p-6 border-2 border-dashed border-[#434C5E] rounded-lg bg-[#3B4252] hover:bg-[#434C5E] transition-colors",
                        ),
                        id="json_upload",
                        accept={"application/json": [".json"]},
                        multiple=False,
                        class_name="w-full mb-4 cursor-pointer",
                    ),
                    rx.el.div(
                        rx.foreach(
                            rx.selected_files("json_upload"),
                            lambda file: rx.el.div(
                                file, class_name="text-sm text-[#88C0D0] font-medium"
                            ),
                        )
                    ),
                    rx.el.button(
                        "Process Uploaded File",
                        on_click=TransactionState.handle_uploaded_file(
                            rx.upload_files(upload_id="json_upload")
                        ),
                        class_name="w-full mt-2 px-4 py-2 text-sm font-medium text-[#2E3440] bg-[#88C0D0] rounded-md shadow-sm hover:bg-[#81A1C1] disabled:opacity-50",
                        disabled=rx.selected_files("json_upload").length() == 0,
                    ),
                    class_name="mb-6",
                ),
                rx.el.div(
                    rx.el.h3(
                        "Paste JSON Content",
                        class_name="text-md font-semibold text-[#ECEFF4] mb-2",
                    ),
                    rx.el.textarea(
                        on_change=TransactionState.set_import_json_text,
                        placeholder='[{"type": "income", "amount": 100.0, "date": "2024-01-01"}]',
                        class_name="w-full min-h-[120px] p-2 border border-[#434C5E] bg-[#3B4252] text-[#ECEFF4] rounded-md text-sm font-mono placeholder-[#4C566A]",
                        default_value=TransactionState.import_json_text,
                    ),
                    rx.el.button(
                        "Validate & Preview",
                        on_click=TransactionState.validate_and_preview_json,
                        class_name="w-full mt-2 px-4 py-2 text-sm font-medium text-[#ECEFF4] bg-[#5E81AC] rounded-md shadow-sm hover:bg-[#81A1C1]",
                    ),
                    class_name="mb-4",
                ),
                rx.el.details(
                    rx.el.summary(
                        "JSON Schema Hint",
                        class_name="text-sm font-semibold text-[#88C0D0] cursor-pointer hover:text-[#81A1C1]",
                    ),
                    rx.el.div(
                        rx.el.code(
                            """[
    {
        "type": "income" | "maaser", // Required
        "amount": 123.45,         // Required
        "date": "YYYY-MM-DD",      // Required
        "memo": "Transaction memo",  // Optional
        "account_id": "uuid_string" // Optional (for bank accounts)
    }
]""",
                            class_name="block whitespace-pre-wrap p-3 bg-[#2E3440] rounded-md text-xs font-mono text-[#D8DEE9]",
                        ),
                        class_name="mt-2 p-3 bg-[#3B4252] border border-[#434C5E] rounded-lg",
                    ),
                    class_name="my-4",
                ),
                rx.cond(
                    TransactionState.import_error != "",
                    rx.el.div(
                        rx.icon("flag_triangle_right", class_name="w-4 h-4 mr-2"),
                        TransactionState.import_error,
                        class_name="flex items-center text-sm text-[#BF616A] bg-[#BF616A]/10 p-3 rounded-md my-4",
                    ),
                    None,
                ),
                rx.cond(
                    TransactionState.import_preview.length() > 0,
                    rx.el.div(
                        rx.el.h4(
                            f"Preview: Found {TransactionState.import_preview.length()} valid transactions",
                            class_name="text-md font-semibold text-[#ECEFF4] mb-2",
                        ),
                        rx.el.div(
                            rx.foreach(
                                TransactionState.import_preview,
                                lambda tx: rx.el.div(
                                    f"{tx['type'].capitalize()}: ${tx['amount']:.2f} on {tx['date']} - {tx['memo']}",
                                    class_name="text-xs p-2 bg-[#2E3440] rounded text-[#D8DEE9] border border-[#434C5E]",
                                ),
                            ),
                            class_name="space-y-1 max-h-32 overflow-y-auto p-2 border border-[#434C5E] rounded-md bg-[#3B4252]",
                        ),
                        class_name="my-4",
                    ),
                    None,
                ),
                rx.el.div(
                    rx.radix.primitives.dialog.close(
                        rx.el.button(
                            "Cancel",
                            class_name="px-4 py-2 text-sm font-medium text-[#D8DEE9] bg-[#3B4252] border border-[#434C5E] rounded-md shadow-sm hover:bg-[#434C5E]/80",
                        )
                    ),
                    rx.el.button(
                        "Confirm Import",
                        on_click=TransactionState.confirm_import,
                        disabled=TransactionState.import_preview.length() == 0,
                        class_name="px-4 py-2 text-sm font-medium text-[#2E3440] bg-[#A3BE8C] rounded-md shadow-sm hover:bg-[#A3BE8C]/90 disabled:bg-[#4C566A]",
                    ),
                    class_name="flex justify-end gap-3 pt-4 border-t border-[#434C5E] mt-4",
                ),
                class_name="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 glass-card rounded-xl shadow-xl w-full max-w-lg p-6 z-50 max-h-[85vh] overflow-y-auto",
            ),
        ),
        open=TransactionState.show_import_modal,
        on_open_change=lambda open_state: rx.cond(
            open_state, rx.noop(), TransactionState.close_import_modal()
        ),
    )