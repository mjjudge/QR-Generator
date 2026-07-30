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

* **Current milestone:** Milestone 1 complete; Milestone 2 — Colour
  controls — under way (`QRG-005` complete, `QRG-006`/`QRG-007` next).
* **Recommended next item:** `QRG-006` — Add foreground colour controls
  (UI), followed by `QRG-007` (background) and `QRG-008` (contrast
  validation).
* **Evidence used to set statuses below:** full read-through of every file
  in `src/`, `tests/`, `pyproject.toml`, `README.md`, `LICENSE`, and
  `THIRD_PARTY_NOTICES.md`; `pytest -q` (26 passed); `ruff check .` (all
  checks passed); `ruff format --check .` (all files formatted);
  scripted Tkinter smoke tests exercising valid, empty, unsupported-scheme
  and long-URL input; and a direct check that custom foreground/background
  colours are correctly threaded through to the rendered image.

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

* **Status:** Proposed.
* **Objective:** UI controls for foreground colour selection.
* **Acceptance criteria:**
  * Palette, graphical picker, HEX, RGB and CMYK entry, all synchronised
    (FR-015–FR-020).
  * Selected colour feeds into `QRSettings.foreground_colour` and is
    reflected in the preview.
  * Invalid values show a validation error (FR-023).
* **Dependencies:** `QRG-005`.
* **Validation requirements:** Manual UI testing; unit tests for any
  non-trivial logic extracted into services.

### QRG-007 — Add background colour controls

* **Status:** Proposed.
* **Objective:** UI controls for background colour selection.
* **Acceptance criteria:** Equivalent to `QRG-006`, applied to
  `QRSettings.background_colour`.
* **Dependencies:** `QRG-005`.
* **Validation requirements:** As `QRG-006`.

### QRG-008 — Add contrast and colour safety validation

* **Status:** Proposed.
* **Objective:** Warn when foreground/background contrast is likely to harm
  scan reliability.
* **Acceptance criteria:**
  * A documented contrast calculation (for example, relative luminance
    difference) (FR-024, NFR requirement for documented method).
  * Dark-on-light preferred as the safe default; deviating combinations are
    flagged (FR-025, FR-026).
  * A defined, conservative policy for transparent backgrounds (FR-027).
  * Unit tests for the contrast calculation and threshold behaviour.
* **Dependencies:** `QRG-005`, `QRG-006`, `QRG-007`.
* **Validation requirements:** Unit tests; manual check that a known
  low-contrast pair (e.g. light grey on white) triggers a warning.

---

## Milestone 3 — Central image

### QRG-009 — Add logo file selection and validation

* **Status:** Proposed.
* **Objective:** Let the user choose, validate, and clear a central image.
* **Acceptance criteria:**
  * Accept PNG, JPEG, JPG (FR-028).
  * Reject unsupported/corrupt files cleanly, without relying on file
    extension alone (FR-029, NFR-008).
  * Support removing/replacing the selected logo.
  * Never modify the user's source file (FR-040).
* **Dependencies:** None (independent of colour work).
* **Validation requirements:** Unit tests with valid, corrupt and
  wrong-extension sample files; `logo_service.py` gains real
  implementation and tests.

### QRG-010 — Implement safe central logo placement

* **Status:** Proposed.
* **Objective:** Composite a validated logo onto the QR code safely.
* **Acceptance criteria:**
  * Aspect ratio preserved (FR-030, FR-039).
  * Conservative default size and enforced safe maximum (FR-035, FR-036).
  * Centred placement with a background clearance panel (FR-032, FR-033).
  * No overlap with finder patterns (FR-034).
  * Forces error-correction level H whenever a logo is present (FR-037).
  * Unit tests, including a decoding test confirming a logo-bearing code
    still decodes to the exact source URL.
* **Dependencies:** `QRG-009`.
* **Validation requirements:** Automated decoding test (see `QRG-015`);
  manual visual check.

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

* **Status:** Proposed.
* **Objective:** Confirm generated codes actually decode back to the exact
  source URL.
* **Acceptance criteria:**
  * Decode a basic black-on-white QR code.
  * Decode a coloured QR code.
  * Decode QR codes bearing representative logos.
  * Assert the decoded text exactly matches the source URL.
  * Any decoding dependency introduced for this purpose is a
    development-only dependency, not a runtime one, unless there is a
    strong justification recorded in `MEMORY.md`.
* **Dependencies:** `QRG-006`–`QRG-010` (need coloured/logo output to
  test against); a decoding library choice, which is an open decision
  (see `MEMORY.md`).
* **Validation requirements:** New automated test suite; `pytest` passes.

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
