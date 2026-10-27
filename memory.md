## 2026-10-27 — Email

The public address is drop@cubedrop.co.uk. It sits under the phone in the hero, the close, and the footer, and on the LocalBusiness details.

## 2026-10-27 — TM on the site logo

The nav wordmark now reads CUBE DROP with a small TM, same as the brand lockup. The company name in the footer stays Cube Drop Limited.

## 2026-10-27 — How much the cube holds

The FAQ now says the cube is about 2.6 metres high and holds about 16 cubic metres inside: a one-bedroom flat, not a whole house. The cube section says the same.

## 2026-10-27 — Headline says what it is

The hero H1 is now “A storage cube, at your door.” The line under it names the secure 10ft cube, delivery and collection, the free trip, £100 a week, dry inside, and optional shelving.

## 2026-10-27 — Deposit and cancellation list

A £50 deposit on the phone secures the cube. Nothing is charged on the page. Under the dates, if the week is gone, people leave the day, the weeks, a name and a phone for the cancellation list. The out-of-area email list is unchanged. Neither form sends anywhere yet.

## 2026-10-27 — Favicon, SEO, and the phone

Favicon is linked at `/favicon.ico`, `/favicon.svg`, and `/favicon-32.png`, and the same files sit at the repo root so the local preview can load them. Title is “10ft storage cube hire from £100 a week | Cube Drop”. The hero says 10ft. 01565 662244 sits under the postcode box, in the price panel, the close, and the footer. The nav stays one line. FAQ schema matches the page, including how to book.



The site photos are a full-size 10ft corrugated cube, not the small cabinet. Files: `brand/media/cube-hero.jpg` and `brand/media/cube-door.jpg`. Contact on the page is Cube Drop Limited, 01565 662244.



New photos are `brand/media/cube-hero.jpg` and `brand/media/cube-door.jpg`. Charcoal cube, orange corner, bamboo bay, real Cube Drop stacked logo composited on the end. The old `bamboo-unit.jpg` path is no longer used on the page.



Backup of the previous wording is `backups/index-2026-10-27.html` and `backups/wording-2026-10-27.md`. Hero stays “Don’t visit your storage.” The rest of the page was rewritten in that voice. “A brighter tomorrow” is gone. Fit numbers are unchanged: 2.44m cube, 2.8m gap, flat ground. Price is still £100 a week, delivery free, one week minimum.



Hero H1 is “Don’t visit your storage.” The line under it says the cube comes to the door and is collected, the trip is free, £100 a week from one week, it stays dry, and shelving is optional. The kicker stays “Storage to you”.

## 2026-10-27 — Cube, not box

The product name on the site is cube. Customer copy, the H1, FAQs, and the offer schema say cube. CSS class names are unchanged.

## 2026-10-27 — Price and product language

£100 a week. Delivery and collection are free. Minimum hire is 1 week, maximum still 26. The product is a secure storage box, not a container. Anti-moisture and condensation treatment is included. Shelving is optional. White-glove delivery to the door. `RATES` in `site/index.html` is storage 100, delivery 0, min 1.

## 2026-10-27 — On-page fit and headline

H1 is “Storage container for hire, delivered to you.” Fit guide: the unit is 2.44m wide, the clear gap is 2.8m, and the ground must be flat and firm. FAQs match that.

## 2026-10-27 — Storage only

Cube Drop is a storage-to-you service. The line under the name is STORAGE. Care and Living are off the site, the brand page, and the print pack.

## 2026-10-27 — Cube Drop

The customer name is Cube Drop. Orange `#FF7A00`, charcoal `#1A1A1A`, Montserrat, isometric cube. Site and `brand/index.html` use it. Print pack is `brand/CUBEDROP-brand-pack.zip`. Rebuild with `brand/print-pack/build_pack.py`. The live domain is still boxedoff.uk.

## 2026-10-15 — Print pack for decals and stationery

Stamp lockups outlined from Bricolage Grotesque, open frame filled (not a stroke). Pack is `brand/BOXEDOFF-brand-pack.zip` (svg, pdf, eps, png, spec). Rebuild with `brand/print-pack/build_pack.py`. Vercel build skips `print-pack` and the zip.

## 2026-10-07 — Vercel and security

Postcode check shows a feedback card, button spinner, input border states, and a brief success pulse when the round matches.

Vercel runs `npm run build` → `dist/` with `index.html` at the deploy root plus `brand/`. Do not set dashboard Output Directory to `site`. `/site/*` redirects to `/`. Security headers in `vercel.json`. `.vercelignore` drops `memory.md`.

## 2026-10-07 — GitHub

Repository: https://github.com/Cernodata/BoxedOff (public). `README.md` and `.gitignore` at repo root. Push with `git -c safe.directory=W:/Cursor/BoxedOff push` if on the W: drive.

## 2026-10-07 — amperee-demo

Created private GitHub repo: https://github.com/Cernodata/amperee-demo. Source lives at `W:\Cursor\Caravan System` (Vite/React Amperee demo). Pushed `main` with `vercel.json` security headers, CSP, `robots.txt` noindex, `.vercelignore`.

## 2026-10-07 — Three brand directions

Built a brand presentation at `brand/index.html`. Open it in a browser. Photographs live in `brand/media/`.

Three directions, not three logo variants:

- **01 The Plan** — architectural luxury. Floor-plan mark with an open door. Graphite unit, timber bay, bronze jamb plate. Quiet on the driveway.
- **02 The Stamp** — disruptive consumer brand. Heavy open-frame icon, kiln orange `#E8421A` corner stripe, black body. The truck shouts; the unit does not.
- **03 The Threshold** — warm premium living. Doorway mark, warm greige, bamboo bay. Solid door for Storage, glazed door for Care and Living.

Shared decisions:

- Master treatment is **BOXEDOFF**: one word, capitals, no space. No cube around the word.
- Divisions are STORAGE, CARE, LIVING under the same mark.
- Driveway branding stays small (“the quiet ask”). Recognition comes from a physical signature, not a billboard.

Recommendation in the presentation: build **The Threshold**. It is the only direction that fits premium storage and temporary care without a costume change.

## 2026-10-07 — Landing page preview

Built `site/index.html` on The Threshold.

- Homepage books storage. Care is a second door into the same reserve flow.
- Guide prices, not a quote: storage £95/week, bathroom £175/week, delivery and collection £149, minimum 2 weeks, dates from 7 days ahead.
- Postcode check, then calendar, then “Reserve these dates”. Nothing is charged in the preview.
- Covered outward codes in the mock: WA14, WA15, WA16, SK7, SK8, SK9, SK10, SK11, M33, CW4.
- Copy answers fit and permission before the commitment. Real rates, deposit rule, and coverage still need the business to confirm.

## 2026-10-07 — Site shifted off The Threshold

The Threshold landing page looked beautiful and read like an interiors brand. The product is a 10ft unit that arrives, stays, and leaves.

`site/index.html` now leads with “Need space? BOXEDOFF.” Black, kiln orange, the open frame, and the black unit photograph. Care uses the same line: “Bathroom downstairs? BOXEDOFF.” Booking flow is unchanged. Guide prices are still samples.

Confirmed: this direction is the one to keep. The quiet interiors version is not.

## 2026-10-07 — Bamboo bay, still a steel box

Site photos now show one bamboo bay on the black unit, plus the orange corner. The rest stays painted corrugated steel. Care uses the same shell with a glazed door. Bamboo is a replaceable panel, not a timber rebuild. Files: `brand/media/bamboo-unit.jpg`, `brand/media/bamboo-care.jpg`.

A small plate sits at the base of the orange corner: NEED ONE?, a QR to https://boxedoff.uk, and the URL. Not a billboard. Plate asset: `brand/media/need-one-plate.png`.

## 2026-10-07 — Photo shape and phone layout

The unit photo was stuck at 720px tall, so it squashed when the column got narrower. Images now keep their shape. On a phone the hero photo is landscape, sections stack, and the delivery button is full width.

## 2026-10-07 — Favicon

The tab icon is the open frame: kiln orange on black. Files sit beside the page: `site/favicon.svg`, `site/favicon.ico`, `site/favicon-32.png`, `site/apple-touch-icon.png`.

## 2026-10-07 — Site sections and on-page SEO

`site/index.html` now has uses, the unit, how it works, warehouse-versus-skip, the Cheshire round, fit and permission, FAQ, and a closing call to action. Booking is unchanged.

UK keyword data (DataForSEO, October 2026) set the language. Primary phrase: “storage container for hire”, about 1,600 searches a month, difficulty 3. “House move storage” is about 590. “Storage during a renovation” and “temporary storage during renovation” are smaller and lightly contested, about 140 and 110. “10ft storage container” is about 210. Town-plus-hire phrases for Knutsford and Alderley Edge have no measurable volume, so the towns stay in the areas section rather than the title. “Garden storage container” was ignored: high volume, but it is retail boxes. Canonical is https://boxedoff.uk/. `site/robots.txt` and `site/sitemap.xml` match that.

## 2026-10-07 — Free postcode radius, £50 a week

Postcode checks use Postcodes.io (free, no key, fair use). A postcode is in range when it is within 12 km of the centroid of Knutsford, Alderley Edge, Wilmslow and Holmes Chapel (53.2833, -2.3000). Holmes Chapel is the furthest centre, at 9.8 km, so 12 km keeps those towns inside. Weekly hire is £50. Delivery and collection stay £149.

## 2026-10-07 — Site is storage only

Bathroom and care copy, the product switch, and the care section are off `site/index.html`. The page books a 10ft store. Care can return later as its own path.
