"""Generate reproducible synthetic HR lifecycle data with controlled quality issues.

The generator uses only the Python standard library. It writes quarterly raw
extracts for three fictitious source systems and a manifest with hashes,
counts, quality-rule results, and controlled-pattern checks.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import shutil
import sys
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Iterable


PROJECT_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = PROJECT_DIR.parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from config import synthetic_data_config as cfg  # noqa: E402


WORKER_FIELDS = [
    "SourceRecordID",
    "SnapshotDate",
    "ExtractedAt",
    "EmployeeID",
    "EmploymentStatus",
    "WorkerType",
    "EmployeeGroup",
    "HireDate",
    "TerminationDate",
    "LeaveStartDate",
    "LeaveExpectedEndDate",
    "ManagerEmployeeID",
    "PositionID",
    "OrgUnitCode",
    "CostCenterCode",
    "LocationCode",
    "CountryCode",
    "SourceUpdatedAt",
    "RecordConfirmedAt",
    "RecordVersion",
]

EVENT_FIELDS = [
    "SourceRecordID",
    "ExtractBatchDate",
    "ExtractedAt",
    "EventID",
    "EmployeeID",
    "EventType",
    "EventStatus",
    "EffectiveDate",
    "CompletedAt",
    "PreviousEmploymentStatus",
    "NewEmploymentStatus",
    "PreviousManagerEmployeeID",
    "NewManagerEmployeeID",
    "PreviousPositionID",
    "NewPositionID",
    "PreviousOrgUnitCode",
    "NewOrgUnitCode",
    "PreviousCostCenterCode",
    "NewCostCenterCode",
    "PreviousLocationCode",
    "NewLocationCode",
    "SourceUpdatedAt",
    "RecordVersion",
]

POSITION_FIELDS = [
    "SourceRecordID",
    "SnapshotDate",
    "ExtractedAt",
    "PositionID",
    "PositionStatus",
    "PositionFamily",
    "OrgUnitCode",
    "OrgUnitName",
    "FunctionGroup",
    "CostCenterCode",
    "CostCenterName",
    "LocationCode",
    "LocationName",
    "LocationType",
    "CountryCode",
    "ManagerEligibleFlag",
    "ManagerRequiredFlag",
    "MaxIncumbents",
    "ValidFrom",
    "ValidTo",
    "SourceUpdatedAt",
    "RecordVersion",
]

CRITICAL_RECON_FIELDS = (
    "EmploymentStatus",
    "ManagerEmployeeID",
    "PositionID",
    "OrgUnitCode",
    "CostCenterCode",
    "LocationCode",
)


def iso_date(value: date | None) -> str:
    return value.isoformat() if value else ""


def iso_timestamp(day: date, hour: int = 6) -> str:
    return f"{day.isoformat()}T{hour:02d}:00:00{cfg.TIMEZONE_OFFSET}"


def random_date(rng: random.Random, start: date, end: date) -> date:
    if end < start:
        return start
    return start + timedelta(days=rng.randint(0, (end - start).days))


def weighted_choice(rng: random.Random, choices: Iterable[tuple[str, float]]) -> str:
    items = list(choices)
    threshold = rng.random() * sum(weight for _, weight in items)
    cumulative = 0.0
    for value, weight in items:
        cumulative += weight
        if threshold <= cumulative:
            return value
    return items[-1][0]


def business_days_between(start: date, end: date) -> int:
    if end <= start:
        return 0
    cursor = start
    count = 0
    while cursor < end:
        cursor += timedelta(days=1)
        if cursor.weekday() < 5:
            count += 1
    return count


def subtract_business_days(day: date, count: int) -> date:
    cursor = day
    remaining = count
    while remaining > 0:
        cursor -= timedelta(days=1)
        if cursor.weekday() < 5:
            remaining -= 1
    return cursor


def next_snapshot(day: date) -> date:
    for snapshot in cfg.SNAPSHOT_DATES:
        if day <= snapshot:
            return snapshot
    return cfg.SNAPSHOT_DATES[-1]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stable_hash(parts: Iterable[str], length: int = 20) -> str:
    value = "|".join(parts).encode("utf-8")
    return hashlib.sha256(value).hexdigest()[:length].upper()


def choose_unique(rng: random.Random, candidates: list[str], count: int) -> list[str]:
    if not candidates or count <= 0:
        return []
    return rng.sample(candidates, min(count, len(candidates)))


def generate_positions(rng: random.Random) -> list[dict[str, Any]]:
    location_weights = [(code, weight) for code, _, _, _, weight in cfg.LOCATIONS]
    function_weights = [(code, weight) for code, _, weight in cfg.FUNCTION_GROUPS]
    location_info = {code: (name, kind, region) for code, name, kind, region, _ in cfg.LOCATIONS}
    function_info = {code: name for code, name, _ in cfg.FUNCTION_GROUPS}
    positions: list[dict[str, Any]] = []

    # Seed manager positions across every location/function pair.
    pairs = [(loc[0], func[0]) for loc in cfg.LOCATIONS for func in cfg.FUNCTION_GROUPS]
    manager_pairs = [pairs[index % len(pairs)] for index in range(120)]

    for index in range(1, cfg.POSITION_COUNT + 1):
        if index <= len(manager_pairs):
            location_code, function_code = manager_pairs[index - 1]
            manager_eligible = True
        else:
            location_code = weighted_choice(rng, location_weights)
            function_code = weighted_choice(rng, function_weights)
            manager_eligible = rng.random() < 0.035

        location_name, location_type, _ = location_info[location_code]
        function_name = function_info[function_code]
        unit_number = 1 + ((index - 1) % 12)
        org_unit_code = f"{function_code}-{location_code}-{unit_number:02d}"
        cost_center_code = f"CC-{location_code}-{function_code}-{1 + ((index - 1) % 18):02d}"
        is_executive = index <= 7
        collective = index > 120 and rng.random() < 0.12
        max_incumbents = rng.choice((2, 3, 4)) if collective else 1
        family = "Management" if manager_eligible else rng.choice(cfg.POSITION_FAMILIES[function_code])
        positions.append(
            {
                "PositionID": f"POS-{index:06d}",
                "PositionStatus": "Active",
                "PositionFamily": family,
                "OrgUnitCode": org_unit_code,
                "OrgUnitName": f"{function_name} {unit_number:02d}",
                "FunctionGroup": function_code,
                "CostCenterCode": cost_center_code,
                "CostCenterName": f"{location_code} {function_code} Cost Center {1 + ((index - 1) % 18):02d}",
                "LocationCode": location_code,
                "LocationName": location_name,
                "LocationType": location_type,
                "CountryCode": "MX",
                "ManagerEligibleFlag": manager_eligible,
                "ManagerRequiredFlag": not is_executive,
                "MaxIncumbents": max_incumbents,
                "ValidFrom": date(2024, 1, 1),
                "ValidTo": None,
                "SourceUpdatedAt": date(2024, 12, 15),
                "RecordVersion": 1,
            }
        )
    return positions


def generate_employee_profiles(rng: random.Random) -> list[dict[str, Any]]:
    location_weights = [(code, weight) for code, _, _, _, weight in cfg.LOCATIONS]
    function_weights = [(code, weight) for code, _, weight in cfg.FUNCTION_GROUPS]
    profiles: list[dict[str, Any]] = []

    for index in range(1, cfg.DISTINCT_WORKERS + 1):
        initial = index <= cfg.STARTING_EMPLOYED_WORKERS
        if initial:
            hire_date = random_date(rng, date(2012, 1, 1), date(2024, 12, 15))
        else:
            hire_date = random_date(rng, date(2025, 1, 15), date(2026, 5, 31))
        profiles.append(
            {
                "EmployeeID": f"EMP-{index:06d}",
                "HireDate": hire_date,
                "PreHireDate": hire_date - timedelta(days=rng.randint(20, 55)),
                "TerminationDate": None,
                "LeaveStartDate": None,
                "LeaveEndDate": None,
                "WorkerType": weighted_choice(rng, cfg.WORKER_TYPE_WEIGHTS),
                "EmployeeGroup": weighted_choice(rng, cfg.EMPLOYEE_GROUP_WEIGHTS),
                "BaseLocationCode": weighted_choice(rng, location_weights),
                "BaseFunctionGroup": weighted_choice(rng, function_weights),
            }
        )

    # Managers are stable initial employees so referential integrity is valid before injection.
    protected_manager_ids = {profile["EmployeeID"] for profile in profiles[:100]}
    initial_candidates = [p for p in profiles[: cfg.STARTING_EMPLOYED_WORKERS] if p["EmployeeID"] not in protected_manager_ids]
    new_candidates = [p for p in profiles[cfg.STARTING_EMPLOYED_WORKERS :] if p["HireDate"] <= date(2026, 2, 28)]
    termination_profiles = rng.sample(initial_candidates, 150) + rng.sample(new_candidates, 30)
    for profile in termination_profiles:
        earliest = max(profile["HireDate"] + timedelta(days=90), date(2025, 2, 1))
        profile["TerminationDate"] = random_date(rng, earliest, cfg.END_DATE)

    leave_candidates = [p for p in profiles if p["EmployeeID"] not in protected_manager_ids and not p["TerminationDate"]]
    for profile in rng.sample(leave_candidates, 150):
        start = random_date(rng, max(profile["HireDate"] + timedelta(days=60), cfg.START_DATE), date(2026, 5, 15))
        profile["LeaveStartDate"] = start
        profile["LeaveEndDate"] = min(start + timedelta(days=rng.randint(35, 100)), cfg.END_DATE + timedelta(days=30))

    return profiles


def status_at(profile: dict[str, Any], snapshot: date) -> str | None:
    if snapshot < profile["PreHireDate"]:
        return None
    if snapshot < profile["HireDate"]:
        return "PreHire"
    if profile["TerminationDate"] and snapshot >= profile["TerminationDate"]:
        return "Terminated"
    if profile["LeaveStartDate"] and profile["LeaveStartDate"] <= snapshot <= profile["LeaveEndDate"]:
        return "Leave"
    return "Active"


def build_category_timeline(rng: random.Random, profiles: list[dict[str, Any]]) -> dict[date, dict[str, tuple[str, str]]]:
    timeline: dict[date, dict[str, tuple[str, str]]] = {}
    current = {p["EmployeeID"]: (p["BaseLocationCode"], p["BaseFunctionGroup"]) for p in profiles}
    function_codes = [item[0] for item in cfg.FUNCTION_GROUPS]
    location_codes = [item[0] for item in cfg.LOCATIONS]
    profile_by_id = {p["EmployeeID"]: p for p in profiles}

    for snapshot_index, snapshot in enumerate(cfg.SNAPSHOT_DATES):
        if snapshot_index > 0:
            visible = [employee_id for employee_id, profile in profile_by_id.items() if status_at(profile, snapshot) in {"PreHire", "Active", "Leave"}]
            move_count = max(1, round(len(visible) * 0.025))
            movers = set(rng.sample(visible, min(move_count, len(visible))))
            if snapshot == date(2025, 9, 30):
                reorg_candidates = [eid for eid in visible if current[eid][1] in {"ENG", "PRJ", "FSV"}]
                movers.update(rng.sample(reorg_candidates, min(120, len(reorg_candidates))))
            for employee_id in sorted(movers):
                old_location, old_function = current[employee_id]
                if rng.random() < 0.55:
                    choices = [value for value in function_codes if value != old_function]
                    new_function = rng.choice(choices)
                    new_location = old_location
                else:
                    choices = [value for value in location_codes if value != old_location]
                    new_location = rng.choice(choices)
                    new_function = old_function
                current[employee_id] = (new_location, new_function)
        timeline[snapshot] = dict(current)
    return timeline


def assign_states(
    rng: random.Random,
    profiles: list[dict[str, Any]],
    positions: list[dict[str, Any]],
) -> dict[date, dict[str, dict[str, Any]]]:
    profile_by_id = {p["EmployeeID"]: p for p in profiles}
    category_timeline = build_category_timeline(rng, profiles)
    positions_by_category: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for position in positions:
        positions_by_category[(position["LocationCode"], position["FunctionGroup"])].append(position)

    manager_positions = [p for p in positions if p["ManagerEligibleFlag"]][:100]
    manager_ids = [p["EmployeeID"] for p in profiles[:100]]
    manager_position_by_employee = dict(zip(manager_ids, manager_positions, strict=True))
    for employee_id, position in manager_position_by_employee.items():
        profile_by_id[employee_id]["BaseLocationCode"] = position["LocationCode"]
        profile_by_id[employee_id]["BaseFunctionGroup"] = position["FunctionGroup"]
        for snapshot in cfg.SNAPSHOT_DATES:
            category_timeline[snapshot][employee_id] = (position["LocationCode"], position["FunctionGroup"])

    last_position: dict[str, str] = {}
    states_by_snapshot: dict[date, dict[str, dict[str, Any]]] = {}
    position_by_id = {p["PositionID"]: p for p in positions}

    for snapshot in cfg.SNAPSHOT_DATES:
        capacity = {p["PositionID"]: p["MaxIncumbents"] for p in positions}
        assignments: dict[str, dict[str, Any]] = {}
        visible_profiles = [p for p in profiles if status_at(p, snapshot) is not None]
        employed_profiles = [p for p in visible_profiles if status_at(p, snapshot) != "Terminated"]

        # Assign stable managers first.
        for profile in employed_profiles:
            employee_id = profile["EmployeeID"]
            if employee_id not in manager_position_by_employee:
                continue
            position = manager_position_by_employee[employee_id]
            assignments[employee_id] = position
            capacity[position["PositionID"]] -= 1
            last_position[employee_id] = position["PositionID"]

        for profile in employed_profiles:
            employee_id = profile["EmployeeID"]
            if employee_id in assignments:
                continue
            location_code, function_code = category_timeline[snapshot][employee_id]
            prior_id = last_position.get(employee_id)
            prior_position = position_by_id.get(prior_id) if prior_id else None
            if (
                prior_position
                and prior_position["LocationCode"] == location_code
                and prior_position["FunctionGroup"] == function_code
                and capacity[prior_id] > 0
                and not prior_position["ManagerEligibleFlag"]
            ):
                position = prior_position
            else:
                candidates = [
                    p
                    for p in positions_by_category[(location_code, function_code)]
                    if capacity[p["PositionID"]] > 0 and not p["ManagerEligibleFlag"]
                ]
                if not candidates:
                    candidates = [p for p in positions if capacity[p["PositionID"]] > 0 and not p["ManagerEligibleFlag"]]
                position = rng.choice(candidates)
            assignments[employee_id] = position
            capacity[position["PositionID"]] -= 1
            last_position[employee_id] = position["PositionID"]

        active_managers = [eid for eid in manager_ids if eid in assignments]
        managers_by_category: dict[tuple[str, str], list[str]] = defaultdict(list)
        managers_by_function: dict[str, list[str]] = defaultdict(list)
        for manager_id in active_managers:
            position = assignments[manager_id]
            managers_by_category[(position["LocationCode"], position["FunctionGroup"])].append(manager_id)
            managers_by_function[position["FunctionGroup"]].append(manager_id)

        snapshot_states: dict[str, dict[str, Any]] = {}
        for profile in visible_profiles:
            employee_id = profile["EmployeeID"]
            status = status_at(profile, snapshot)
            if status == "Terminated":
                prior_position_id = last_position.get(employee_id)
                if not prior_position_id:
                    location_code, function_code = category_timeline[snapshot][employee_id]
                    historical_candidates = [
                        p
                        for p in positions_by_category[(location_code, function_code)]
                        if not p["ManagerEligibleFlag"]
                    ]
                    historical_position = historical_candidates[
                        (int(employee_id[-4:]) - 1) % len(historical_candidates)
                    ]
                    prior_position_id = historical_position["PositionID"]
                    last_position[employee_id] = prior_position_id
                position = position_by_id[prior_position_id]
            else:
                position = assignments[employee_id]

            if not position["ManagerRequiredFlag"]:
                manager_id = ""
            elif employee_id in manager_ids:
                higher_managers = [eid for eid in manager_ids[:7] if eid != employee_id]
                manager_id = higher_managers[(int(employee_id[-3:]) - 1) % len(higher_managers)]
            else:
                category_managers = managers_by_category[(position["LocationCode"], position["FunctionGroup"])]
                function_managers = managers_by_function[position["FunctionGroup"]]
                candidates = category_managers or function_managers or active_managers
                manager_id = candidates[int(employee_id[-4:]) % len(candidates)]

            snapshot_states[employee_id] = {
                "EmployeeID": employee_id,
                "EmploymentStatus": status,
                "WorkerType": profile["WorkerType"],
                "EmployeeGroup": profile["EmployeeGroup"],
                "HireDate": profile["HireDate"],
                "TerminationDate": profile["TerminationDate"],
                "LeaveStartDate": profile["LeaveStartDate"] if status == "Leave" else None,
                "LeaveExpectedEndDate": profile["LeaveEndDate"] if status == "Leave" else None,
                "ManagerEmployeeID": manager_id,
                "PositionID": position["PositionID"],
                "OrgUnitCode": position["OrgUnitCode"],
                "CostCenterCode": position["CostCenterCode"],
                "LocationCode": position["LocationCode"],
                "CountryCode": "MX",
            }
        states_by_snapshot[snapshot] = snapshot_states
    return states_by_snapshot


def create_events(
    states_by_snapshot: dict[date, dict[str, dict[str, Any]]],
    profiles: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    event_counter = 1

    def add_event(
        employee_id: str,
        event_type: str,
        effective_date: date,
        previous: dict[str, Any] | None,
        new: dict[str, Any],
    ) -> None:
        nonlocal event_counter
        completed_date = min(max(effective_date, cfg.START_DATE - timedelta(days=30)), cfg.END_DATE)
        completed_at = iso_timestamp(completed_date, 14)
        batch_date = next_snapshot(completed_date)
        event_id = f"EVT-{effective_date.year}-{event_counter:05d}"
        events.append(
            {
                "SourceRecordID": f"LHROPS-{event_counter:07d}",
                "ExtractBatchDate": batch_date,
                "ExtractedAt": iso_timestamp(batch_date + timedelta(days=1)),
                "EventID": event_id,
                "EmployeeID": employee_id,
                "EventType": event_type,
                "EventStatus": "Completed",
                "EffectiveDate": effective_date,
                "CompletedAt": completed_at,
                "PreviousEmploymentStatus": previous.get("EmploymentStatus", "") if previous else "",
                "NewEmploymentStatus": new.get("EmploymentStatus", ""),
                "PreviousManagerEmployeeID": previous.get("ManagerEmployeeID", "") if previous else "",
                "NewManagerEmployeeID": new.get("ManagerEmployeeID", ""),
                "PreviousPositionID": previous.get("PositionID", "") if previous else "",
                "NewPositionID": new.get("PositionID", ""),
                "PreviousOrgUnitCode": previous.get("OrgUnitCode", "") if previous else "",
                "NewOrgUnitCode": new.get("OrgUnitCode", ""),
                "PreviousCostCenterCode": previous.get("CostCenterCode", "") if previous else "",
                "NewCostCenterCode": new.get("CostCenterCode", ""),
                "PreviousLocationCode": previous.get("LocationCode", "") if previous else "",
                "NewLocationCode": new.get("LocationCode", ""),
                "SourceUpdatedAt": completed_at,
                "RecordVersion": 1,
            }
        )
        event_counter += 1

    profile_by_id = {p["EmployeeID"]: p for p in profiles}
    first_snapshot = cfg.SNAPSHOT_DATES[0]

    for employee_id, profile in profile_by_id.items():
        visible_snapshots = [s for s in cfg.SNAPSHOT_DATES if employee_id in states_by_snapshot[s]]
        if not visible_snapshots:
            continue
        first_visible = visible_snapshots[0]
        first_state = states_by_snapshot[first_visible][employee_id]
        if profile["HireDate"] < cfg.START_DATE:
            hire_state = dict(first_state)
            hire_state["EmploymentStatus"] = "Active"
            add_event(employee_id, "Hire", profile["HireDate"], None, hire_state)
        else:
            prehire_state = dict(first_state)
            prehire_state["EmploymentStatus"] = "PreHire"
            add_event(employee_id, "PreHireCreated", profile["PreHireDate"], None, prehire_state)
            hire_state = dict(first_state)
            hire_state["EmploymentStatus"] = "Active"
            add_event(employee_id, "Hire", profile["HireDate"], prehire_state, hire_state)

        if profile["LeaveStartDate"]:
            before = dict(first_state)
            before["EmploymentStatus"] = "Active"
            leave_state = dict(before)
            leave_state["EmploymentStatus"] = "Leave"
            add_event(employee_id, "LeaveStart", profile["LeaveStartDate"], before, leave_state)
            active_state = dict(leave_state)
            active_state["EmploymentStatus"] = "Active"
            add_event(employee_id, "LeaveEnd", profile["LeaveEndDate"], leave_state, active_state)

        if profile["TerminationDate"]:
            prior = dict(first_state)
            prior["EmploymentStatus"] = "Active"
            terminated = dict(prior)
            terminated["EmploymentStatus"] = "Terminated"
            add_event(employee_id, "Termination", profile["TerminationDate"], prior, terminated)

    for prior_snapshot, snapshot in zip(cfg.SNAPSHOT_DATES, cfg.SNAPSHOT_DATES[1:]):
        prior_states = states_by_snapshot[prior_snapshot]
        current_states = states_by_snapshot[snapshot]
        effective_date = snapshot - timedelta(days=35)
        for employee_id in sorted(set(prior_states) & set(current_states)):
            previous = prior_states[employee_id]
            current = current_states[employee_id]
            changed = [field for field in CRITICAL_RECON_FIELDS[1:] if previous[field] != current[field]]
            if not changed:
                continue
            if changed == ["ManagerEmployeeID"]:
                event_type = "ManagerChange"
            elif changed == ["LocationCode"]:
                event_type = "LocationChange"
            elif changed == ["CostCenterCode"]:
                event_type = "CostCenterChange"
            else:
                event_type = "Promotion" if int(employee_id[-2:]) % 5 == 0 else "Transfer"
            add_event(employee_id, event_type, effective_date, previous, current)

    events.sort(key=lambda row: (row["ExtractBatchDate"], row["EffectiveDate"], row["EventID"]))
    return events


def latest_source_update(employee_id: str, snapshot: date, events: list[dict[str, Any]], hire_date: date) -> date:
    relevant: list[date] = []
    for event in events:
        if event["EmployeeID"] != employee_id or event["EventStatus"] != "Completed":
            continue
        if event["EffectiveDate"] <= snapshot:
            relevant.append(date.fromisoformat(event["CompletedAt"][:10]))
    return max(relevant, default=hire_date)


def make_worker_rows(
    states_by_snapshot: dict[date, dict[str, dict[str, Any]]],
    events: list[dict[str, Any]],
) -> dict[date, list[dict[str, Any]]]:
    rows_by_snapshot: dict[date, list[dict[str, Any]]] = {}
    for snapshot, states in states_by_snapshot.items():
        rows: list[dict[str, Any]] = []
        for row_number, employee_id in enumerate(sorted(states), start=1):
            state = states[employee_id]
            source_updated = latest_source_update(employee_id, snapshot, events, state["HireDate"])
            confirmed = subtract_business_days(snapshot, 1)
            rows.append(
                {
                    "SourceRecordID": f"GHRIS-{snapshot:%Y%m%d}-{row_number:06d}",
                    "SnapshotDate": snapshot,
                    "ExtractedAt": iso_timestamp(snapshot + timedelta(days=1)),
                    "EmployeeID": employee_id,
                    "EmploymentStatus": state["EmploymentStatus"],
                    "WorkerType": state["WorkerType"],
                    "EmployeeGroup": state["EmployeeGroup"],
                    "HireDate": state["HireDate"],
                    "TerminationDate": state["TerminationDate"],
                    "LeaveStartDate": state["LeaveStartDate"],
                    "LeaveExpectedEndDate": state["LeaveExpectedEndDate"],
                    "ManagerEmployeeID": state["ManagerEmployeeID"],
                    "PositionID": state["PositionID"],
                    "OrgUnitCode": state["OrgUnitCode"],
                    "CostCenterCode": state["CostCenterCode"],
                    "LocationCode": state["LocationCode"],
                    "CountryCode": state["CountryCode"],
                    "SourceUpdatedAt": iso_timestamp(source_updated, 14),
                    "RecordConfirmedAt": iso_timestamp(confirmed, 16),
                    "RecordVersion": 1,
                }
            )
        rows_by_snapshot[snapshot] = rows
    return rows_by_snapshot


def adjusted_rate(rule: str, snapshot: date) -> float:
    rate = cfg.BASE_ISSUE_RATES[rule]
    if snapshot == date(2025, 9, 30) and rule in {"DQ-003", "DQ-007"}:
        rate *= 2.2
    if snapshot == date(2026, 3, 31) and rule in {"DQ-001", "DQ-005"}:
        rate *= 2.0
    if snapshot == date(2026, 6, 30) and rule in {"DQ-001", "DQ-008"}:
        rate *= 0.40
    return rate


def inject_quality_issues(
    rng: random.Random,
    rows_by_snapshot: dict[date, list[dict[str, Any]]],
    positions: list[dict[str, Any]],
    states_by_snapshot: dict[date, dict[str, dict[str, Any]]],
) -> dict[date, dict[str, int]]:
    position_by_id = {p["PositionID"]: p for p in positions}
    manager_position_ids = {p["PositionID"] for p in positions if p["ManagerEligibleFlag"]}
    injected: dict[date, dict[str, int]] = {}

    for snapshot, rows in rows_by_snapshot.items():
        row_by_employee = {row["EmployeeID"]: row for row in rows}
        untouched = set(row_by_employee)
        counts: dict[str, int] = {}

        def take(rule: str, candidates: list[str]) -> list[str]:
            requested = max(1, round(len(rows) * adjusted_rate(rule, snapshot)))
            eligible = [eid for eid in candidates if eid in untouched]
            selected = choose_unique(rng, eligible, requested)
            untouched.difference_update(selected)
            counts[rule] = len(selected)
            return selected

        # DQ-001: omit a required field.
        candidates = [eid for eid, row in row_by_employee.items() if row["EmploymentStatus"] != "Terminated"]
        for employee_id in take("DQ-001", candidates):
            field = rng.choice(("WorkerType", "EmployeeGroup", "OrgUnitCode", "CostCenterCode", "LocationCode"))
            row_by_employee[employee_id][field] = ""

        # DQ-003: invalid or self-referencing manager.
        candidates = [
            eid
            for eid, row in row_by_employee.items()
            if row["EmploymentStatus"] in {"PreHire", "Active", "Leave"}
            and row["ManagerEmployeeID"]
        ]
        for index, employee_id in enumerate(take("DQ-003", candidates)):
            row_by_employee[employee_id]["ManagerEmployeeID"] = employee_id if index % 3 == 0 else "EMP-999999"

        # DQ-004: assignment disagrees with the position reference.
        candidates = [eid for eid, row in row_by_employee.items() if row["PositionID"]]
        for employee_id in take("DQ-004", candidates):
            row_by_employee[employee_id]["CostCenterCode"] = "CC-INVALID"

        # DQ-005: assign extra occupants to valid single-incumbent positions.
        single_positions = [p for p in positions if p["MaxIncumbents"] == 1 and not p["ManagerEligibleFlag"]]
        occupancy_targets: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        for position in single_positions:
            occupancy_targets[(position["LocationCode"], position["FunctionGroup"])].append(position)
        candidates = [
            eid
            for eid, row in row_by_employee.items()
            if row["EmploymentStatus"] in {"PreHire", "Active", "Leave"}
            and row["PositionID"] not in manager_position_ids
        ]
        selected = take("DQ-005", candidates)
        for employee_id in selected:
            current = row_by_employee[employee_id]
            truth = states_by_snapshot[snapshot][employee_id]
            truth_position = position_by_id[truth["PositionID"]]
            category = (truth_position["LocationCode"], truth_position["FunctionGroup"])
            occupied_ids = [
                row["PositionID"]
                for eid, row in row_by_employee.items()
                if eid != employee_id and row["EmploymentStatus"] in {"PreHire", "Active", "Leave"}
            ]
            target = next((p for p in occupancy_targets[category] if p["PositionID"] in occupied_ids), None)
            if target:
                current["PositionID"] = target["PositionID"]
                current["OrgUnitCode"] = target["OrgUnitCode"]
                current["CostCenterCode"] = target["CostCenterCode"]
                current["LocationCode"] = target["LocationCode"]

        # DQ-006: impossible employment dates.
        candidates = [eid for eid, row in row_by_employee.items() if row["HireDate"]]
        for employee_id in take("DQ-006", candidates):
            hire_date = row_by_employee[employee_id]["HireDate"]
            row_by_employee[employee_id]["TerminationDate"] = hire_date - timedelta(days=1)

        # DQ-007: use another valid manager so only reconciliation should fail.
        valid_managers = [
            eid
            for eid, row in row_by_employee.items()
            if row["PositionID"] in manager_position_ids and row["EmploymentStatus"] in {"Active", "Leave"}
        ]
        candidates = [
            eid
            for eid, row in row_by_employee.items()
            if row["EmploymentStatus"] in {"PreHire", "Active", "Leave"} and row["ManagerEmployeeID"]
        ]
        for employee_id in take("DQ-007", candidates):
            current_manager = row_by_employee[employee_id]["ManagerEmployeeID"]
            alternatives = [manager for manager in valid_managers if manager not in {employee_id, current_manager}]
            if alternatives:
                row_by_employee[employee_id]["ManagerEmployeeID"] = rng.choice(alternatives)

        # DQ-008: both change and confirmation timestamps are stale.
        candidates = [
            eid
            for eid, row in row_by_employee.items()
            if row["EmploymentStatus"] in {"PreHire", "Active", "Leave"}
        ]
        for employee_id in take("DQ-008", candidates):
            stale_date = subtract_business_days(snapshot, rng.randint(8, 18))
            row_by_employee[employee_id]["SourceUpdatedAt"] = iso_timestamp(stale_date, 11)
            row_by_employee[employee_id]["RecordConfirmedAt"] = iso_timestamp(stale_date, 11)

        # DQ-002 is injected last so the duplicated row preserves raw ambiguity.
        duplicate_candidates = [eid for eid in sorted(untouched) if row_by_employee[eid]["EmployeeID"]]
        duplicate_count = max(1, round(len(rows) * adjusted_rate("DQ-002", snapshot)))
        duplicate_ids = choose_unique(rng, duplicate_candidates, duplicate_count)
        counts["DQ-002"] = len(duplicate_ids)
        duplicates = []
        for duplicate_index, employee_id in enumerate(duplicate_ids, start=1):
            duplicate = deepcopy(row_by_employee[employee_id])
            duplicate["SourceRecordID"] = f"GHRIS-{snapshot:%Y%m%d}-DUP-{duplicate_index:04d}"
            duplicates.append(duplicate)
        rows.extend(duplicates)
        rows.sort(key=lambda row: (row["EmployeeID"], row["SourceRecordID"]))
        injected[snapshot] = dict(sorted(counts.items()))

    return injected


def make_position_rows(positions: list[dict[str, Any]]) -> dict[date, list[dict[str, Any]]]:
    output: dict[date, list[dict[str, Any]]] = {}
    for snapshot in cfg.SNAPSHOT_DATES:
        rows = []
        for index, position in enumerate(positions, start=1):
            rows.append(
                {
                    "SourceRecordID": f"ORGMD-{snapshot:%Y%m%d}-{index:06d}",
                    "SnapshotDate": snapshot,
                    "ExtractedAt": iso_timestamp(snapshot + timedelta(days=1)),
                    **position,
                }
            )
        output[snapshot] = rows
    return output


def serialize_value(value: Any) -> str | int:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, date):
        return value.isoformat()
    return value


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: serialize_value(row.get(field)) for field in fieldnames})


def canonical_rows(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["EmployeeID"]:
            grouped[row["EmployeeID"]].append(row)
    return {employee_id: sorted(group, key=lambda row: row["SourceRecordID"])[0] for employee_id, group in grouped.items()}


def evaluate_quality(
    rows_by_snapshot: dict[date, list[dict[str, Any]]],
    positions: list[dict[str, Any]],
    states_by_snapshot: dict[date, dict[str, dict[str, Any]]],
) -> dict[str, Any]:
    position_by_id = {p["PositionID"]: p for p in positions}
    summaries: dict[str, dict[str, dict[str, int]]] = {}
    scores: dict[str, float] = {}

    for snapshot, rows in rows_by_snapshot.items():
        results = {rule: {"eligible": 0, "passed": 0, "failed": 0} for rule in cfg.RULE_SEVERITY}
        canonical = canonical_rows(rows)
        grouped = Counter(row["EmployeeID"] for row in rows if row["EmployeeID"])

        required_base = (
            "EmployeeID",
            "EmploymentStatus",
            "WorkerType",
            "EmployeeGroup",
            "HireDate",
            "PositionID",
            "OrgUnitCode",
            "CostCenterCode",
            "LocationCode",
            "SourceUpdatedAt",
            "RecordConfirmedAt",
        )
        for row in rows:
            missing = [field for field in required_base if not row.get(field)]
            if row.get("EmploymentStatus") == "Terminated" and not row.get("TerminationDate"):
                missing.append("TerminationDate")
            if row.get("EmploymentStatus") == "Leave":
                if not row.get("LeaveStartDate"):
                    missing.append("LeaveStartDate")
                if not row.get("LeaveExpectedEndDate"):
                    missing.append("LeaveExpectedEndDate")
            results["DQ-001"]["eligible"] += 1
            results["DQ-001"]["failed" if missing else "passed"] += 1

        for employee_id, count in grouped.items():
            results["DQ-002"]["eligible"] += 1
            results["DQ-002"]["failed" if count != 1 else "passed"] += 1

        for employee_id, row in canonical.items():
            position = position_by_id.get(row.get("PositionID"))
            status = row.get("EmploymentStatus")

            if status in {"PreHire", "Active", "Leave"} and position and position["ManagerRequiredFlag"]:
                results["DQ-003"]["eligible"] += 1
                manager_id = row.get("ManagerEmployeeID")
                manager = canonical.get(manager_id)
                manager_position = position_by_id.get(manager.get("PositionID")) if manager else None
                invalid = (
                    not manager_id
                    or manager_id == employee_id
                    or not manager
                    or manager.get("EmploymentStatus") not in {"Active", "Leave"}
                    or not manager_position
                    or not manager_position["ManagerEligibleFlag"]
                )
                results["DQ-003"]["failed" if invalid else "passed"] += 1

            if row.get("PositionID"):
                results["DQ-004"]["eligible"] += 1
                invalid = not position or any(
                    row.get(field) != position.get(field)
                    for field in ("OrgUnitCode", "CostCenterCode", "LocationCode", "CountryCode")
                )
                results["DQ-004"]["failed" if invalid else "passed"] += 1

            results["DQ-006"]["eligible"] += 1
            try:
                hire_date = row["HireDate"] if isinstance(row["HireDate"], date) else date.fromisoformat(row["HireDate"])
                termination = row.get("TerminationDate")
                if termination and not isinstance(termination, date):
                    termination = date.fromisoformat(termination)
                temporal_invalid = hire_date > snapshot or bool(termination and termination < hire_date)
                if status == "Terminated":
                    temporal_invalid = temporal_invalid or not termination or termination > snapshot
                if status in {"Active", "Leave"} and termination and termination <= snapshot:
                    temporal_invalid = True
                if status == "Leave":
                    leave_start = row.get("LeaveStartDate")
                    leave_end = row.get("LeaveExpectedEndDate")
                    temporal_invalid = temporal_invalid or not leave_start or not leave_end or leave_start > leave_end
            except (TypeError, ValueError):
                temporal_invalid = True
            results["DQ-006"]["failed" if temporal_invalid else "passed"] += 1

            truth = states_by_snapshot[snapshot].get(employee_id)
            if truth:
                results["DQ-007"]["eligible"] += 1
                mismatch = any(row.get(field) != truth.get(field) for field in CRITICAL_RECON_FIELDS)
                results["DQ-007"]["failed" if mismatch else "passed"] += 1

            if status in {"PreHire", "Active", "Leave"}:
                results["DQ-008"]["eligible"] += 1
                try:
                    updated = date.fromisoformat(str(row["SourceUpdatedAt"])[:10])
                    confirmed = date.fromisoformat(str(row["RecordConfirmedAt"])[:10])
                    freshest = max(updated, confirmed)
                    stale = freshest > snapshot or business_days_between(freshest, snapshot) > 5
                except (TypeError, ValueError):
                    stale = True
                results["DQ-008"]["failed" if stale else "passed"] += 1

        occupants: dict[str, list[str]] = defaultdict(list)
        for employee_id, row in canonical.items():
            if row.get("EmploymentStatus") in {"PreHire", "Active", "Leave"} and row.get("PositionID"):
                occupants[row["PositionID"]].append(employee_id)
        for position_id, employee_ids in occupants.items():
            position = position_by_id.get(position_id)
            if not position:
                continue
            results["DQ-005"]["eligible"] += 1
            failed = len(employee_ids) > int(position["MaxIncumbents"])
            results["DQ-005"]["failed" if failed else "passed"] += 1

        weighted_passed = 0
        weighted_eligible = 0
        for rule, counts in results.items():
            weight = cfg.SEVERITY_WEIGHTS[cfg.RULE_SEVERITY[rule]]
            weighted_passed += counts["passed"] * weight
            weighted_eligible += counts["eligible"] * weight
        score = round(100 * weighted_passed / weighted_eligible, 1)
        summaries[snapshot.isoformat()] = results
        scores[snapshot.isoformat()] = score

    return {"by_snapshot": summaries, "score_by_snapshot": scores}


def build_pattern_checks(quality: dict[str, Any]) -> dict[str, Any]:
    by_snapshot = quality["by_snapshot"]

    def failures(snapshot: str, rule: str) -> int:
        return by_snapshot[snapshot][rule]["failed"]

    return {
        "q3_2025_reorganization": {
            "passed": failures("2025-09-30", "DQ-003") > failures("2025-06-30", "DQ-003")
            and failures("2025-09-30", "DQ-007") > failures("2025-06-30", "DQ-007"),
            "observed": {
                "DQ-003_2025-06-30": failures("2025-06-30", "DQ-003"),
                "DQ-003_2025-09-30": failures("2025-09-30", "DQ-003"),
                "DQ-007_2025-06-30": failures("2025-06-30", "DQ-007"),
                "DQ-007_2025-09-30": failures("2025-09-30", "DQ-007"),
            },
        },
        "q1_2026_onboarding_wave": {
            "passed": failures("2026-03-31", "DQ-001") > failures("2025-12-31", "DQ-001")
            and failures("2026-03-31", "DQ-005") > failures("2025-12-31", "DQ-005"),
            "observed": {
                "DQ-001_2025-12-31": failures("2025-12-31", "DQ-001"),
                "DQ-001_2026-03-31": failures("2026-03-31", "DQ-001"),
                "DQ-005_2025-12-31": failures("2025-12-31", "DQ-005"),
                "DQ-005_2026-03-31": failures("2026-03-31", "DQ-005"),
            },
        },
        "q2_2026_data_quality_intervention": {
            "passed": failures("2026-06-30", "DQ-001") < failures("2026-03-31", "DQ-001")
            and failures("2026-06-30", "DQ-008") < failures("2026-03-31", "DQ-008"),
            "observed": {
                "DQ-001_2026-03-31": failures("2026-03-31", "DQ-001"),
                "DQ-001_2026-06-30": failures("2026-06-30", "DQ-001"),
                "DQ-008_2026-03-31": failures("2026-03-31", "DQ-008"),
                "DQ-008_2026-06-30": failures("2026-06-30", "DQ-008"),
            },
        },
    }


def file_entry(path: Path, output_dir: Path, rows: int, columns: int) -> dict[str, Any]:
    return {
        "path": path.relative_to(output_dir).as_posix(),
        "rows": rows,
        "columns": columns,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def generate_dataset(output_dir: Path, seed: int = cfg.RANDOM_SEED, force: bool = False) -> dict[str, Any]:
    output_dir = output_dir.resolve()
    raw_dir = output_dir / "raw"
    manifest_path = output_dir / "manifest.json"
    if raw_dir.exists() or manifest_path.exists():
        if not force:
            raise FileExistsError(f"Output already exists in {output_dir}. Use --force to replace generated artifacts.")
        if raw_dir.exists():
            shutil.rmtree(raw_dir)
        if manifest_path.exists():
            manifest_path.unlink()

    rng = random.Random(seed)
    positions = generate_positions(rng)
    profiles = generate_employee_profiles(rng)
    states_by_snapshot = assign_states(rng, profiles, positions)
    events = create_events(states_by_snapshot, profiles)
    worker_rows = make_worker_rows(states_by_snapshot, events)
    injected = inject_quality_issues(rng, worker_rows, positions, states_by_snapshot)
    position_rows = make_position_rows(positions)

    event_batches: dict[date, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        event_batches[event["ExtractBatchDate"]].append(event)

    inventory: list[dict[str, Any]] = []
    for snapshot in cfg.SNAPSHOT_DATES:
        worker_path = raw_dir / "global_hris" / f"snapshot_date={snapshot.isoformat()}" / "workers.csv"
        write_csv(worker_path, WORKER_FIELDS, worker_rows[snapshot])
        inventory.append(file_entry(worker_path, output_dir, len(worker_rows[snapshot]), len(WORKER_FIELDS)))

        event_path = raw_dir / "local_hr_operations" / f"extract_date={snapshot.isoformat()}" / "lifecycle_events.csv"
        write_csv(event_path, EVENT_FIELDS, event_batches[snapshot])
        inventory.append(file_entry(event_path, output_dir, len(event_batches[snapshot]), len(EVENT_FIELDS)))

        position_path = raw_dir / "organization_master" / f"snapshot_date={snapshot.isoformat()}" / "positions.csv"
        write_csv(position_path, POSITION_FIELDS, position_rows[snapshot])
        inventory.append(file_entry(position_path, output_dir, len(position_rows[snapshot]), len(POSITION_FIELDS)))

    quality = evaluate_quality(worker_rows, positions, states_by_snapshot)
    pattern_checks = build_pattern_checks(quality)
    status_counts = {
        snapshot.isoformat(): dict(sorted(Counter(state["EmploymentStatus"] for state in states.values()).items()))
        for snapshot, states in states_by_snapshot.items()
    }

    config_path = PROJECT_DIR / "config" / "synthetic-data-spec.yaml"
    manifest = {
        "project_id": "hr-data-quality-lifecycle-workbench",
        "organization": "EnergiaNova Industrial Mexico",
        "disclaimer": "Fully synthetic learning scenario; not Siemens Energy data or process.",
        "seed": seed,
        "generated_at": cfg.GENERATED_AT,
        "period": {"start": cfg.START_DATE.isoformat(), "end": cfg.END_DATE.isoformat()},
        "snapshot_dates": [snapshot.isoformat() for snapshot in cfg.SNAPSHOT_DATES],
        "population": {
            "distinct_workers": len(profiles),
            "starting_employed_workers": cfg.STARTING_EMPLOYED_WORKERS,
            "ending_employed_workers": sum(
                1
                for state in states_by_snapshot[cfg.CUTOFF_DATE].values()
                if state["EmploymentStatus"] in {"Active", "Leave"}
            ),
            "positions": len(positions),
            "lifecycle_events": len(events),
            "status_by_snapshot": status_counts,
        },
        "injected_primary_issues": {
            snapshot.isoformat(): counts for snapshot, counts in injected.items()
        },
        "quality_evaluation": quality,
        "controlled_pattern_checks": pattern_checks,
        "privacy": {
            "synthetic_identifiers_only": True,
            "prohibited_fields_present": False,
            "prohibited_fields": [
                "EmployeeName",
                "Email",
                "Phone",
                "NationalIdentifier",
                "BirthDate",
                "Gender",
                "Salary",
                "MedicalInformation",
                "PerformanceRating",
                "FreeTextComment",
            ],
        },
        "configuration": {
            "path": config_path.relative_to(PROJECT_DIR).as_posix(),
            "sha256": sha256_file(config_path),
        },
        "files": sorted(inventory, key=lambda item: item["path"]),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=PROJECT_DIR / "data")
    parser.add_argument("--seed", type=int, default=cfg.RANDOM_SEED)
    parser.add_argument("--force", action="store_true", help="Replace only the generated raw folder and manifest in output-dir.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        manifest = generate_dataset(args.output_dir, seed=args.seed, force=args.force)
    except FileExistsError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    failed_patterns = [name for name, result in manifest["controlled_pattern_checks"].items() if not result["passed"]]
    if failed_patterns:
        print(f"Generation completed, but controlled patterns failed: {', '.join(failed_patterns)}", file=sys.stderr)
        return 1
    print("Synthetic HR data generated successfully")
    print(f"Output: {args.output_dir.resolve()}")
    print(f"Files: {len(manifest['files'])}")
    print(f"Lifecycle events: {manifest['population']['lifecycle_events']}")
    print(f"Final DQ score: {manifest['quality_evaluation']['score_by_snapshot'][cfg.CUTOFF_DATE.isoformat()]:.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

