"""The main application window.

Contains only widget layout and event wiring. URL validation and QR
generation are delegated to the service layer.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from PIL import ImageTk

from qr_code_generator.models.qr_settings import QRSettings
from qr_code_generator.services.qr_service import generate_qr_image
from qr_code_generator.services.validation_service import (
    URLValidationError,
    get_url_length_warning,
    validate_url,
)

WINDOW_TITLE = "QR Code Generator"
WINDOW_SIZE = "480x600"
WINDOW_MIN_SIZE = (360, 480)


class MainWindow(ttk.Frame):
    """Top-level frame holding the URL entry, generate button and QR preview."""

    def __init__(self, master: tk.Tk) -> None:
        super().__init__(master, padding=16)
        master.title(WINDOW_TITLE)
        master.geometry(WINDOW_SIZE)
        master.minsize(*WINDOW_MIN_SIZE)

        self._qr_photo: ImageTk.PhotoImage | None = None

        self._build_widgets()
        self.pack(fill=tk.BOTH, expand=True)

    def _build_widgets(self) -> None:
        ttk.Label(self, text="URL:").pack(anchor=tk.W)

        self._url_var = tk.StringVar()
        url_entry = ttk.Entry(self, textvariable=self._url_var, width=50)
        url_entry.pack(fill=tk.X, pady=(0, 8))
        url_entry.bind("<Return>", lambda _event: self._on_generate())
        url_entry.focus_set()

        ttk.Button(self, text="Generate", command=self._on_generate).pack(anchor=tk.W, pady=(0, 12))

        preview_frame = ttk.Frame(self, borderwidth=1, relief=tk.SUNKEN)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        self._preview_label = ttk.Label(preview_frame, anchor=tk.CENTER)
        self._preview_label.pack(fill=tk.BOTH, expand=True)

        self._status_var = tk.StringVar(value="Enter a URL and click Generate.")
        ttk.Label(self, textvariable=self._status_var, foreground="#444444").pack(
            anchor=tk.W, fill=tk.X
        )

    def _on_generate(self) -> None:
        try:
            url = validate_url(self._url_var.get())
        except URLValidationError as error:
            self._status_var.set(str(error))
            return

        try:
            image = generate_qr_image(QRSettings(url=url))
        except Exception as error:  # noqa: BLE001 - surfaced to the user, not swallowed
            self._status_var.set(f"Could not generate QR code: {error}")
            return

        self._qr_photo = ImageTk.PhotoImage(image)
        self._preview_label.configure(image=self._qr_photo)

        warning = get_url_length_warning(url)
        if warning:
            self._status_var.set(f"Generated QR code for {url}. {warning}")
        else:
            self._status_var.set(f"Generated QR code for {url}")
