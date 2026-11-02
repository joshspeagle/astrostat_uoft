# `docs/`

Design specifications, token checks, and icon generator utilities for the ART website.

## Contents

- **[`DESIGN.md`](./DESIGN.md)** — Canonical visual design specification: color tokens (`scss/_tokens.scss`), typography (`Urbanist` + `Inclusive Sans`), two-column rail layout, component rules (`People` cards, `Research` blocks, `Home` hero and pathways), and icon geometry.
- **[`check_tokens.py`](./check_tokens.py)** — Verifies the color palette in `scss/_tokens.scss` against WCAG contrast floors (`4.5:1` for text, `3.0:1` for graphical marks) in both light and dark themes, and checks that no hex color values appear in other SCSS partials. Run with:
  ```bash
  python3 docs/check_tokens.py
  ```
- **[`design/icons/`](./design/icons/)** — Python generator scripts (`icons.py`, `brand.py`, `mkog.py`, `measure.py`, `build.py`) and geometric notes (`NOTES.md`) that produce the shipped theme icons (`svg/themes-sprite.svg`), brand mark (`svg/art-mark.svg`), favicons (`ico/`), and OpenGraph card (`static/og-image.png`).
