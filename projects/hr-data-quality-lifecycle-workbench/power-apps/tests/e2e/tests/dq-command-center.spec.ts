import { expect, test } from "@playwright/test";
import { DqCommandCenterPage } from "../pages/dq-command-center.page";

test.beforeEach(async ({ page }, testInfo) => {
  testInfo.annotations.push({ type: "app", description: "DQ Command Center Generative" });
});

test("loads the published Command Center without host errors", async ({ page }) => {
  const app = await DqCommandCenterPage.open(page, process.env.DQ_COMMAND_CENTER_URL!);
  await expect(app.heading("Operational health")).toBeVisible();
  await expect(app.heading("Priority queue")).toBeVisible();
  await expect(app.heading("Case readiness")).toBeVisible();
  expect(await app.hasHostError()).toBe(false);
});

test("filters every data domain without crashing on exceptions that have no case", async ({ page }) => {
  const app = await DqCommandCenterPage.open(page, process.env.DQ_COMMAND_CENTER_URL!);
  const filter = app.filter("Data domain");
  const values = await app.filterValues("Data domain");

  for (const value of values) {
    await filter.selectOption(value);
    await expect(app.heading("Priority queue")).toBeVisible();
    expect(await app.hasHostError()).toBe(false);
  }
});

test("supports time, domain, and severity filtering together", async ({ page }) => {
  const app = await DqCommandCenterPage.open(page, process.env.DQ_COMMAND_CENTER_URL!);
  await app.filter("Time range").selectOption("all");
  await app.filter("Data domain").selectOption("HRIS Integration");
  await app.filter("Severity").selectOption("Critical");
  await expect(app.record("EMP-000407")).toBeVisible();
  expect(await app.hasHostError()).toBe(false);
});

test("opens the selected remediation case in the operational app", async ({ page, context }) => {
  const app = await DqCommandCenterPage.open(page, process.env.DQ_COMMAND_CENTER_URL!);
  await app.record("EMP-000407").click();
  const opened = context.waitForEvent("page");
  await app.openCaseButton().click();
  const operationalPage = await opened;
  await operationalPage.waitForLoadState("domcontentloaded");
  await expect.poll(() => operationalPage.url()).toContain(process.env.DQ_OPERATIONAL_APP_ID!);
  await operationalPage.close();
  expect(await app.hasHostError()).toBe(false);
});

test("@mutation creates a populated remediation case before opening it", async ({ page, context }) => {
  const businessKey = process.env.DQ_CREATE_CASE_BUSINESS_KEY;
  test.skip(!businessKey, "Set DQ_CREATE_CASE_BUSINESS_KEY to 'auto' or to an exception that does not have a case.");

  const app = await DqCommandCenterPage.open(page, process.env.DQ_COMMAND_CENTER_URL!);
  if (businessKey === "auto") {
    let candidateFound = false;
    const records = app.recordButtons();
    for (let index = 0; index < await records.count(); index += 1) {
      await records.nth(index).click();
      if (await app.createCaseButton().isVisible()) {
        candidateFound = true;
        break;
      }
    }
    expect(candidateFound, "No published exception without a remediation case was available.").toBe(true);
  } else {
    await app.record(businessKey!).click();
  }
  await expect(app.createCaseButton()).toBeVisible();

  const opened = context.waitForEvent("page");
  await app.createCaseButton().click();
  const operationalPage = await opened;
  await expect.poll(() => operationalPage.url(), { timeout: 30_000 }).toContain(process.env.DQ_OPERATIONAL_APP_ID!);
  await expect.poll(() => operationalPage.url(), { timeout: 30_000 }).toMatch(/[?&]id=[0-9a-f-]{36}/i);
  await operationalPage.close();
  expect(await app.hasHostError()).toBe(false);
});

test("@visual captures the stable Command Center surface", async ({ page }) => {
  const app = await DqCommandCenterPage.open(page, process.env.DQ_COMMAND_CENTER_URL!);
  await expect(app.heading("Priority queue")).toBeVisible();
  await expect(page).toHaveScreenshot("dq-command-center.png", {
    animations: "disabled",
    maxDiffPixelRatio: 0.01,
  });
});
