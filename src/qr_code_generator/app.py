"""Application bootstrap: builds the root Tk window and starts the event loop."""

from __future__ import annotations

import tkinter as tk

from qr_code_generator.ui.main_window import MainWindow


def run() -> None:
    """Create the root window and run the Tkinter main loop until it is closed."""
    root = tk.Tk()
    MainWindow(root)
    root.mainloop()
