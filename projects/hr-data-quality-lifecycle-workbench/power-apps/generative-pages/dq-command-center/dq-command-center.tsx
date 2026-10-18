import React, { useEffect, useMemo, useState } from "react";
import {
  Button,
  MessageBar,
  MessageBarBody,
  Skeleton,
  SkeletonItem,
  Spinner,
  makeStyles,
  mergeClasses,
} from "@fluentui/react-components";
import {
  ArrowClockwiseRegular,
  CheckmarkCircleRegular,
  CircleRegular,
  ClockRegular,
  DatabaseRegular,
  DocumentRegular,
  OpenRegular,
  PeopleRegular,
  PersonRegular,
  WarningRegular,
} from "@fluentui/react-icons";
import type {
  GeneratedComponentProps,
  mprpa_dqcaseactivity,
  mprpa_dqcaseevidence,
  mprpa_dqexceptionreference,
  mprpa_dqremediationcase,
  mprpa_dqstatus,
} from "./RuntimeTypes";

type Severity = "Critical" | "High" | "Medium" | "Low";
type TimeRange = "30" | "90" | "all";

type LoadedData = {
  exceptions: mprpa_dqexceptionreference[];
  cases: mprpa_dqremediationcase[];
  evidence: mprpa_dqcaseevidence[];
  activities: mprpa_dqcaseactivity[];
  statuses: mprpa_dqstatus[];
  operationalAppUrl: string;
  loadedAt: Date;
};

type PageState = {
  data?: LoadedData;
  loading: boolean;
  error?: string;
};

type QueueItem = {
  exception: mprpa_dqexceptionreference;
  remediationCase?: mprpa_dqremediationcase;
  evidence: mprpa_dqcaseevidence[];
  activities: mprpa_dqcaseactivity[];
  severity: Severity;
  status: string;
  dueState: "Overdue" | "Due soon" | "On track" | "Not scheduled";
};

const CACHE_KEY = "__dqCommandCenterCache_v1";
const INFLIGHT_KEY = "__dqCommandCenterInflight_v1";
const CASE_TABLE = "mprpa_dqremediationcase";
const OPERATIONAL_APP_URL_SCHEMA = "mprpa_DQOperationalAppURL";

const useStyles = makeStyles({
  root: {
    position: "relative",
    contain: "layout",
    display: "flex",
    flexDirection: "column",
    minHeight: "680px",
    height: "100%",
    overflow: "hidden",
    color: "#0C2631",
    backgroundColor: "#F6F7F7",
    fontFamily: "'Segoe UI', Arial, sans-serif",
    fontSize: "14px",
    boxSizing: "border-box",
    "& *": { boxSizing: "border-box" },
    "& ::selection": { backgroundColor: "#BDE9E6", color: "#062F32" },
  },
  header: {
    display: "grid",
    gridTemplateColumns: "minmax(22rem, 1fr) auto",
    alignItems: "center",
    gap: "24px",
    padding: "14px 24px",
    color: "#FFFFFF",
    backgroundColor: "#093838",
    minHeight: "88px",
    "@media (max-width: 1080px)": { gridTemplateColumns: "1fr", gap: "1rem" },
  },
  title: { margin: 0, fontSize: "clamp(28px, 2.35vw, 38px)", lineHeight: 1.05, letterSpacing: "-0.025em", fontWeight: 700 },
  subtitle: { margin: "5px 0 0", color: "#D6E9E8", fontSize: "14px" },
  headerTools: { display: "flex", alignItems: "end", justifyContent: "flex-end", gap: "14px", flexWrap: "wrap" },
  updated: { minWidth: "128px", fontSize: "11px", lineHeight: 1.35, color: "#D6E9E8" },
  updatedValue: { display: "block", marginTop: "0.15rem", color: "#FFFFFF", fontVariantNumeric: "tabular-nums" },
  filter: { display: "grid", gap: "4px", minWidth: "145px" },
  label: { fontSize: "11px", color: "#D6E9E8" },
  select: {
    minHeight: "34px",
    padding: "6px 30px 6px 10px",
    borderTopStyle: "solid", borderRightStyle: "solid", borderBottomStyle: "solid", borderLeftStyle: "solid",
    borderTopWidth: "1px", borderRightWidth: "1px", borderBottomWidth: "1px", borderLeftWidth: "1px",
    borderTopColor: "#9BC5C2", borderRightColor: "#9BC5C2", borderBottomColor: "#9BC5C2", borderLeftColor: "#9BC5C2",
    borderRadius: "2px",
    color: "#FFFFFF",
    backgroundColor: "#093838",
    fontSize: "13px",
    outlineStyle: "none",
    "&:focus-visible": { outlineStyle: "solid", outlineWidth: "3px", outlineColor: "#65D8D2", outlineOffset: "2px" },
  },
  refreshButton: {
    color: "#FFFFFF",
    backgroundColor: "transparent",
    borderTopColor: "#9BC5C2", borderRightColor: "#9BC5C2", borderBottomColor: "#9BC5C2", borderLeftColor: "#9BC5C2",
    borderRadius: "2px",
    "&:hover": { backgroundColor: "#0D5553", color: "#FFFFFF" },
  },
  body: {
    display: "grid",
    gridTemplateColumns: "minmax(0, 2.65fr) minmax(320px, 1fr)",
    gap: "12px",
    padding: "12px 16px 0",
    minHeight: 0,
    flexGrow: 1,
    "@media (max-width: 980px)": { gridTemplateColumns: "1fr", overflow: "auto" },
  },
  mainColumn: { display: "grid", gridTemplateRows: "auto minmax(0, 1fr)", gap: "12px", minWidth: 0, minHeight: 0 },
  surface: {
    backgroundColor: "#FFFFFF",
    borderTopStyle: "solid", borderRightStyle: "solid", borderBottomStyle: "solid", borderLeftStyle: "solid",
    borderTopWidth: "1px", borderRightWidth: "1px", borderBottomWidth: "1px", borderLeftWidth: "1px",
    borderTopColor: "#D8DEE2", borderRightColor: "#D8DEE2", borderBottomColor: "#D8DEE2", borderLeftColor: "#D8DEE2",
    borderRadius: "3px",
  },
  sectionHeader: { display: "flex", alignItems: "center", justifyContent: "space-between", gap: "16px", padding: "10px 16px", borderBottom: "1px solid #D8DEE2" },
  sectionTitle: { margin: 0, fontSize: "19px", lineHeight: 1.2, fontWeight: 700 },
  sectionMeta: { color: "#506570", fontSize: "12px" },
  metrics: { display: "grid", gridTemplateColumns: "repeat(6, minmax(118px, 1fr))", overflowX: "auto" },
  metric: { padding: "14px 16px", minWidth: "118px", borderRight: "1px solid #E0E5E8" },
  metricValue: { display: "block", fontSize: "28px", fontWeight: 700, lineHeight: 1, fontVariantNumeric: "tabular-nums" },
  metricLabel: { display: "block", marginTop: "6px", color: "#425A66", fontSize: "12px" },
  metricMark: { display: "flex", alignItems: "end", gap: "3px", height: "1.2rem", marginTop: "0.7rem" },
  mark: { display: "block", width: "4px", backgroundColor: "#089591" },
  queue: { display: "flex", flexDirection: "column", minHeight: 0, overflow: "hidden" },
  tableWrap: { overflow: "auto", minHeight: 0, flexGrow: 1 },
  table: { width: "100%", borderCollapse: "collapse", minWidth: "920px", fontSize: "13px" },
  tableHead: { position: "sticky", top: 0, zIndex: 1, color: "#263F4A", backgroundColor: "#F8FAFA" },
  th: { padding: "10px 12px", textAlign: "left", fontWeight: 600, borderBottom: "1px solid #D8DEE2", whiteSpace: "nowrap" },
  row: { cursor: "pointer", backgroundColor: "#FFFFFF", "&:hover": { backgroundColor: "#EFF8F7" } },
  selectedRow: { backgroundColor: "#E2F5F3", boxShadow: "inset 3px 0 0 #089591" },
  cell: { height: "42px", padding: "9px 12px", borderBottom: "1px solid #E3E8EA", whiteSpace: "nowrap", maxWidth: "240px", overflow: "hidden", textOverflow: "ellipsis" },
  recordButton: { padding: 0, minWidth: 0, color: "#075C60", backgroundColor: "transparent", textDecorationLine: "underline", textUnderlineOffset: "3px", borderRadius: "2px" },
  severity: { display: "inline-flex", alignItems: "center", gap: "0.45rem", fontWeight: 600 },
  dot: { width: "0.58rem", height: "0.58rem", borderRadius: "50%", flexShrink: 0 },
  critical: { backgroundColor: "#D8342A" },
  high: { backgroundColor: "#F5A623" },
  medium: { backgroundColor: "#8BA6B2" },
  low: { backgroundColor: "#6E8F92" },
  status: { display: "inline-block", minWidth: "102px", padding: "4px 8px", borderRadius: "3px", backgroundColor: "#DDE7EB", textAlign: "center" },
  rightRail: { display: "flex", flexDirection: "column", minHeight: 0, overflow: "auto" },
  selectedSummary: { display: "grid", gap: "6px", padding: "13px 16px 15px", borderBottom: "1px solid #D8DEE2" },
  selectedEyebrow: { color: "#425A66", fontSize: "12px" },
  selectedLine: { display: "flex", justifyContent: "space-between", gap: "12px", alignItems: "center", fontSize: "16px", fontWeight: 700 },
  stage: { display: "grid", gridTemplateColumns: "46px 1fr", gap: "12px", padding: "14px 16px", borderBottom: "1px solid #D8DEE2" },
  stageIcon: { display: "grid", placeItems: "center", width: "42px", height: "42px", borderRadius: "50%", color: "#0C2631", backgroundColor: "#EDF3F3", fontSize: "22px" },
  stageTitle: { margin: 0, fontSize: "14px", fontWeight: 700 },
  stageState: { display: "flex", alignItems: "center", gap: "0.35rem", marginTop: "0.2rem", color: "#087F7C", fontWeight: 700 },
  stageStateNeutral: { color: "#0C2631" },
  stageDetail: { margin: "3px 0 0", color: "#586C76", fontSize: "12px", lineHeight: 1.35 },
  progressTrack: { height: "0.48rem", marginTop: "0.55rem", overflow: "hidden", backgroundColor: "#E4EAEC", borderRadius: "2px" },
  progressFill: { display: "block", height: "100%", backgroundColor: "#089591" },
  primaryAction: { margin: "auto 12px 12px", minHeight: "48px", borderRadius: "2px", color: "#FFFFFF", backgroundColor: "#089591", fontSize: "14px", fontWeight: 700, "&:hover": { backgroundColor: "#067773", color: "#FFFFFF" } },
  empty: { display: "grid", placeItems: "center", gap: "0.75rem", padding: "3rem 1rem", color: "#506570", textAlign: "center" },
  loading: { display: "grid", gridTemplateColumns: "3fr 1fr", gap: "0.75rem", padding: "0.75rem 1rem", flexGrow: 1 },
  skeleton: { display: "grid", gap: "0.75rem" },
  footer: { display: "flex", justifyContent: "space-between", alignItems: "center", gap: "16px", minHeight: "36px", padding: "8px 24px", color: "#425A66", backgroundColor: "#FFFFFF", borderTop: "1px solid #D8DEE2", fontSize: "11px", flexWrap: "wrap" },
  footerGroup: { display: "flex", alignItems: "center", gap: "0.75rem" },
  healthy: { display: "inline-flex", alignItems: "center", gap: "0.35rem" },
});

function annotation(row: unknown, field: string): string | undefined {
  if (!row || typeof row !== "object") return undefined;
  const value = (row as Record<string, unknown>)[`${field}@OData.Community.Display.V1.FormattedValue`];
  return typeof value === "string" ? value : undefined;
}

function normalizeLookup(value: unknown): string | undefined {
  if (typeof value !== "string") return undefined;
  const match = value.match(/\(([0-9a-f-]{36})\)/i);
  return (match?.[1] ?? value).replace(/[{}]/g, "").toLowerCase();
}

function dateValue(value: unknown): Date | undefined {
  if (value instanceof Date && !Number.isNaN(value.getTime())) return value;
  if (typeof value === "string") {
    const parsed = new Date(value);
    return Number.isNaN(parsed.getTime()) ? undefined : parsed;
  }
  return undefined;
}

function formatDate(value: Date | undefined, includeTime = false): string {
  if (!value) return "Not available";
  return new Intl.DateTimeFormat(undefined, includeTime
    ? { dateStyle: "medium", timeStyle: "short" }
    : { dateStyle: "medium" }).format(value);
}

function addBusinessDays(start: Date, businessDays: number): Date {
  const due = new Date(start);
  let remaining = Math.max(0, Math.floor(businessDays));
  while (remaining > 0) {
    due.setUTCDate(due.getUTCDate() + 1);
    const day = due.getUTCDay();
    if (day !== 0 && day !== 6) remaining -= 1;
  }
  return due;
}

function severityFor(row: mprpa_dqexceptionreference): Severity {
  const formatted = annotation(row, "mprpa_operationalseverity") as Severity | undefined;
  if (formatted === "Critical" || formatted === "High" || formatted === "Medium" || formatted === "Low") return formatted;
  const labels: Record<number, Severity> = { 557440000: "Critical", 557440001: "High", 557440002: "Medium", 557440003: "Low" };
  return labels[Number(row.mprpa_operationalseverity)] ?? "Low";
}

function yes(value: unknown): boolean {
  return value === true || value === 1 || value === "1" || value === "Yes";
}

function statusName(row: mprpa_dqremediationcase | undefined, statuses: mprpa_dqstatus[]): string {
  if (!row) return "No case";
  const statusId = normalizeLookup(row._mprpa_casestatus_value);
  const status = statuses.find(item => item.mprpa_dqstatusid.toLowerCase() === statusId);
  return status?.mprpa_statusname || annotation(row, "_mprpa_casestatus_value") || "Active case";
}

function dueState(row: mprpa_dqremediationcase | undefined): QueueItem["dueState"] {
  const due = dateValue(row?.mprpa_dueat);
  if (!due) return "Not scheduled";
  const remaining = due.getTime() - Date.now();
  if (remaining < 0) return "Overdue";
  if (remaining < 3 * 86400000) return "Due soon";
  return "On track";
}

async function loadOperationalAppUrl(dataApi: GeneratedComponentProps["dataApi"]): Promise<string> {
  const definitions = await dataApi.queryTable("environmentvariabledefinition", {
    select: ["environmentvariabledefinitionid", "schemaname", "defaultvalue"],
    filter: `schemaname eq '${OPERATIONAL_APP_URL_SCHEMA}' and statecode eq 0`,
    pageSize: 1,
  });
  const definition = definitions.rows[0];
  if (!definition) throw new Error(`Environment variable ${OPERATIONAL_APP_URL_SCHEMA} is unavailable.`);

  const values = await dataApi.queryTable("environmentvariablevalue", {
    select: ["environmentvariablevalueid", "value", "_environmentvariabledefinitionid_value"],
    filter: `_environmentvariabledefinitionid_value eq ${definition.environmentvariabledefinitionid} and statecode eq 0`,
    pageSize: 5,
  });
  const configured = values.rows.find(value => normalizeLookup(value._environmentvariabledefinitionid_value) === definition.environmentvariabledefinitionid.toLowerCase())?.value;
  const operationalAppUrl = configured || definition.defaultvalue;
  if (!operationalAppUrl) throw new Error(`Environment variable ${OPERATIONAL_APP_URL_SCHEMA} has no value.`);

  try {
    return new URL(operationalAppUrl).toString();
  } catch {
    throw new Error(`Environment variable ${OPERATIONAL_APP_URL_SCHEMA} is not a valid URL.`);
  }
}

async function loadData(dataApi: GeneratedComponentProps["dataApi"], force = false): Promise<LoadedData> {
  const host = window as unknown as Record<string, unknown>;
  if (!force && host[CACHE_KEY]) return host[CACHE_KEY] as LoadedData;
  if (!force && host[INFLIGHT_KEY]) return host[INFLIGHT_KEY] as Promise<LoadedData>;

  const promise = Promise.all([
    dataApi.queryTable("mprpa_dqexceptionreference", {
      select: ["mprpa_dqexceptionreferenceid", "mprpa_exceptionlabel", "mprpa_exceptioninstanceid", "mprpa_recurrencekey", "mprpa_businesskey", "mprpa_rulename", "mprpa_qualitydimension", "mprpa_operationalseverity", "mprpa_ownerdomain", "mprpa_slabusinessdays", "mprpa_snapshotdate", "mprpa_sourcesystem"],
      filter: "statecode eq 0", pageSize: 100,
    }),
    dataApi.queryTable("mprpa_dqremediationcase", {
      select: ["mprpa_dqremediationcaseid", "mprpa_casenumber", "mprpa_casetitle", "mprpa_exceptioninstanceid", "mprpa_dueat", "mprpa_evidencecomplete", "mprpa_sourcecorrectionstate", "mprpa_approvaloutcome", "_mprpa_casestatus_value", "mprpa_slastartat", "mprpa_lasttransitionat"],
      filter: "statecode eq 0", pageSize: 100,
    }),
    dataApi.queryTable("mprpa_dqcaseevidence", {
      select: ["mprpa_dqcaseevidenceid", "mprpa_evidencetitle", "mprpa_supportsclosure", "_mprpa_remediationcase_value"],
      filter: "statecode eq 0", pageSize: 100,
    }),
    dataApi.queryTable("mprpa_dqcaseactivity", {
      select: ["mprpa_dqcaseactivityid", "mprpa_activitytitle", "mprpa_activitytype", "mprpa_occurredat", "_mprpa_remediationcase_value"],
      filter: "statecode eq 0", orderBy: "mprpa_occurredat desc", pageSize: 100,
    }),
    dataApi.queryTable("mprpa_dqstatus", {
      select: ["mprpa_dqstatusid", "mprpa_statusname", "mprpa_statuscode", "mprpa_sequence", "mprpa_initial", "mprpa_requiresapproval", "mprpa_requiresevidence", "mprpa_terminal"],
      filter: "statecode eq 0", orderBy: "mprpa_sequence asc", pageSize: 50,
    }),
    loadOperationalAppUrl(dataApi),
  ]).then(([exceptions, cases, evidence, activities, statuses, operationalAppUrl]) => {
    const value: LoadedData = {
      exceptions: exceptions.rows,
      cases: cases.rows,
      evidence: evidence.rows,
      activities: activities.rows,
      statuses: statuses.rows,
      operationalAppUrl,
      loadedAt: new Date(),
    };
    host[CACHE_KEY] = value;
    delete host[INFLIGHT_KEY];
    return value;
  }).catch(error => {
    delete host[INFLIGHT_KEY];
    throw error;
  });

  host[INFLIGHT_KEY] = promise;
  return promise;
}

function buildQueue(data: LoadedData): QueueItem[] {
  return data.exceptions.map(exception => {
    const remediationCase = data.cases.find(item => item.mprpa_exceptioninstanceid === exception.mprpa_exceptioninstanceid);
    const caseId = remediationCase?.mprpa_dqremediationcaseid.toLowerCase();
    return {
      exception,
      remediationCase,
      evidence: data.evidence.filter(item => normalizeLookup(item._mprpa_remediationcase_value) === caseId),
      activities: data.activities.filter(item => normalizeLookup(item._mprpa_remediationcase_value) === caseId),
      severity: severityFor(exception),
      status: statusName(remediationCase, data.statuses),
      dueState: dueState(remediationCase),
    };
  });
}

function Metric({ value, label, tone }: { value: number; label: string; tone?: Severity }) {
  const styles = useStyles();
  const heights = [7, 13, 10, 17, 12, 19, 15, 21];
  const toneClass = tone === "Critical" ? styles.critical : tone === "High" ? styles.high : tone === "Medium" ? styles.medium : styles.mark;
  return <div className={styles.metric}>
    <span className={styles.metricValue}>{value}</span>
    <span className={styles.metricLabel}>{label}</span>
    <span className={styles.metricMark} aria-hidden="true">
      {heights.map((height, index) => <i key={index} className={mergeClasses(styles.mark, toneClass)} style={{ height }} />)}
    </span>
  </div>;
}

function Stage({ icon, title, state, detail, positive = false, progress }: { icon: React.ReactNode; title: string; state: string; detail: string; positive?: boolean; progress?: number }) {
  const styles = useStyles();
  return <section className={styles.stage} aria-label={`${title}: ${state}`}>
    <div className={styles.stageIcon} aria-hidden="true">{icon}</div>
    <div>
      <h3 className={styles.stageTitle}>{title}</h3>
      <div className={mergeClasses(styles.stageState, !positive && styles.stageStateNeutral)}>
        {positive ? <CheckmarkCircleRegular /> : <CircleRegular />}{state}
      </div>
      <p className={styles.stageDetail}>{detail}</p>
      {typeof progress === "number" && <div className={styles.progressTrack} aria-label={`${progress}% elapsed`}><span className={styles.progressFill} style={{ width: `${Math.max(0, Math.min(100, progress))}%` }} /></div>}
    </div>
  </section>;
}

function LoadingView() {
  const styles = useStyles();
  return <div className={styles.loading} aria-label="Loading DQ Command Center">
    <div className={styles.skeleton}><Skeleton><SkeletonItem size={96} /><SkeletonItem size={128} /></Skeleton><Spinner label="Loading Dataverse records" /></div>
    <Skeleton><SkeletonItem size={128} /></Skeleton>
  </div>;
}

function GeneratedComponent({ dataApi }: GeneratedComponentProps) {
  const styles = useStyles();
  const host = window as unknown as Record<string, unknown>;
  const cached = host[CACHE_KEY] as LoadedData | undefined;
  const [state, setState] = useState<PageState>({ data: cached, loading: !cached });
  const [timeRange, setTimeRange] = useState<TimeRange>("30");
  const [domain, setDomain] = useState("all");
  const [severity, setSeverity] = useState("all");
  const [selectedId, setSelectedId] = useState<string>();
  const [reloadKey, setReloadKey] = useState(0);
  const [actionError, setActionError] = useState<string>();
  const [creatingCase, setCreatingCase] = useState(false);
  const dataReady = !!dataApi;

  useEffect(() => {
    if (!dataReady) return;
    let active = true;
    loadData(dataApi, reloadKey > 0).then(data => {
      if (active) setState({ data, loading: false });
    }).catch(error => {
      if (active) setState({ loading: false, error: error instanceof Error ? error.message : "Dataverse could not be queried." });
    });
    return () => { active = false; };
    // dataApi is intentionally excluded because the host replaces its reference on render.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dataReady, reloadKey]);

  const queue = useMemo(() => state.data ? buildQueue(state.data) : [], [state.data]);
  const newestSnapshot = useMemo(() => queue.reduce<Date | undefined>((latest, item) => {
    const date = dateValue(item.exception.mprpa_snapshotdate);
    return !latest || (date && date > latest) ? date : latest;
  }, undefined), [queue]);
  const domains = useMemo(() => Array.from(new Set(queue.map(item => item.exception.mprpa_ownerdomain).filter(Boolean))).sort(), [queue]);
  const filtered = useMemo(() => {
    const severityRank: Record<Severity, number> = { Critical: 0, High: 1, Medium: 2, Low: 3 };
    return queue.filter(item => {
      const snapshot = dateValue(item.exception.mprpa_snapshotdate);
      const cutoffDays = timeRange === "all" ? undefined : Number(timeRange);
      const inRange = !cutoffDays || !newestSnapshot || !snapshot || snapshot.getTime() >= newestSnapshot.getTime() - cutoffDays * 86400000;
      return inRange && (domain === "all" || item.exception.mprpa_ownerdomain === domain) && (severity === "all" || item.severity === severity);
    }).sort((a, b) => {
      const overdue = Number(b.dueState === "Overdue") - Number(a.dueState === "Overdue");
      return overdue || severityRank[a.severity] - severityRank[b.severity] || a.exception.mprpa_businesskey.localeCompare(b.exception.mprpa_businesskey);
    });
  }, [queue, timeRange, newestSnapshot, domain, severity]);

  useEffect(() => {
    if (!filtered.length) setSelectedId(undefined);
    else if (!selectedId || !filtered.some(item => item.exception.mprpa_dqexceptionreferenceid === selectedId)) setSelectedId(filtered[0].exception.mprpa_dqexceptionreferenceid);
  }, [filtered, selectedId]);

  const selected = filtered.find(item => item.exception.mprpa_dqexceptionreferenceid === selectedId);
  const metrics = {
    total: filtered.length,
    critical: filtered.filter(item => item.severity === "Critical").length,
    high: filtered.filter(item => item.severity === "High").length,
    medium: filtered.filter(item => item.severity === "Medium").length,
    overdue: filtered.filter(item => item.dueState === "Overdue").length,
    ready: filtered.filter(item => yes(item.remediationCase?.mprpa_evidencecomplete) && item.evidence.some(e => yes(e.mprpa_supportsclosure))).length,
  };

  const refresh = () => {
    delete host[CACHE_KEY]; delete host[INFLIGHT_KEY];
    setState(current => ({ data: current.data, loading: true }));
    setReloadKey(value => value + 1);
  };

  const caseUrl = (caseId: string) => {
    if (!state.data?.operationalAppUrl) throw new Error("The operational app URL is unavailable.");
    const url = new URL(state.data.operationalAppUrl);
    url.searchParams.set("pagetype", "entityrecord");
    url.searchParams.set("etn", CASE_TABLE);
    url.searchParams.set("id", caseId.replace(/[{}]/g, ""));
    return url.toString();
  };

  const openCase = async () => {
    if (!selected) return;

    setActionError(undefined);
    if (selected.remediationCase) {
      const opened = window.open(caseUrl(selected.remediationCase.mprpa_dqremediationcaseid), "_blank");
      if (!opened) setActionError("Your browser blocked the case window. Allow pop-ups for Power Apps and try again.");
      else opened.opener = null;
      return;
    }

    const initialStatus = state.data?.statuses.find(status =>
      status.mprpa_statuscode?.toUpperCase() === "NEW" || yes(status.mprpa_initial));
    if (!initialStatus) {
      setActionError("The initial New status is unavailable. Refresh the page or contact the app administrator.");
      return;
    }

    // Open synchronously so the browser does not treat navigation after createRow as an unsolicited popup.
    const opened = window.open("about:blank", "_blank");
    if (!opened) {
      setActionError("Your browser blocked the case window. Allow pop-ups for Power Apps and try again.");
      return;
    }

    setCreatingCase(true);
    try {
      const createdAt = new Date();
      const now = createdAt.toISOString();
      const dueAt = addBusinessDays(createdAt, Number(selected.exception.mprpa_slabusinessdays) || 0).toISOString();
      const newCaseId = await dataApi.createRow(CASE_TABLE, {
        mprpa_casetitle: `${selected.exception.mprpa_rulename} - ${selected.exception.mprpa_businesskey}`.slice(0, 200),
        mprpa_exceptioninstanceid: selected.exception.mprpa_exceptioninstanceid,
        mprpa_recurrencekey: selected.exception.mprpa_recurrencekey,
        mprpa_slastartat: now,
        mprpa_dueat: dueAt,
        mprpa_lasttransitionat: now,
        mprpa_evidencecomplete: false,
        mprpa_sourcecorrectionstate: 557440000,
        "mprpa_ExceptionReference@odata.bind": `/mprpa_dqexceptionreference(${selected.exception.mprpa_dqexceptionreferenceid})`,
        "mprpa_CaseStatus@odata.bind": `/mprpa_dqstatus(${initialStatus.mprpa_dqstatusid})`,
      });

      opened.opener = null;
      opened.location.href = caseUrl(newCaseId);
      refresh();
    } catch (error) {
      opened.close();
      setActionError(error instanceof Error ? `Remediation case could not be created: ${error.message}` : "Remediation case could not be created.");
    } finally {
      setCreatingCase(false);
    }
  };

  if (state.loading && !state.data) return <div className={styles.root}><LoadingView /></div>;

  return <div className={styles.root}>
    <header className={styles.header}>
      <div><h1 className={styles.title}>DQ Command Center</h1><p className={styles.subtitle}>HR data quality operations&nbsp;&nbsp;|&nbsp;&nbsp;Industrial energy</p></div>
      <div className={styles.headerTools}>
        <div className={styles.updated}>Last updated<span className={styles.updatedValue}>{formatDate(state.data?.loadedAt, true)}</span></div>
        <Button className={styles.refreshButton} appearance="outline" icon={<ArrowClockwiseRegular />} onClick={refresh} disabled={state.loading}>{state.loading ? "Refreshing" : "Refresh"}</Button>
        <label className={styles.filter}><span className={styles.label}>Time range</span><select className={styles.select} value={timeRange} onChange={event => setTimeRange(event.target.value as TimeRange)}><option value="30">Last 30 days</option><option value="90">Last 90 days</option><option value="all">All snapshots</option></select></label>
        <label className={styles.filter}><span className={styles.label}>Data domain</span><select className={styles.select} value={domain} onChange={event => setDomain(event.target.value)}><option value="all">All HR</option>{domains.map(item => <option key={item} value={item}>{item}</option>)}</select></label>
        <label className={styles.filter}><span className={styles.label}>Severity</span><select className={styles.select} value={severity} onChange={event => setSeverity(event.target.value)}><option value="all">All</option><option>Critical</option><option>High</option><option>Medium</option><option>Low</option></select></label>
      </div>
    </header>

    {state.error && <MessageBar intent="error"><MessageBarBody>Dataverse query failed: {state.error} <Button appearance="transparent" onClick={refresh}>Retry</Button></MessageBarBody></MessageBar>}
    {actionError && <MessageBar intent="warning"><MessageBarBody>{actionError}</MessageBarBody></MessageBar>}

    <div className={styles.body}>
      <main className={styles.mainColumn}>
        <section className={styles.surface} aria-labelledby="health-title">
          <div className={styles.sectionHeader}><h2 id="health-title" className={styles.sectionTitle}>Operational health</h2><span className={styles.sectionMeta}>Synthetic demo data</span></div>
          <div className={styles.metrics}>
            <Metric value={metrics.total} label="Data quality exceptions" />
            <Metric value={metrics.critical} label="Critical" tone="Critical" />
            <Metric value={metrics.high} label="High" tone="High" />
            <Metric value={metrics.medium} label="Medium" tone="Medium" />
            <Metric value={metrics.overdue} label="Overdue" tone="Critical" />
            <Metric value={metrics.ready} label="Evidence ready" />
          </div>
        </section>

        <section className={mergeClasses(styles.surface, styles.queue)} aria-labelledby="queue-title">
          <div className={styles.sectionHeader}><h2 id="queue-title" className={styles.sectionTitle}>Priority queue</h2><span className={styles.sectionMeta}>{filtered.length} active exceptions</span></div>
          {!filtered.length ? <div className={styles.empty}><WarningRegular fontSize={28} /><strong>No exceptions match these filters</strong><span>Broaden the time range, domain, or severity.</span></div> :
          <div className={styles.tableWrap}><table className={styles.table}>
            <thead className={styles.tableHead}><tr><th className={styles.th}>#</th><th className={styles.th}>Business key</th><th className={styles.th}>Rule name</th><th className={styles.th}>Quality dimension</th><th className={styles.th}>Severity</th><th className={styles.th}>Owner domain</th><th className={styles.th}>Status</th><th className={styles.th}>SLA</th></tr></thead>
            <tbody>{filtered.map((item, index) => <tr key={item.exception.mprpa_dqexceptionreferenceid} className={mergeClasses(styles.row, item.exception.mprpa_dqexceptionreferenceid === selectedId && styles.selectedRow)} onClick={() => setSelectedId(item.exception.mprpa_dqexceptionreferenceid)}>
              <td className={styles.cell}>{index + 1}</td>
              <td className={styles.cell}><Button className={styles.recordButton} appearance="transparent" onClick={() => setSelectedId(item.exception.mprpa_dqexceptionreferenceid)} aria-label={`Select ${item.exception.mprpa_businesskey}`}>{item.exception.mprpa_businesskey}</Button></td>
              <td className={styles.cell} title={item.exception.mprpa_rulename}>{item.exception.mprpa_rulename}</td>
              <td className={styles.cell}>{item.exception.mprpa_qualitydimension}</td>
              <td className={styles.cell}><span className={styles.severity}><i className={mergeClasses(styles.dot, item.severity === "Critical" ? styles.critical : item.severity === "High" ? styles.high : item.severity === "Medium" ? styles.medium : styles.low)} />{item.severity}</span></td>
              <td className={styles.cell}>{item.exception.mprpa_ownerdomain}</td>
              <td className={styles.cell}><span className={styles.status}>{item.status}</span></td>
              <td className={styles.cell}>{item.dueState}</td>
            </tr>)}</tbody>
          </table></div>}
        </section>
      </main>

      <aside className={mergeClasses(styles.surface, styles.rightRail)} aria-labelledby="readiness-title">
        <div className={styles.sectionHeader}><h2 id="readiness-title" className={styles.sectionTitle}>Case readiness</h2></div>
        {selected ? <>
          <div className={styles.selectedSummary}><span className={styles.selectedEyebrow}>Selected record</span><div className={styles.selectedLine}><span>{selected.exception.mprpa_businesskey}</span><span className={styles.severity}><i className={mergeClasses(styles.dot, selected.severity === "Critical" ? styles.critical : selected.severity === "High" ? styles.high : selected.severity === "Medium" ? styles.medium : styles.low)} />{selected.severity}</span></div><span className={styles.sectionMeta}>{selected.exception.mprpa_exceptionlabel}</span></div>
          <Stage icon={<PersonRegular />} title="Ownership" state={selected.remediationCase ? "Assigned" : "Case required"} detail={selected.remediationCase ? `Domain: ${selected.exception.mprpa_ownerdomain}` : "Create a remediation case to assign accountable ownership."} positive={!!selected.remediationCase} />
          <Stage icon={<DatabaseRegular />} title="Source correction" state={selected.remediationCase ? annotation(selected.remediationCase, "mprpa_sourcecorrectionstate") || "Not checked" : "Not started"} detail={`Source: ${selected.exception.mprpa_sourcesystem || "HR source system"}`} positive={Number(selected.remediationCase?.mprpa_sourcecorrectionstate) === 557440002} />
          <Stage icon={<DocumentRegular />} title="Evidence" state={yes(selected.remediationCase?.mprpa_evidencecomplete) && selected.evidence.some(item => yes(item.mprpa_supportsclosure)) ? "Complete" : "Not complete"} detail={`${selected.evidence.filter(item => yes(item.mprpa_supportsclosure)).length} of ${Math.max(1, selected.evidence.length)} items support closure`} positive={yes(selected.remediationCase?.mprpa_evidencecomplete) && selected.evidence.some(item => yes(item.mprpa_supportsclosure))} />
          <Stage icon={<PeopleRegular />} title="Approval" state={selected.remediationCase ? annotation(selected.remediationCase, "mprpa_approvaloutcome") || "Not started" : "Not started"} detail={selected.status === "Pending Approval" ? "Awaiting data owner decision" : "Required when the case reaches approval"} positive={Number(selected.remediationCase?.mprpa_approvaloutcome) === 557440001} />
          <Stage icon={<ClockRegular />} title="SLA" state={selected.dueState} detail={selected.remediationCase?.mprpa_dueat ? `Due ${formatDate(dateValue(selected.remediationCase.mprpa_dueat))}` : `Target: ${selected.exception.mprpa_slabusinessdays} business day${selected.exception.mprpa_slabusinessdays === 1 ? "" : "s"}`} positive={selected.dueState === "On track"} progress={selected.dueState === "Overdue" ? 100 : selected.dueState === "Due soon" ? 80 : selected.dueState === "On track" ? 50 : undefined} />
          <Button className={styles.primaryAction} appearance="primary" icon={<OpenRegular />} onClick={openCase} disabled={creatingCase}>{selected.remediationCase ? "Open remediation case" : creatingCase ? "Creating remediation case" : "Create remediation case"}</Button>
        </> : <div className={styles.empty}><CircleRegular fontSize={28} /><strong>Select an exception</strong><span>Case readiness will appear here.</span></div>}
      </aside>
    </div>

    <footer className={styles.footer}>
      <span>Synthetic demo data</span>
      <div className={styles.footerGroup}><span>Fabric snapshot&nbsp;&nbsp;{formatDate(newestSnapshot)}</span><span className={styles.healthy}><CheckmarkCircleRegular color="#089591" />Dataverse connected</span><span>Last refresh&nbsp;&nbsp;{formatDate(state.data?.loadedAt, true)}</span></div>
    </footer>
  </div>;
}

class CommandCenterErrorBoundary extends React.Component<{ children: React.ReactNode }, { error?: Error }> {
  state: { error?: Error } = {};

  static getDerivedStateFromError(error: Error) {
    return { error };
  }

  render() {
    if (!this.state.error) return this.props.children;
    return <div style={{ minHeight: 320, display: "grid", placeItems: "center", padding: 32, color: "#0C2631", background: "#F6F7F7", fontFamily: "'Segoe UI', Arial, sans-serif" }}>
      <div style={{ maxWidth: 560, padding: 24, border: "1px solid #D8DEE2", borderLeft: "4px solid #D62B22", background: "#FFFFFF" }}>
        <h2 style={{ margin: "0 0 8px", fontSize: 22 }}>This view could not be completed</h2>
        <p style={{ margin: "0 0 16px", color: "#425A66" }}>A record contains an unexpected or incomplete value. Reload the Command Center; your Dataverse data has not been changed.</p>
        <Button appearance="primary" onClick={() => window.location.reload()}>Reload Command Center</Button>
      </div>
    </div>;
  }
}

function SafeGeneratedComponent(props: GeneratedComponentProps) {
  return <CommandCenterErrorBoundary><GeneratedComponent {...props} /></CommandCenterErrorBoundary>;
}

export default SafeGeneratedComponent;
