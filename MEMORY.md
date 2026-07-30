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
  picker + HEX + RGB + CMYK, all synchronised), instantiated twice in
  `MainWindow` — once for the foreground colour (`QRG-006`) and once for
  the background colour (`QRG-007`) — each independently validated.
* Changing a colour while a valid URL is already entered live-refreshes
  the preview (FR-042); an invalid/empty URL is silently ignored by that
  live-refresh path rather than surfacing a validation error, so adjusting
  colours before typing a URL does not spam error messages.
* Contrast/colour-safety warnings use the WCAG relative-luminance contrast
  ratio (`colour_service.contrast_ratio`), warning below 4.5:1 (the WCAG
  "AA" text minimum, adopted as a documented baseline — see "Open
  decisions" below for the caveat that a QR-specific threshold has not
  been validated by real scan testing). A second, independent check warns
  if the foreground is lighter than the background, even when contrast is
  otherwise fine (FR-025/FR-026).
* Transparency is not offered anywhere in the current colour model
  (`Colour` has no alpha channel) — this is the deliberate, conservative
  reading of FR-027 for this release: rather than support a transparent
  background that could silently fail to scan, transparency simply is not
  an option yet.
* `services/logo_service.load_logo` validates a candidate logo file by its
  actual decoded Pillow format (`image.format`), never by its file
  extension — confirmed to correctly reject a genuine BMP saved with a
  `.png` extension. It returns an independent in-memory copy and never
  modifies the source file (FR-040).

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
* Both the foreground and background colours are now user-controllable in
  the UI (palette, picker, HEX, RGB, CMYK — `QRG-006`, `QRG-007`), each
  with a live preview refresh and validation errors shown in the status
  label. Verified directly: setting foreground to red and background to
  yellow simultaneously produced a red finder-pattern pixel and a yellow
  quiet-zone pixel in the same rendered image, and an invalid value in one
  control did not affect the other.
* Contrast and colour-safety warnings are implemented (`QRG-008`).
  Verified directly: black-on-white shows no warning; a light-grey
  foreground on white shows a low-contrast warning quoting the actual
  ratio; white-on-black shows a light-on-dark polarity warning even though
  its contrast ratio is high. These are Warnings, not Errors — generation
  is never blocked.
* Logo file selection and validation are implemented (`QRG-009`): a
  "Choose image…"/"Remove" pair in the main window loads and validates a
  PNG/JPEG/JPG file via `logo_service.load_logo`. Verified directly: a
  valid PNG is accepted and its filename/dimensions shown; a corrupt file
  and a BMP disguised with a `.png` extension are both rejected with a
  clear message, leaving any previously-selected valid logo untouched;
  Remove clears the selection. **The selected logo is not yet placed on
  the QR code** — this is `QRG-010`, and the status message says so
  explicitly so as not to imply more than has been built.

**What tests exist:** `tests/test_validation_service.py` (valid HTTP/HTTPS,
empty input, whitespace-only input, unsupported scheme, unusual-but-valid
characters preserved exactly, no warning at/below the 300-character
threshold, warning above it, no network calls made), `tests/test_qr_service.py`
(a PIL image is produced; the exact supplied URL is what gets passed to
Segno), `tests/test_colour_service.py` (HEX/RGB/CMYK parsing and
validation; known-value HEX↔RGB↔CMYK round trips for black, white and pure
red; relative luminance and contrast ratio known values; and contrast/
polarity warning behaviour), and `tests/test_logo_service.py` (valid PNG
and JPEG/JPG loading; missing file, corrupt content, and
extension-spoofed-format rejection; no modification of the source file;
and a genuine in-memory copy). All 41 tests pass.

**What is not yet implemented:** logo placement/compositing onto the QR
code (the logo is validated and stored, but not yet drawn — `QRG-010`);
PNG/SVG export (`export_service.py` is a docstring-only placeholder, no
save dialog exists); any preferences storage; automated QR decoding
tests; any packaging; any CI configuration.

**Current milestone:** Milestone 3 — Central image — under way
(`QRG-009` complete).

**Recommended next backlog item:** `QRG-010` — Implement safe central
logo placement (see `BACKLOG.md`).

## Open decisions

Genuinely unresolved, durable questions:

* Whether to explicitly pass `micro=False` to Segno for defence-in-depth.
  Current behaviour was verified correct (Segno does not select a Micro QR
  Code for representative short or long URL content), but this is not
  structurally guaranteed by the code — only observed.
* The exact logo-size safe default and maximum (`SPECIFICATION.md`
  FR-035/FR-036) — pending real scan testing.
* Whether the 4.5:1 WCAG contrast threshold (`SPECIFICATION.md` FR-024) is
  actually the right bar for QR scan reliability specifically, as opposed
  to text readability — it was adopted as a documented, defensible
  standard in the absence of a QR-specific one, but has not been checked
  against physical scan testing (`QRG-016`).
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
