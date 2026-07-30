# Third-Party Notices

This project uses the following third-party libraries. Their original
licence notices remain applicable to any redistribution of this software and
are not superseded by this file.

## Segno

* **Purpose:** QR code generation.
* **Homepage:** <https://pypi.org/project/segno/>
* **Licence:** BSD 3-Clause Licence.

## Pillow

* **Purpose:** Image handling and generation of preview bitmaps.
* **Homepage:** <https://pypi.org/project/Pillow/>
* **Licence:** MIT-CMU Licence (the historical PIL Software Licence).

## zxing-cpp

* **Purpose:** Development-only dependency, used solely in automated tests
  to confirm generated QR codes (including logo-bearing ones) decode back
  to the exact source URL. Not required at runtime and not bundled with
  the application.
* **Homepage:** <https://github.com/zxing-cpp/zxing-cpp>
* **Licence:** Apache License 2.0.

Consult each project's own repository or PyPI page for the full, current
licence text.
