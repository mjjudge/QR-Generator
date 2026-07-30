# AGENTS.md — Mandatory Contributor Instructions

These instructions bind any coding agent (and are strongly recommended for
any human contributor) working in this repository. `MUST`/`MUST NOT` are
non-negotiable; `SHOULD` is a strong default that needs a stated reason to
deviate from; `MAY` is a genuine option.

## Authority and precedence

When instructions conflict, resolve them in this order:

1. **Explicit user instruction** for the current task.
2. **`AGENTS.md`** (this file).
3. **`SPECIFICATION.md`**.
4. **`BACKLOG.md`**.
5. **`MEMORY.md`**.
6. **Existing implementation and code comments.**

A conflict between these sources MUST be reported to the user and resolved
explicitly. Agents MUST NOT silently guess which source wins, and MUST NOT
silently "fix" a conflict by editing documentation to match code (or code to
match documentation) without flagging it.

## Required workflow

Every task follows: **plan → change → validate → document → report.**

1. **Inspect** — read the relevant existing files before changing anything.
2. **Understand** — identify the applicable `BACKLOG.md` item (or state that
   none exists and one should be created).
3. **Plan** — state the intended change before substantial implementation,
   especially for anything non-trivial.
4. **Change** — make focused changes. Avoid unrelated refactoring.
5. **Validate** — run the relevant tests and lint checks (see "Testing
   requirements" below).
6. **Review** — review the final diff before reporting completion.
7. **Document** — update `README.md`, `SPECIFICATION.md`, `BACKLOG.md`
   and/or `MEMORY.md` in the *same* change whenever behaviour, scope or
   architecture changes.
8. **Commit** only when requested or explicitly permitted.

Agents MUST report incomplete validation honestly (e.g. "tests not run
because X") rather than implying success.

## Backlog discipline

* `BACKLOG.md` is the authoritative delivery record for this project.
* New work MUST be tied to a stable backlog ID (`QRG-NNN`); if none exists,
  propose one as part of the change.
* Status MUST NOT be changed to **Complete** without evidence (tests run,
  manual checks performed, documentation updated).
* Partially satisfied acceptance criteria MUST NOT be reported as complete.
* Blockers MUST be recorded on the relevant backlog item as **Blocked**,
  with the reason.
* Scope discovered mid-task SHOULD become a new backlog item rather than
  being silently folded into the current change.
* One focused backlog item per change is preferred.

## Safety and product invariants

These MUST be preserved in every change, without exception:

* Encode the exact user-provided URL — nothing else.
* Never substitute a third-party redirect, shortener or tracking link for
  the user's URL.
* Never add tracking, analytics or telemetry.
* Never require an account.
* Never require a subscription.
* Never introduce monetisation (ads, payments, upsells).
* Never transmit the URL or an uploaded logo over a network.
* Never contact the destination URL during generation or validation.
* Never add a database without an explicit, approved architectural change
  recorded in `MEMORY.md`.
* Never add a web server or cloud dependency without explicit approval.
* Never store URL history by default.
* Scannability takes priority over visual customisation whenever the two
  are in tension.
* The quiet zone and finder patterns MUST remain protected in every code
  path that produces output (preview and export alike).
* Ordinary invalid input MUST be handled with a clear message, never only
  an unhandled traceback.

## Architecture boundaries

* UI code (`ui/`) coordinates; it MUST NOT contain business logic.
* URL validation belongs in `services/validation_service.py`.
* Colour conversion and validation belong in `services/colour_service.py`.
* QR creation belongs in `services/qr_service.py`.
* Logo handling belongs in `services/logo_service.py`.
* Export belongs in `services/export_service.py`.
* Shared configuration/data passed between layers belongs in typed
  dataclasses under `models/` (see `models/qr_settings.py`).
* Circular imports MUST be avoided.
* Global mutable state SHOULD be avoided.
* New dependencies require a stated justification and MUST be recorded in
  `THIRD_PARTY_NOTICES.md` and `pyproject.toml`.
* Heavy frameworks (web frameworks, ORMs, DI containers, alternative GUI
  toolkits) MUST NOT be introduced for convenience.

## Coding standards

* Use Python type hints throughout.
* Prefer small, focused functions and modules over large ones.
* Use clear, descriptive names.
* Use British English in all interface text, docstrings and comments.
* Docstrings should be concise and explain the *why*/architectural role for
  public classes, functions and module boundaries — not restate the code.
* No speculative abstractions (no design patterns, plugin systems or
  configuration layers not needed by the current, actual requirement).
* No commented-out code.
* No secrets or credentials committed, ever.
* No generated build artefacts, virtual environments, or IDE-specific state
  committed (respect `.gitignore`; extend it rather than working around
  it).
* Use `pathlib` for filesystem paths where practical.
* Handle file and image errors safely and explicitly.
* Do not trust a file's extension alone when validating an uploaded image —
  validate the actual content.

## Testing requirements

Tests are required for:

* New service behaviour.
* Defect fixes (as a regression test).
* Boundary conditions (empty input, maximum sizes, edge values).
* Invalid input handling.
* Exact URL encoding (the decoded/encoded content must match the source
  URL precisely).
* Colour conversion correctness.
* Logo sizing rules.
* Export correctness.

UI-only manual testing is **not** sufficient for any logic that can be
tested below the UI layer — if it can be a service-level test, it MUST be
one, in addition to any manual UI check.

Run, at minimum, the commands recorded as validated in `MEMORY.md`
("Validated commands"), which currently are:

```bash
pytest
ruff check .
ruff format --check .
```

Do not hard-code different commands that conflict with `pyproject.toml`.
If the validated commands change (for example, a new lint rule set, a new
test path), update `MEMORY.md` in the same change.

## QR reliability rules

* Use a normal QR code, not a Micro QR code, especially whenever logo
  functionality is involved.
* Use error-correction level H whenever a central logo may be present.
* Preserve a four-module quiet zone unless a documented, standards-based
  reason justifies otherwise.
* Use integer-scaled modules; never blur-resize a generated QR image.
* Never export the QR code itself as JPEG.
* Keep logo sizing conservative and never allow finder-pattern overlap.
* Treat dark-on-light as the safest default colour relationship.
* Automated decoding tests are necessary wherever practical, but they do
  NOT replace physical print-and-scan testing before a production-oriented
  release.

## Dependency rules

* Prefer the Python standard library where it reasonably covers the need.
* Runtime dependencies must stay minimal and justified.
* Development-only tools (test/lint tooling, decoding libraries used only
  for testing) stay as development dependencies, not runtime ones.
* Licences of any new dependency must be compatible with MIT distribution.
* `THIRD_PARTY_NOTICES.md` MUST be updated in the same change whenever
  dependencies change.
* Any network-enabled or telemetry-enabled dependency requires explicit,
  separate review and approval before use — this is a high bar given the
  project's offline-first, no-telemetry invariants.

## Documentation rules

* Documentation drift is a defect, not a low-priority cleanup item.
* `README.md` describes current, actual, user-facing reality only.
* `SPECIFICATION.md` describes intended, approved behaviour — it is not a
  status report.
* `BACKLOG.md` describes delivery state, with evidence.
* `MEMORY.md` records durable facts and decisions, not a chronological log.
* Comments explain *why*, never restate what the code obviously does.
* Never claim unvalidated support for a platform, format or feature.

## Git discipline

* Review `git status` before and after making changes.
* Do not overwrite unrelated local changes.
* Do not use destructive Git commands (`reset --hard`, `checkout --`,
  `clean -f`, force-push, branch deletion) without explicit instruction.
* Do not force-push.
* Do not push unless asked.
* Do not commit secrets, generated files, or local environment files
  (`.venv/`, caches, build artefacts).
* Prefer one focused commit per backlog item.
* Reference the backlog ID in the commit message where practical (for
  example, `QRG-004: warn on unusually long URLs`).
* Committing a change is not the same as completing it — a backlog item is
  only Complete once `MEMORY.md`'s Definition of Done is satisfied.

## Completion report

At the end of a task, report:

* The backlog item(s) addressed.
* Files changed.
* What behaviour changed, in plain terms.
* Tests run and their results.
* Manual validation performed, if any.
* Documentation updated.
* Known limitations remaining within the item's scope.
* Remaining work, if the item is not fully complete.
* Any assumptions made.
