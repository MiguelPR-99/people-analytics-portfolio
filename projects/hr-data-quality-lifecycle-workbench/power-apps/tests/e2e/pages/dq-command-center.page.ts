import { type Frame, type Page } from "@playwright/test";

type Surface = Page | Frame;

export class DqCommandCenterPage {
  private constructor(
    readonly hostPage: Page,
    readonly surface: Surface,
  ) {}

  static async open(page: Page, url: string): Promise<DqCommandCenterPage> {
    await page.goto(url, { waitUntil: "domcontentloaded" });

    const deadline = Date.now() + 60_000;
    while (Date.now() < deadline) {
      for (const surface of [page, ...page.frames()]) {
        if (await surface.getByRole("heading", { name: "DQ Command Center" }).count()) {
          return new DqCommandCenterPage(page, surface);
        }
      }
      await page.waitForTimeout(500);
    }

    throw new Error("DQ Command Center did not become available in the Power Apps shell.");
  }

  heading(name: string) {
    return this.surface.getByRole("heading", { name });
  }

  filter(name: "Time range" | "Data domain" | "Severity") {
    return this.surface.getByLabel(name);
  }

  record(businessKey: string) {
    return this.surface.getByRole("button", { name: `Select ${businessKey}` });
  }

  recordButtons() {
    return this.surface.getByRole("button", { name: /^Select / });
  }

  openCaseButton() {
    return this.surface.getByRole("button", { name: "Open remediation case" });
  }

  createCaseButton() {
    return this.surface.getByRole("button", { name: "Create remediation case" });
  }

  async filterValues(name: "Time range" | "Data domain" | "Severity") {
    return this.filter(name).locator("option").evaluateAll(options =>
      options.map(option => (option as HTMLOptionElement).value),
    );
  }

  async hasHostError() {
    const spanish = await this.hostPage.getByText("Se ha producido un error", { exact: false }).count();
    const english = await this.hostPage.getByText("An error has occurred", { exact: false }).count();
    return spanish + english > 0;
  }
}
