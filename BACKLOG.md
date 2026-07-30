# QR Code Generator — Backlog

This is the authoritative record of delivery status for this project. If
this file disagrees with the actual repository, the repository is right and
this file is out of date — treat that as a defect to fix immediately.

## Status definitions

* **Proposed** — an idea, not yet planned in detail or committed to a
  milestone.
* **Ready** — scoped clearly enough to start; not yet begun.
* **In Progress** — actively being worked on; not all acceptance criteria
  are met yet.
* **Blocked** — work cannot continue until a stated dependency or decision
  is resolved.
* **Complete** — all acceptance criteria, validation and documentation
  requirements below are satisfied, with evidence.
* **Deferred** — deliberately not being pursued now; may be reconsidered
  later.

**Rules:**

* Existing code alone is not evidence of completion. Tests passing, manual
  validation, and accurate documentation are all required.
* Documentation drift (this file, `SPECIFICATION.md`, `AGENTS.md` or
  `MEMORY.md` disagreeing with the repository or each other) is a defect.
* Every backlog item has a stable ID in the form `QRG-NNN`. IDs are never
  reused or renumbered.
* Status changes must be evidence-based — cite what was run or checked.
* One focused backlog item per change is preferred.

---

## Current state (evidence-based, as of this document's creation)

* **Current milestone:** Milestone 5 — Scannability and quality — under
  way (`QRG-015`, `QRG-017` complete; `QRG-016` partial, needs a human
  with real hardware).
* **Recommended next item:** `QRG-018` — Harden error handling (the last
  agent-completable item in this milestone).
* **Evidence used to set statuses below:** full read-through of every file
  in `src/`, `tests/`, `pyproject.toml`, `README.md`, `LICENSE`, and
  `THIRD_PARTY_NOTICES.md`; `pytest -q` (81 passed); `ruff check .` (all
  checks passed); `ruff format --check .` (all files formatted);
  scripted Tkinter smoke tests exercising valid, empty, unsupported-scheme
  and long-URL input, foreground and background colour synchronisation,
  validation and live preview refresh, contrast/polarity warnings, logo
  selection/rejection/removal, logo placement and size adjustment with a
  live decoding check, both PNG and SVG export (no-URL validation, a
  plain export, a logo-bearing export, and dialog cancellation), and
  distinct default filenames suggested for distinct URLs; direct
  pixel/byte-level/XML-structure checks confirming chosen colours render
  correctly, logo files are never modified on disk, finder-pattern pixels
  are never touched, exported PNGs reopen and decode to the exact URL,
  and exported SVGs are well-formed with untouched vector modules;
  outside the test suite, a real user-requested QR code (Rotary blue on
  white, with a transparent-PNG club logo) was generated through the
  actual export pipeline and confirmed to decode correctly from the
  saved file, at two different logo sizes, and confirmed by the user to
  scan correctly on an iPhone from a screen; and a keyboard-accessibility
  audit (a full 38-stop tab-order walk, synthetic-keyboard activation of
  the previously mouse-only palette swatches, and a 1.8x font-scale
  robustness check).

---

## Milestone 1 — Foundation and basic generation

### QRG-001 — Establish project governance and specification

* **Status:** Complete.
* **Objective:** Create and align `SPECIFICATION.md`, `BACKLOG.md`,
  `AGENTS.md` and `MEMORY.md`.
* **Acceptance criteria:**
  * All four files exist. ✅
  * The documents agree with one another and with the actual repository
    state. ✅ (cross-checked at the end of this task — see `MEMORY.md`
    "Repository governance").
  * Scope and exclusions are explicit (see `SPECIFICATION.md` §15). ✅
  * Stable backlog IDs and statuses are defined (this file). ✅
  * Agent workflow and Definition of Done are defined (`AGENTS.md`,
    `MEMORY.md`). ✅
  * Current implementation status is evidence-based, not assumed. ✅
* **Validation:** All four documents read end-to-end after creation to
  check terminology, scope and status consistency; no contradictions found
  requiring correction beyond normal drafting.
* **Documentation impact:** This task *is* the documentation.

### QRG-002 — Establish application scaffold

* **Status:** Complete.
* **Objective:** A clean, runnable Python project skeleton.
* **Acceptance criteria:**
  * `src/qr_code_generator/` package layout with `__init__.py`,
    `__main__.py`, `app.py`, `ui/`, `models/`, `services/`. ✅
  * Entry point: `python -m qr_code_generator` and a `qr-code-generator`
    console script. ✅
  * A Tkinter/ttk main window titled "QR Code Generator" opens. ✅
    (verified by a scripted smoke test constructing `MainWindow` and
    exercising it without a full interactive session.)
  * Runtime dependencies (Segno, Pillow) and dev dependencies (pytest,
    Ruff) declared in `pyproject.toml`. ✅
  * `pytest` and `ruff` configuration present in `pyproject.toml`. ✅
  * `README.md` accurately describes current functionality and
    limitations. ✅
  * MIT `LICENSE` present. ✅
  * `THIRD_PARTY_NOTICES.md` present, naming Segno and Pillow. ✅
* **Validation:** `pytest -q` → 7 passed. `ruff check .` → all checks
  passed. `ruff format --check .` → 17 files already formatted.
* **Known limitation:** No continuous integration exists yet (see
  `QRG-020`); no packaging exists yet (see `QRG-019`).

### QRG-003 — Generate a basic static URL QR code

* **Status:** Complete.
* **Objective:** A minimal end-to-end vertical slice: enter a URL, generate
  and preview a black-on-white QR code.
* **Acceptance criteria:**
  * HTTP and HTTPS validation via `validation_service.validate_url`. ✅
  * The exact supplied URL is encoded — confirmed by
    `tests/test_qr_service.py::test_uses_the_url_supplied_in_settings`,
    which asserts the content passed into Segno matches the input exactly.
    ✅
  * Segno generation via `services/qr_service.py`, using error-correction
    level H and a four-module quiet zone. ✅
  * Preview shown in the main window on successful generation. ✅
  * Ordinary invalid input (empty URL, unsupported scheme) is handled via
    the status label, not an unhandled traceback. ✅ (verified by scripted
    smoke test.)
  * Tests exist and pass for both the validation and QR-generation
    services. ✅
* **Validation:** `pytest -q` (7 passed, including the two QR-service
  tests); a direct interactive check confirming `segno.make` does not
  select a Micro QR Code for representative short and long URLs (`is_micro`
  is `False` in both cases tested).
* **Known limitation:** `qr_service.py` does not explicitly pass
  `micro=False` to Segno; it relies on Segno's automatic selection, which
  was verified *not* to choose Micro QR for URL-shaped content in the cases
  tested, but this is not structurally guaranteed by the code. Recorded as
  an open decision in `MEMORY.md` — a candidate for explicit hardening
  under `QRG-004` or a small follow-up, not currently a defect.

### QRG-004 — Strengthen URL validation

* **Status:** Complete.
* **Objective:** Make URL validation robust and complete against
  `SPECIFICATION.md` §5 "URL input".
* **Acceptance criteria:**
  * ~~Reject empty input.~~ Satisfied (`QRG-003`).
  * ~~Reject unsupported schemes.~~ Satisfied (`QRG-003`).
  * Whitespace-trimming documented as the only permitted normalisation
    (FR-003). ✅ (`services/validation_service.py`, `MEMORY.md`.)
  * Warn about unusually long URLs (FR-006), threshold 300 characters,
    surfaced via `services/validation_service.get_url_length_warning` and
    shown in the status label without blocking generation. ✅
  * Explicit confirmation that no network access occurs during validation
    — asserted by `test_validate_url_makes_no_network_calls`, which blocks
    `socket.socket` and confirms `validate_url` never calls it. ✅
  * Additional edge-case tests: unusual-but-valid characters (query string,
    fragment, percent-encoding), and boundary tests exactly at and just
    above the 300-character threshold. ✅
* **Validation:** `pytest -q` → 11 passed (4 new: preserves unusual
  characters, no warning at/below threshold, warning above threshold,
  no-network-calls). `ruff check .` and `ruff format --check .` → both
  clean. A scripted Tkinter check confirmed a 370-character URL produces
  both a successful QR code and the expected warning text in the status
  label, and a normal-length URL produces no warning.
* **Documentation impact:** `SPECIFICATION.md` FR-006 updated with the
  300-character threshold; `MEMORY.md` "Open decisions" and "Durable
  product decisions" updated accordingly.

---

## Milestone 2 — Colour controls

### QRG-005 — Implement the internal colour model

* **Status:** Complete.
* **Objective:** A colour model supporting HEX, RGB and CMYK input, stored
  internally as sRGB, with conversion and validation.
* **Acceptance criteria:**
  * HEX ↔ RGB ↔ CMYK conversion functions, with sRGB as the internal
    representation (FR-021, FR-022). ✅ `models/colour.py` (the `Colour`
    dataclass, sRGB channels) and `services/colour_service.py`
    (`parse_hex`, `parse_rgb`, `parse_cmyk`, `to_cmyk`).
  * Validation of each input form with understandable errors (FR-023). ✅
    `ColourValidationError`, raised with a specific message for malformed
    HEX, out-of-range RGB channels, and out-of-range CMYK components.
  * A single synchronisation rule so changing one representation updates
    the others consistently (FR-020). ✅ All three input forms construct
    the same `Colour` type, which is the single source of truth;
    `test_hex_and_rgb_stay_synchronised_via_the_same_colour` confirms HEX
    and RGB entry for the same colour compare equal.
  * Unit tests for conversion correctness and validation edge cases. ✅
    `tests/test_colour_service.py` (15 tests): HEX parsing (with/without
    `#`, wrong length, non-hex characters), RGB validation (in range,
    out of range, negative), CMYK validation (out of range), and known-value
    round trips for black, white and pure red in both directions.
* **Validation:** `pytest -q` → 26 passed (15 new). `ruff check .` and
  `ruff format --check .` → both clean.
* **Known limitation:** No UI exposes this yet (see `QRG-006`/`QRG-007`);
  `qr_service.py`/`QRSettings` still take plain HEX strings directly, which
  continues to work unchanged — this item deliberately did not touch that
  already-complete, already-tested path.
* **Documentation impact:** None beyond this entry and `MEMORY.md`
  "Durable technical decisions".

### QRG-006 — Add foreground colour controls

* **Status:** Complete.
* **Objective:** UI controls for foreground colour selection.
* **Acceptance criteria:**
  * Palette, graphical picker, HEX, RGB and CMYK entry, all synchronised
    (FR-015–FR-020). ✅ `ui/colour_control.py`'s `ColourControl` widget:
    a six-swatch palette, a native Tk colour picker (`tkinter.colorchooser`,
    standard library — no new dependency), and HEX/RGB/CMYK entry fields.
    Every entry method constructs a `Colour` via `colour_service`, and
    `set_colour()` re-populates every other representation from it, so they
    cannot drift apart.
  * Selected colour feeds into `QRSettings.foreground_colour` (via
    `MainWindow._generate_and_show`) and is reflected in the preview,
    including a **live refresh**: changing colour while a valid URL is
    already entered regenerates the preview immediately (FR-042), without
    showing a validation error if the URL field is currently empty/invalid
    (`MainWindow._refresh_preview_if_url_valid`).
  * Invalid values show a validation error (FR-023) via the shared status
    label, and the colour is left unchanged (the user's typed text is not
    silently discarded or replaced). ✅
* **Validation:** `pytest -q` → 26 passed (unchanged — no new pure-logic
  tests were needed as `colour_service` was already fully tested in
  `QRG-005`; the new code here is UI wiring). `ruff check .` and
  `ruff format --check .` → both clean. A scripted Tkinter smoke test
  verified: HEX entry synchronises RGB/CMYK fields correctly; RGB entry
  synchronises HEX; invalid HEX/RGB/CMYK each produce a specific error
  message and leave the colour unchanged; a direct pixel check confirmed a
  chosen colour (red) actually renders in the generated QR image, not only
  in widget state.
* **Known limitation:** As with `QRG-002`/`QRG-003`, UI wiring is validated
  by scripted smoke test rather than an automated `pytest` UI test, since
  `pytest` should remain runnable in headless environments that lack a
  display — this mirrors the precedent set for the original vertical
  slice, not a new gap specific to this item.
* **Documentation impact:** `SPECIFICATION.md` FR-015–FR-020, FR-023 and
  FR-042 move from "target" to "implemented (foreground only)" — see
  `MEMORY.md`.

### QRG-007 — Add background colour controls

* **Status:** Complete.
* **Objective:** UI controls for background colour selection.
* **Acceptance criteria:** Equivalent to `QRG-006`, applied to
  `QRSettings.background_colour`. ✅ A second `ColourControl` instance
  (`MainWindow._background_control`) reuses the same widget built for
  `QRG-006`; `_on_background_changed` updates `self._background_colour`
  and triggers the same live-refresh path. `_generate_and_show` now passes
  `self._background_colour.to_hex()` instead of the fixed
  `DEFAULT_BACKGROUND_COLOUR` constant.
* **Validation:** `pytest -q` → 26 passed (unchanged; this item is UI
  wiring reusing already-tested `colour_service`/`ColourControl` code, as
  anticipated when `ColourControl` was built as a reusable widget in
  `QRG-006`). `ruff check .` and `ruff format --check .` → both clean. A
  scripted Tkinter smoke test set foreground to red and background to
  yellow simultaneously and confirmed both colours render correctly and
  independently in the generated image (a red finder-pattern pixel, a
  yellow quiet-zone pixel), and confirmed invalid input in one control
  (background RGB `999`) produces a clear error without altering either
  control's colour.
* **Documentation impact:** None beyond this entry and `MEMORY.md`.

### QRG-008 — Add contrast and colour safety validation

* **Status:** Complete.
* **Objective:** Warn when foreground/background contrast is likely to harm
  scan reliability.
* **Acceptance criteria:**
  * A documented contrast calculation (FR-024). ✅
    `colour_service.relative_luminance`/`contrast_ratio` implement the
    standard WCAG relative-luminance formula; `CONTRAST_WARNING_THRESHOLD
    = 4.5` (the WCAG "AA" text minimum, adopted as a documented baseline
    in the absence of a QR-specific standard — see `SPECIFICATION.md`
    FR-024).
  * Dark-on-light preferred as the safe default; deviating combinations
    are flagged (FR-025, FR-026). ✅ `get_contrast_warning` independently
    checks contrast ratio and foreground/background luminance ordering,
    warning if the foreground is lighter than the background even when
    contrast is otherwise acceptable (e.g. white-on-black).
  * A defined, conservative policy for transparent backgrounds (FR-027).
    ✅ `Colour` has no alpha channel and no UI offers a transparent
    background — transparency is not offered at all in this release,
    which conservatively avoids the risk FR-027 describes rather than
    attempting to manage it.
  * Unit tests for the contrast calculation and threshold behaviour. ✅
    7 new tests in `tests/test_colour_service.py`: known luminance values
    for black/white, the standard 21:1 black/white contrast ratio,
    order-independence, no warning for black-on-white, a warning for a
    low-contrast pair, and a warning for light-on-dark polarity even
    though its contrast ratio passes.
* **Validation:** `pytest -q` → 33 passed (7 new). `ruff check .` and
  `ruff format --check .` → both clean. A scripted Tkinter smoke test
  confirmed: default black/white shows no warning; light grey (#DCDCDC)
  foreground on white background shows the low-contrast warning with the
  actual computed ratio (1.4:1); white-on-black shows the polarity warning
  without the low-contrast warning (since 21:1 comfortably passes).
* **Documentation impact:** `SPECIFICATION.md` FR-024 updated with the
  4.5:1 threshold; `colour_service.py`'s module docstring updated to state
  the transparency policy explicitly.

---

## Milestone 3 — Central image

### QRG-009 — Add logo file selection and validation

* **Status:** Complete.
* **Objective:** Let the user choose, validate, and clear a central image.
* **Acceptance criteria:**
  * Accept PNG, JPEG, JPG (FR-028). ✅ `services/logo_service.load_logo`
    accepts any file Pillow decodes as PNG or JPEG (both `.jpg` and
    `.jpeg` decode as Pillow format "JPEG").
  * Reject unsupported/corrupt files cleanly, without relying on file
    extension alone (FR-029, NFR-008). ✅ Validation checks the actual
    decoded `image.format`, not the filename — a genuine BMP saved with a
    misleading `.png` extension is correctly rejected
    (`test_rejects_unsupported_format_even_with_a_png_extension`); a
    corrupt/non-image file raises a clear `LogoValidationError` rather
    than propagating a raw Pillow exception.
  * Support removing/replacing the selected logo. ✅ "Choose image…" and
    "Remove" buttons in `MainWindow`; choosing a new file after a
    previous failed/successful selection is a plain replace.
  * Never modify the user's source file (FR-040). ✅
    `test_does_not_modify_the_source_file` compares the file's raw bytes
    before/after loading; `load_logo` returns an independent in-memory
    `.copy()`, confirmed by
    `test_returns_an_independent_in_memory_copy` (the source file is
    deleted after loading, and the returned image is still usable).
* **Validation:** `pytest -q` → 41 passed (8 new, in
  `tests/test_logo_service.py`). `ruff check .` and `ruff format --check .`
  → both clean. A scripted Tkinter smoke test exercised: a valid PNG
  (accepted, filename/dimensions shown); a corrupt file (clear error,
  previous valid logo state left untouched); a BMP disguised with a
  `.png` extension (rejected by content); and Remove (clears state back
  to "No logo selected").
* **Known limitation:** Selecting a logo only validates and stores it —
  it is **not** yet drawn on the QR preview or included in generation.
  The status message says so explicitly
  ("Placing it on the QR code is not yet supported.") to avoid implying
  more than this item delivers. Placement is `QRG-010`.
* **Documentation impact:** None beyond this entry and `MEMORY.md`.

### QRG-010 — Implement safe central logo placement

* **Status:** Complete.
* **Objective:** Composite a validated logo onto the QR code safely.
* **Acceptance criteria:**
  * Aspect ratio preserved (FR-030, FR-039). ✅ `logo_service.apply_logo`
    uses `PIL.ImageOps.contain`, which fits the logo within its bounding
    box without stretching; verified by
    `test_apply_logo_preserves_overall_image_size` with a deliberately
    wide (200×50) logo.
  * Conservative default size and enforced safe maximum (FR-035, FR-036).
    ✅ `DEFAULT_LOGO_SIZE_RATIO = 0.18` (18% of QR width);
    `MAX_LOGO_SIZE_RATIO = 0.30` (30%, chosen to stay well under
    error-correction level H's ~30% correctable-codeword budget, per
    FR-038 — high error correction is not a blank cheque). The effective
    footprint is `min(requested, MAX_LOGO_SIZE_RATIO,
    max_safe_logo_ratio(...))` — see the next bullet for the third term.
  * No overlap with finder patterns (FR-034). ✅ `max_safe_logo_ratio`
    computes, from the QR image's own pixel dimensions, the largest
    centred square guaranteed clear of all three (corner-only) finder
    patterns, **for that specific QR code**. Derivation: the three
    finder patterns are always exactly 7×7 modules, in the three corners,
    for every QR version (ISO/IEC 18004). A centred square footprint of
    `S` modules, in an image of `module_count + 2*border` modules per
    side, avoids all three exactly when
    `S <= module_count - 2*7 + 1` (one module of margin included). This
    holds regardless of QR version — only the resulting safe *fraction*
    grows as the code gets bigger. Verified against the known worst case
    (a synthetic version-1-sized image, 21 modules) in
    `test_max_safe_logo_ratio_matches_known_derivation`, and directly
    against a real generated QR code in
    `test_apply_logo_does_not_touch_finder_pattern_pixels`, which asserts
    the composited result is pixel-for-pixel identical to the
    pre-logo image at all three finder-pattern centres.
  * Centred placement with a background clearance panel (FR-032, FR-033).
    ✅ A square panel, filled with the QR's own background colour (sampled
    from a known-background pixel, not hardcoded), is drawn behind the
    logo with a 12%-of-panel padding margin.
  * Forces error-correction level H whenever a logo is present (FR-037).
    ✅ Already true unconditionally in `qr_service.py` regardless of
    whether a logo is present, since level H is always used (see
    `QRG-003`) — now asserted directly by
    `test_error_correction_is_always_level_h`, so a future change can't
    silently regress this invariant.
  * Unit tests, including a decoding test confirming a logo-bearing code
    still decodes to the exact source URL. ✅ Added `zxing-cpp` as a
    **development-only** dependency (pure pip wheel, no system package
    needed — see `MEMORY.md`) specifically to make this provable now,
    rather than waiting for `QRG-015`.
    `test_logo_bearing_qr_code_still_decodes_to_the_exact_url` decodes a
    logo-bearing code for both the shortest URL validation allows
    (tightest, smallest QR code — the worst case for finder-pattern
    clearance) and a longer, more typical URL, asserting the decoded text
    matches exactly.
* **Validation:** `pytest -q` → 48 passed (7 new: aspect-ratio
  preservation, finder-pattern non-overlap, no mutation of either input,
  the known-derivation check, two decoding cases, plus the FR-037
  regression test). `ruff check .` and `ruff format --check .` → both
  clean. A scripted Tkinter smoke test selected a logo with a URL already
  entered, confirmed the preview live-refreshed with the logo composited,
  decoded the actual displayed image back to the exact URL via
  `zxingcpp`, then removed the logo and confirmed the preview reverted
  (and still decoded correctly).
* **Known limitation:** The logo size is not yet user-adjustable — only
  the fixed 18% default is used. User-adjustable sizing within these same
  safe limits, with warnings/blocking as it approaches them, is `QRG-011`.
* **Documentation impact:** `SPECIFICATION.md` FR-035/FR-036 updated with
  the concrete percentages; `MEMORY.md` "Open decisions" — the
  QR-decoding library choice is now resolved (`zxing-cpp`), pulled
  forward from `QRG-015`.

### QRG-011 — Add logo sizing controls and warnings

* **Status:** Complete.
* **Objective:** Let the user adjust logo size within safe limits.
* **Acceptance criteria:**
  * Adjustable size within the safe range established by `QRG-010`. ✅ A
    `ttk.Scale` in the Logo section, ranging from 5% to
    `MAX_LOGO_SIZE_RATIO` (30%) — its `to=` bound structurally prevents
    requesting anything above the absolute maximum at all, satisfying the
    "hard rejection" criterion below by construction rather than by a
    runtime check. `MainWindow._logo_size_ratio` drives
    `apply_logo(..., size_ratio=...)`, live-refreshing the preview as the
    slider moves (FR-042).
  * Immediate warning as size approaches the safe maximum (FR-038). ✅
    `logo_service.get_logo_size_warning`, shown alongside the other
    status warnings: at or above `LARGE_LOGO_WARNING_RATIO` (80% of the
    absolute maximum, i.e. 24%), a caution is shown that a large logo can
    reduce scan reliability even with high error correction — even when
    the size is otherwise within all hard limits.
  * Hard rejection beyond the maximum, not just a warning. ✅ Two layers:
    the slider's own range makes requesting above 30% impossible in the
    UI at all; independently, `effective_logo_ratio` also clamps to
    whichever is smaller of the absolute maximum and the per-code
    finder-pattern-safe maximum from `QRG-010`, and
    `get_logo_size_warning` reports when that clamping actually changed
    the requested size.
* **Validation:** `pytest -q` → 54 passed (6 new:
  `effective_logo_ratio` returning the request unchanged when well within
  limits, clamped by the absolute maximum, and clamped by finder-pattern
  safety; `get_logo_size_warning` for no-warning, reduced, and
  large-but-safe cases). `ruff check .` and `ruff format --check .` →
  both clean. A scripted Tkinter smoke test dragged the slider to 30% on
  the shortest URL validation allows (the tightest real-world QR case)
  and to 25% on a longer URL, confirming appropriate warnings appear, and
  that the actual displayed image still decodes to the exact URL at
  whatever size was actually applied.
* **Known nuance (evidence-based, not assumed):** in practice, even the
  shortest URL `validate_url` accepts already produces QR version 2 (not
  the theoretical version-1 minimum), whose finder-pattern-safe ratio
  (~36%) is *above* the absolute 30% cap — so for every realistic URL
  this application can generate, the **absolute** 30% cap is what
  actually binds, not the geometric finder-pattern one. The
  finder-pattern-safety clamp is still real, correct, and covered by
  direct unit tests against a synthetic version-1-sized image
  (`test_effective_logo_ratio_clamped_by_finder_pattern_safety`); it is
  just not reachable through the live application with any URL currently
  accepted, which is why the smoke test above shows the "large but safe"
  warning rather than a "reduced to" one.
* **Documentation impact:** None beyond this entry and `MEMORY.md`.

---

## Milestone 4 — Export

### QRG-012 — Implement PNG export

* **Status:** Complete.
* **Objective:** Save the generated (possibly coloured, possibly
  logo-bearing) QR code as a PNG file.
* **Acceptance criteria:**
  * Preset useful output dimensions (FR-049). ✅
    `export_service.PNG_SIZE_PRESETS`: Small (512 px), Medium (1024 px,
    default), Large (2048 px), offered via a read-only dropdown.
  * Integer module scaling preserved (FR-011, FR-047). ✅
    `render_png_for_export` regenerates the QR **from scratch** at a
    scale chosen to land as close as possible to the target size
    (`qr_service.module_count` gives the exact module count without a
    full render first), rather than resizing an already-rasterised
    preview — this keeps every exported pixel a genuine, crisp,
    integer-scaled module rather than an interpolated blur.
  * Quiet zone preserved (FR-047). ✅ Unchanged from `qr_service` (the
    four-module border applies at every scale).
  * Logo compositing included when present. ✅ `render_png_for_export`
    takes the current logo and size ratio and calls `apply_logo` at the
    *export* scale (not the preview scale), so the logo is sized
    correctly for the resolution actually being exported.
  * A save dialog; overwrite confirmation (FR-051). ✅ The native
    `tkinter.filedialog.asksaveasfilename` dialog is used as-is, relying
    on its built-in "replace existing file?" prompt (standard GTK/Tk
    behaviour on Ubuntu) rather than a redundant custom confirmation —
    see the note below on what this does and doesn't let us test.
  * Clear error handling on failure (FR-052). ✅ `export_service.save_png`
    wraps the write in `try`/`except OSError`, raising a descriptive
    `ExportError`; `MainWindow._on_export_png` catches it and shows the
    message via the status label, and separately validates the URL
    first (reusing `validate_url`) before ever opening the save dialog.
  * Export-level tests (file is written, is a valid PNG, decodes
    correctly). ✅ `tests/test_export_service.py` (9 tests): each preset
    size renders within one module-width of its target; an unknown size
    label is rejected; a provided logo visibly changes the centre pixel
    versus no logo; a saved file re-opens as a valid PNG at the right
    size; the saved file decodes (via `zxingcpp`) to the exact source
    URL; and an unwritable path (nonexistent parent directory) raises
    `ExportError` rather than an unhandled `OSError`. Also added
    `qr_service.module_count` with its own regression test
    (`test_module_count_matches_the_rendered_image`).
* **Validation:** `pytest -q` → 63 passed (9 new). `ruff check .` and
  `ruff format --check .` → both clean. A scripted smoke test
  (monkeypatching `filedialog.asksaveasfilename` to bypass the native
  dialog, the same technique used for logo selection in `QRG-009`)
  exercised: exporting with no URL entered (validation error, no dialog);
  a plain Medium export that reopens and decodes to the exact URL; a
  Large export with a logo present, which also decodes correctly at the
  larger resolution; and cancelling the dialog (empty path) causing no
  crash and no unwanted status change.
* **Known limitation — cannot be automated-tested:** the native save
  dialog's own overwrite-confirmation prompt is standard GTK/Tk behaviour
  on Ubuntu, not custom code, so there is nothing of ours to unit-test
  here; it has not been manually verified interactively in this
  environment (headless-ish sandbox), only reasoned about from documented
  Tk/GTK behaviour. Worth a manual check on a real Ubuntu desktop.
* **Documentation impact:** `SPECIFICATION.md` FR-049 updated with the
  concrete preset sizes.

### QRG-013 — Implement SVG export

* **Status:** Complete.
* **Objective:** Save the generated QR code as SVG.
* **Acceptance criteria:**
  * Vector QR modules at the selected colours (FR-046). ✅
    `export_service.render_svg_for_export` delegates directly to Segno's
    own SVG writer for the QR modules — no size presets are offered for
    SVG, since vector output scales losslessly to any size
    (`SPECIFICATION.md` §10), unlike PNG.
  * Quiet zone preserved (FR-047). ✅ Unchanged — the same
    `QUIET_ZONE_MODULES` border passed to Segno.
  * Self-contained embedded logo where technically practical (FR-050). ✅
    When a logo is present, it is embedded as a base64-encoded PNG
    `<image>` element behind a solid `<rect>` clearance panel (using the
    QR's own background colour), inserted just before `</svg>` — no
    external file references. The QR modules themselves remain pure
    vector; only the small logo area is raster, which is the "where
    technically practical" compromise FR-050 anticipates.
  * Save dialog; export-level tests. ✅ An "Export SVG…" button, using
    the same URL-validation-then-native-dialog pattern as PNG export
    (`QRG-012`).
* **Refactor enabling this cleanly:** extracted `logo_service`'s
  finder-pattern-safety and sizing maths into module-count-based
  functions (`max_safe_logo_ratio_for_modules`,
  `effective_logo_ratio_for_modules`) and a shared
  `fit_logo_and_panel(canvas_size, effective_ratio, logo)` geometry
  helper, so the SVG path computes the *exact* same panel/logo placement
  as the PNG path (`apply_logo`) without needing a rendered raster QR
  image first. All 63 pre-existing tests still passed unchanged after
  this refactor, confirming it altered no behaviour.
* **Validation:** `pytest -q` → 70 passed (7 new): the no-logo SVG is
  byte-identical to calling Segno directly (proving nothing is altered
  when there's no logo); the logo-bearing SVG is well-formed XML
  (`xml.etree.ElementTree`) with the expected `<g>`/`<rect>`/`<image>`
  structure; the `<g>` (vector QR modules) is byte-identical with and
  without a logo present (proving the injection never touches the
  modules); the panel's `fill` matches the exact configured background
  colour; the embedded `<image>`'s position/size and decoded PNG bytes
  match what `fit_logo_and_panel` computes directly; and `save_svg`
  writes the exact text and raises `ExportError` for an unwritable path.
  `ruff check .` and `ruff format --check .` → both clean. A scripted
  smoke test exercised no-URL validation, a plain export, a logo-bearing
  export, and dialog cancellation, inspecting the actual written file's
  XML structure each time.
* **Known limitation — not automated:** unlike PNG, the exported SVG is
  not verified by actually *decoding* it as a QR code, because that would
  require rasterising the SVG first (e.g. via a browser or a rendering
  library), which was judged disproportionate to add as a new dependency
  for this. Confidence instead comes from: Segno's SVG output being used
  completely unmodified (proven byte-identical in the no-logo case), and
  the logo-embedding geometry being proven identical to the
  already-decode-tested PNG path. Physical/visual verification of SVG
  output remains part of `QRG-016`.
* **Documentation impact:** None beyond this entry and `MEMORY.md`.

### QRG-014 — Add export settings and filename handling

* **Status:** Complete.
* **Objective:** Sensible default/safe filenames and export settings.
* **Acceptance criteria:**
  * Sensible default filename. ✅
    `export_service.default_export_filename(url, extension)` derives it
    from the URL itself (e.g. `example.com-leaflet-campaign-utm-1.png`),
    so exporting for different URLs no longer suggests the same generic
    name every time — verified directly that two different URLs produce
    two different suggested filenames.
  * Filesystem-safe filename generation. ✅ `safe_filename_stem` keeps
    only letters, digits, dots, hyphens and underscores (safe on Linux,
    Windows and macOS alike), collapsing everything else — spaces,
    `: / ? & < > "`, non-ASCII characters — to a single hyphen, trims to
    60 characters, and falls back to `"qrcode"` if nothing safe remains
    (e.g. a URL that is only a scheme).
  * "Last export directory" preference only if local preferences are
    separately approved. ✅ **Deliberately not implemented** — local
    preferences remain **Proposed**, not committed scope (see "Later or
    proposed items" below), so no directory is remembered between
    exports; the native save dialog's own default starting location is
    used as-is.
  * No URL history stored (FR-063). ✅ Confirmed by inspection — the
    filename is derived from the URL only at the moment of export and is
    never written anywhere or retained; this was already true and
    remains true.
  * Clear success status shown after export. ✅ Unchanged from `QRG-012`/
    `QRG-013` (`"Exported PNG to <name>."` / `"Exported SVG to <name>."`)
    — already satisfied that criterion; re-confirmed still accurate here.
* **Validation:** `pytest -q` → 79 passed (9 new): known-value filename
  stems (query strings, ports, punctuation), a fuzz-style check that only
  safe characters ever appear in the output, truncation of very long
  input, fallback to `"qrcode"` for all-unsafe input, extension
  correctness, determinism for the same URL, and distinctness for
  different URLs. `ruff check .` and `ruff format --check .` → both
  clean. A scripted smoke test intercepted `asksaveasfilename` to inspect
  the suggested filename directly: confirmed distinct, safe filenames for
  two different URLs, for both PNG and SVG.
* **Documentation impact:** None beyond this entry and `MEMORY.md`.
  This closes Milestone 4 (Export): `QRG-012` through `QRG-014`.

---

## Milestone 5 — Scannability and quality

### QRG-015 — Add automated QR decoding tests

* **Status:** Complete.
* **Objective:** Confirm generated codes actually decode back to the exact
  source URL.
* **Acceptance criteria:**
  * Decode a basic black-on-white QR code. ✅
    `test_generated_qr_decodes_to_the_exact_url_black_on_white`
    (`tests/test_qr_service.py`).
  * Decode a coloured QR code. ✅
    `test_generated_qr_decodes_to_the_exact_url_with_custom_colours`
    (dark green on white).
  * Decode QR codes bearing representative logos. ✅ Done in `QRG-010`
    (`tests/test_logo_service.py`), for both a very short and a more
    typical URL.
  * Assert the decoded text exactly matches the source URL. ✅ Done for
    all three cases above (plain, coloured, logo-bearing).
  * Any decoding dependency introduced for this purpose is a
    development-only dependency. ✅ `zxing-cpp`, added as a `dev` extra
    only (see `MEMORY.md`).
* **Validation:** `pytest -q` → 81 passed (2 new). `ruff check .` and
  `ruff format --check .` → both clean.
* **Documentation impact:** None beyond this entry and `MEMORY.md`. This
  completes the automated-decoding acceptance criteria for Milestone 5;
  physical print-and-scan validation remains separate, manual work
  (`QRG-016`).

### QRG-016 — Establish physical scan test matrix

* **Status:** In Progress (partial evidence only — this needs a human with
  real hardware; an agent cannot complete it).
* **Objective:** Structured manual scan testing before any
  production-oriented release.
* **Acceptance criteria:**
  * Tested on at least one common Android device and one iPhone. 🟡
    iPhone confirmed (on-screen); Android not yet tested.
  * Tested on-screen and on printed paper. 🟡 On-screen confirmed;
    printed paper not yet tested (the user's own assessment is "I think
    it'll be fine from a proper printed leaflet" — an expectation, not a
    result, and recorded as such rather than upgraded to a pass).
  * Tested at realistic leaflet size. ❌ Not yet tested at a physical
    printed size at all.
  * Tested under several lighting conditions. ❌ Not yet tested.
  * Tested with coloured output and with logos present. ✅ The real
    Rotary-blue-on-white, logo-bearing code generated for the user (see
    `MEMORY.md`) was scanned successfully on an iPhone from a screen.
  * Results recorded somewhere durable. 🟡 Recorded here and in
    `MEMORY.md` for now; a more durable/structured location remains an
    open decision.
* **Dependencies:** `QRG-010`, `QRG-012`, `QRG-013` (all done).
* **Validation requirements:** This item's own acceptance criteria are the
  validation. Remaining: Android device, printed/leaflet-size output, and
  varied lighting conditions.

### QRG-017 — Improve accessibility and keyboard operation

* **Status:** Complete.
* **Objective:** Meet `SPECIFICATION.md` §11 in full.
* **Acceptance criteria:**
  * Reasonable, predictable focus/tab order across all controls. ✅
    Verified by walking `tk_focusNext()` from the initial focus (the URL
    entry) all the way around: 38 stops, covering every interactive
    control in exactly the visual top-to-bottom order (URL → foreground
    palette/picker/HEX/RGB/CMYK → background, same → logo
    choose/remove → size slider → Generate → export size, PNG, SVG),
    looping back to the start with no dead ends and no skipped controls.
    No manual tab-order overrides were needed — the natural creation
    order was already correct.
  * All primary actions reachable and operable by keyboard alone. ✅
    Found and fixed a real gap: the six palette colour swatches (in
    `ui/colour_control.py`, used for both foreground and background) were
    plain `tk.Label` widgets bound only to `<Button-1>` — mouse-only, with
    no way to reach or activate them from the keyboard at all. Added
    `takefocus=True` and `highlightthickness=2` (so they join the tab
    order and show a visible focus ring using Tk's own built-in
    focus-highlight mechanism) plus `<Return>`/`<space>` bindings that
    trigger the exact same `set_colour` action as a mouse click. Verified
    directly: focusing a swatch and sending a synthetic `<Return>` (and,
    on a different swatch, `<space>`) changed the control's colour to
    exactly that swatch's colour. Every other control (`ttk.Entry`,
    `ttk.Button`, `ttk.Combobox`, `ttk.Scale`) was already
    keyboard-operable out of the box via standard ttk behaviour.
  * Status messaging never relies on colour alone. ✅ Already true before
    this item: the status label uses one fixed colour
    (`foreground="#444444"`) for every message — success, warning and
    error alike — so meaning has only ever come from the message text,
    never from colour-coding. No change needed; confirmed by inspection.
  * A review of behaviour under OS-level font/scaling changes. ✅/🟡
    Scripted check: rebuilt the window with every named Tk font scaled
    to 1.8x its default size. The application still constructs, updates
    and generates a QR code without error, and the window remains
    user-resizable in both dimensions (`root.resizable()` →
    `(True, True)`) — the built-in Tk mechanism for a user to compensate
    if content feels cramped. **Found and recorded, not fixed:** at that
    1.8x scale, the content's requested height (943px) exceeds the
    fixed initial window height (760px) — about 24% short — so some
    content would be below the fold until the user manually resizes the
    window. The window does not auto-grow to fit larger fonts. This is a
    real, verified limitation, not a crash or data-loss risk, and is
    listed as a candidate for a future increase to the default window
    size or a scroll region, rather than fixed speculatively now. A true
    OS-level "change the system text-scaling setting and look at it"
    check on a real Ubuntu desktop was not possible in this environment
    and remains genuinely unverified.
* **Validation:** `pytest -q` → 81 passed (unchanged — this item is UI
  wiring plus scripted structural checks, not new pure-logic behaviour
  requiring new unit tests). `ruff check .` and `ruff format --check .`
  → both clean. Three scripted checks as described above: keyboard
  activation of palette swatches, a full tab-order walk, and a font-scale
  robustness check.
* **Documentation impact:** None beyond this entry and `MEMORY.md`.

### QRG-018 — Harden error handling

* **Status:** Proposed.
* **Objective:** Cover every user-facing error case listed in
  `SPECIFICATION.md` §12 that is not already covered by earlier items.
* **Acceptance criteria:** Each case in §12 (invalid URL, invalid colour,
  unsupported logo format, corrupt image, oversized image, failed
  generation, failed export, permission errors, missing optional
  dependency, unexpected internal error) results in a clear status message
  or dialog, never a bare traceback.
* **Dependencies:** Most of Milestones 2–4.
* **Validation requirements:** A test or manual check per error case.

---

## Milestone 6 — Packaging and release

### QRG-019 — Package for Ubuntu

* **Status:** Proposed.
* **Objective:** A standalone Ubuntu build.
* **Acceptance criteria:**
  * Built with PyInstaller, or a justified equivalent recorded in
    `MEMORY.md`.
  * Verified to launch in a clean Ubuntu test environment (not just the
    development machine).
  * Bundled dependencies; an application icon; `LICENSE` and
    `THIRD_PARTY_NOTICES.md` included alongside the build.
* **Dependencies:** A functionally complete application (Milestones 2–5).
* **Validation requirements:** Manual launch verification in a clean
  environment.

### QRG-020 — Add continuous integration

* **Status:** Proposed.
* **Objective:** Automated `pytest` and Ruff checks on every change.
* **Acceptance criteria:**
  * CI runs tests and Ruff against the supported Python version(s).
  * No automatic publishing step unless separately, explicitly approved.
* **Dependencies:** None — could reasonably be pulled forward if desired,
  but is sequenced here as it is not required for the current manual
  workflow.
* **Validation requirements:** A green CI run on a representative change.

### QRG-021 — Prepare initial release documentation

* **Status:** Proposed.
* **Objective:** User-facing documentation ready for a first release.
* **Acceptance criteria:**
  * Installation and usage instructions.
  * Known limitations stated plainly.
  * Static vs dynamic QR explanation (already present in `README.md` and
    `SPECIFICATION.md` §1; carry forward and keep accurate).
  * Scannability guidance for end users.
  * Licence information.
  * Release notes.
* **Dependencies:** Most of Milestones 2–5.
* **Validation requirements:** Documentation review against actual
  behaviour at release time.

### QRG-022 — Validate initial release

* **Status:** Proposed.
* **Objective:** Confirm every criterion in `SPECIFICATION.md` §16 before
  calling any version "released".
* **Acceptance criteria:** All twelve release criteria in §16 are met, with
  evidence recorded in `MEMORY.md`.
* **Dependencies:** All prior milestones.
* **Validation requirements:** A final, explicit checklist pass against
  §16.

---

## Later or proposed items

These are recorded as **Proposed** or **Deferred** — not committed initial
scope:

* **Proposed** — Remember non-sensitive local preferences (last export
  directory, last colours, last dimensions).
* **Proposed** — Additional Linux packaging formats beyond the initial
  Ubuntu build.
* **Proposed** — Windows packaging.
* **Proposed** — macOS packaging.
* **Proposed** — Batch URL generation (multiple codes in one operation).
* **Proposed** — Reusable visual presets (saved colour/logo combinations).
* **Proposed** — Command-line generation, as an alternative interface to
  the desktop UI.

Dynamic QR codes, tracking, monetisation and hosted redirect services are
**rejected scope** (see `SPECIFICATION.md` §15) — they are not listed here
because they are not future work under consideration, they are permanently
excluded product decisions.
