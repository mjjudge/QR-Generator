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
* `zxing-cpp` is a **development-only** dependency (a pip extra under
  `dev`, not a runtime dependency), used solely to prove in automated
  tests that generated QR codes — including logo-bearing ones — decode
  back to the exact source URL. Chosen because it ships a prebuilt Linux
  wheel with no system package required, keeping the Ubuntu offline setup
  simple. This resolves the "which decoding library" open decision ahead
  of schedule (originally slated for `QRG-015`), pulled forward into
  `QRG-010` because that item's own acceptance criteria required it.
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
* Decoding coverage (`QRG-015`) now spans all three shapes generated
  codes can take: plain black-on-white, custom-coloured, and
  logo-bearing (the last one added earlier, in `QRG-010`) — each
  asserting the decoded text matches the source URL exactly.
* Finder-pattern protection for a central logo is enforced geometrically,
  not by a fixed guess: `logo_service.max_safe_logo_ratio` derives, from
  the QR image's own module count, the largest centred square guaranteed
  clear of all three (corner-only, always-7×7-module) finder patterns.
  This is combined with a fixed 30% absolute ceiling
  (`MAX_LOGO_SIZE_RATIO`) and an 18% default (`DEFAULT_LOGO_SIZE_RATIO`) —
  whichever of the three is smallest wins. See `BACKLOG.md` `QRG-010` for
  the full derivation.
* Even the shortest URL `validate_url` accepts already produces QR
  version 2, not version 1 — meaning the finder-pattern-safe ratio (~36%
  at version 2) is always above the 30% absolute cap for any URL this
  application can actually generate. In practice, the **absolute** cap is
  what binds, not the geometric one, though the geometric clamp is real
  and directly unit-tested against a synthetic version-1-sized image.
  Logo size is user-adjustable via a slider whose range (5%-30%) itself
  structurally prevents requesting above the absolute maximum; warnings
  cover both an actual reduction and a "large but safe" caution at ≥24%
  (`QRG-011`).
* PNG export (`QRG-012`) always **regenerates** the QR code at a scale
  chosen for the target output size, rather than resizing the on-screen
  preview — `qr_service.module_count(url)` gives the exact module count
  via Segno directly (`symbol_size(scale=1, border=0)`), with no need to
  render a throwaway image first. The logo, if present, is recomposited
  at that same export scale, not the preview's scale. Overwrite
  confirmation relies entirely on the native
  `tkinter.filedialog.asksaveasfilename` dialog's own built-in prompt —
  there is no custom overwrite-confirmation code to test, and this
  reliance has not been manually verified interactively on a real Ubuntu
  desktop in this environment (see "Open decisions").
* Export filenames are suggested, not remembered (`QRG-014`):
  `export_service.default_export_filename` derives a distinct, filesystem
  -safe suggestion from the URL itself (e.g.
  `example.com-leaflet-campaign-utm-1.png`), replacing the previous fixed
  `qrcode.png`/`qrcode.svg` for every export. "Last export directory" was
  deliberately **not** implemented — local preferences remain unapproved,
  proposed-only scope (see "Open decisions" and the backlog's "Later or
  proposed items"), so the native save dialog's own default starting
  location is used as-is, every time.
* SVG export (`QRG-013`) has **no size presets** — vector output scales
  losslessly, so there is no "target resolution" the way PNG needs one.
  The QR modules are Segno's own SVG output, used completely unmodified
  when no logo is present (proven byte-identical in tests). When a logo
  is present, it is embedded as a base64 PNG `<image>` behind a `<rect>`
  clearance panel, inserted just before `</svg>` — the vector modules
  themselves are never touched (also proven directly in tests). This
  reuses the exact same placement geometry as PNG export via
  `logo_service.fit_logo_and_panel`, factored out specifically so both
  formats place the logo identically for the same settings.
  `logo_service`'s finder-pattern-safety maths (`max_safe_logo_ratio`,
  `effective_logo_ratio`) were refactored into module-count-based
  variants (`..._for_modules`) for the same reason — the SVG path never
  needs to rasterise a QR image just to learn its module count.

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
  Remove clears the selection.
* Logo placement is implemented (`QRG-010`): selecting a logo composites
  it, centred, onto the QR preview immediately (live refresh), with a
  background clearance panel matching the QR's own background colour.
  Verified directly, against the actual displayed image: the result still
  decodes (via `zxingcpp`) to the exact source URL with the logo present,
  and reverts cleanly (still decoding correctly) when the logo is
  removed. Finder-pattern protection and sizing (18% default / 30% max /
  a geometrically-derived per-code safe maximum, whichever is smallest)
  are described above under "Durable technical decisions".
* Logo size is user-adjustable (`QRG-011`) via a slider (5%-30%), with
  live preview refresh and two independent warnings: a reduction notice
  if the requested size had to be clamped, and a "large but safe" caution
  at 24% and above. Verified directly against the live application: both
  warning types appear appropriately, and the composited result still
  decodes to the exact URL at whatever size was actually applied.
* PNG export is implemented (`QRG-012`): a size dropdown (Small/Medium/
  Large) and an "Export PNG…" button, validating the URL first, then
  using the native save dialog. Verified directly: exporting with no URL
  entered shows a validation error without opening a dialog; a plain
  export and a logo-bearing Large export both reopen as valid PNGs and
  decode (via `zxingcpp`) to the exact source URL; cancelling the dialog
  does nothing.
* SVG export is implemented (`QRG-013`): an "Export SVG…" button beside
  the PNG one, same validation-then-native-dialog pattern, no size
  dropdown (not applicable to vector output). Verified directly: exported
  files are well-formed XML with the expected structure, both with and
  without a logo present.
* Both export dialogs now suggest a distinct, safe, URL-derived default
  filename rather than a fixed generic one (`QRG-014`). Verified directly
  by intercepting the save dialog: two different URLs produce two
  different suggested filenames, for both PNG and SVG. **Not yet
  implemented:** remembering the last export directory (deliberately, not
  an oversight — see "Open decisions").

**What tests exist:** `tests/test_validation_service.py` (valid HTTP/HTTPS,
empty input, whitespace-only input, unsupported scheme, unusual-but-valid
characters preserved exactly, no warning at/below the 300-character
threshold, warning above it, no network calls made), `tests/test_qr_service.py`
(a PIL image is produced; the exact supplied URL is what gets passed to
Segno; error correction is always level H), `tests/test_colour_service.py`
(HEX/RGB/CMYK parsing and validation; known-value HEX↔RGB↔CMYK round trips
for black, white and pure red; relative luminance and contrast ratio known
values; and contrast/polarity warning behaviour), and
`tests/test_logo_service.py` (valid PNG and JPEG/JPG loading; missing
file, corrupt content, and extension-spoofed-format rejection; no
modification of the source file; a genuine in-memory copy; the
finder-pattern-safe-ratio derivation against a known worst case;
aspect-ratio preservation; no mutation of either input to `apply_logo`;
finder-pattern pixels left untouched; and logo-bearing codes decoding to
the exact URL for both the shortest and a typical URL). All 48 tests
pass.

* Real-world validation, outside the automated test suite: a genuine
  QR code was generated on request (Rotary Royal Blue `#17458F` on
  white, with a transparent-PNG club logo), exported as both PNG and
  SVG, and the saved PNG file was decoded and confirmed to match the
  requested URL exactly — first at the 18% default logo size, then
  again at 22% after a size increase. This is the first time the
  application has been used for its actual intended purpose rather than
  synthetic test data. The user additionally scanned it with an iPhone
  camera directly from a screen and confirmed it works — genuine
  physical-device evidence for `QRG-016`, though only one data point
  (iPhone, on-screen, one colour/logo combination) out of that item's
  full matrix (also needs Android, printed paper, leaflet size, varied
  lighting). The user expects printed leaflets to work too but has not
  yet tested that; recorded as an expectation, not a result.

* Accessibility and keyboard operation were audited and one real gap
  fixed (`QRG-017`): the palette colour swatches were mouse-only (plain
  `tk.Label`s with only a `<Button-1>` binding); they now take keyboard
  focus and activate on `<Return>`/`<space>`, verified directly with
  synthetic keyboard events. A full tab-order walk (38 stops) confirmed
  every interactive control is reachable in a sensible order with no
  manual overrides needed. Status messages already used one fixed colour
  for every message, so meaning never depended on colour. At 1.8x
  default font scale the app still runs correctly and the window remains
  user-resizable, but does **not** auto-grow — content can run about 24%
  taller than the fixed initial window height at that scale, requiring a
  manual resize. A true OS-level scaling check on a real desktop remains
  unverified in this environment.
* Error handling was audited against every case in `SPECIFICATION.md`
  §12 (`QRG-018`), not just assumed correct. Two real bugs were found
  and fixed: `load_logo` let `Image.DecompressionBombError` (Pillow's
  oversized-image safety limit, which does not inherit from `OSError`)
  propagate unhandled; and `_on_export_png`/`_on_export_svg` only caught
  `ExportError`, missing any unexpected failure during rendering (as
  opposed to saving). Both were reproduced directly before fixing, and
  confirmed fixed afterwards by re-reproducing the same failure and
  observing a clean status message instead. Every other §12 case was
  already handled by earlier work and re-confirmed by reading the actual
  code, not recalled from memory.

**What is not yet implemented:** any preferences storage (including a
remembered last export directory — deliberately deferred, not an
oversight); any packaging; any CI configuration.

**Current milestone:** Milestone 5 — Scannability and quality —
agent-completable work complete (`QRG-015`, `QRG-017`, `QRG-018`;
`QRG-016` partial, needs a human with real hardware).

**Recommended next backlog item:** No purely agent-completable item
remains in Milestone 5 without `QRG-016` (needs a human with real
hardware). `QRG-020` (continuous integration, Milestone 6) has no hard
dependency on it and could reasonably be pulled forward if the user
wants to keep going (see `BACKLOG.md`).

## Open decisions

Genuinely unresolved, durable questions:

* Whether to explicitly pass `micro=False` to Segno for defence-in-depth.
  Current behaviour was verified correct (Segno does not select a Micro QR
  Code for representative short or long URL content), but this is not
  structurally guaranteed by the code — only observed.
* The logo-size default (18%) and absolute maximum (30%) are now decided
  and implemented (`SPECIFICATION.md` FR-035/FR-036), but not yet
  validated against real print-and-scan testing (`QRG-016`) — the numbers
  are a reasoned engineering choice (comfortably under error-correction
  level H's ~30% correctable-codeword budget), not an empirically proven
  one yet.
* Whether the 4.5:1 WCAG contrast threshold (`SPECIFICATION.md` FR-024) is
  actually the right bar for QR scan reliability specifically, as opposed
  to text readability — it was adopted as a documented, defensible
  standard in the absence of a QR-specific one, but has not been checked
  against physical scan testing (`QRG-016`).
* Whether the native `tkinter.filedialog.asksaveasfilename` overwrite
  prompt actually appears and behaves as expected on a real Ubuntu
  desktop — reasoned from documented GTK/Tk behaviour and exercised in
  automated tests only via monkeypatching (the dialog itself cannot be
  driven headlessly), so it has not been manually verified interactively.
* Whether to ever add an SVG-rasterising dependency (e.g. `cairosvg`) so
  exported SVGs can be decode-tested the same way PNGs are, or whether
  the current structural proof (Segno's output used byte-identically;
  the logo geometry proven identical to the already-decode-tested PNG
  path) is considered sufficient indefinitely. Not added yet — judged
  disproportionate for this task (`QRG-013`).
* Whether the fixed initial window size (`WINDOW_SIZE`,
  `ui/main_window.py`) should be increased, or a scroll region added, to
  accommodate large OS-level font scaling without requiring a manual
  resize — found during `QRG-017` (content can run ~24% taller than the
  window at 1.8x default font scale) but deliberately not fixed
  speculatively; the window is user-resizable in the meantime.
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
