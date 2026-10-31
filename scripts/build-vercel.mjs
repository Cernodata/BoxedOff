import {
  cpSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  rmSync,
  writeFileSync,
  existsSync,
} from "node:fs";
import { join } from "node:path";

const root = process.cwd();
const dist = join(root, "dist");

function resolveGaId() {
  if (process.env.GA_MEASUREMENT_ID) return process.env.GA_MEASUREMENT_ID.trim();
  const cfgPath = join(root, "ga4.config.json");
  if (existsSync(cfgPath)) {
    try {
      const cfg = JSON.parse(readFileSync(cfgPath, "utf8"));
      if (cfg.measurementId) return cfg.measurementId;
    } catch {
      /* ignore */
    }
  }
  return "";
}

const gaId = resolveGaId();

rmSync(dist, { recursive: true, force: true });
mkdirSync(dist, { recursive: true });

const brand = join(root, "brand");
cpSync(brand, join(dist, "brand"), {
  recursive: true,
  filter: (src) =>
    !src.includes("print-pack") &&
    !src.endsWith("BOXEDOFF-brand-pack.zip") &&
    !src.endsWith("CUBEDROP-brand-pack.zip"),
});

for (const name of readdirSync(join(root, "site"))) {
  const src = join(root, "site", name);
  const dest = join(dist, name);
  if (name === "consent.js") {
    let js = readFileSync(src, "utf8");
    js = js.replace(/__CD_GA_MEASUREMENT_ID__/g, gaId);
    writeFileSync(dest, js);
    continue;
  }
  cpSync(src, dest, { recursive: true });
}

if (gaId) {
  console.log("Build: GA_MEASUREMENT_ID injected into consent.js");
} else {
  console.warn("Build: no GA_MEASUREMENT_ID — analytics disabled until env or ga4.config.json");
}
