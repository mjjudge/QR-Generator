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
from qr_code_generator.services.export_service import (
    DEFAULT_PNG_SIZE_LABEL,
    PNG_SIZE_PRESETS,
    ExportError,
    render_png_for_export,
    save_png,
)
from qr_code_generator.services.logo_service import (
    DEFAULT_LOGO_SIZE_RATIO,
    MAX_LOGO_SIZE_RATIO,
    LogoValidationError,
    apply_logo,
    effective_logo_ratio,
    get_logo_size_warning,
    load_logo,
)
from qr_code_generator.services.qr_service import generate_qr_image
from qr_code_generator.services.validation_service import (
    URLValidationError,
    get_url_length_warning,
    validate_url,
)
from qr_code_generator.ui.colour_control import ColourControl

_LOGO_FILE_TYPES = [("Image files", "*.png *.jpg *.jpeg"), ("All files", "*.*")]
_MIN_LOGO_SIZE_PERCENT = 5
_MAX_LOGO_SIZE_PERCENT = round(MAX_LOGO_SIZE_RATIO * 100)

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
        self._logo_size_ratio: float = DEFAULT_LOGO_SIZE_RATIO

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

        logo_row = ttk.Frame(logo_frame)
        logo_row.pack(fill=tk.X)
        self._logo_filename_var = tk.StringVar(value="No logo selected.")
        ttk.Label(logo_row, textvariable=self._logo_filename_var).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(logo_row, text="Choose image…", command=self._on_choose_logo).pack(side=tk.LEFT)
        ttk.Button(logo_row, text="Remove", command=self._on_remove_logo).pack(
            side=tk.LEFT, padx=(4, 0)
        )

        size_row = ttk.Frame(logo_frame)
        size_row.pack(fill=tk.X, pady=(6, 0))
        ttk.Label(size_row, text="Size:").pack(side=tk.LEFT)
        self._logo_size_var = tk.StringVar(value=f"{round(DEFAULT_LOGO_SIZE_RATIO * 100)}%")
        ttk.Label(size_row, textvariable=self._logo_size_var, width=5).pack(side=tk.LEFT)
        ttk.Scale(
            size_row,
            from_=_MIN_LOGO_SIZE_PERCENT,
            to=_MAX_LOGO_SIZE_PERCENT,
            value=round(DEFAULT_LOGO_SIZE_RATIO * 100),
            command=self._on_logo_size_changed,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))

        ttk.Button(self, text="Generate", command=self._on_generate).pack(anchor=tk.W, pady=(0, 12))

        export_frame = ttk.Frame(self)
        export_frame.pack(fill=tk.X, pady=(0, 12))
        ttk.Label(export_frame, text="Export size:").pack(side=tk.LEFT)
        self._png_size_var = tk.StringVar(value=DEFAULT_PNG_SIZE_LABEL)
        ttk.Combobox(
            export_frame,
            textvariable=self._png_size_var,
            values=list(PNG_SIZE_PRESETS),
            state="readonly",
            width=16,
        ).pack(side=tk.LEFT, padx=(4, 12))
        ttk.Button(export_frame, text="Export PNG…", command=self._on_export_png).pack(side=tk.LEFT)

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

    def _on_logo_size_changed(self, value: str) -> None:
        percent = round(float(value))
        self._logo_size_var.set(f"{percent}%")
        self._logo_size_ratio = percent / 100
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

    def _current_settings(self, url: str) -> QRSettings:
        return QRSettings(
            url=url,
            foreground_colour=self._foreground_colour.to_hex(),
            background_colour=self._background_colour.to_hex(),
        )

    def _on_export_png(self) -> None:
        try:
            url = validate_url(self._url_var.get())
        except URLValidationError as error:
            self._status_var.set(str(error))
            return

        path = filedialog.asksaveasfilename(
            title="Export as PNG",
            defaultextension=".png",
            filetypes=[("PNG image", "*.png")],
            initialfile="qrcode.png",
        )
        if not path:
            return

        try:
            image = render_png_for_export(
                self._current_settings(url),
                self._png_size_var.get(),
                logo=self._logo_image,
                logo_size_ratio=self._logo_size_ratio,
            )
            save_png(image, path)
        except ExportError as error:
            self._status_var.set(f"Could not export PNG: {error}")
            return

        self._status_var.set(f"Exported PNG to {Path(path).name}.")

    def _generate_and_show(self, url: str) -> None:
        settings = self._current_settings(url)
        logo_size_warning = None
        try:
            image = generate_qr_image(settings)
            if self._logo_image is not None:
                logo_size_warning = get_logo_size_warning(
                    effective_logo_ratio(image, self._logo_size_ratio), self._logo_size_ratio
                )
                image = apply_logo(image, self._logo_image, size_ratio=self._logo_size_ratio)
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
                logo_size_warning,
            )
            if warning
        ]
        if warnings:
            self._status_var.set(f"Generated QR code for {url}. " + " ".join(warnings))
        else:
            self._status_var.set(f"Generated QR code for {url}")
