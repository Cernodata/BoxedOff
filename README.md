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

## Deploy on Vercel

1. Import **https://github.com/Cernodata/BoxedOff** in [Vercel](https://vercel.com/new).
2. **Framework Preset:** Other. Build command and output directory come from `vercel.json` (`npm run build` → `dist/`).
3. In Project → Settings → General, leave **Root Directory** blank. If **Output Directory** is set in the dashboard, clear it so `vercel.json` wins.
4. Add domain **boxedoff.uk**, then redeploy.
5. Homepage is `/`. Brand book is `/brand/`.

Security: `vercel.json` sets HSTS, CSP, frame denial, and nosniff. Postcode lookup calls **Postcodes.io** over HTTPS only. No API keys in the repo. `memory.md` is excluded from deploy via `.vercelignore`.
