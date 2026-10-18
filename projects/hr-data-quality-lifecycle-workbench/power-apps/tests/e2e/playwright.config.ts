import { defineConfig, devices } from "@playwright/test";
import dotenv from "dotenv";
import path from "node:path";

dotenv.config({ path: path.resolve(__dirname, ".env") });

const appUrl = process.env.DQ_COMMAND_CENTER_URL;
if (!appUrl) throw new Error("DQ_COMMAND_CENTER_URL is required. Copy .env.example to .env.");

export default defineConfig({
  testDir: "./tests",
  timeout: 90_000,
  expect: { timeout: 15_000 },
  fullyParallel: false,
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  reporter: [["list"], ["html", { open: "never" }]],
  use: {
    baseURL: appUrl,
    storageState: path.resolve(__dirname, ".auth/state.json"),
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    actionTimeout: 20_000,
    navigationTimeout: 60_000,
  },
  projects: [{
    name: "power-apps-edge",
    use: { ...devices["Desktop Edge"], channel: "msedge" },
  }],
});
