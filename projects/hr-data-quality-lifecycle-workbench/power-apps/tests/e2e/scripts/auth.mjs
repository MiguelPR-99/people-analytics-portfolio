import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import dotenv from "dotenv";
import { chromium } from "playwright";

const root = path.resolve(import.meta.dirname, "..");
dotenv.config({ path: path.join(root, ".env") });

const url = process.env.DQ_COMMAND_CENTER_URL;
if (!url) {
  console.error("DQ_COMMAND_CENTER_URL is required. Copy .env.example to .env first.");
  process.exit(1);
}

const authDir = path.join(root, ".auth");
const profileDir = path.join(authDir, "edge-profile");
const statePath = path.join(authDir, "state.json");
fs.mkdirSync(authDir, { recursive: true });

const context = await chromium.launchPersistentContext(profileDir, {
  channel: "msedge",
  headless: false,
  viewport: { width: 1512, height: 945 },
});

try {
  const page = context.pages()[0] ?? await context.newPage();
  await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60_000 });
  console.log("Complete Microsoft sign-in if requested. The window will close after the Command Center loads.");

  const deadline = Date.now() + 300_000;
  let ready = false;
  while (Date.now() < deadline && !ready) {
    for (const openPage of context.pages()) {
      for (const surface of [openPage, ...openPage.frames()]) {
        if (await surface.getByRole("heading", { name: "DQ Command Center" }).count()) {
          ready = true;
          break;
        }
      }
      if (ready) break;
    }
    if (!ready) await new Promise(resolve => setTimeout(resolve, 500));
  }

  if (!ready) throw new Error("Authentication timed out before the DQ Command Center became visible.");
  // Institutional Microsoft identities can keep reusable tokens in IndexedDB.
  // Export it alongside cookies/localStorage so a fresh test context remains signed in.
  await context.storageState({ path: statePath, indexedDB: true });
  console.log(`Authentication state saved to ${statePath}`);
} finally {
  await context.close();
}
