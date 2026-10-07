import { cpSync, mkdirSync, readdirSync, rmSync } from "node:fs";
import { join } from "node:path";

const root = process.cwd();
const dist = join(root, "dist");

rmSync(dist, { recursive: true, force: true });
mkdirSync(dist, { recursive: true });

cpSync(join(root, "brand"), join(dist, "brand"), { recursive: true });

for (const name of readdirSync(join(root, "site"))) {
  cpSync(join(root, "site", name), join(dist, name), { recursive: true });
}
