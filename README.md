# QR Code Generator

A lightweight, offline QR code generator for Ubuntu desktops.

## Project status

This repository is an **early project skeleton**. It currently provides a
minimal working vertical slice — entering a URL and generating a plain
black-on-white QR code — on top of a clean architecture intended to support
the fuller feature set described below. It is **not yet ready for production
printing or general use**. A detailed specification and backlog will be added
separately to guide the remaining work.

## Purpose

The goal is a simple desktop tool that lets someone:

* Enter an HTTP or HTTPS URL.
* Generate a static QR code containing that exact URL.
* Choose foreground and background colours (palette, colour picker, RGB,
  CMYK or HEX).
* Add an optional central PNG, JPEG or JPG image.
* Export the result as PNG and SVG.

All of this is intended to work entirely offline, with no accounts,
tracking, subscriptions, redirects, analytics or monetisation.

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

* A Tkinter/ttk desktop window titled "QR Code Generator" with a URL field, a
  Generate button, a preview area and a status message.
* Validation that the URL field is not empty and starts with `http://` or
  `https://`.
* Generation of a conventional black-on-white QR code (using
  [Segno](https://pypi.org/project/segno/)) with a standard quiet zone and
  error-correction level H, displayed in the preview area.

## Current limitations

The following are **not yet implemented**:

* Central logo overlay (PNG/JPEG/JPG).
* Colour palette, colour picker, RGB or CMYK selection.
* PNG or SVG export.
* Any preferences or settings storage.
* Automated QR decoding/verification.
* Packaging into a standalone executable.
* Professional print colour management.
* Update checking, analytics or any network access.

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

## Running Ruff

```bash
ruff check .
ruff format --check .
```

## Licence

This project is licensed under the MIT Licence — see [LICENSE](LICENSE).
Third-party library attribution is in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
