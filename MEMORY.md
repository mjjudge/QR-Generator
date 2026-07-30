# MEMORY.md — Durable Project Memory

This file records durable facts and decisions. It is not a session log or a
chronological diary — see "Editing rules" at the end.

## Project identity

* **Name:** QR Code Generator (package: `qr_code_generator`; repository:
  `QR-Generator`). This naming is already in consistent use (window title,
  package name, `pyproject.toml`) and is treated as decided, not open.
* **Purpose:** a free, local, offline QR code generator for Ubuntu desktops,
  producing permanent static QR codes without relying on subscription-based
  redirect QR services.
* **Intended users:** individuals and small/community groups needing
  occasional QR codes for leaflets, posters, signs, event material, or
  linking documents/websites — not enterprise account management or bulk
  marketing tooling.
* **Licence and commercial model:** MIT-licensed; no monetisation of any
  kind.
* **Platform focus:** offline Ubuntu desktop, using Tkinter/ttk.

## Durable product decisions

* Static QR codes only — no dynamic/redirect-based codes.
* The exact destination URL the user enters is encoded; it is never
  substituted, shortened, redirected or rewritten.
* No hosted redirects, ever.
* HTTP and HTTPS URLs only, for the initial release.
* No accounts, no analytics, no telemetry, no monetisation.
* No network requirement for ordinary use.
* No database.
* URL history is not stored by default.
* Output formats: PNG and SVG.
* Accepted central image formats: PNG, JPEG and JPG.
* QR reliability takes priority over visual appearance whenever the two are
  in tension.
* CMYK input is converted to sRGB approximately in the initial release (no
  ICC profile).
* Professional ICC-profile-based print workflows are out of scope for the
  initial release.
* Trimming leading/trailing whitespace from the entered URL is the one
  permitted, documented "harmless normalisation" — it is not treated as an
  open question; it is already implemented
  (`services/validation_service.py`) and recorded in `SPECIFICATION.md`
  FR-003.
* The long-URL warning threshold is 300 characters (`SPECIFICATION.md`
  FR-006). Above this length, generation still proceeds — it is a
  **Warning**, not an **Error**.

## Durable technical decisions

* Python 3.11 or later.
* Tkinter and ttk for the desktop interface.
* Segno for QR encoding.
* Pillow for image handling.
* pytest for automated tests.
* Ruff for linting (`ruff check`) and formatting (`ruff format`).
* `src` package layout (`src/qr_code_generator/...`).
* Separation of concerns: `ui/` (presentation only), `models/` (typed
  dataclasses shared between layers), `services/` (business logic:
  validation, colour, QR generation, logo, export).
* Ubuntu system dependency: `python3-tk`, installed via `apt`, not pip.
* Editable install workflow: `python3 -m venv .venv`, `pip install -e
  ".[dev]"`.
* PyInstaller remains the intended eventual Ubuntu packaging approach (not
  yet attempted or validated — see `BACKLOG.md` `QRG-019`).
* No CI configuration exists yet (see `BACKLOG.md` `QRG-020`).
* The colour model (`models/colour.py`'s `Colour` dataclass, plus
  `services/colour_service.py`'s HEX/RGB/CMYK parsing and conversion) is
  the single sRGB source of truth that keeps colour entry methods
  synchronised (FR-020).
* The graphical colour picker uses the Python standard library's
  `tkinter.colorchooser` — no additional dependency was needed for FR-016.
* `ui/colour_control.py`'s `ColourControl` is a reusable widget (palette +
  picker + HEX + RGB + CMYK, all synchronised) used for the foreground
  colour (`QRG-006`) and intended to be reused as-is for the background
  colour (`QRG-007`).
* Changing a colour while a valid URL is already entered live-refreshes
  the preview (FR-042); an invalid/empty URL is silently ignored by that
  live-refresh path rather than surfacing a validation error, so adjusting
  colours before typing a URL does not spam error messages.

## QR safety rules

* Use a normal QR code, not a Micro QR code, especially wherever logo
  functionality is involved.
* Use high error correction (level H) whenever a central logo is present.
* Preserve the quiet zone (currently four modules) in both preview and
  export.
* Use integer module scaling; never blur-resize a generated QR image.
* Keep logo sizing conservative; protect the finder patterns from overlap.
* Dark foreground on light background is the default and safest
  relationship.
* Automated decoding tests are required wherever practical; physical
  print-and-scan testing (Android, iPhone, printed leaflet sizes) is
  additionally required before any production-oriented release — automated
  decoding does not substitute for it.

## Repository governance

* `BACKLOG.md` is authoritative for delivery status.
* `SPECIFICATION.md` defines approved, intended requirements (not current
  status).
* `AGENTS.md` defines mandatory contributor/agent behaviour.
* `MEMORY.md` (this file) contains durable facts and decisions only.
* Documentation drift between any of these four files, or between them and
  the actual repository, is treated as a defect.
* Work follows: plan → change → validate → document → report.
* Stable backlog IDs use the `QRG-` prefix and are never reused or
  renumbered.
* One focused backlog item per change is preferred.

## Validated commands

These commands were run directly against this repository and succeeded:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"      # installs segno, Pillow, pytest, ruff
python -m qr_code_generator   # launches the main window
pytest                        # 7 passed
ruff check .                  # all checks passed
ruff format --check .         # all files already formatted
```

Not yet validated: any packaging command (PyInstaller has not been
attempted), any CI workflow (none exists), any QR-decoding test command (no
decoding dependency has been chosen or added yet).

## Definition of Done

A backlog item is **Complete** only when:

* Its stated acceptance criteria are satisfied.
* Relevant tests exist and pass.
* `ruff check` (and `ruff format --check`, since formatting is configured)
  pass.
* User-facing behaviour has been manually validated where relevant.
* Error paths have been considered and handled.
* Documentation (`README.md`, `SPECIFICATION.md`, `BACKLOG.md`, this file)
  matches the implementation.
* Dependencies and `THIRD_PARTY_NOTICES.md` are updated where applicable.
* No unrelated changes are bundled in.
* No known critical defect remains within the item's scope.
* The final diff has been reviewed.
* Any limitations are recorded (in `BACKLOG.md` and/or here).
* Evidence of validation (commands run, results) is available, not just
  asserted.

For QR generation or export changes specifically, also require:

* The decoded result exactly matches the intended URL.
* Quiet zone and finder-pattern protections are preserved.
* Representative output has been scan-tested.
* Logo and colour choices remain within the documented safety rules above.

## Known current state

Verified by direct inspection and by running `pytest`, `ruff check .`,
`ruff format --check .`, and scripted checks against the running
application, as of this document's creation:

**What currently runs and works:**

* `python -m qr_code_generator` opens a Tkinter/ttk window titled "QR Code
  Generator" with a URL field, a Generate button, a preview area and a
  status label.
* Entering a valid `http://` or `https://` URL and clicking Generate (or
  pressing Enter) renders a black-on-white QR code (error-correction level
  H, four-module quiet zone) in the preview, and the status label confirms
  success.
* Empty input and unsupported schemes (verified with `ftp://`) are rejected
  with a clear status message, not a traceback.
* URLs over 300 characters produce a non-blocking warning in the status
  label alongside the success message (verified by scripted check with a
  370-character URL); shorter URLs show no warning.
* `qr_service.generate_qr_image` already accepts arbitrary
  foreground/background colour overrides via `QRSettings` and threads them
  correctly through to the rendered image (verified directly: a custom
  colour pair produced the expected pixel colour).
* The foreground colour is now user-controllable in the UI (palette,
  picker, HEX, RGB, CMYK — see `QRG-006`), with a live preview refresh and
  validation errors shown in the status label. Verified directly: setting
  HEX to `FF0000` and generating produced a pure red pixel at the finder
  pattern in the rendered image. The background colour is not yet
  user-controllable (still fixed at white pending `QRG-007`).

**What tests exist:** `tests/test_validation_service.py` (valid HTTP/HTTPS,
empty input, whitespace-only input, unsupported scheme, unusual-but-valid
characters preserved exactly, no warning at/below the 300-character
threshold, warning above it, no network calls made), `tests/test_qr_service.py`
(a PIL image is produced; the exact supplied URL is what gets passed to
Segno), and `tests/test_colour_service.py` (HEX/RGB/CMYK parsing and
validation, and known-value HEX↔RGB↔CMYK round trips for black, white and
pure red). All 26 tests pass.

**What is not yet implemented:** background colour controls (still fixed
white pending `QRG-007`); contrast/colour-safety warnings (`QRG-008`);
central logo upload and placement (`logo_service.py` is a docstring-only
placeholder); PNG/SVG export (`export_service.py` is a docstring-only
placeholder, no save dialog exists); any preferences storage; automated QR
decoding tests; any packaging; any CI configuration.

**Current milestone:** Milestone 1 complete; Milestone 2 — Colour controls
— under way (`QRG-005`, `QRG-006` complete).

**Recommended next backlog item:** `QRG-007` — Add background colour
controls (see `BACKLOG.md`).

## Open decisions

Genuinely unresolved, durable questions:

* Whether to explicitly pass `micro=False` to Segno for defence-in-depth.
  Current behaviour was verified correct (Segno does not select a Micro QR
  Code for representative short or long URL content), but this is not
  structurally guaranteed by the code — only observed.
* The exact logo-size safe default and maximum (`SPECIFICATION.md`
  FR-035/FR-036) — pending real scan testing.
* Which automated QR-decoding library to use for `QRG-015` (a
  development-only dependency).
* The specific Ubuntu packaging format/tooling detail beyond "PyInstaller is
  the intended default" (e.g. plain PyInstaller bundle vs `.deb` vs
  AppImage).
* Where physical scan-test results (`QRG-016`) should be recorded.
* Whether local, non-sensitive preferences (last export directory, last
  colours, last dimensions) will be included at all — currently only
  **Proposed**, not committed.
* Minimum supported Ubuntu version (not yet specified anywhere).

## Editing rules for MEMORY.md

This file **should** contain: durable decisions, validated commands,
important architectural constraints, current verified state, and the
Definition of Done.

This file **should not** contain: chat transcripts, temporary debugging
notes, personal information, speculation, duplicated backlog detail, or a
chronological activity log. When the "current state" section changes,
overwrite it with the new verified state rather than appending a history of
past states.
