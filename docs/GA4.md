# Cube Drop — Google Analytics 4

## IDs

| | |
|--|--|
| Property | `561711191` (Cube Drop Website) |
| Measurement | `G-VNP2ZTELH7` |
| Stream | https://www.cubedrop.co.uk |

Service account (read API): `cursor-analytics@model-aria-502620-r2.iam.gserviceaccount.com` — add as **Viewer** on the GA4 property.

## Vercel

Set environment variable (Production + Preview):

```bash
GA_MEASUREMENT_ID=G-VNP2ZTELH7
```

Redeploy. Build injects the ID into `dist/consent.js`.

Local build uses `ga4.config.json` if env is unset.

## Consent

`site/consent.js` — no GA loads until the user accepts analytics. Consent Mode v2 defaults denied, then granted on accept.

## Events

| Event | When |
|-------|------|
| `page_view` | Each page load (after consent) |
| `postcode_check` | Postcode lookup result |
| `booking_step` | Funnel steps 1–4 |
| `pricing_update` | Hire weeks changed |
| `select_delivery_date` | Calendar day chosen |
| `form_submit` | Form attempt / success |
| `generate_lead` | Reserve or cancellation list success |
| `join_waitlist` | Out-of-area email |
| `navigation_click` | Nav links |
| `contact_click` | Phone / email links |
| `cta_click` | Hero check delivery |

Mark `generate_lead` and `join_waitlist` as conversions in GA4 Admin.
