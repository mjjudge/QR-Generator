"""The main application window.

Contains only widget layout and event wiring. URL validation and QR
generation are delegated to the service layer.
"""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

from PIL import Image, ImageTk

from qr_code_generator.models.colour import Colour
from qr_code_generator.models.qr_settings import QRSettings
from qr_code_generator.services.colour_service import (
    DEFAULT_BACKGROUND_COLOUR,
    DEFAULT_FOREGROUND_COLOUR,
    PALETTE,
    get_contrast_warning,
    parse_hex,
)
from qr_code_generator.services.logo_service import LogoValidationError, apply_logo, load_logo
from qr_code_generator.services.qr_service import generate_qr_image
from qr_code_generator.services.validation_service import (
    URLValidationError,
    get_url_length_warning,
    validate_url,
)
from qr_code_generator.ui.colour_control import ColourControl

_LOGO_FILE_TYPES = [("Image files", "*.png *.jpg *.jpeg"), ("All files", "*.*")]

WINDOW_TITLE = "QR Code Generator"
WINDOW_SIZE = "480x760"
WINDOW_MIN_SIZE = (360, 600)


class MainWindow(ttk.Frame):
    """Top-level frame holding the URL entry, generate button and QR preview."""

    def __init__(self, master: tk.Tk) -> None:
        super().__init__(master, padding=16)
        master.title(WINDOW_TITLE)
        master.geometry(WINDOW_SIZE)
        master.minsize(*WINDOW_MIN_SIZE)

        self._qr_photo: ImageTk.PhotoImage | None = None
        self._foreground_colour: Colour = parse_hex(DEFAULT_FOREGROUND_COLOUR)
        self._background_colour: Colour = parse_hex(DEFAULT_BACKGROUND_COLOUR)
        self._logo_image: Image.Image | None = None

        self._build_widgets()
        self.pack(fill=tk.BOTH, expand=True)

    def _build_widgets(self) -> None:
        ttk.Label(self, text="URL:").pack(anchor=tk.W)

        self._url_var = tk.StringVar()
        url_entry = ttk.Entry(self, textvariable=self._url_var, width=50)
        url_entry.pack(fill=tk.X, pady=(0, 8))
        url_entry.bind("<Return>", lambda _event: self._on_generate())
        url_entry.focus_set()

        self._foreground_control = ColourControl(
            self,
            title="Foreground colour",
            initial=self._foreground_colour,
            palette=PALETTE,
            on_change=self._on_foreground_changed,
            on_error=self._show_error,
        )
        self._foreground_control.pack(fill=tk.X, pady=(0, 8))

        self._background_control = ColourControl(
            self,
            title="Background colour",
            initial=self._background_colour,
            palette=PALETTE,
            on_change=self._on_background_changed,
            on_error=self._show_error,
        )
        self._background_control.pack(fill=tk.X, pady=(0, 8))

        logo_frame = ttk.LabelFrame(self, text="Logo (optional)", padding=8)
        logo_frame.pack(fill=tk.X, pady=(0, 8))

        self._logo_filename_var = tk.StringVar(value="No logo selected.")
        ttk.Label(logo_frame, textvariable=self._logo_filename_var).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(logo_frame, text="Choose image…", command=self._on_choose_logo).pack(
            side=tk.LEFT
        )
        ttk.Button(logo_frame, text="Remove", command=self._on_remove_logo).pack(
            side=tk.LEFT, padx=(4, 0)
        )

        ttk.Button(self, text="Generate", command=self._on_generate).pack(anchor=tk.W, pady=(0, 12))

        preview_frame = ttk.Frame(self, borderwidth=1, relief=tk.SUNKEN)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        self._preview_label = ttk.Label(preview_frame, anchor=tk.CENTER)
        self._preview_label.pack(fill=tk.BOTH, expand=True)

        self._status_var = tk.StringVar(value="Enter a URL and click Generate.")
        ttk.Label(self, textvariable=self._status_var, foreground="#444444").pack(
            anchor=tk.W, fill=tk.X
        )

    def _show_error(self, message: str) -> None:
        self._status_var.set(message)

    def _on_foreground_changed(self, colour: Colour) -> None:
        self._foreground_colour = colour
        self._refresh_preview_if_url_valid()

    def _on_background_changed(self, colour: Colour) -> None:
        self._background_colour = colour
        self._refresh_preview_if_url_valid()

    def _on_choose_logo(self) -> None:
        path = filedialog.askopenfilename(
            title="Choose a central image", filetypes=_LOGO_FILE_TYPES
        )
        if path:
            self._apply_logo_path(path)

    def _apply_logo_path(self, path: str) -> None:
        """Load and validate the image at ``path``, updating logo state on success.

        Split out from `_on_choose_logo` so it can be exercised directly
        (e.g. by a scripted check) without going through the native file
        dialog.
        """
        name = Path(path).name
        try:
            image = load_logo(path)
        except LogoValidationError as error:
            self._status_var.set(str(error))
            return
        self._logo_image = image
        self._logo_filename_var.set(f"{name} ({image.width}×{image.height})")
        self._status_var.set(f"Logo '{name}' loaded.")
        self._refresh_preview_if_url_valid()

    def _on_remove_logo(self) -> None:
        self._logo_image = None
        self._logo_filename_var.set("No logo selected.")
        self._status_var.set("Logo removed.")
        self._refresh_preview_if_url_valid()

    def _refresh_preview_if_url_valid(self) -> None:
        """Re-render the preview after a setting change (FR-042), without
        showing a validation error for a URL the user has not finished typing.
        """
        try:
            url = validate_url(self._url_var.get())
        except URLValidationError:
            return
        self._generate_and_show(url)

    def _on_generate(self) -> None:
        try:
            url = validate_url(self._url_var.get())
        except URLValidationError as error:
            self._status_var.set(str(error))
            return
        self._generate_and_show(url)

    def _generate_and_show(self, url: str) -> None:
        settings = QRSettings(
            url=url,
            foreground_colour=self._foreground_colour.to_hex(),
            background_colour=self._background_colour.to_hex(),
        )
        try:
            image = generate_qr_image(settings)
            if self._logo_image is not None:
                image = apply_logo(image, self._logo_image)
        except Exception as error:  # noqa: BLE001 - surfaced to the user, not swallowed
            self._status_var.set(f"Could not generate QR code: {error}")
            return

        self._qr_photo = ImageTk.PhotoImage(image)
        self._preview_label.configure(image=self._qr_photo)

        warnings = [
            warning
            for warning in (
                get_url_length_warning(url),
                get_contrast_warning(self._foreground_colour, self._background_colour),
            )
            if warning
        ]
        if warnings:
            self._status_var.set(f"Generated QR code for {url}. " + " ".join(warnings))
        else:
            self._status_var.set(f"Generated QR code for {url}")
