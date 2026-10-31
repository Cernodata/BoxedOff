/**
 * Cube Drop GA4 setup: node scripts/setup-ga4.mjs
 * Uses GOOGLE_APPLICATION_CREDENTIALS (default: Agent Manager ga4-key.json).
 */
import { google } from "googleapis";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, "..");

const KEY_PATH =
  process.env.GOOGLE_APPLICATION_CREDENTIALS ||
  "W:\\Cursor\\Agent Manager\\ga4-key.json";
const SERVICE_ACCOUNT_EMAIL =
  "cursor-analytics@model-aria-502620-r2.iam.gserviceaccount.com";
const SITE_URL = "https://www.cubedrop.co.uk";
const PROPERTY_NAME = "Cube Drop Website";
const STREAM_NAME = "Cube Drop Production";
const TIMEZONE = "Europe/London";
const CURRENCY = "GBP";

const analyticsadmin = google.analyticsadmin("v1beta");

async function getAuth() {
  const keyFile = JSON.parse(fs.readFileSync(KEY_PATH, "utf8"));
  return new google.auth.GoogleAuth({
    credentials: keyFile,
    scopes: ["https://www.googleapis.com/auth/analytics.edit"],
  });
}

async function listAccounts(auth) {
  const res = await analyticsadmin.accounts.list({ auth, pageSize: 50 });
  return res.data.accounts ?? [];
}

async function listProperties(auth, accountName) {
  const res = await analyticsadmin.accountSummaries.list({ auth, pageSize: 100 });
  const summaries = res.data.accountSummaries ?? [];
  for (const s of summaries) {
    if (s.account !== accountName) continue;
    return s.propertySummaries ?? [];
  }
  return [];
}

async function findExistingProperty(auth, accountName) {
  const props = await listProperties(auth, accountName);
  return props.find((p) => p.displayName === PROPERTY_NAME);
}

async function createProperty(auth, accountName) {
  const res = await analyticsadmin.properties.create({
    auth,
    requestBody: {
      parent: accountName,
      displayName: PROPERTY_NAME,
      timeZone: TIMEZONE,
      currencyCode: CURRENCY,
      industryCategory: "OTHER",
    },
  });
  return res.data;
}

async function listStreams(auth, propertyName) {
  const res = await analyticsadmin.properties.dataStreams.list({
    auth,
    parent: propertyName,
  });
  return res.data.dataStreams ?? [];
}

async function createWebStream(auth, propertyName) {
  const res = await analyticsadmin.properties.dataStreams.create({
    auth,
    parent: propertyName,
    requestBody: {
      type: "WEB_DATA_STREAM",
      displayName: STREAM_NAME,
      webStreamData: { defaultUri: SITE_URL },
    },
  });
  return res.data;
}

function writeGaConfig(measurementId, propertyId) {
  const envExample = path.join(ROOT, ".env.example");
  const line = `GA_MEASUREMENT_ID=${measurementId}`;
  const example = `# Vercel / local build\n${line}\nGA4_PROPERTY_ID=${propertyId}\n`;
  fs.writeFileSync(envExample, example);

  const gaJson = path.join(ROOT, "ga4.config.json");
  fs.writeFileSync(
    gaJson,
    JSON.stringify(
      {
        measurementId,
        propertyId,
        siteUrl: SITE_URL,
        updatedAt: new Date().toISOString(),
      },
      null,
      2
    ) + "\n"
  );

  console.log("Wrote ga4.config.json and .env.example");
}

async function main() {
  const auth = await getAuth();
  const accounts = await listAccounts(auth);
  if (!accounts.length) {
    console.error("No GA account for service account. Add admin in GA Admin.");
    process.exit(1);
  }
  const account = accounts[0];
  console.log("Account:", account.displayName);

  let propertyName;
  const existing = await findExistingProperty(auth, account.name);
  if (existing) {
    propertyName = existing.property;
    console.log("Property exists:", existing.displayName, propertyName);
  } else {
    const property = await createProperty(auth, account.name);
    propertyName = property.name;
    console.log("Created property:", propertyName);
  }

  const propertyId = propertyName.split("/").pop();
  let stream = (await listStreams(auth, propertyName)).find(
    (s) => s.displayName === STREAM_NAME
  );
  if (!stream) {
    stream = await createWebStream(auth, propertyName);
    console.log("Created stream:", stream.name);
  } else {
    console.log("Stream exists:", stream.displayName);
  }

  const measurementId = stream.webStreamData?.measurementId;
  if (!measurementId) {
    console.error("No measurement ID on stream");
    process.exit(1);
  }

  writeGaConfig(measurementId, propertyId);
  console.log("\n=== GA4 ready ===");
  console.log("Property ID:   ", propertyId);
  console.log("Measurement ID:", measurementId);
  console.log("\nNext:");
  console.log("1. GA Admin → Property access → add", SERVICE_ACCOUNT_EMAIL, "Viewer");
  console.log("2. Set GA_MEASUREMENT_ID in Vercel, redeploy");
  console.log("3. Mark GA4 recommended events: generate_lead, join_waitlist (custom)");
}

main().catch((err) => {
  console.error(err?.response?.data?.error?.message || err.message || err);
  process.exit(1);
});
