# QR Code Generator

A lightweight, offline QR code generator for Ubuntu desktops.

## Project status

Core functionality is substantially complete: entering a URL, choosing
colours, adding a central logo, and exporting as PNG or SVG all work
end-to-end today, with an automated test suite (including QR-decoding
verification) behind them. What remains before a production-oriented
release is physical print-and-scan validation on real devices and paper,
standalone packaging, and continuous integration — see
[BACKLOG.md](BACKLOG.md) for exactly what's done and what's left. This
project is **not yet packaged for distribution** and has **not yet
completed physical print-and-scan testing**, so treat printed output as
provisional until that validation is done.

A detailed specification, delivery backlog, contributor rules and durable
project memory live alongside this README:

* [SPECIFICATION.md](SPECIFICATION.md) — the intended, approved product
  and technical specification.
* [BACKLOG.md](BACKLOG.md) — the authoritative, evidence-based delivery
  status for every piece of work, milestone by milestone.
* [AGENTS.md](AGENTS.md) — mandatory rules for anyone (human or AI)
  contributing to this repository.
* [MEMORY.md](MEMORY.md) — durable decisions, validated commands and the
  project's Definition of Done.

## Purpose

The goal is a simple desktop tool that lets someone:

* Enter an HTTP or HTTPS URL.
* Generate a static QR code containing that exact URL.
* Choose foreground and background colours (palette, colour picker, RGB,
  CMYK or HEX).
* Add an optional central PNG, JPEG or JPG image.
* Export the result as PNG and SVG.

All of this works entirely offline, with no accounts, tracking,
subscriptions, redirects, analytics or monetisation.

### Static QR codes vs redirect services

A **static QR code**, which is what this project produces, encodes the exact
URL you enter directly in the code itself. It works forever, for free, and
does not depend on any third party. This is different from commercial
"dynamic" QR services, which encode a short link to their own server and
then redirect the scanner to your real URL. Those services typically require
an account or subscription, can stop working if you stop paying or the
provider shuts down, and can track or log every scan. This project
deliberately avoids that model.

## Current functionality

* A Tkinter/ttk desktop window titled "QR Code Generator": a URL field,
  foreground and background colour controls, an optional logo picker,
  export controls, a live preview and a status/warnings message.
* URL validation: must be non-empty and start with `http://` or
  `https://`; leading/trailing whitespace is trimmed (the only
  normalisation applied — the rest of the URL is preserved exactly); a
  non-blocking warning appears for unusually long URLs (over 300
  characters). Validation never contacts the destination or any network.
* QR generation via [Segno](https://pypi.org/project/segno/), always at
  error-correction level H with a standard four-module quiet zone, and a
  live-refreshing preview whenever a setting changes.
* Foreground and background colour selection: a predefined palette, a
  native colour picker, and direct HEX/RGB/CMYK entry — all kept in sync,
  since every entry method converts through the same internal sRGB colour.
  A warning appears for low-contrast or unconventional (light-on-dark)
  colour pairings; generation is never blocked by it.
* An optional central logo (PNG, JPEG or JPG): validated by its actual
  image content, not its filename; placed centrally with a matching
  background clearance panel; kept clear of the QR code's finder patterns
  by construction; sized with an adjustable slider (5%–30%) that warns
  when a request has to be reduced for safety, or when a size is merely
  large rather than unsafe. The logo file itself is never modified.
* Export as PNG (Small/Medium/Large presets, each freshly rendered at a
  crisp integer module scale — not a resized preview) or SVG (true vector
  QR modules, with any logo embedded as a self-contained base64 image).
  Both suggest a sensible, filesystem-safe default filename derived from
  the URL, and use the native save dialog's own overwrite confirmation.

## Current limitations

The following are **not yet implemented**:

* Any preferences or settings storage (including remembering the last
  export directory — a deliberate choice pending a separate decision, not
  an oversight).
* Packaging into a standalone executable.
* Professional, ICC-profile-based print colour management.
* Continuous integration.
* A completed physical print-and-scan test matrix (Android + iPhone,
  on-screen + printed, several lighting conditions) — see
  [BACKLOG.md](BACKLOG.md) `QRG-016` for exactly what has and hasn't been
  tested so far.

Update checking, analytics, tracking and any other network access are not
"not yet implemented" — they are permanently out of scope by design.

## Ubuntu prerequisites

Tkinter is provided by the operating system rather than PyPI. Install it
before setting up the project:

```bash
sudo apt install python3-tk
```

Python 3.11 or later is required.

## Environment setup

Using a virtual environment and pip (no Poetry, Conda or Docker required):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Running the application

```bash
python -m qr_code_generator
```

## Running the tests

```bash
pytest
```

The suite includes unit tests for validation, colour conversion, QR
generation, logo placement and export, plus automated QR-decoding checks
(via a development-only dependency) confirming generated codes — plain,
coloured, and logo-bearing alike — decode back to the exact source URL.

## Running Ruff

```bash
ruff check .
ruff format --check .
```

## Licence

This project is licensed under the MIT Licence — see [LICENSE](LICENSE).
Third-party library attribution is in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
