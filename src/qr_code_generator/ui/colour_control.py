"""A synchronised palette/picker/HEX/RGB/CMYK colour input widget.

All entry methods construct the same :class:`~qr_code_generator.models.colour.Colour`,
which is what keeps them synchronised (SPECIFICATION.md FR-020): changing
any one representation updates every other one to match.
"""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable, Sequence
from tkinter import colorchooser, ttk

from qr_code_generator.models.colour import Colour
from qr_code_generator.services.colour_service import (
    ColourValidationError,
    parse_cmyk,
    parse_hex,
    parse_rgb,
    to_cmyk,
)


class ColourControl(ttk.LabelFrame):
    """A labelled frame offering palette, picker, HEX, RGB and CMYK colour entry."""

    def __init__(
        self,
        master: tk.Misc,
        *,
        title: str,
        initial: Colour,
        palette: Sequence[Colour],
        on_change: Callable[[Colour], None],
        on_error: Callable[[str], None],
    ) -> None:
        super().__init__(master, text=title, padding=8)
        self._on_change = on_change
        self._on_error = on_error
        self._colour = initial

        self._build_widgets(palette)
        self.set_colour(initial, notify=False)

    @property
    def colour(self) -> Colour:
        """The currently selected colour."""
        return self._colour

    def set_colour(self, colour: Colour, *, notify: bool = True) -> None:
        """Update every displayed representation to match ``colour``."""
        self._colour = colour
        self._swatch.configure(background=colour.to_hex())
        self._hex_var.set(colour.to_hex())
        for var, value in zip(self._rgb_vars, (colour.red, colour.green, colour.blue), strict=True):
            var.set(str(value))
        for var, value in zip(self._cmyk_vars, to_cmyk(colour), strict=True):
            var.set(f"{value:g}")
        if notify:
            self._on_change(colour)

    def _build_widgets(self, palette: Sequence[Colour]) -> None:
        palette_row = ttk.Frame(self)
        palette_row.pack(fill=tk.X, pady=(0, 6))

        self._swatch = tk.Label(palette_row, width=3, relief=tk.SUNKEN, borderwidth=1)
        self._swatch.pack(side=tk.LEFT, padx=(0, 8))

        for swatch_colour in palette:
            swatch = tk.Label(
                palette_row,
                width=2,
                relief=tk.RAISED,
                borderwidth=1,
                background=swatch_colour.to_hex(),
                cursor="hand2",
                takefocus=True,
                highlightthickness=2,
            )
            swatch.pack(side=tk.LEFT, padx=1)
            swatch.bind("<Button-1>", lambda _event, c=swatch_colour: self.set_colour(c))
            swatch.bind("<Return>", lambda _event, c=swatch_colour: self.set_colour(c))
            swatch.bind("<space>", lambda _event, c=swatch_colour: self.set_colour(c))

        ttk.Button(palette_row, text="Pick…", command=self._open_picker).pack(
            side=tk.LEFT, padx=(8, 0)
        )

        hex_row = ttk.Frame(self)
        hex_row.pack(fill=tk.X, pady=(0, 4))
        ttk.Label(hex_row, text="HEX:").pack(side=tk.LEFT)
        self._hex_var = tk.StringVar()
        hex_entry = ttk.Entry(hex_row, textvariable=self._hex_var, width=9)
        hex_entry.pack(side=tk.LEFT, padx=(4, 0))
        hex_entry.bind("<Return>", lambda _event: self._apply_hex())
        hex_entry.bind("<FocusOut>", lambda _event: self._apply_hex())

        rgb_row = ttk.Frame(self)
        rgb_row.pack(fill=tk.X, pady=(0, 4))
        self._rgb_vars = [tk.StringVar() for _ in range(3)]
        for label, var in zip(("R:", "G:", "B:"), self._rgb_vars, strict=True):
            ttk.Label(rgb_row, text=label).pack(side=tk.LEFT)
            entry = ttk.Entry(rgb_row, textvariable=var, width=4)
            entry.pack(side=tk.LEFT, padx=(2, 6))
            entry.bind("<Return>", lambda _event: self._apply_rgb())
            entry.bind("<FocusOut>", lambda _event: self._apply_rgb())

        cmyk_row = ttk.Frame(self)
        cmyk_row.pack(fill=tk.X)
        self._cmyk_vars = [tk.StringVar() for _ in range(4)]
        for label, var in zip(("C:", "M:", "Y:", "K:"), self._cmyk_vars, strict=True):
            ttk.Label(cmyk_row, text=label).pack(side=tk.LEFT)
            entry = ttk.Entry(cmyk_row, textvariable=var, width=4)
            entry.pack(side=tk.LEFT, padx=(2, 6))
            entry.bind("<Return>", lambda _event: self._apply_cmyk())
            entry.bind("<FocusOut>", lambda _event: self._apply_cmyk())

    def _open_picker(self) -> None:
        _rgb, hex_colour = colorchooser.askcolor(
            color=self._colour.to_hex(), title="Choose a colour"
        )
        if hex_colour:
            self.set_colour(parse_hex(hex_colour))

    def _apply_hex(self) -> None:
        try:
            colour = parse_hex(self._hex_var.get())
        except ColourValidationError as error:
            self._on_error(str(error))
            return
        self.set_colour(colour)

    def _apply_rgb(self) -> None:
        try:
            red, green, blue = (int(var.get()) for var in self._rgb_vars)
        except ValueError:
            self._on_error("RGB values must be whole numbers between 0 and 255.")
            return
        try:
            colour = parse_rgb(red, green, blue)
        except ColourValidationError as error:
            self._on_error(str(error))
            return
        self.set_colour(colour)

    def _apply_cmyk(self) -> None:
        try:
            cyan, magenta, yellow, key = (float(var.get()) for var in self._cmyk_vars)
        except ValueError:
            self._on_error("CMYK values must be numbers between 0 and 100.")
            return
        try:
            colour = parse_cmyk(cyan, magenta, yellow, key)
        except ColourValidationError as error:
            self._on_error(str(error))
            return
        self.set_colour(colour)
