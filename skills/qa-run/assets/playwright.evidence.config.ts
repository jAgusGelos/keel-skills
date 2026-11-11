import { defineConfig } from "@playwright/test";
import * as path from "node:path";

// Evidence runs for qa-run, not a regression suite: one worker, everything recorded,
// specs and results gitignored. Match baseURL and the session file to docs/qa-setup.md.
export default defineConfig({
  testDir: "./evidence",
  outputDir: "./results",
  fullyParallel: false,
  workers: 1,
  retries: 0,
  reporter: [["list"]],
  use: {
    baseURL: process.env["QA_BASE_URL"] ?? "http://localhost:4200",
    // Recorded once by a human with the login command; agents never sign in.
    // Per-role sessions override this per spec with test.use({ storageState }).
    storageState: path.join(__dirname, ".auth", "user.json"),
    video: "on",
    screenshot: "on",
    // A trace records request headers, bearer token included: keep it on failure only, never ship it.
    trace: "retain-on-failure",
    viewport: { width: 1440, height: 900 },
    // Paces every operation so the recorded video is followable in one normal viewing pass.
    launchOptions: { slowMo: 500 },
  },
});
