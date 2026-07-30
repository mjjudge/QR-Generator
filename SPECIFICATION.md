# QR Code Generator — Specification

Status: living document. This specification describes the **intended,
approved** behaviour of the product. It is not a status report. For what is
actually implemented and validated today, see `BACKLOG.md` and `MEMORY.md`.
Documentation drift between this file, `BACKLOG.md`, `AGENTS.md` and
`MEMORY.md` is treated as a defect.

Language: British English throughout.

---

## 1. Purpose

Many "QR code generator" services on the web are actually **dynamic** or
**redirect-based** services. They encode a short URL pointing at the
provider's own server, and that server redirects the scanner to the real
destination. This model has real costs for ordinary users: the code can stop
working if a subscription lapses or the provider shuts the service down, the
provider can log or analyse every scan, and the user has no independent copy
of a working QR code they fully own.

This project exists to remove that dependency. It is a free, local, offline
QR code generator for Ubuntu desktops that:

* Encodes the user's exact destination URL directly into the QR code.
* Produces output that is a self-contained, standards-compliant QR code,
  usable and scannable indefinitely, independently of this application, this
  repository, or any server.
* Requires no account, subscription, payment or ongoing service from this
  project or any third party to keep working.

### Static vs dynamic QR codes

A **static QR code** encodes its final content (here, a URL) directly. Once
generated, it needs nothing further from anyone to keep working — it is just
a pattern of black and white (or coloured) modules that any QR reader can
decode.

A **dynamic QR code** encodes a short link to a redirect service, which looks
up the real destination and forwards the scanner there. This project
deliberately produces only static QR codes, and must never substitute a
redirect, shortener, tracking link, or application- or third-party-owned URL
in place of what the user typed.

---

## 2. Product principles

1. **Offline first.** The application must work with no internet connection.
2. **Static and permanent output.** Generated codes must keep working forever,
   independent of this application or repository.
3. **Scannability before appearance.** When a choice must be made, reliable
   scanning takes priority over visual customisation.
4. **Minimal dependencies.** Prefer the standard library; add third-party
   dependencies only where they earn their place (Segno, Pillow).
5. **Transparent behaviour.** The application does exactly what it appears to
   do, with no hidden network calls, substitutions or tracking.
6. **No monetisation.** No payments, subscriptions, ads or upsells.
7. **No tracking.** No analytics, telemetry or scan logging.
8. **No unnecessary storage.** No database, no URL history by default, and no
   more local storage than the user explicitly asks for.
9. **Simple Ubuntu desktop experience.** A small, approachable Tkinter/ttk
   application, not an enterprise tool.
10. **Accurate documentation.** README, specification, backlog and memory
    describe reality, not aspiration.

---

## 3. Target users

People who occasionally need a reliable QR code for:

* Leaflets and flyers.
* Posters and signs.
* Event materials (tickets, programmes, table cards).
* Charity or community project publicity.
* Linking printed material or documents to a website.

This is a tool for individuals and small/community groups producing modest
volumes of printed material. It is not intended to provide enterprise account
management, bulk marketing campaign tooling, or scan-tracking dashboards.

---

## 4. Supported platforms

* **Ubuntu desktop** is the initial, actively supported and tested platform.
  Setup instructions (including the `python3-tk` system package) target
  Ubuntu specifically.
* **Other Linux distributions** with a working Python 3.11+ and Tkinter
  installation may well work, since nothing in the application is
  Ubuntu-specific, but this is not initially tested or guaranteed.
* **Windows and macOS** are not officially supported in this release. Because
  the application only depends on Tkinter, Segno and Pillow — all of which
  are available on those platforms — it may work from source, but this has
  not been tested or validated, and the documented setup steps (in
  particular the `apt install python3-tk` prerequisite) are Ubuntu-specific
  and do not apply. Official support for other platforms is a possible,
  unscheduled future enhancement (see `BACKLOG.md`, "Later or proposed
  items"), not a current commitment.

---

## 5. Functional requirements

Requirement IDs are stable once assigned. Do not renumber or reuse an ID.

### URL input

* **FR-001** — Accept non-empty URLs using the `http://` or `https://`
  scheme.
* **FR-002** — Reject empty input and unsupported or missing schemes (for
  example `ftp://`, `mailto:`, or plain text with no scheme).
* **FR-003** — Preserve the URL exactly as entered, with no unrequested
  modification. The only permitted normalisation is trimming leading and
  trailing whitespace, which must be documented wherever the behaviour is
  described.
* **FR-004** — Never contact the destination URL (no HTTP request, no DNS
  lookup, no reachability check) as part of validation or generation.
* **FR-005** — Never shorten, redirect through, or rewrite the URL via any
  first-party or third-party service.
* **FR-006** — Warn the user about unusually long URLs, since they produce
  denser, harder-to-scan QR codes. The threshold is 300 characters: above
  this length a warning is shown, but generation is not blocked (this is a
  **Warning**, not an **Error** — see §8).

### QR generation

* **FR-007** — Generate standards-compliant QR codes using Segno.
* **FR-008** — Generate a normal QR code rather than a Micro QR code,
  regardless of how short the input URL is.
* **FR-009** — Use an appropriate quiet zone: four modules on every side
  unless a documented, standards-based reason justifies a different value.
* **FR-010** — Default to error-correction level H wherever a central logo
  may be present, since the logo needs the redundancy budget.
* **FR-011** — Render modules as squares with integer pixel scaling (no
  fractional module sizes that would blur edges).
* **FR-012** — Avoid decorative module shapes (rounded dots, custom finder
  patterns, and so on) in the initial release.
* **FR-013** — Produce deterministic output from the same settings (same
  URL, colours, logo and size) wherever practical, so re-generation is
  predictable.

### Foreground and background colours

* **FR-014** — Default to a black foreground and white background.
* **FR-015** — Support choosing colours from a predefined palette.
* **FR-016** — Support a graphical colour picker.
* **FR-017** — Support direct HEX input.
* **FR-018** — Support direct RGB input.
* **FR-019** — Support direct CMYK input.
* **FR-020** — Keep all colour entry methods (palette, picker, HEX, RGB,
  CMYK) synchronised, so changing one updates the others consistently.
* **FR-021** — Store and process working colours internally as sRGB.
* **FR-022** — Make clear in the interface that CMYK input is converted to
  sRGB approximately, in the absence of an ICC colour profile.
* **FR-023** — Validate colour values on entry and show an understandable
  error for invalid values (for example a malformed HEX code, or an
  out-of-range RGB/CMYK component).
* **FR-024** — Warn when the chosen foreground/background combination has
  poor contrast. The threshold is a WCAG relative-luminance contrast ratio
  below 4.5:1 (the WCAG 2.x "AA" text minimum, adopted here as a
  documented, standard baseline in the absence of a QR-specific one).
* **FR-025** — Treat a dark foreground on a light background as the
  preferred, safest default relationship.
* **FR-026** — Prevent, or strongly warn against, colour combinations likely
  to be unreadable by a typical camera scanner.
* **FR-027** — Treat transparency conservatively: a transparent or
  near-transparent background must not be allowed to silently produce a
  code that fails to scan against arbitrary print or display backgrounds.

### Central image

* **FR-028** — Accept PNG, JPEG and JPG files as a central image.
* **FR-029** — Reject unsupported file types and corrupt image data cleanly,
  with a clear message, never an unhandled exception.
* **FR-030** — Preserve the image's aspect ratio when placing it.
* **FR-031** — Support transparent PNG images.
* **FR-032** — Place the image centrally over the QR code.
* **FR-033** — Provide a background clearance panel behind the image where
  needed, so the image does not sit directly on top of QR modules without
  separation.
* **FR-034** — Prevent the image from overlapping the QR code's finder
  patterns (the three large corner squares).
* **FR-035** — Default to a conservative image size relative to the
  overall code: 18% of the QR code's width.
* **FR-036** — Enforce a safe maximum image size, beyond which placement is
  refused or strongly blocked: 30% of the QR code's width, or the largest
  footprint geometrically guaranteed not to overlap the finder patterns
  for that specific QR code (FR-034), whichever is smaller.
* **FR-037** — Require error-correction level H whenever a central image is
  present.
* **FR-038** — Make clear to the user that high error correction alone does
  not make every image size safe to scan.
* **FR-039** — Never stretch or distort the image out of its original aspect
  ratio.
* **FR-040** — Never permanently modify the user's source image file; all
  resizing/compositing operates on an in-memory or temporary copy.

### Preview

* **FR-041** — Show a preview reflecting the currently selected URL, colours
  and logo.
* **FR-042** — Refresh the preview predictably whenever the user generates or
  changes a relevant setting.
* **FR-043** — Show validation warnings near the relevant controls or the
  preview itself.
* **FR-044** — Never present an invalid or failed generation as if it had
  succeeded.

### Export

* **FR-045** — Support exporting the generated QR code as PNG.
* **FR-046** — Support exporting the generated QR code as SVG.
* **FR-047** — Preserve the required quiet zone in exported files.
* **FR-048** — Never offer JPEG as an output format for the QR code itself
  (JPEG's lossy compression risks corrupting sharp module edges).
* **FR-049** — Offer a choice of useful PNG output dimensions: Small
  (512 px), Medium (1024 px) and Large (2048 px), each rendered at the
  nearest integer module scale to the target (FR-011).
* **FR-050** — Ensure SVG output is self-contained (embedded logo included)
  where technically practical, so the file remains usable without external
  references.
* **FR-051** — Prompt before overwriting an existing file on export.
* **FR-052** — Report export failures (for example, permission errors)
  clearly rather than failing silently.
* **FR-053** — Do not embed unnecessary personal information as file
  metadata in exported output.

### Scannability validation

* **FR-054** — Perform automated contrast checks on the chosen colours.
* **FR-055** — Perform automated quiet-zone checks.
* **FR-056** — Perform automated logo-size checks against the safe maximum.
* **FR-057** — Perform automated finder-pattern protection checks.
* **FR-058** — Perform automated QR decoding tests wherever practical, to
  confirm generated output actually decodes.
* **FR-059** — Run decoding tests against the actual generated PNG output,
  not only in-memory data structures.
* **FR-060** — Manually test on common Android and iPhone camera
  applications before any production-oriented release.
* **FR-061** — Test printed samples at realistic leaflet sizes as part of
  release validation.

Automated decoding is necessary wherever it is practical, but it does not by
itself guarantee that a printed, coloured, or logo-bearing code will scan
reliably in the real world; physical print-and-scan testing (FR-060, FR-061)
remains part of the release process.

### Preferences

Local preferences are optional/later scope, not required for an initial
release. If implemented, preferences:

* **FR-062** — MAY remember the last export directory, last selected
  colours, and last output dimensions.
* **FR-063** — MUST NOT include URL history by default.

---

## 6. Non-functional requirements

* **NFR-001** — Offline operation: no feature required for ordinary use may
  depend on network access.
* **NFR-002** — Privacy: URLs and images the user supplies are processed
  entirely locally and never transmitted anywhere.
* **NFR-003** — Performance: QR generation and preview refresh should feel
  immediate (well under a second) for typical inputs on typical desktop
  hardware.
* **NFR-004** — Lightweight installation: runtime dependencies are limited to
  Segno and Pillow; no heavy frameworks (web frameworks, ORMs, GUI
  toolkits beyond Tkinter) are introduced for convenience.
* **NFR-005** — Maintainability: the codebase keeps UI, models and services
  separated, with small, clearly named modules.
* **NFR-006** — Accessibility: primary controls are keyboard-operable, with
  visible labels and status text that does not rely on colour alone.
* **NFR-007** — Clear errors: ordinary invalid user input (bad URL, bad
  colour, bad image) must never leave an unhandled traceback as the only
  feedback.
* **NFR-008** — Security of local file handling: file paths and uploaded
  image content are handled defensively; the application does not trust a
  file's extension alone.
* **NFR-009** — No arbitrary code execution results from opening or
  processing an uploaded image file.
* **NFR-010** — No background network traffic occurs during ordinary
  operation.
* **NFR-011** — No telemetry of any kind is collected or transmitted.
* **NFR-012** — Reproducibility: identical inputs and settings produce
  identical output wherever practical.
* **NFR-013** — Testability: business logic (validation, colour conversion,
  QR generation, logo placement, export) is unit-testable independently of
  the Tkinter UI.
* **NFR-014** — All interface text and documentation use British English.
* **NFR-015** — The application shuts down cleanly when the main window is
  closed, with no hung processes or unhandled exceptions.
* **NFR-016** — Dependency and licence attribution in
  `THIRD_PARTY_NOTICES.md` is kept accurate as dependencies change.

---

## 7. User interface specification

The interface is a single main window, laid out compactly enough to remain
usable on a typical laptop display without scrolling, broadly organised as:

* URL input.
* Foreground colour controls.
* Background colour controls.
* Logo controls (file selection, remove/replace, size).
* Output settings (export dimensions/format choice).
* A "Generate" action.
* Export actions (PNG, SVG).
* A preview area.
* A status/warnings area.

A simple two-column arrangement (controls on one side, preview and status on
the other), or an equivalent compact single-window layout, is expected. This
specification does not prescribe pixel-perfect design, exact widget
placement, or a particular ttk theme.

The interface must remain usable on a typical laptop display (for example
1366×768) and should support keyboard navigation (Tab between controls,
Enter/Space to activate buttons) wherever Tkinter/ttk makes this practical.

---

## 8. Validation and warning levels

Three levels are used consistently across the application:

* **Error** — generation or export is blocked until the user corrects the
  problem. Example: an empty URL, an unsupported scheme, a corrupt image
  file, an invalid HEX/RGB/CMYK value.
* **Warning** — output can still be generated, but scan reliability may be
  reduced. Example: low foreground/background contrast, an unusually long
  URL, a large central logo.
* **Information** — explanatory guidance with no blocking effect. Example: a
  note that CMYK conversion is approximate, or that high error correction
  does not guarantee every logo size will scan.

---

## 9. Data and privacy

* URLs are processed entirely locally; they are never transmitted anywhere,
  and the destination is never contacted.
* Uploaded images are processed entirely locally.
* No information the user enters or uploads is transmitted over a network by
  this application.
* No database is required or used.
* URL history is not stored by default.
* Generated files are written to disk only where and when the user
  explicitly chooses to export.
* Any temporary files created during processing should be avoided where
  practical, and safely cleaned up when they are unavoidable.

---

## 10. File formats and colour model

* **PNG** is a raster output format: fixed pixel dimensions, suitable for
  screens and straightforward printing.
* **SVG** is a vector output format: scales to any size without pixellation,
  and is generally preferable for print design work.
* **JPEG** is accepted only as an *input* format for an uploaded central
  image; it is never used as QR output, because lossy compression risks
  corrupting sharp module edges.
* Working colours are represented internally as sRGB.
* CMYK input is converted to sRGB approximately, using a standard
  conversion formula, for screen preview and standard (non-professional)
  export. This is explicitly not a colour-managed, ICC-profile-based
  conversion.
* Professional ICC-profile-based print workflows are out of scope for the
  initial release.

---

## 11. Accessibility

* Primary controls (URL entry, colour inputs, logo selection, Generate,
  export actions) must be operable via keyboard.
* Labels are always visible; meaning is never conveyed by colour alone.
* Validation messages are written in plain, understandable language.
* Status text does not rely solely on red/green colouring to convey
  success or failure.
* Tab order follows a reasonable, predictable reading order through the
  window.
* The application should respect operating-system font and scaling
  settings where Tkinter's defaults permit this without additional work.

---

## 12. Error handling

The application must handle the following without an unhandled traceback as
the only feedback:

* Invalid URL (empty, wrong scheme).
* Invalid colour value (HEX, RGB or CMYK).
* Unsupported logo file format.
* Corrupt image file.
* Oversized image.
* Failed QR generation (for example, content too large to encode even at
  the lowest error-correction level).
* Failed export (for example, disk full, invalid path).
* Filesystem permission errors.
* A missing optional dependency, if one is ever introduced.
* Any other unexpected internal error, which must degrade to a clear status
  message rather than crashing the application outright.

---

## 13. Testing strategy

* **Unit tests** for validation, colour conversion, and other pure logic.
* **Service-level tests** for QR generation, logo placement and export,
  independent of the Tkinter UI.
* **Export tests** confirming PNG and SVG files are written correctly and
  are re-openable/parseable.
* **QR decoding tests** confirming generated output decodes back to the
  exact source URL, wherever a decoding dependency is available.
* **Manual UI testing** of the primary workflow (enter URL, generate,
  adjust colours/logo, export).
* **Physical print-and-scan testing** at realistic leaflet sizes, on common
  Android and iPhone camera apps, before any production-oriented release.
* **Regression tests** for every previously fixed defect, so it cannot
  silently reappear.

---

## 14. Packaging and distribution

The intended eventual approach is a standalone Ubuntu build using
PyInstaller (or another lightweight, equivalent method, if PyInstaller
proves unsuitable — any change of approach must be recorded in
`MEMORY.md`). As of this specification, **no packaging has been built or
validated**; this section describes the target, not current capability.

Intended stages:

1. **Running from source** — the currently working method: clone the
   repository, create a virtual environment, `pip install -e ".[dev]"`, run
   `python -m qr_code_generator`. Requires the Ubuntu system package
   `python3-tk`.
2. **Virtual environment installation** — as above; no Poetry, Conda or
   Docker requirement.
3. **Standalone executable or application bundle** — a later milestone (see
   `BACKLOG.md` QRG-019), not yet attempted.
4. **Licence and third-party notices distributed with packaged builds** —
   `LICENSE` and `THIRD_PARTY_NOTICES.md` must be included alongside any
   packaged build once packaging exists.

---

## 15. Out of scope

The following are explicitly excluded from this project, not merely
deferred:

* Dynamic QR codes.
* Hosted redirects.
* URL shortening.
* Scan analytics.
* User tracking.
* User accounts.
* Cloud storage.
* Databases.
* Network services (the application is not a server and does not expose
  one).
* Advertising.
* Monetisation of any kind.
* QR content types other than URLs (for example contact cards, Wi-Fi
  credentials, plain text, email/telephone links, or other barcode
  formats).
* A mobile application.
* Professional print-shop colour management (ICC profiles) in the initial
  release.
* QR styling templates (decorative module shapes/themes).
* Animated QR codes.
* Batch generation of multiple codes in one operation.
* Cloud synchronisation.
* Account-based preferences.
* Scan statistics.

---

## 16. Release criteria

An initial usable version is release-ready only when all of the following
hold, with evidence (not merely code presence):

1. Valid HTTP/HTTPS URLs generate QR codes containing the exact input URL.
2. Foreground and background colour selection works end-to-end (palette,
   picker, HEX, RGB, CMYK, synchronised).
3. Central logo placement is implemented and conservatively constrained
   (safe default and maximum size, finder-pattern protection).
4. PNG and SVG export both work, with overwrite confirmation and clear
   failure reporting.
5. Automated tests pass (`pytest`).
6. `ruff check` and, where configured, `ruff format --check` pass.
7. Generated outputs decode successfully in automated decoding tests.
8. Manual testing succeeds on both a common Android and a common iPhone
   camera application.
9. Printed, leaflet-sized examples scan reliably, including coloured and
   logo-bearing variants.
10. Documentation (`README.md`, this specification, the backlog and
    memory) matches actual behaviour.
11. `LICENSE` and `THIRD_PARTY_NOTICES.md` are present and accurate.
12. No network requests occur during ordinary operation.

None of these criteria are met in full as of this document's creation; see
`BACKLOG.md` and `MEMORY.md` for the current, evidence-based state.
