#!/usr/bin/env python3
"""Generate the synthetic HR Services Control Tower dataset.

The script uses only Python's standard library. It creates deterministic CSV
files in data/processed and intentionally imperfect exports in data/raw.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import shutil
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any, Iterable, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.synthetic_data_config import CONFIG  # noqa: E402


DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
RAW_EXTRACT_ID = "EXT-20260701-A"


def parse_date(value: str) -> date:
    return datetime.strptime(value, DATE_FORMAT).date()


def parse_datetime(value: str) -> datetime:
    return datetime.strptime(value, DATETIME_FORMAT)


def date_key(value: date | datetime | None) -> int | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        value = value.date()
    return int(value.strftime("%Y%m%d"))


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def weighted_choice(rng: random.Random, items: Sequence[Any], weights: Sequence[float]) -> Any:
    return rng.choices(items, weights=weights, k=1)[0]


def daterange(start: date, end: date) -> Iterable[date]:
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def monday_of(value: date) -> date:
    return value - timedelta(days=value.weekday())


def csv_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, datetime):
        return value.strftime(DATETIME_FORMAT)
    if isinstance(value, date):
        return value.strftime(DATE_FORMAT)
    if isinstance(value, float):
        return f"{value:.4f}".rstrip("0").rstrip(".")
    return value


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        if not rows:
            raise ValueError(f"Cannot infer columns for empty file: {path}")
        fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: csv_value(row.get(column)) for column in fieldnames})


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class BusinessCalendar:
    def __init__(self, config: dict[str, Any]) -> None:
        self.start_hour = int(config["service_start_hour"])
        self.end_hour = int(config["service_end_hour"])
        self.hours_per_day = self.end_hour - self.start_hour
        self.holidays = {parse_date(value) for value in config["holidays"]}

    def is_business_day(self, value: date) -> bool:
        return value.weekday() < 5 and value not in self.holidays

    def next_business_day(self, value: date) -> date:
        candidate = value + timedelta(days=1)
        while not self.is_business_day(candidate):
            candidate += timedelta(days=1)
        return candidate

    def normalize(self, value: datetime) -> datetime:
        current = value
        while not self.is_business_day(current.date()):
            current = datetime.combine(self.next_business_day(current.date()), time(self.start_hour))
        if current.time() < time(self.start_hour):
            return datetime.combine(current.date(), time(self.start_hour))
        if current.time() >= time(self.end_hour):
            return datetime.combine(self.next_business_day(current.date()), time(self.start_hour))
        return current

    def add_hours(self, value: datetime, hours: float) -> datetime:
        if hours < 0:
            raise ValueError("Business hours cannot be negative")
        current = self.normalize(value)
        remaining = float(hours)
        while remaining > 1e-9:
            day_end = datetime.combine(current.date(), time(self.end_hour))
            available = (day_end - current).total_seconds() / 3600
            if remaining <= available + 1e-9:
                return current + timedelta(hours=remaining)
            remaining -= available
            current = datetime.combine(self.next_business_day(current.date()), time(self.start_hour))
        return current

    def hours_between(self, start: datetime, end: datetime) -> float:
        if end <= start:
            return 0.0
        current_date = start.date()
        total = 0.0
        while current_date <= end.date():
            if self.is_business_day(current_date):
                window_start = datetime.combine(current_date, time(self.start_hour))
                window_end = datetime.combine(current_date, time(self.end_hour))
                segment_start = max(start, window_start)
                segment_end = min(end, window_end)
                if segment_end > segment_start:
                    total += (segment_end - segment_start).total_seconds() / 3600
            current_date += timedelta(days=1)
        return round(total, 4)


def build_date_dimension(config: dict[str, Any], calendar: BusinessCalendar) -> list[dict[str, Any]]:
    start = parse_date(config["start_date"])
    end = parse_date(config["end_date"])
    holiday_names = {holiday: "Simulated non-working day" for holiday in calendar.holidays}
    rows: list[dict[str, Any]] = []
    for current in daterange(start, end):
        iso_year, iso_week, _ = current.isocalendar()
        is_holiday = current in calendar.holidays
        is_business = calendar.is_business_day(current)
        rows.append(
            {
                "DateKey": date_key(current),
                "Date": current,
                "Year": current.year,
                "Quarter": f"Q{((current.month - 1) // 3) + 1}",
                "MonthNumber": current.month,
                "MonthName": current.strftime("%b"),
                "YearMonth": current.strftime("%Y-%m"),
                "ISOWeek": iso_week,
                "ISOYear": iso_year,
                "WeekStartDate": monday_of(current),
                "DayOfWeekNumber": current.weekday() + 1,
                "DayOfWeekName": current.strftime("%a"),
                "IsWeekend": current.weekday() >= 5,
                "IsHoliday": is_holiday,
                "HolidayName": holiday_names.get(current),
                "IsBusinessDay": is_business,
                "BusinessHoursAvailable": float(calendar.hours_per_day if is_business else 0),
            }
        )
    return rows


def clean_dimension_rows(rows: list[dict[str, Any]], excluded: set[str]) -> list[dict[str, Any]]:
    return [{key: value for key, value in row.items() if key not in excluded} for row in rows]


def organization_weights_for_location(location_key: int) -> list[float]:
    if location_key == 1:
        return [0.57, 0.14, 0.08, 0.14, 0.01, 0.02, 0.04]
    if location_key == 2:
        return [0.08, 0.10, 0.30, 0.10, 0.08, 0.12, 0.22]
    return [0.04, 0.16, 0.12, 0.06, 0.24, 0.16, 0.22]


def build_requesters(config: dict[str, Any], rng: random.Random) -> list[dict[str, Any]]:
    start = parse_date(config["start_date"])
    end = parse_date(config["end_date"])
    locations = config["locations"]
    organizations = config["organizations"]
    rows: list[dict[str, Any]] = []
    for index in range(1, config["requester_count"] + 1):
        location = weighted_choice(rng, locations, [row["weight"] for row in locations])
        organization = weighted_choice(
            rng,
            organizations,
            organization_weights_for_location(location["LocationKey"]),
        )
        joins_in_period = rng.random() < 0.12
        join_floor = date(2014, 1, 1)
        join_ceiling = end - timedelta(days=15) if joins_in_period else start - timedelta(days=1)
        join_start = start if joins_in_period else join_floor
        join_date = join_start + timedelta(days=rng.randint(0, max(0, (join_ceiling - join_start).days)))
        exit_date: date | None = None
        if rng.random() < 0.09:
            exit_start = max(start, join_date + timedelta(days=60))
            if exit_start <= end:
                exit_date = exit_start + timedelta(days=rng.randint(0, (end - exit_start).days))
        employee_group = "Hourly" if location["LocationKey"] == 1 and rng.random() < 0.72 else "Salaried"
        worker_type = weighted_choice(rng, ["Regular", "Temporary", "Intern"], [0.86, 0.09, 0.05])
        rows.append(
            {
                "RequesterKey": index,
                "RequesterID": f"REQ-{index:04d}",
                "HomeLocationKey": location["LocationKey"],
                "OrgUnitKey": organization["OrgUnitKey"],
                "EmployeeGroup": employee_group,
                "WorkerType": worker_type,
                "PreferredLanguage": "English" if rng.random() < 0.18 else "Spanish",
                "JoinDate": join_date,
                "ExitDate": exit_date,
                "ActiveAtCutoffFlag": exit_date is None or exit_date > end,
            }
        )
    return rows


def build_agents(config: dict[str, Any], rng: random.Random) -> list[dict[str, Any]]:
    aliases = [
        "Atlas", "Beacon", "Cedar", "Delta", "Ember", "Falcon",
        "Grove", "Harbor", "Indigo", "Juniper", "Kite", "Lumen",
        "Mesa", "Nova", "Orbit", "Pine", "Quartz", "River",
    ]
    rows: list[dict[str, Any]] = []
    index = 0
    for team in config["teams"]:
        for location in config["locations"]:
            for _ in range(2):
                index += 1
                active_from = date(2023, 1, 1) + timedelta(days=rng.randint(0, 600))
                rows.append(
                    {
                        "AgentKey": index,
                        "AgentID": f"AGT-{index:03d}",
                        "AgentAlias": f"{aliases[index - 1]}-{index:02d}",
                        "PrimaryTeamKey": team["TeamKey"],
                        "WorkLocationKey": location["LocationKey"],
                        "ExperienceBand": weighted_choice(rng, ["0-1 year", "1-3 years", "3+ years"], [0.28, 0.47, 0.25]),
                        "ActiveFrom": active_from,
                        "ActiveTo": None,
                        "WeeklyContractHours": 40.0,
                        "ActiveAtCutoffFlag": True,
                    }
                )
    return rows


def build_service_dimension(config: dict[str, Any]) -> list[dict[str, Any]]:
    excluded = {"group_weight", "type_weight"}
    rows = clean_dimension_rows(config["services"], excluded)
    for row in rows:
        row["ActiveFlag"] = True
    return rows


def priority_for_default(rng: random.Random, default: str) -> str:
    distributions = {
        "Critical": (["Critical", "High", "Standard"], [0.52, 0.40, 0.08]),
        "High": (["Critical", "High", "Standard", "Low"], [0.03, 0.57, 0.36, 0.04]),
        "Standard": (["Critical", "High", "Standard", "Low"], [0.005, 0.12, 0.67, 0.205]),
        "Low": (["Critical", "High", "Standard", "Low"], [0.001, 0.03, 0.22, 0.749]),
    }
    values, weights = distributions[default]
    return weighted_choice(rng, values, weights)


def varied_complexity(rng: random.Random, base: str) -> str:
    levels = ["Low", "Medium", "High"]
    base_index = levels.index(base)
    if rng.random() < 0.82:
        return base
    possible = [levels[max(0, base_index - 1)], levels[min(2, base_index + 1)]]
    return rng.choice(possible)


def random_created_at(rng: random.Random, value: date, calendar: BusinessCalendar) -> datetime:
    if calendar.is_business_day(value) and rng.random() < 0.72:
        hour = rng.randint(calendar.start_hour, calendar.end_hour - 1)
    else:
        hour = rng.randint(0, 23)
    return datetime.combine(value, time(hour, rng.randint(0, 59), rng.randint(0, 59)))


def is_month_end_window(value: date) -> bool:
    return value.day >= 26 or value.day <= 3


def in_benefits_delay(value: date) -> bool:
    return date(2025, 4, 1) <= value <= date(2025, 6, 30)


def in_bajio_event(value: date) -> bool:
    return date(2025, 9, 1) <= value <= date(2025, 10, 31)


def after_data_intervention(value: date) -> bool:
    return value >= date(2026, 1, 1)


def open_probability(created_date: date, cutoff_date: date) -> float:
    age_days = (cutoff_date - created_date).days
    if age_days <= 7:
        return 0.75
    if age_days <= 30:
        return 0.55
    if age_days <= 90:
        return 0.25
    return 0.01


def choose_agent(
    rng: random.Random,
    agents: list[dict[str, Any]],
    team_key: int,
    location_key: int,
    exclude_agent_key: int | None = None,
) -> dict[str, Any]:
    exact = [
        row for row in agents
        if row["PrimaryTeamKey"] == team_key
        and row["WorkLocationKey"] == location_key
        and row["AgentKey"] != exclude_agent_key
    ]
    pool = exact or [
        row for row in agents
        if row["PrimaryTeamKey"] == team_key and row["AgentKey"] != exclude_agent_key
    ]
    return rng.choice(pool)


def active_requesters(
    requesters: list[dict[str, Any]],
    location_key: int,
    created_date: date,
) -> list[dict[str, Any]]:
    return [
        row for row in requesters
        if row["HomeLocationKey"] == location_key
        and row["JoinDate"] <= created_date
        and (row["ExitDate"] is None or row["ExitDate"] >= created_date)
    ]


def event_row(
    case_key: int,
    case_id: str,
    sequence: int,
    event_type: str,
    status_from: str | None,
    status_to: str,
    event_at: datetime,
    agent_key: int | None,
    team_key: int | None,
    reason_code: str | None,
    prior_at: datetime | None,
    calendar: BusinessCalendar,
    extracted_at: datetime,
) -> dict[str, Any]:
    return {
        "EventKey": 0,
        "CaseKey": case_key,
        "CaseID": case_id,
        "EventSequence": sequence,
        "EventType": event_type,
        "StatusFrom": status_from,
        "StatusTo": status_to,
        "EventAt": event_at,
        "EventDateKey": date_key(event_at),
        "AgentKey": agent_key,
        "TeamKey": team_key,
        "ReasonCode": reason_code,
        "BusinessHoursSincePriorEvent": 0.0 if prior_at is None else calendar.hours_between(prior_at, event_at),
        "IsWaitingStateFlag": status_to.startswith("Waiting for"),
        "ExtractedAt": extracted_at,
    }


def summarize_waiting_hours(
    events: list[dict[str, Any]],
    cutoff: datetime,
    calendar: BusinessCalendar,
) -> dict[str, float]:
    totals = {"Employee": 0.0, "Approval": 0.0, "Vendor": 0.0}
    open_wait: tuple[str, datetime] | None = None
    for event in events:
        status_to = event["StatusTo"]
        status_from = event["StatusFrom"]
        if status_to.startswith("Waiting for"):
            reason = status_to.replace("Waiting for ", "")
            open_wait = (reason, event["EventAt"])
        elif open_wait and status_from and status_from.startswith("Waiting for"):
            reason, started = open_wait
            totals[reason] += calendar.hours_between(started, event["EventAt"])
            open_wait = None
    if open_wait:
        reason, started = open_wait
        totals[reason] += calendar.hours_between(started, cutoff)
    return {key: round(value, 4) for key, value in totals.items()}


def generate_case(
    *,
    case_key: int,
    case_id: str,
    created_at: datetime,
    requester: dict[str, Any],
    service: dict[str, Any],
    priority: str,
    channel: str,
    complexity: str,
    information_complete: bool,
    approval_required: bool,
    vendor_dependent: bool,
    initial_agent: dict[str, Any],
    agents: list[dict[str, Any]],
    force_open: bool,
    cancel_case: bool,
    rng: random.Random,
    calendar: BusinessCalendar,
    cutoff: datetime,
    extracted_at: datetime,
    sla_by_priority: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    initial_team_key = service["OwnerTeamKey"]
    current_agent = initial_agent
    current_team_key = initial_team_key
    full_events: list[dict[str, Any]] = []
    current_status: str | None = None

    def append(
        event_type: str,
        status_to: str,
        event_at: datetime,
        reason_code: str | None = None,
        agent: dict[str, Any] | None = None,
        team_key: int | None = None,
    ) -> None:
        nonlocal current_status, current_agent, current_team_key
        if agent is not None:
            current_agent = agent
        if team_key is not None:
            current_team_key = team_key
        prior_at = full_events[-1]["EventAt"] if full_events else None
        full_events.append(
            event_row(
                case_key,
                case_id,
                len(full_events) + 1,
                event_type,
                current_status,
                status_to,
                event_at,
                current_agent["AgentKey"] if current_agent else None,
                current_team_key,
                reason_code,
                prior_at,
                calendar,
                extracted_at,
            )
        )
        current_status = status_to

    append("Created", "Submitted", created_at, "CASE_CREATED")

    response_base = {"Critical": 1.2, "High": 2.8, "Standard": 5.8, "Low": 9.5}[priority]
    first_response_hours = clamp(rng.lognormvariate(math.log(response_base), 0.42), 0.15, 30.0)
    capacity_event = (
        requester["HomeLocationKey"] == 1
        and service["OwnerTeamKey"] == 3
        and in_bajio_event(created_at.date())
    )
    if capacity_event:
        first_response_hours *= 1.35

    assigned_at = calendar.add_hours(created_at, min(2.0, max(0.1, first_response_hours * 0.30)))
    append("Assigned", "Assigned", assigned_at, "AUTO_ROUTED")
    first_response_at_full = calendar.add_hours(created_at, first_response_hours)

    if cancel_case:
        cancel_after = max(first_response_hours * rng.uniform(0.45, 1.10), rng.uniform(0.5, 8.0))
        cancelled_at = calendar.add_hours(created_at, cancel_after)
        if first_response_at_full < cancelled_at:
            append("First Response", "In Progress", first_response_at_full, "FIRST_CONTACT")
        append("Cancelled", "Cancelled", cancelled_at, "REQUEST_WITHDRAWN")
    else:
        append("First Response", "In Progress", first_response_at_full, "FIRST_CONTACT")

        if force_open:
            open_at = calendar.add_hours(first_response_at_full, rng.uniform(0.25, 3.0))
            if not information_complete:
                append("Status Change", "Waiting for Employee", open_at, "MISSING_INFORMATION")
            elif vendor_dependent:
                append("Status Change", "Waiting for Vendor", open_at, "EXTERNAL_DEPENDENCY")
            elif approval_required:
                append("Status Change", "Waiting for Approval", open_at, "APPROVAL_REQUIRED")
            else:
                append("Status Change", "In Progress", open_at, "WORK_IN_PROGRESS")
        else:
            current_at = first_response_at_full
            if not information_complete:
                enter_at = calendar.add_hours(current_at, rng.uniform(0.25, 1.0))
                append("Status Change", "Waiting for Employee", enter_at, "MISSING_INFORMATION")
                employee_wait = clamp(rng.lognormvariate(math.log(14.0), 0.55), 2.0, 80.0)
                current_at = calendar.add_hours(enter_at, employee_wait)
                append("Status Change", "In Progress", current_at, "INFORMATION_RECEIVED")

            if approval_required:
                enter_at = calendar.add_hours(current_at, rng.uniform(0.25, 1.25))
                append("Status Change", "Waiting for Approval", enter_at, "APPROVAL_REQUIRED")
                approval_wait = clamp(rng.lognormvariate(math.log(7.0), 0.50), 1.0, 48.0)
                current_at = calendar.add_hours(enter_at, approval_wait)
                append("Status Change", "In Progress", current_at, "APPROVAL_RECEIVED")

            if vendor_dependent:
                enter_at = calendar.add_hours(current_at, rng.uniform(0.25, 1.25))
                append("Status Change", "Waiting for Vendor", enter_at, "EXTERNAL_DEPENDENCY")
                vendor_wait = clamp(rng.lognormvariate(math.log(16.0), 0.60), 2.0, 96.0)
                if in_benefits_delay(created_at.date()) and service["ServiceCode"] in {"BEN-02", "BEN-03"}:
                    vendor_wait *= 1.80
                current_at = calendar.add_hours(enter_at, vendor_wait)
                append("Status Change", "In Progress", current_at, "VENDOR_RESPONSE_RECEIVED")

            transfer_probability = 0.10
            if complexity == "High":
                transfer_probability += 0.10
            if not information_complete:
                transfer_probability += 0.04
            transfer_count_planned = 0
            if rng.random() < transfer_probability:
                transfer_count_planned = 2 if rng.random() < 0.08 else 1
            for _ in range(transfer_count_planned):
                current_at = calendar.add_hours(current_at, rng.uniform(0.25, 2.0))
                if rng.random() < 0.84:
                    next_team_key = current_team_key
                else:
                    next_team_key = rng.choice([key for key in (1, 2, 3) if key != current_team_key])
                next_agent = choose_agent(
                    rng,
                    agents,
                    next_team_key,
                    requester["HomeLocationKey"],
                    exclude_agent_key=current_agent["AgentKey"],
                )
                append("Transfer", "In Progress", current_at, "QUEUE_REASSIGNMENT", next_agent, next_team_key)

            active_base = {"Low": 4.5, "Medium": 12.0, "High": 24.0}[complexity]
            active_hours = clamp(rng.lognormvariate(math.log(active_base), 0.52), 0.5, 110.0)
            if capacity_event:
                active_hours *= 1.45
            intervention_eligible = (
                service["ServiceGroup"] == "Employee Data Changes"
                and channel == "Portal"
                and after_data_intervention(created_at.date())
            )
            if intervention_eligible:
                active_hours *= 0.80
            current_at = calendar.add_hours(current_at, active_hours)
            append("Resolved", "Resolved", current_at, "RESOLUTION_PROVIDED")

            reopen_probability = 0.065
            if not information_complete:
                reopen_probability += 0.035
            if complexity == "High":
                reopen_probability += 0.025
            reopen_count_planned = 0
            if rng.random() < reopen_probability:
                reopen_count_planned = 2 if rng.random() < 0.04 else 1
            for _ in range(reopen_count_planned):
                current_at = calendar.add_hours(current_at, rng.uniform(1.0, 16.0))
                append("Reopened", "In Progress", current_at, "ISSUE_NOT_FULLY_RESOLVED")
                current_at = calendar.add_hours(current_at, rng.uniform(3.0, 18.0))
                append("Resolved", "Resolved", current_at, "RESOLUTION_PROVIDED")

            current_at = calendar.add_hours(current_at, rng.uniform(0.5, 7.0))
            append("Closed", "Closed", current_at, "CASE_CONFIRMED_OR_AUTO_CLOSED")

    events = [row for row in full_events if row["EventAt"] <= cutoff]
    if not events:
        raise AssertionError(f"Case {case_id} has no events at cutoff")
    for sequence, row in enumerate(events, start=1):
        row["EventSequence"] = sequence

    current_status_at_cutoff = events[-1]["StatusTo"]
    first_response_events = [row for row in events if row["EventType"] == "First Response"]
    first_response_at = first_response_events[0]["EventAt"] if first_response_events else None
    resolved_events = [row for row in events if row["EventType"] == "Resolved"]
    reopened_events = [row for row in events if row["EventType"] == "Reopened"]
    resolved_at = resolved_events[-1]["EventAt"] if current_status_at_cutoff in {"Resolved", "Closed"} and resolved_events else None
    closed_events = [row for row in events if row["EventType"] in {"Closed", "Cancelled"}]
    closed_at = closed_events[-1]["EventAt"] if closed_events else None
    transfer_count = sum(1 for row in events if row["EventType"] == "Transfer")
    reopen_count = len(reopened_events)
    waiting = summarize_waiting_hours(events, cutoff, calendar)
    gross_resolution_hours = calendar.hours_between(created_at, resolved_at) if resolved_at else None
    excluded_hours = waiting["Employee"]
    net_resolution_hours = max(0.0, gross_resolution_hours - excluded_hours) if gross_resolution_hours is not None else None
    first_response_business_hours = calendar.hours_between(created_at, first_response_at) if first_response_at else None
    sla = sla_by_priority[priority]
    first_response_within = (
        first_response_business_hours <= sla["FirstResponseSLAHours"]
        if first_response_business_hours is not None
        else None
    )
    resolution_within = (
        net_resolution_hours <= sla["ResolutionSLAHours"]
        if net_resolution_hours is not None and current_status_at_cutoff != "Cancelled"
        else None
    )

    fcr_probability = service["FirstContactResolutionBaseProbability"]
    if not information_complete:
        fcr_probability *= 0.55
    if channel == "Phone":
        fcr_probability *= 1.08
    if transfer_count or reopen_count:
        fcr_probability = 0.0
    first_contact_resolved = (
        rng.random() < clamp(fcr_probability, 0.02, 0.95)
        if resolved_at is not None
        else None
    )
    interaction_count = 1 + (0 if information_complete else 1) + transfer_count + reopen_count
    if resolved_at and not first_contact_resolved:
        interaction_count += rng.randint(1, 3)

    final_agent_key = next((row["AgentKey"] for row in reversed(events) if row["AgentKey"] is not None), None)
    final_team_key = next((row["TeamKey"] for row in reversed(events) if row["TeamKey"] is not None), None)
    process_intervention_eligible = service["ServiceGroup"] == "Employee Data Changes" and channel == "Portal"
    case = {
        "CaseKey": case_key,
        "CaseID": case_id,
        "RequesterKey": requester["RequesterKey"],
        "CreatedDateKey": date_key(created_at),
        "FirstResponseDateKey": date_key(first_response_at),
        "ResolvedDateKey": date_key(resolved_at),
        "ClosedDateKey": date_key(closed_at),
        "LocationKey": requester["HomeLocationKey"],
        "OrgUnitKey": requester["OrgUnitKey"],
        "ServiceKey": service["ServiceKey"],
        "SLAPolicyKey": sla["SLAPolicyKey"],
        "InitialAgentKey": initial_agent["AgentKey"],
        "FinalAgentKey": final_agent_key,
        "InitialTeamKey": initial_team_key,
        "FinalTeamKey": final_team_key,
        "SourceChannel": channel,
        "CreatedAt": created_at,
        "FirstResponseAt": first_response_at,
        "ResolvedAt": resolved_at,
        "ClosedAt": closed_at,
        "CurrentStatusAtCutoff": current_status_at_cutoff,
        "Priority": priority,
        "ComplexityBand": complexity,
        "InformationCompleteAtSubmissionFlag": information_complete,
        "ApprovalRequiredFlag": approval_required,
        "VendorDependentFlag": vendor_dependent,
        "CancelledFlag": current_status_at_cutoff == "Cancelled",
        "TransferCount": transfer_count,
        "ReopenCount": reopen_count,
        "InteractionCount": interaction_count,
        "WaitingEmployeeBusinessHours": waiting["Employee"],
        "WaitingApprovalBusinessHours": waiting["Approval"],
        "WaitingVendorBusinessHours": waiting["Vendor"],
        "GrossResolutionBusinessHours": gross_resolution_hours,
        "SLAExcludedBusinessHours": excluded_hours,
        "NetResolutionBusinessHours": net_resolution_hours,
        "FirstResponseBusinessHours": first_response_business_hours,
        "FirstResponseWithinSLAFlag": first_response_within,
        "ResolutionWithinSLAFlag": resolution_within,
        "FirstContactResolvedFlag": first_contact_resolved,
        "SurveyInvitedFlag": False,
        "ProcessInterventionEligibleFlag": process_intervention_eligible,
        "ExtractedAt": extracted_at,
    }
    return case, events


def build_cases_and_events(
    config: dict[str, Any],
    requesters: list[dict[str, Any]],
    agents: list[dict[str, Any]],
    rng: random.Random,
    calendar: BusinessCalendar,
    case_count: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    start = parse_date(config["start_date"])
    end = parse_date(config["end_date"])
    cutoff = parse_datetime(config["cutoff"])
    extracted_at = parse_datetime(config["extracted_at"])
    all_dates = list(daterange(start, end))
    arrival_weights: list[float] = []
    for current in all_dates:
        weight = 1.0 if calendar.is_business_day(current) else 0.25
        if current.month in {1, 6}:
            weight *= 1.08
        elif current.month == 12:
            weight *= 0.85
        arrival_weights.append(weight)
    created_dates = sorted(rng.choices(all_dates, weights=arrival_weights, k=case_count))

    services_by_group: dict[str, list[dict[str, Any]]] = defaultdict(list)
    group_weights: dict[str, float] = {}
    for service in config["services"]:
        services_by_group[service["ServiceGroup"]].append(service)
        group_weights[service["ServiceGroup"]] = service["group_weight"]
    group_names = list(group_weights)
    sla_by_priority = {row["Priority"]: row for row in config["sla"]}
    channel_names = list(config["channels"])
    channel_weights = [config["channels"][name]["weight"] for name in channel_names]

    cases: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    year_sequence: Counter[int] = Counter()
    for case_key, created_date_value in enumerate(created_dates, start=1):
        year_sequence[created_date_value.year] += 1
        case_id = f"CASE-{created_date_value.year}-{year_sequence[created_date_value.year]:05d}"
        adjusted_group_weights = [group_weights[name] for name in group_names]
        if is_month_end_window(created_date_value):
            adjusted_group_weights = [
                weight * 1.60 if name == "Payroll & Compensation" else weight
                for name, weight in zip(group_names, adjusted_group_weights)
            ]
        service_group = weighted_choice(rng, group_names, adjusted_group_weights)
        group_services = services_by_group[service_group]
        service = weighted_choice(rng, group_services, [row["type_weight"] for row in group_services])

        location_weights = [row["weight"] for row in config["locations"]]
        if in_bajio_event(created_date_value):
            location_weights = [
                weight * 1.30 if row["LocationKey"] == 1 else weight
                for row, weight in zip(config["locations"], location_weights)
            ]
        location = weighted_choice(rng, config["locations"], location_weights)
        requester_pool = active_requesters(requesters, location["LocationKey"], created_date_value)
        if not requester_pool:
            requester_pool = [row for row in requesters if row["HomeLocationKey"] == location["LocationKey"]]
        requester = rng.choice(requester_pool)

        channel = weighted_choice(rng, channel_names, channel_weights)
        incomplete_probability = config["channels"][channel]["incomplete"]
        if (
            service_group == "Employee Data Changes"
            and channel == "Portal"
            and after_data_intervention(created_date_value)
        ):
            incomplete_probability *= 0.45
        information_complete = rng.random() >= incomplete_probability
        approval_required = rng.random() < service["ApprovalProbability"]
        vendor_probability = service["VendorDependencyProbability"]
        if in_benefits_delay(created_date_value) and service["ServiceCode"] in {"BEN-02", "BEN-03"}:
            vendor_probability = clamp(vendor_probability * 1.55, 0.0, 0.95)
        vendor_dependent = rng.random() < vendor_probability
        priority = priority_for_default(rng, service["DefaultPriority"])
        complexity = varied_complexity(rng, service["BaseComplexity"])
        initial_agent = choose_agent(rng, agents, service["OwnerTeamKey"], requester["HomeLocationKey"])
        created_at = random_created_at(rng, created_date_value, calendar)
        force_open = rng.random() < open_probability(created_date_value, cutoff.date())
        cancel_case = not force_open and rng.random() < 0.015

        case, case_events = generate_case(
            case_key=case_key,
            case_id=case_id,
            created_at=created_at,
            requester=requester,
            service=service,
            priority=priority,
            channel=channel,
            complexity=complexity,
            information_complete=information_complete,
            approval_required=approval_required,
            vendor_dependent=vendor_dependent,
            initial_agent=initial_agent,
            agents=agents,
            force_open=force_open,
            cancel_case=cancel_case,
            rng=rng,
            calendar=calendar,
            cutoff=cutoff,
            extracted_at=extracted_at,
            sla_by_priority=sla_by_priority,
        )
        cases.append(case)
        events.extend(case_events)

    for event_key, row in enumerate(events, start=1):
        row["EventKey"] = event_key
    return cases, events


def build_surveys(
    config: dict[str, Any],
    cases: list[dict[str, Any]],
    rng: random.Random,
    calendar: BusinessCalendar,
) -> list[dict[str, Any]]:
    cutoff = parse_datetime(config["cutoff"])
    rows: list[dict[str, Any]] = []
    for case in cases:
        if case["CurrentStatusAtCutoff"] != "Closed" or case["ClosedAt"] is None:
            continue
        invited_at = calendar.add_hours(case["ClosedAt"], rng.uniform(0.25, 1.0))
        if invited_at > cutoff or rng.random() >= 0.70:
            continue
        case["SurveyInvitedFlag"] = True
        response_probability = config["channels"][case["SourceChannel"]]["survey_response"]
        if rng.random() >= response_probability:
            continue
        responded_at = calendar.add_hours(invited_at, rng.uniform(2.0, 48.0))
        if responded_at > cutoff:
            continue

        score = 4.20 + rng.gauss(0.0, 0.65)
        if case["ResolutionWithinSLAFlag"] is False:
            score -= 0.55
        score -= 0.35 * case["TransferCount"]
        score -= 0.75 * case["ReopenCount"]
        if not case["InformationCompleteAtSubmissionFlag"]:
            score -= 0.20
        satisfaction = int(round(clamp(score, 1.0, 5.0)))
        ease_score = int(round(clamp(score + rng.gauss(0.0, 0.45), 1.0, 5.0)))

        if case["ReopenCount"]:
            feedback_topic = weighted_choice(rng, ["Accuracy", "Communication", "Speed"], [0.55, 0.25, 0.20])
        elif case["ResolutionWithinSLAFlag"] is False:
            feedback_topic = weighted_choice(rng, ["Speed", "Communication", "Accuracy"], [0.64, 0.24, 0.12])
        elif not case["InformationCompleteAtSubmissionFlag"]:
            feedback_topic = weighted_choice(rng, ["Self-Service", "Communication", "Speed"], [0.55, 0.30, 0.15])
        else:
            feedback_topic = weighted_choice(
                rng,
                ["Speed", "Communication", "Accuracy", "Self-Service", "Other"],
                [0.24, 0.24, 0.24, 0.18, 0.10],
            )
        resolution_confirmed_probability = clamp(0.35 + 0.13 * satisfaction - 0.12 * case["ReopenCount"], 0.15, 0.97)
        rows.append(
            {
                "SurveyKey": len(rows) + 1,
                "CaseKey": case["CaseKey"],
                "CaseID": case["CaseID"],
                "InvitationDateKey": date_key(invited_at),
                "ResponseDateKey": date_key(responded_at),
                "InvitedAt": invited_at,
                "RespondedAt": responded_at,
                "OverallSatisfactionScore": satisfaction,
                "EaseScore": ease_score,
                "ResolutionConfirmedFlag": rng.random() < resolution_confirmed_probability,
                "FeedbackTopic": feedback_topic,
                "LowRatingFlag": satisfaction <= 2,
            }
        )
    return rows


def age_bucket(age_business_days: float) -> str:
    if age_business_days <= 2:
        return "0-2 business days"
    if age_business_days <= 5:
        return "3-5 business days"
    if age_business_days <= 10:
        return "6-10 business days"
    if age_business_days <= 20:
        return "11-20 business days"
    return "21+ business days"


def build_backlog_daily(
    config: dict[str, Any],
    cases: list[dict[str, Any]],
    events: list[dict[str, Any]],
    calendar: BusinessCalendar,
) -> list[dict[str, Any]]:
    cutoff = parse_datetime(config["cutoff"])
    events_by_case: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        events_by_case[event["CaseKey"]].append(event)
    sla_by_key = {row["SLAPolicyKey"]: row for row in config["sla"]}
    rows: list[dict[str, Any]] = []
    for case in cases:
        case_events = sorted(events_by_case[case["CaseKey"]], key=lambda row: row["EventAt"])
        current_date = case["CreatedAt"].date()
        end_date = min(cutoff.date(), case["ClosedAt"].date() if case["ClosedAt"] else cutoff.date())
        while current_date <= end_date:
            snapshot_at = datetime.combine(current_date, time(23, 59, 59))
            if snapshot_at > cutoff:
                snapshot_at = cutoff
            available_events = [row for row in case_events if row["EventAt"] <= snapshot_at]
            if not available_events:
                current_date += timedelta(days=1)
                continue
            latest = available_events[-1]
            if latest["StatusTo"] in {"Closed", "Cancelled"}:
                current_date += timedelta(days=1)
                continue
            age_hours = calendar.hours_between(case["CreatedAt"], snapshot_at)
            waiting = summarize_waiting_hours(available_events, snapshot_at, calendar)
            net_elapsed = max(0.0, age_hours - waiting["Employee"])
            resolution_target = sla_by_key[case["SLAPolicyKey"]]["ResolutionSLAHours"]
            current_agent_key = next(
                (row["AgentKey"] for row in reversed(available_events) if row["AgentKey"] is not None),
                None,
            )
            current_team_key = next(
                (row["TeamKey"] for row in reversed(available_events) if row["TeamKey"] is not None),
                None,
            )
            waiting_reason = None
            if latest["StatusTo"].startswith("Waiting for"):
                waiting_reason = latest["StatusTo"].replace("Waiting for ", "")
            age_days = age_hours / calendar.hours_per_day
            rows.append(
                {
                    "SnapshotDateKey": date_key(current_date),
                    "CaseKey": case["CaseKey"],
                    "ServiceKey": case["ServiceKey"],
                    "LocationKey": case["LocationKey"],
                    "CurrentAgentKey": current_agent_key,
                    "CurrentTeamKey": current_team_key,
                    "StatusAtEndOfDay": latest["StatusTo"],
                    "WaitingReason": waiting_reason,
                    "BacklogAgeBusinessDays": round(age_days, 4),
                    "AgeBucket": age_bucket(age_days),
                    "ResolutionSLABreachedAtSnapshotFlag": net_elapsed > resolution_target,
                }
            )
            current_date += timedelta(days=1)
    return rows


def build_capacity_weekly(
    config: dict[str, Any],
    rng: random.Random,
) -> list[dict[str, Any]]:
    start = monday_of(parse_date(config["start_date"]))
    end = monday_of(parse_date(config["end_date"]))
    rows: list[dict[str, Any]] = []
    current = start
    event_start = date(2025, 9, 8)
    event_end = event_start + timedelta(weeks=6) - timedelta(days=1)
    while current <= end:
        for team in config["teams"]:
            for location in config["locations"]:
                planned_fte = 2.0
                scheduled = planned_fte * 40.0
                absence = round(clamp(rng.triangular(0.0, 13.0, 3.0), 0.0, 18.0), 2)
                training = round(clamp(rng.triangular(0.0, 8.0, 2.0), 0.0, 10.0), 2)
                other = round(clamp(rng.triangular(0.0, 5.0, 1.0), 0.0, 8.0), 2)
                event_flag = (
                    team["TeamCode"] == "DATALIFE"
                    and location["LocationCode"] == "BJPL"
                    and event_start <= current <= event_end
                )
                if event_flag:
                    other += scheduled * 0.20
                available = round(max(0.0, scheduled - absence - training - other), 2)
                rows.append(
                    {
                        "WeekStartDateKey": date_key(current),
                        "TeamKey": team["TeamKey"],
                        "LocationKey": location["LocationKey"],
                        "PlannedFTE": planned_fte,
                        "ScheduledHours": scheduled,
                        "AbsenceHours": absence,
                        "TrainingHours": training,
                        "OtherUnavailableHours": round(other, 2),
                        "AvailableHours": available,
                        "CapacityReductionEventFlag": event_flag,
                    }
                )
        current += timedelta(weeks=1)
    return rows


def add_raw_metadata(rows: list[dict[str, Any]], source_system: str) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        copied = dict(row)
        copied["SourceRowNumber"] = index
        copied["SourceSystem"] = source_system
        copied["RawExtractID"] = RAW_EXTRACT_ID
        output.append(copied)
    return output


def mixed_boolean(value: bool, rng: random.Random) -> str:
    style = rng.choice(["yn", "truefalse", "numeric"])
    if style == "yn":
        return "Y" if value else "N"
    if style == "numeric":
        return "1" if value else "0"
    return "TRUE" if value else "FALSE"


def build_raw_cases(
    config: dict[str, Any],
    cases: list[dict[str, Any]],
    services: list[dict[str, Any]],
    rng: random.Random,
) -> list[dict[str, Any]]:
    service_by_key = {row["ServiceKey"]: row for row in services}
    issue = config["raw_issues"]
    raw_rows = add_raw_metadata(cases, "SYNTHETIC_HR_CASE_EXPORT")
    channel_variants = {
        "Portal": ["portal", "Portal ", "SELF SERVICE"],
        "Email": ["E-mail", "email", "EMAIL "],
        "Teams": ["MS Teams", "teams", "Teams "],
        "Phone": ["Telephone", "phone", "PHONE "],
    }
    boolean_columns = [key for key in cases[0] if key.endswith("Flag")]
    for row in raw_rows:
        canonical_channel = row.pop("SourceChannel")
        raw_channel = canonical_channel
        raw_service = service_by_key[row["ServiceKey"]]["RequestType"]
        if rng.random() < issue["label_variant_rate"]:
            raw_channel = rng.choice(channel_variants[canonical_channel])
            raw_service = rng.choice([raw_service.lower(), f"{raw_service} ", raw_service.upper()])
        if rng.random() < issue["blank_channel_rate"]:
            raw_channel = ""
        row["RawChannel"] = raw_channel
        row["RawServiceName"] = raw_service
        if rng.random() < issue["whitespace_rate"]:
            row["Priority"] = f" {row['Priority']} "
        if rng.random() < issue["mixed_boolean_rate"]:
            for column in boolean_columns:
                if isinstance(row.get(column), bool):
                    row[column] = mixed_boolean(row[column], rng)
    duplicate_count = round(len(raw_rows) * issue["duplicate_case_rate"])
    duplicates = [dict(row) for row in rng.sample(raw_rows, duplicate_count)]
    raw_rows.extend(duplicates)
    rng.shuffle(raw_rows)
    return raw_rows


def build_raw_events(
    config: dict[str, Any],
    events: list[dict[str, Any]],
    rng: random.Random,
) -> list[dict[str, Any]]:
    raw_rows = add_raw_metadata(events, "SYNTHETIC_HR_EVENT_LOG")
    duplicate_count = round(len(raw_rows) * config["raw_issues"]["duplicate_event_rate"])
    raw_rows.extend(dict(row) for row in rng.sample(raw_rows, duplicate_count))
    rng.shuffle(raw_rows)
    return raw_rows


def build_raw_surveys(
    config: dict[str, Any],
    surveys: list[dict[str, Any]],
    rng: random.Random,
) -> list[dict[str, Any]]:
    raw_rows = add_raw_metadata(surveys, "SYNTHETIC_HR_SURVEY_EXPORT")
    orphan_count = max(1, round(len(raw_rows) * config["raw_issues"]["orphan_survey_rate"])) if raw_rows else 0
    for index in range(orphan_count):
        template = dict(rng.choice(raw_rows))
        template["SurveyKey"] = 900000 + index
        template["CaseKey"] = 900000 + index
        template["CaseID"] = f"ORPHAN-{index + 1:04d}"
        template["SourceRowNumber"] = len(raw_rows) + 1
        raw_rows.append(template)
    rng.shuffle(raw_rows)
    return raw_rows


def percentile(values: list[float], probability: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = (len(ordered) - 1) * probability
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (index - lower)


def rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def validate_dataset(
    config: dict[str, Any],
    cases: list[dict[str, Any]],
    events: list[dict[str, Any]],
    surveys: list[dict[str, Any]],
    backlog: list[dict[str, Any]],
    requesters: list[dict[str, Any]],
    agents: list[dict[str, Any]],
    services: list[dict[str, Any]],
) -> dict[str, Any]:
    checks: dict[str, bool] = {}
    strict_pattern_checks = len(cases) >= 3000
    checks["case_count"] = len(cases) > 0
    checks["case_id_unique"] = len({row["CaseID"] for row in cases}) == len(cases)
    checks["case_key_unique"] = len({row["CaseKey"] for row in cases}) == len(cases)

    requester_keys = {row["RequesterKey"] for row in requesters}
    agent_keys = {row["AgentKey"] for row in agents}
    service_keys = {row["ServiceKey"] for row in services}
    case_keys = {row["CaseKey"] for row in cases}
    checks["case_foreign_keys"] = all(
        row["RequesterKey"] in requester_keys
        and row["ServiceKey"] in service_keys
        and row["InitialAgentKey"] in agent_keys
        and (row["FinalAgentKey"] is None or row["FinalAgentKey"] in agent_keys)
        for row in cases
    )
    checks["event_case_keys"] = all(row["CaseKey"] in case_keys for row in events)
    checks["survey_case_keys"] = all(row["CaseKey"] in case_keys for row in surveys)
    checks["survey_scores"] = all(
        1 <= row["OverallSatisfactionScore"] <= 5 and 1 <= row["EaseScore"] <= 5
        for row in surveys
    )

    event_pairs = [(row["CaseKey"], row["EventSequence"]) for row in events]
    checks["event_sequence_unique"] = len(event_pairs) == len(set(event_pairs))
    events_by_case: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        events_by_case[event["CaseKey"]].append(event)
    checks["event_timestamps_monotonic"] = all(
        all(left["EventAt"] <= right["EventAt"] for left, right in zip(case_events, case_events[1:]))
        for case_events in events_by_case.values()
    )
    checks["non_negative_durations"] = all(
        (row["FirstResponseBusinessHours"] is None or row["FirstResponseBusinessHours"] >= 0)
        and (row["NetResolutionBusinessHours"] is None or row["NetResolutionBusinessHours"] >= 0)
        and row["WaitingEmployeeBusinessHours"] >= 0
        and row["WaitingApprovalBusinessHours"] >= 0
        and row["WaitingVendorBusinessHours"] >= 0
        for row in cases
    )
    checks["case_event_counters"] = all(
        row["TransferCount"] == sum(1 for event in events_by_case[row["CaseKey"]] if event["EventType"] == "Transfer")
        and row["ReopenCount"] == sum(1 for event in events_by_case[row["CaseKey"]] if event["EventType"] == "Reopened")
        for row in cases
    )

    cutoff_key = date_key(parse_datetime(config["cutoff"]))
    final_snapshot_cases = {row["CaseKey"] for row in backlog if row["SnapshotDateKey"] == cutoff_key}
    expected_final_backlog = {
        row["CaseKey"] for row in cases if row["CurrentStatusAtCutoff"] not in {"Closed", "Cancelled"}
    }
    checks["final_backlog_reconciles"] = final_snapshot_cases == expected_final_backlog

    channel_metrics: dict[str, dict[str, float]] = {}
    for channel in config["channels"]:
        channel_cases = [row for row in cases if row["SourceChannel"] == channel]
        incomplete = sum(1 for row in channel_cases if not row["InformationCompleteAtSubmissionFlag"])
        channel_metrics[channel] = {
            "cases": len(channel_cases),
            "incomplete_rate": rate(incomplete, len(channel_cases)),
        }
    email_portal_ratio = (
        channel_metrics["Email"]["incomplete_rate"] / channel_metrics["Portal"]["incomplete_rate"]
        if channel_metrics["Portal"]["incomplete_rate"]
        else 0.0
    )
    checks["email_more_incomplete_than_portal"] = (
        not strict_pattern_checks or email_portal_ratio >= 2.5
    )

    service_by_key = {row["ServiceKey"]: row for row in services}
    payroll_window = [
        row for row in cases
        if is_month_end_window(row["CreatedAt"].date())
    ]
    payroll_outside = [
        row for row in cases
        if not is_month_end_window(row["CreatedAt"].date())
    ]
    payroll_window_share = rate(
        sum(1 for row in payroll_window if service_by_key[row["ServiceKey"]]["ServiceGroup"] == "Payroll & Compensation"),
        len(payroll_window),
    )
    payroll_outside_share = rate(
        sum(1 for row in payroll_outside if service_by_key[row["ServiceKey"]]["ServiceGroup"] == "Payroll & Compensation"),
        len(payroll_outside),
    )
    checks["payroll_month_end_pattern"] = (
        not strict_pattern_checks or payroll_window_share > payroll_outside_share * 1.20
    )

    eligible_pre = [
        row for row in cases
        if service_by_key[row["ServiceKey"]]["ServiceGroup"] == "Employee Data Changes"
        and row["SourceChannel"] == "Portal"
        and row["CreatedAt"].date() < date(2026, 1, 1)
    ]
    eligible_post = [
        row for row in cases
        if service_by_key[row["ServiceKey"]]["ServiceGroup"] == "Employee Data Changes"
        and row["SourceChannel"] == "Portal"
        and row["CreatedAt"].date() >= date(2026, 1, 1)
    ]
    pre_incomplete_rate = rate(
        sum(1 for row in eligible_pre if not row["InformationCompleteAtSubmissionFlag"]),
        len(eligible_pre),
    )
    post_incomplete_rate = rate(
        sum(1 for row in eligible_post if not row["InformationCompleteAtSubmissionFlag"]),
        len(eligible_post),
    )
    intervention_ratio = post_incomplete_rate / pre_incomplete_rate if pre_incomplete_rate else 0.0
    checks["data_change_intervention_pattern"] = (
        not strict_pattern_checks or intervention_ratio <= 0.70
    )

    benefit_delay_durations = [
        row["NetResolutionBusinessHours"]
        for row in cases
        if service_by_key[row["ServiceKey"]]["ServiceCode"] in {"BEN-02", "BEN-03"}
        and date(2025, 4, 1) <= row["CreatedAt"].date() <= date(2025, 6, 30)
        and row["NetResolutionBusinessHours"] is not None
    ]
    benefit_recovery_durations = [
        row["NetResolutionBusinessHours"]
        for row in cases
        if service_by_key[row["ServiceKey"]]["ServiceCode"] in {"BEN-02", "BEN-03"}
        and date(2025, 7, 1) <= row["CreatedAt"].date() <= date(2025, 9, 30)
        and row["NetResolutionBusinessHours"] is not None
    ]
    delay_p90 = percentile(benefit_delay_durations, 0.90)
    recovery_p90 = percentile(benefit_recovery_durations, 0.90)
    checks["benefits_vendor_delay_pattern"] = (
        not strict_pattern_checks
        or bool(delay_p90 is not None and recovery_p90 is not None and delay_p90 >= recovery_p90 * 1.15)
    )

    survey_case = {row["CaseKey"]: row for row in cases}
    reopened_scores = [
        row["OverallSatisfactionScore"] for row in surveys if survey_case[row["CaseKey"]]["ReopenCount"] > 0
    ]
    not_reopened_scores = [
        row["OverallSatisfactionScore"] for row in surveys if survey_case[row["CaseKey"]]["ReopenCount"] == 0
    ]
    reopened_mean = sum(reopened_scores) / len(reopened_scores) if reopened_scores else None
    not_reopened_mean = sum(not_reopened_scores) / len(not_reopened_scores) if not_reopened_scores else None
    csat_difference = (
        reopened_mean - not_reopened_mean
        if reopened_mean is not None and not_reopened_mean is not None
        else None
    )
    checks["reopen_csat_pattern"] = (
        not strict_pattern_checks
        or bool(csat_difference is not None and csat_difference <= -0.30)
    )

    failed = [name for name, passed in checks.items() if not passed]
    metrics = {
        "case_count": len(cases),
        "strict_pattern_checks_applied": strict_pattern_checks,
        "event_count": len(events),
        "survey_count": len(surveys),
        "backlog_snapshot_count": len(backlog),
        "final_backlog_count": len(expected_final_backlog),
        "status_distribution": dict(Counter(row["CurrentStatusAtCutoff"] for row in cases)),
        "channel_metrics": channel_metrics,
        "email_to_portal_incomplete_ratio": round(email_portal_ratio, 4),
        "payroll_window_share": round(payroll_window_share, 4),
        "payroll_outside_share": round(payroll_outside_share, 4),
        "data_change_pre_incomplete_rate": round(pre_incomplete_rate, 4),
        "data_change_post_incomplete_rate": round(post_incomplete_rate, 4),
        "data_change_post_to_pre_ratio": round(intervention_ratio, 4),
        "benefits_delay_p90_hours": round(delay_p90, 4) if delay_p90 is not None else None,
        "benefits_recovery_p90_hours": round(recovery_p90, 4) if recovery_p90 is not None else None,
        "reopened_csat_mean": round(reopened_mean, 4) if reopened_mean is not None else None,
        "not_reopened_csat_mean": round(not_reopened_mean, 4) if not_reopened_mean is not None else None,
        "reopened_csat_difference": round(csat_difference, 4) if csat_difference is not None else None,
    }
    return {"passed": not failed, "checks": checks, "failed_checks": failed, "metrics": metrics}


def prepare_output_directory(output_root: Path, force: bool) -> tuple[Path, Path]:
    output_root.mkdir(parents=True, exist_ok=True)
    raw_dir = output_root / "raw"
    processed_dir = output_root / "processed"
    existing = [path for path in (raw_dir, processed_dir, output_root / "manifest.json") if path.exists()]
    if existing and not force:
        names = ", ".join(path.name for path in existing)
        raise FileExistsError(
            f"Output already exists ({names}). Re-run with --force only if you want to regenerate it."
        )
    if force:
        for directory in (raw_dir, processed_dir):
            if directory.exists():
                shutil.rmtree(directory)
        manifest = output_root / "manifest.json"
        if manifest.exists():
            manifest.unlink()
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    return raw_dir, processed_dir


def write_dataset(
    output_root: Path,
    raw_dir: Path,
    processed_dir: Path,
    processed_tables: dict[str, list[dict[str, Any]]],
    raw_tables: dict[str, list[dict[str, Any]]],
    seed: int,
    validation: dict[str, Any],
) -> dict[str, Any]:
    file_records: list[dict[str, Any]] = []
    for filename, rows in processed_tables.items():
        path = processed_dir / filename
        write_csv(path, rows)
        file_records.append(
            {"layer": "processed", "file": filename, "rows": len(rows), "sha256": sha256_file(path)}
        )
    for filename, rows in raw_tables.items():
        path = raw_dir / filename
        write_csv(path, rows)
        file_records.append(
            {"layer": "raw", "file": filename, "rows": len(rows), "sha256": sha256_file(path)}
        )
    manifest = {
        "project": "HR Services / Service Delivery Control Tower",
        "synthetic_data": True,
        "seed": seed,
        "generated_at": CONFIG["extracted_at"],
        "validation": validation,
        "files": file_records,
    }
    manifest_path = output_root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def generate(seed: int, case_count: int, output_root: Path, force: bool) -> dict[str, Any]:
    config = dict(CONFIG)
    config["seed"] = seed
    config["case_count"] = case_count
    rng = random.Random(seed)
    calendar = BusinessCalendar(config)
    raw_dir, processed_dir = prepare_output_directory(output_root, force)

    date_dimension = build_date_dimension(config, calendar)
    requesters = build_requesters(config, rng)
    agents = build_agents(config, rng)
    locations = clean_dimension_rows(config["locations"], {"weight"})
    organizations = clean_dimension_rows(config["organizations"], {"weight"})
    teams = [dict(row) for row in config["teams"]]
    services = build_service_dimension(config)
    sla = [dict(row) for row in config["sla"]]
    cases, events = build_cases_and_events(config, requesters, agents, rng, calendar, case_count)
    surveys = build_surveys(config, cases, rng, calendar)
    backlog = build_backlog_daily(config, cases, events, calendar)
    capacity = build_capacity_weekly(config, rng)

    validation = validate_dataset(
        config,
        cases,
        events,
        surveys,
        backlog,
        requesters,
        agents,
        services,
    )
    if not validation["passed"]:
        failed = ", ".join(validation["failed_checks"])
        raise AssertionError(f"Synthetic dataset failed validation: {failed}")

    processed_tables = {
        "dim_date.csv": date_dimension,
        "dim_location.csv": locations,
        "dim_organization.csv": organizations,
        "dim_team.csv": teams,
        "dim_requester.csv": requesters,
        "dim_agent.csv": agents,
        "dim_service_catalog.csv": services,
        "dim_sla_policy.csv": sla,
        "fact_cases.csv": cases,
        "fact_case_events.csv": events,
        "fact_surveys.csv": surveys,
        "fact_backlog_daily.csv": backlog,
        "fact_queue_capacity_weekly.csv": capacity,
    }
    raw_tables = {
        "hr_case_export.csv": build_raw_cases(config, cases, services, rng),
        "hr_case_event_log.csv": build_raw_events(config, events, rng),
        "hr_survey_responses.csv": build_raw_surveys(config, surveys, rng),
        "hr_requester_roster.csv": add_raw_metadata(requesters, "SYNTHETIC_HR_ROSTER"),
        "hr_agent_roster.csv": add_raw_metadata(agents, "SYNTHETIC_AGENT_ROSTER"),
        "hr_service_catalog.csv": add_raw_metadata(services, "SYNTHETIC_SERVICE_CATALOG"),
        "hr_locations.csv": add_raw_metadata(locations, "SYNTHETIC_REFERENCE_DATA"),
        "hr_organization_units.csv": add_raw_metadata(organizations, "SYNTHETIC_REFERENCE_DATA"),
        "hr_teams.csv": add_raw_metadata(teams, "SYNTHETIC_REFERENCE_DATA"),
        "hr_sla_policy.csv": add_raw_metadata(sla, "SYNTHETIC_REFERENCE_DATA"),
        "hr_queue_capacity_weekly.csv": add_raw_metadata(capacity, "SYNTHETIC_CAPACITY_EXPORT"),
    }
    return write_dataset(
        output_root,
        raw_dir,
        processed_dir,
        processed_tables,
        raw_tables,
        seed,
        validation,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate the fully synthetic HR Services Control Tower dataset."
    )
    parser.add_argument("--seed", type=int, default=CONFIG["seed"], help="Random seed for reproducibility")
    parser.add_argument(
        "--case-count",
        type=int,
        default=CONFIG["case_count"],
        help="Number of cases to generate (default: 9000)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "data",
        help="Destination directory (default: project/data)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace previously generated raw/processed outputs",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.case_count < 100:
        print("Error: --case-count must be at least 100", file=sys.stderr)
        return 2
    output_root = args.output_dir.resolve()
    try:
        manifest = generate(args.seed, args.case_count, output_root, args.force)
    except (AssertionError, FileExistsError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    metrics = manifest["validation"]["metrics"]
    print("\nGeneracion terminada correctamente")
    print(f"  Casos: {metrics['case_count']:,}")
    print(f"  Eventos: {metrics['event_count']:,}")
    print(f"  Encuestas: {metrics['survey_count']:,}")
    print(f"  Snapshots de backlog: {metrics['backlog_snapshot_count']:,}")
    print(f"  Backlog al corte: {metrics['final_backlog_count']:,}")
    print(f"  Carpeta: {output_root}")
    print("  Validaciones: todas aprobadas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
