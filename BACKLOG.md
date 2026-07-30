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

* **Current milestone:** Milestone 3 — Central image — under way
  (`QRG-009`, `QRG-010` complete).
* **Recommended next item:** `QRG-011` — Add logo sizing controls and
  warnings (user-adjustable size within the safe limits `QRG-010`
  established).
* **Evidence used to set statuses below:** full read-through of every file
  in `src/`, `tests/`, `pyproject.toml`, `README.md`, `LICENSE`, and
  `THIRD_PARTY_NOTICES.md`; `pytest -q` (48 passed); `ruff check .` (all
  checks passed); `ruff format --check .` (all files formatted);
  scripted Tkinter smoke tests exercising valid, empty, unsupported-scheme
  and long-URL input, foreground and background colour synchronisation,
  validation and live preview refresh, contrast/polarity warnings, logo
  selection/rejection/removal, and logo placement with a live decoding
  check against the actual displayed image; and direct pixel/byte-level
  checks confirming chosen colours render correctly, logo files are never
  modified on disk, and finder-pattern pixels are never touched.

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

* **Status:** Proposed.
* **Objective:** Let the user adjust logo size within safe limits.
* **Acceptance criteria:**
  * Adjustable size within the safe range established by `QRG-010`.
  * Immediate warning as size approaches the safe maximum (FR-038).
  * Hard rejection beyond the maximum, not just a warning.
* **Dependencies:** `QRG-010`.
* **Validation requirements:** Manual UI testing; unit test for the
  boundary condition.

---

## Milestone 4 — Export

### QRG-012 — Implement PNG export

* **Status:** Proposed.
* **Objective:** Save the generated (possibly coloured, possibly
  logo-bearing) QR code as a PNG file.
* **Acceptance criteria:**
  * Preset useful output dimensions (FR-049).
  * Integer module scaling preserved (FR-011, FR-047).
  * Quiet zone preserved (FR-047).
  * Logo compositing included when present.
  * A save dialog; overwrite confirmation (FR-051).
  * Clear error handling on failure (FR-052).
  * Export-level tests (file is written, is a valid PNG, decodes
    correctly).
* **Dependencies:** `QRG-003`; benefits from `QRG-006`–`QRG-010` but does
  not strictly require them (can export the current black-and-white,
  logo-free code first).
* **Validation requirements:** Automated export tests; manual save-dialog
  check.

### QRG-013 — Implement SVG export

* **Status:** Proposed.
* **Objective:** Save the generated QR code as SVG.
* **Acceptance criteria:**
  * Vector QR modules at the selected colours (FR-046).
  * Quiet zone preserved (FR-047).
  * Self-contained embedded logo where technically practical (FR-050).
  * Save dialog; export-level tests.
* **Dependencies:** As `QRG-012`.
* **Validation requirements:** Automated export tests confirming the SVG
  parses and, where practical, decodes.

### QRG-014 — Add export settings and filename handling

* **Status:** Proposed.
* **Objective:** Sensible default/safe filenames and export settings.
* **Acceptance criteria:**
  * Sensible default filename.
  * Filesystem-safe filename generation.
  * "Last export directory" preference only if local preferences
    (`QRG` later-scope item) are separately approved.
  * No URL history stored (FR-063).
  * Clear success status shown after export.
* **Dependencies:** `QRG-012`, `QRG-013`.
* **Validation requirements:** Unit tests for filename sanitisation; manual
  check of the success status.

---

## Milestone 5 — Scannability and quality

### QRG-015 — Add automated QR decoding tests

* **Status:** In Progress (partially pulled forward into `QRG-010`).
* **Objective:** Confirm generated codes actually decode back to the exact
  source URL.
* **Acceptance criteria:**
  * ~~Decode a basic black-on-white QR code.~~ Covered indirectly by
    `test_logo_bearing_qr_code_still_decodes_to_the_exact_url`'s
    same-library decoding, though no dedicated no-logo/no-colour decoding
    test exists yet as its own item.
  * Decode a coloured QR code — **not yet covered**.
  * ~~Decode QR codes bearing representative logos.~~ ✅ Done in `QRG-010`
    (`tests/test_logo_service.py`), for both a very short and a more
    typical URL.
  * ~~Assert the decoded text exactly matches the source URL.~~ ✅ Done
    for the logo-bearing case.
  * ~~Any decoding dependency introduced for this purpose is a
    development-only dependency.~~ ✅ `zxing-cpp`, added as a `dev` extra
    only (see `MEMORY.md`).
* **Dependencies:** `QRG-006`–`QRG-010` (done); decoding library choice
  (resolved: `zxing-cpp`, see `MEMORY.md`).
* **Validation requirements:** Remaining: a dedicated test decoding a
  plain black-on-white code and a coloured (non-logo) code, for
  completeness/symmetry with the logo case already covered.
* **Documentation impact:** None further until the remaining coverage is
  added.

### QRG-016 — Establish physical scan test matrix

* **Status:** Proposed.
* **Objective:** Structured manual scan testing before any
  production-oriented release.
* **Acceptance criteria:**
  * Tested on at least one common Android device and one iPhone.
  * Tested on-screen and on printed paper.
  * Tested at realistic leaflet size.
  * Tested under several lighting conditions.
  * Tested with coloured output and with logos present.
  * Results recorded (pass/fail per combination) somewhere durable — a
    location for these results is itself an open decision (see
    `MEMORY.md`).
* **Dependencies:** `QRG-010`, `QRG-012`, `QRG-013`.
* **Validation requirements:** This item's own acceptance criteria are the
  validation.

### QRG-017 — Improve accessibility and keyboard operation

* **Status:** Proposed.
* **Objective:** Meet `SPECIFICATION.md` §11 in full.
* **Acceptance criteria:**
  * Reasonable, predictable focus/tab order across all controls.
  * All primary actions reachable and operable by keyboard alone.
  * Status messaging never relies on colour alone.
  * A review of behaviour under OS-level font/scaling changes.
* **Dependencies:** Best done once `QRG-006`–`QRG-013` add most of the
  remaining controls, so the full control set can be reviewed together.
* **Validation requirements:** Manual keyboard-only walkthrough.

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
