# BOXEDOFF

Premium 10ft storage container hire — delivered to the drive, collected when the hire ends.

- **Live site (preview):** `site/index.html` — storage booking, postcode check, guide pricing from £50/week.
- **Brand book:** `brand/index.html` — three brand directions (Stamp is the customer-facing direction).
- **Handover:** `memory.md` — decisions and history for agents.

## Run locally

From the repo root:

```bash
python -m http.server 8766
```

Open [http://127.0.0.1:8766/site/](http://127.0.0.1:8766/site/) for the landing page and [http://127.0.0.1:8766/brand/](http://127.0.0.1:8766/brand/) for the brand presentation.

## Structure

| Path | Purpose |
|------|---------|
| `site/` | Public storage hire site, favicons, `robots.txt`, `sitemap.xml` |
| `brand/` | Brand presentation and unit photography |
| `memory.md` | Project log |

Canonical domain (when live): `https://boxedoff.uk/`
