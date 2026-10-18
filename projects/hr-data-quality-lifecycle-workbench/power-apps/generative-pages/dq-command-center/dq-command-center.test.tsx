import assert from "node:assert/strict";
import { afterEach, before, beforeEach, test } from "node:test";
import { JSDOM } from "jsdom";

const dom = new JSDOM("<!doctype html><html><body></body></html>", {
  url: "https://contoso.crm.dynamics.com/main.aspx",
});

Object.assign(globalThis, {
  window: dom.window,
  document: dom.window.document,
  HTMLElement: dom.window.HTMLElement,
  Element: dom.window.Element,
  Node: dom.window.Node,
  MutationObserver: dom.window.MutationObserver,
  getComputedStyle: dom.window.getComputedStyle,
  requestAnimationFrame: (callback: FrameRequestCallback) => setTimeout(callback, 0),
  cancelAnimationFrame: (handle: number) => clearTimeout(handle),
});
Object.defineProperty(globalThis, "navigator", { configurable: true, value: dom.window.navigator });

Object.defineProperty(dom.window, "matchMedia", {
  configurable: true,
  value: () => ({ matches: false, addListener() {}, removeListener() {}, addEventListener() {}, removeEventListener() {}, dispatchEvent: () => false }),
});

class ResizeObserverStub {
  observe() {}
  unobserve() {}
  disconnect() {}
}
Object.assign(globalThis, { ResizeObserver: ResizeObserverStub });
Object.assign(dom.window, {
  ResizeObserver: ResizeObserverStub,
  requestAnimationFrame: (callback: FrameRequestCallback) => setTimeout(callback, 0),
  cancelAnimationFrame: (handle: number) => clearTimeout(handle),
});

let React: typeof import("react");
let cleanup: typeof import("@testing-library/react")["cleanup"];
let fireEvent: typeof import("@testing-library/react")["fireEvent"];
let render: typeof import("@testing-library/react")["render"];
let screen: typeof import("@testing-library/react")["screen"];
let waitFor: typeof import("@testing-library/react")["waitFor"];
let CommandCenter: typeof import("./dq-command-center")["default"];

before(async () => {
  React = await import("react");
  ({ cleanup, fireEvent, render, screen, waitFor } = await import("@testing-library/react"));
  ({ default: CommandCenter } = await import("./dq-command-center"));
});

const severities = [557440000, 557440000, 557440001, 557440001, 557440001, 557440001, 557440001, 557440002];
const domains = ["HRIS Integration", "HR Operations Data", "Organization Management", "Organization Management", "HRIS Integration", "HR Operations Data", "Organization Management", "HRIS Integration"];

const exceptions = Array.from({ length: 8 }, (_, index) => ({
  mprpa_dqexceptionreferenceid: `00000000-0000-0000-0000-${String(index + 1).padStart(12, "0")}`,
  mprpa_exceptionlabel: `DQ-00${index + 1} | EMP-${String(index + 407).padStart(6, "0")} | 2026-06-30`,
  mprpa_exceptioninstanceid: `exception-${index + 1}`,
  mprpa_recurrencekey: `recurrence-${index + 1}`,
  mprpa_businesskey: `EMP-${String(index + 407).padStart(6, "0")}`,
  mprpa_rulename: `Data quality rule ${index + 1}`,
  mprpa_qualitydimension: ["Uniqueness", "Temporal Coherence", "Referential Integrity", "Validity", "Cross-system Consistency", "Completeness", "Consistency", "Timeliness"][index],
  mprpa_operationalseverity: severities[index],
  mprpa_ownerdomain: domains[index],
  mprpa_slabusinessdays: index < 2 ? 1 : 5,
  mprpa_snapshotdate: "2026-06-30T00:00:00Z",
  mprpa_sourcesystem: "HRIS",
}));

const remediationCase = {
  mprpa_dqremediationcaseid: "10000000-0000-0000-0000-000000000001",
  mprpa_casenumber: "DQCASE-000001",
  mprpa_casetitle: "Duplicate employee snapshot",
  mprpa_exceptioninstanceid: "exception-1",
  mprpa_evidencecomplete: false,
  mprpa_sourcecorrectionstate: 557440000,
  mprpa_approvaloutcome: undefined,
  _mprpa_casestatus_value: "20000000-0000-0000-0000-000000000001",
  "mprpa_sourcecorrectionstate@OData.Community.Display.V1.FormattedValue": "Not Checked",
};

const rowsByTable: Record<string, unknown[]> = {
  environmentvariabledefinition: [{
    environmentvariabledefinitionid: "40000000-0000-0000-0000-000000000001",
    schemaname: "mprpa_DQOperationalAppURL",
    defaultvalue: "",
    statecode: 0,
  }],
  environmentvariablevalue: [{
    environmentvariablevalueid: "40000000-0000-0000-0000-000000000002",
    _environmentvariabledefinitionid_value: "/environmentvariabledefinition(40000000-0000-0000-0000-000000000001)",
    value: "https://contoso.crm.dynamics.com/main.aspx?appid=00000000-0000-0000-0000-000000000001",
    statecode: 0,
  }],
  mprpa_dqexceptionreference: exceptions,
  mprpa_dqremediationcase: [remediationCase],
  mprpa_dqcaseevidence: [],
  mprpa_dqcaseactivity: [],
  mprpa_dqstatus: [{
    mprpa_dqstatusid: "20000000-0000-0000-0000-000000000001",
    mprpa_statusname: "Triaged",
    mprpa_statuscode: "TRIAGED",
    mprpa_sequence: 20,
    mprpa_initial: false,
  }, {
    mprpa_dqstatusid: "20000000-0000-0000-0000-000000000002",
    mprpa_statusname: "New",
    mprpa_statuscode: "NEW",
    mprpa_sequence: 10,
    mprpa_initial: true,
  }],
};

function createDataApi(queryShouldFail = false, createShouldFail = false) {
  let calls = 0;
  const createdRows: Array<{ table: string; row: Record<string, unknown> }> = [];
  return {
    get calls() { return calls; },
    get createdRows() { return createdRows; },
    async createRow(table: string, row: Record<string, unknown>) {
      if (createShouldFail) throw new Error("Synthetic create failure");
      createdRows.push({ table, row });
      return "30000000-0000-0000-0000-000000000001";
    },
    async queryTable(table: string) {
      calls += 1;
      if (queryShouldFail) throw new Error("Synthetic Dataverse failure");
      return { rows: rowsByTable[table] ?? [] };
    },
  };
}

function clearRuntimeCache() {
  delete (window as unknown as Record<string, unknown>).__dqCommandCenterCache_v1;
  delete (window as unknown as Record<string, unknown>).__dqCommandCenterInflight_v1;
}

beforeEach(() => clearRuntimeCache());
afterEach(() => cleanup());

test("selects every exception, including all seven records without a remediation case", async () => {
  render(React.createElement(CommandCenter, { dataApi: createDataApi() } as never));
  await screen.findByText("EMP-000407");

  for (const exception of exceptions) {
    fireEvent.click(screen.getByRole("button", { name: `Select ${exception.mprpa_businesskey}` }));
    await waitFor(() => assert.equal(screen.queryByText("This view could not be completed"), null));
  }

  assert.ok(screen.getByRole("button", { name: "Create remediation case" }));
});

test("survives the complete time-range, domain, and severity filter matrix", async () => {
  render(React.createElement(CommandCenter, { dataApi: createDataApi() } as never));
  await screen.findByText("EMP-000407");

  const timeRange = screen.getByLabelText("Time range") as HTMLSelectElement;
  const domain = screen.getByLabelText("Data domain") as HTMLSelectElement;
  const severity = screen.getByLabelText("Severity") as HTMLSelectElement;
  const values = (select: HTMLSelectElement) => Array.from(select.options).map(option => option.value);

  for (const timeValue of values(timeRange)) {
    for (const domainValue of values(domain)) {
      for (const severityValue of values(severity)) {
        fireEvent.change(timeRange, { target: { value: timeValue } });
        fireEvent.change(domain, { target: { value: domainValue } });
        fireEvent.change(severity, { target: { value: severityValue } });
        assert.equal(screen.queryByText("This view could not be completed"), null);
      }
    }
  }
});

test("opens an existing case and creates a complete new case before opening it", async () => {
  const openedWindows: Array<{ initialUrl: string; location: { href: string }; opener: unknown; close(): void; closed: boolean }> = [];
  Object.defineProperty(window, "open", {
    configurable: true,
    value: (url: string) => {
      const opened = {
        initialUrl: url,
        location: { href: url },
        opener: window as unknown,
        closed: false,
        close() { this.closed = true; },
      };
      openedWindows.push(opened);
      return opened;
    },
  });

  const dataApi = createDataApi();
  render(React.createElement(CommandCenter, { dataApi } as never));
  await screen.findByText("EMP-000407");
  fireEvent.click(screen.getByRole("button", { name: "Open remediation case" }));

  fireEvent.click(screen.getByRole("button", { name: "Select EMP-000408" }));
  fireEvent.click(screen.getByRole("button", { name: "Create remediation case" }));

  await waitFor(() => assert.equal(dataApi.createdRows.length, 1));
  assert.equal(openedWindows.length, 2);
  assert.match(openedWindows[0].initialUrl, /appid=00000000-0000-0000-0000-000000000001/);
  assert.match(openedWindows[0].initialUrl, /id=10000000-0000-0000-0000-000000000001/);
  assert.equal(openedWindows[1].initialUrl, "about:blank");
  assert.match(openedWindows[1].location.href, /id=30000000-0000-0000-0000-000000000001/);

  const created = dataApi.createdRows[0];
  assert.equal(created.table, "mprpa_dqremediationcase");
  assert.equal(created.row.mprpa_casetitle, "Data quality rule 2 - EMP-000408");
  assert.equal(created.row.mprpa_exceptioninstanceid, "exception-2");
  assert.equal(created.row.mprpa_recurrencekey, "recurrence-2");
  assert.equal(created.row.mprpa_evidencecomplete, false);
  assert.equal(created.row.mprpa_sourcecorrectionstate, 557440000);
  assert.equal(created.row["mprpa_ExceptionReference@odata.bind"], "/mprpa_dqexceptionreference(00000000-0000-0000-0000-000000000002)");
  assert.equal(created.row["mprpa_CaseStatus@odata.bind"], "/mprpa_dqstatus(20000000-0000-0000-0000-000000000002)");
  assert.ok(typeof created.row.mprpa_slastartat === "string");
  assert.ok(typeof created.row.mprpa_dueat === "string");
  assert.ok(new Date(String(created.row.mprpa_dueat)) > new Date(String(created.row.mprpa_slastartat)));
  assert.equal(created.row.mprpa_slastartat, created.row.mprpa_lasttransitionat);
});

test("keeps the page usable and closes the placeholder window when case creation fails", async () => {
  const popup = { location: { href: "about:blank" }, opener: window as unknown, closed: false, close() { this.closed = true; } };
  Object.defineProperty(window, "open", { configurable: true, value: () => popup });

  render(React.createElement(CommandCenter, { dataApi: createDataApi(false, true) } as never));
  await screen.findByText("EMP-000407");
  fireEvent.click(screen.getByRole("button", { name: "Select EMP-000408" }));
  fireEvent.click(screen.getByRole("button", { name: "Create remediation case" }));

  await screen.findByText(/Remediation case could not be created: Synthetic create failure/);
  assert.equal(popup.closed, true);
  assert.ok(screen.getByRole("button", { name: "Create remediation case" }));
});

test("shows an in-page Dataverse failure instead of crashing the Power Apps shell", async () => {
  render(React.createElement(CommandCenter, { dataApi: createDataApi(true) } as never));
  await screen.findByText(/Dataverse query failed: Synthetic Dataverse failure/);
  assert.equal(screen.queryByText("This view could not be completed"), null);
});
