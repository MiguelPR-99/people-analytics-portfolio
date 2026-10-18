"""Executable configuration for the synthetic data generator.

The human-readable contract lives in ``synthetic-data-spec.yaml``. This module
keeps the generator dependency-free and mirrors the approved values.
"""

from __future__ import annotations

from datetime import date


RANDOM_SEED = 20261012
START_DATE = date(2025, 1, 1)
END_DATE = date(2026, 6, 30)
CUTOFF_DATE = END_DATE
SNAPSHOT_DATES = (
    date(2025, 3, 31),
    date(2025, 6, 30),
    date(2025, 9, 30),
    date(2025, 12, 31),
    date(2026, 3, 31),
    date(2026, 6, 30),
)
EXTRACT_HOUR = 6
TIMEZONE_OFFSET = "-06:00"
GENERATED_AT = "2026-07-01T06:00:00-06:00"

STARTING_EMPLOYED_WORKERS = 1200
NEW_HIRES = 300
TERMINATIONS = 180
DISTINCT_WORKERS = STARTING_EMPLOYED_WORKERS + NEW_HIRES
ENDING_EMPLOYED_WORKERS = STARTING_EMPLOYED_WORKERS + NEW_HIRES - TERMINATIONS
POSITION_COUNT = 1450

LOCATIONS = (
    ("BJPL", "Bajio Manufacturing Plant", "Plant", "Central Mexico", 0.45),
    ("QESC", "Queretaro Engineering and Service Center", "Engineering and Service Center", "Central Mexico", 0.20),
    ("MXCO", "Mexico City Corporate Office", "Corporate Office", "Central Mexico", 0.15),
    ("MFSH", "Monterrey Field Service Hub", "Field Service Hub", "Northern Mexico", 0.20),
)

FUNCTION_GROUPS = (
    ("MFG", "Manufacturing Operations", 0.30),
    ("ENG", "Engineering and R&D", 0.16),
    ("FSV", "Field Service", 0.15),
    ("PRJ", "Project Execution", 0.10),
    ("SCM", "Supply Chain", 0.11),
    ("COM", "Sales and Commercial", 0.07),
    ("COR", "Corporate Functions", 0.11),
)

POSITION_FAMILIES = {
    "MFG": ("Production", "Quality", "Maintenance", "Operations Engineering"),
    "ENG": ("Mechanical Engineering", "Electrical Engineering", "Digital Engineering", "R&D"),
    "FSV": ("Field Service", "Technical Support", "Service Planning"),
    "PRJ": ("Project Management", "Project Controls", "Site Coordination"),
    "SCM": ("Procurement", "Logistics", "Materials Planning"),
    "COM": ("Sales", "Commercial Management", "Business Development"),
    "COR": ("Finance", "People and Organization", "Digital and IT", "Legal and Compliance"),
}

WORKER_TYPE_WEIGHTS = (("Regular", 0.84), ("Temporary", 0.10), ("Intern", 0.06))
EMPLOYEE_GROUP_WEIGHTS = (("Salaried", 0.58), ("Hourly", 0.42))

SEVERITY_WEIGHTS = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
SLA_BUSINESS_DAYS = {"Critical": 1, "High": 3, "Medium": 5, "Low": 10}
RULE_SEVERITY = {
    "DQ-001": "High",
    "DQ-002": "Critical",
    "DQ-003": "High",
    "DQ-004": "High",
    "DQ-005": "High",
    "DQ-006": "Critical",
    "DQ-007": "Critical",
    "DQ-008": "Medium",
}

BASE_ISSUE_RATES = {
    "DQ-001": 0.007,
    "DQ-002": 0.003,
    "DQ-003": 0.010,
    "DQ-004": 0.008,
    "DQ-005": 0.005,
    "DQ-006": 0.003,
    "DQ-007": 0.012,
    "DQ-008": 0.010,
}

SOURCE_SYSTEMS = {
    "GHRIS": "Global HRIS worker snapshot",
    "LHROPS": "Local employee lifecycle events",
    "ORGMD": "Organization master data",
}

