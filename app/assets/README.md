# app/assets

Runtime assets the application reads from disk. Everything here must be small, web/PDF-usable, and
deployable — this directory ships inside the Docker image via `COPY app ./app`.

| File | Used by | Source |
|---|---|---|
| `dxc-brand-mark-dark.svg` | `app/pdf.py` → `_logo_flowable()` | `assets/DXC Logo/Brand Mark/1 Color/RGB/DXC-1-Color-Dark.svg` |

## Why this is a copy

`assets/` at the repository root holds the full DXC brand kit — 62 files, 20 MB, mostly `.eps` print
masters in CMYK. None of that is usable at runtime and none of it belongs in a container image. So
the single SVG the PDF generator needs is vendored here instead, and the brand kit stays put as the
source of truth for design work.

**If the brand kit is ever updated, this copy does not follow.** Re-copy it:

```bash
cp "assets/DXC Logo/Brand Mark/1 Color/RGB/DXC-1-Color-Dark.svg" \
   app/assets/dxc-brand-mark-dark.svg
```

## Note on failure mode

`_logo_flowable()` in `app/pdf.py` catches every exception and returns `None`, so a missing or
unparseable file **silently drops the logo from the generated PDF** — no error, no log line. If a
scorecard comes out unbranded, check this file first.
