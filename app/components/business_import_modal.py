import reflex as rx
from app.states.business_expense_state import BusinessExpenseState


def business_import_modal() -> rx.Component:
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.portal(
            rx.radix.primitives.dialog.overlay(
                class_name="fixed inset-0 z-50 bg-black/60"
            ),
            rx.radix.primitives.dialog.content(
                rx.radix.primitives.dialog.title(
                    "Import Business Expenses", class_name="text-xl font-bold text-white tracking-tight"
                ),
                rx.radix.primitives.dialog.description(
                    "Upload a JSON file or paste JSON content to import expenses.",
                    class_name="text-sm text-slate-400 mt-1 mb-4",
                ),
                rx.radix.primitives.dialog.close(
                    rx.el.button(
                        rx.icon("x", class_name="w-5 h-5"),
                        class_name="absolute top-4 right-4 p-1 rounded-full text-slate-400 hover:bg-white/10 hover:text-white transition-colors",
                    )
                ),
                rx.el.div(
                    rx.el.h3(
                        "Upload JSON File",
                        class_name="text-md font-semibold text-slate-200 mb-2",
                    ),
                    rx.upload.root(
                        rx.el.div(
                            rx.icon(
                                tag="cloud_upload", class_name="w-8 h-8 text-slate-500"
                            ),
                            rx.el.p("Drag & drop a JSON file here, or click to select", class_name="text-slate-400"),
                            class_name="flex flex-col items-center justify-center p-6 border-2 border-dashed border-slate-700 rounded-lg bg-slate-800/50 hover:bg-slate-800/80 transition-colors",
                        ),
                        id="business_json_upload",
                        accept={"application/json": [".json"]},
                        multiple=False,
                        class_name="w-full mb-4 cursor-pointer",
                    ),
                    rx.el.div(
                        rx.foreach(
                            rx.selected_files("business_json_upload"),
                            lambda file: rx.el.div(
                                file, class_name="text-sm text-slate-300 font-medium my-1"
                            ),
                        )
                    ),
                    rx.el.button(
                        "Process Uploaded File",
                        on_click=BusinessExpenseState.handle_uploaded_file(
                            rx.upload_files(upload_id="business_json_upload")
                        ),
                        class_name="w-full mt-2 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-emerald-500 to-teal-500 rounded-md shadow-[0_0_15px_rgba(16,185,129,0.2)] hover:shadow-[0_0_20px_rgba(16,185,129,0.3)] hover:from-emerald-400 hover:to-teal-400 transition-all disabled:opacity-50",
                        disabled=rx.selected_files("business_json_upload").length() == 0,
                    ),
                    class_name="mb-6",
                ),
                rx.el.div(
                    rx.el.h3(
                        "Paste JSON Content",
                        class_name="text-md font-semibold text-slate-200 mb-2",
                    ),
                    rx.el.textarea(
                        on_change=BusinessExpenseState.set_import_json_text,
                        placeholder='[{"amount": 100.0, "date": "2024-01-01", "memo": "Lunch", "status": "pending"}]',
                        class_name="w-full min-h-[120px] p-2 border border-slate-700 bg-slate-800 text-slate-200 rounded-md text-sm font-mono placeholder:text-slate-600",
                        default_value=BusinessExpenseState.import_json_text,
                    ),
                    rx.el.button(
                        "Validate & Preview",
                        on_click=BusinessExpenseState.validate_and_preview_json,
                        class_name="w-full mt-2 px-4 py-2 text-sm font-medium text-white bg-blue-600/80 rounded-md shadow-sm hover:bg-blue-600 transition-colors",
                    ),
                    class_name="mb-4",
                ),
                rx.el.details(
                    rx.el.summary(
                        "JSON Schema Hint",
                        class_name="text-sm font-semibold text-slate-400 cursor-pointer hover:text-slate-200 transition-colors",
                    ),
                    rx.el.div(
                        rx.el.code(
                            """[
    {
        "amount": 123.45,         // Required
        "date": "YYYY-MM-DD",      // Required
        "memo": "Expense memo",    // Optional
        "status": "pending" | "reimbursed", // Optional (default: pending)
        "account_id": "uuid_string" // Optional
    }
]""",
                            class_name="block whitespace-pre-wrap p-3 bg-slate-900 rounded-md text-xs font-mono text-indigo-300/80",
                        ),
                        class_name="mt-2 p-3 bg-slate-800/50 border border-slate-700 rounded-lg",
                    ),
                    class_name="my-4",
                ),
                rx.cond(
                    BusinessExpenseState.import_error != "",
                    rx.el.div(
                        rx.icon("flag_triangle_right", class_name="w-4 h-4 mr-2"),
                        BusinessExpenseState.import_error,
                        class_name="flex items-center text-sm text-red-600 bg-red-50 p-3 rounded-md my-4",
                    ),
                    None,
                ),
                rx.cond(
                    BusinessExpenseState.import_preview.length() > 0,
                    rx.el.div(
                        rx.el.h4(
                            f"Preview: Found {BusinessExpenseState.import_preview.length()} valid expenses",
                            class_name="text-md font-semibold text-white mb-2",
                        ),
                        rx.el.div(
                            rx.foreach(
                                BusinessExpenseState.import_preview,
                                lambda tx: rx.el.div(
                                    f"${tx['amount']:.2f} on {tx['date']} - {tx['memo']} ({tx['status']})",
                                    class_name="text-xs p-2 bg-white/5 rounded text-slate-300",
                                ),
                            ),
                            class_name="space-y-1 max-h-32 overflow-y-auto p-2 border border-slate-700 rounded-md bg-slate-800/50",
                        ),
                        class_name="my-4",
                    ),
                    None,
                ),
                rx.el.div(
                    rx.radix.primitives.dialog.close(
                        rx.el.button(
                            "Cancel",
                            class_name="px-4 py-2 text-sm font-medium text-slate-300 bg-white/5 border border-white/10 rounded-md shadow-sm hover:bg-white/10 transition-colors",
                        )
                    ),
                    rx.el.button(
                        "Confirm Import",
                        on_click=BusinessExpenseState.confirm_import,
                        disabled=BusinessExpenseState.import_preview.length() == 0,
                        class_name="px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-emerald-500 to-teal-500 rounded-md shadow-[0_0_15px_rgba(16,185,129,0.2)] hover:shadow-[0_0_20px_rgba(16,185,129,0.3)] hover:from-emerald-400 hover:to-teal-400 transition-all disabled:opacity-30",
                    ),
                    class_name="flex justify-end gap-3 pt-4 border-t border-white/10 mt-4",
                ),
                class_name="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-slate-900 border border-white/5 rounded-xl shadow-2xl w-full max-w-lg p-6 z-50 max-h-[85vh] overflow-y-auto text-slate-200",
            ),
        ),
        open=BusinessExpenseState.show_import_modal,
        on_open_change=lambda open_state: rx.cond(
            open_state, rx.noop(), BusinessExpenseState.close_import_modal()
        ),
    )
