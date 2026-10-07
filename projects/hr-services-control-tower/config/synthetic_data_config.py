"""Executable configuration for the synthetic HR Services dataset.

The human-readable design contract lives in synthetic-data-spec.yaml. This
module mirrors the values required by the generator while keeping the runtime
dependency-free for beginners.
"""

from __future__ import annotations


CONFIG = {
    "seed": 20260824,
    "start_date": "2025-01-01",
    "end_date": "2026-06-30",
    "cutoff": "2026-06-30T23:59:59",
    "extracted_at": "2026-07-01T06:00:00",
    "requester_count": 1200,
    "agent_count": 18,
    "case_count": 9000,
    "service_start_hour": 8,
    "service_end_hour": 16,
    "holidays": [
        "2025-01-01",
        "2025-02-03",
        "2025-03-17",
        "2025-05-01",
        "2025-09-16",
        "2025-11-17",
        "2025-12-25",
        "2026-01-01",
        "2026-02-02",
        "2026-03-16",
        "2026-05-01",
    ],
    "locations": [
        {
            "LocationKey": 1,
            "LocationCode": "BJPL",
            "LocationName": "Bajio Manufacturing Plant",
            "LocationType": "Plant",
            "Region": "Central Mexico",
            "weight": 0.52,
        },
        {
            "LocationKey": 2,
            "LocationCode": "QHSC",
            "LocationName": "Queretaro HR Service Center",
            "LocationType": "Service Center",
            "Region": "Central Mexico",
            "weight": 0.23,
        },
        {
            "LocationKey": 3,
            "LocationCode": "MXCO",
            "LocationName": "Mexico City Corporate Office",
            "LocationType": "Corporate Office",
            "Region": "Central Mexico",
            "weight": 0.25,
        },
    ],
    "organizations": [
        {"OrgUnitKey": 1, "OrgUnitCode": "MFG", "OrgUnitName": "Manufacturing", "FunctionGroup": "Operations", "weight": 0.35},
        {"OrgUnitKey": 2, "OrgUnitCode": "ENG", "OrgUnitName": "Engineering", "FunctionGroup": "Operations", "weight": 0.14},
        {"OrgUnitKey": 3, "OrgUnitCode": "SVO", "OrgUnitName": "Service Operations", "FunctionGroup": "Operations", "weight": 0.14},
        {"OrgUnitKey": 4, "OrgUnitCode": "SC", "OrgUnitName": "Supply Chain", "FunctionGroup": "Operations", "weight": 0.12},
        {"OrgUnitKey": 5, "OrgUnitCode": "SAL", "OrgUnitName": "Sales", "FunctionGroup": "Commercial", "weight": 0.09},
        {"OrgUnitKey": 6, "OrgUnitCode": "FIN", "OrgUnitName": "Finance", "FunctionGroup": "Corporate", "weight": 0.07},
        {"OrgUnitKey": 7, "OrgUnitCode": "COR", "OrgUnitName": "Corporate Functions", "FunctionGroup": "Corporate", "weight": 0.09},
    ],
    "teams": [
        {"TeamKey": 1, "TeamCode": "PAYTIME", "TeamName": "Payroll & Time", "ServiceScope": "Payroll, compensation, time and attendance"},
        {"TeamKey": 2, "TeamCode": "BENDOC", "TeamName": "Benefits & Documents", "ServiceScope": "Benefits, certificates and HR documents"},
        {"TeamKey": 3, "TeamCode": "DATALIFE", "TeamName": "Employee Data & Lifecycle", "ServiceScope": "Employee data, onboarding and offboarding"},
    ],
    "sla": [
        {"SLAPolicyKey": 1, "Priority": "Critical", "FirstResponseSLAHours": 2.0, "ResolutionSLAHours": 8.0, "PauseOnEmployeeWaitFlag": True, "PolicyVersion": "SYN-1.0"},
        {"SLAPolicyKey": 2, "Priority": "High", "FirstResponseSLAHours": 4.0, "ResolutionSLAHours": 16.0, "PauseOnEmployeeWaitFlag": True, "PolicyVersion": "SYN-1.0"},
        {"SLAPolicyKey": 3, "Priority": "Standard", "FirstResponseSLAHours": 8.0, "ResolutionSLAHours": 40.0, "PauseOnEmployeeWaitFlag": True, "PolicyVersion": "SYN-1.0"},
        {"SLAPolicyKey": 4, "Priority": "Low", "FirstResponseSLAHours": 16.0, "ResolutionSLAHours": 80.0, "PauseOnEmployeeWaitFlag": True, "PolicyVersion": "SYN-1.0"},
    ],
    "channels": {
        "Portal": {"weight": 0.55, "incomplete": 0.05, "survey_response": 0.48},
        "Email": {"weight": 0.25, "incomplete": 0.22, "survey_response": 0.42},
        "Teams": {"weight": 0.12, "incomplete": 0.12, "survey_response": 0.38},
        "Phone": {"weight": 0.08, "incomplete": 0.10, "survey_response": 0.32},
    },
    "services": [
        {"ServiceKey": 1, "ServiceCode": "PAY-01", "ServiceGroup": "Payroll & Compensation", "RequestType": "Payslip Clarification", "OwnerTeamKey": 1, "group_weight": 0.18, "type_weight": 0.35, "BaseComplexity": "Low", "DefaultPriority": "Standard", "ApprovalProbability": 0.02, "VendorDependencyProbability": 0.02, "FirstContactResolutionBaseProbability": 0.78},
        {"ServiceKey": 2, "ServiceCode": "PAY-02", "ServiceGroup": "Payroll & Compensation", "RequestType": "Payment Discrepancy", "OwnerTeamKey": 1, "group_weight": 0.18, "type_weight": 0.40, "BaseComplexity": "High", "DefaultPriority": "High", "ApprovalProbability": 0.18, "VendorDependencyProbability": 0.05, "FirstContactResolutionBaseProbability": 0.42},
        {"ServiceKey": 3, "ServiceCode": "PAY-03", "ServiceGroup": "Payroll & Compensation", "RequestType": "Bank or Tax Data", "OwnerTeamKey": 1, "group_weight": 0.18, "type_weight": 0.25, "BaseComplexity": "Medium", "DefaultPriority": "Standard", "ApprovalProbability": 0.20, "VendorDependencyProbability": 0.03, "FirstContactResolutionBaseProbability": 0.58},
        {"ServiceKey": 4, "ServiceCode": "BEN-01", "ServiceGroup": "Benefits", "RequestType": "Enrollment or Change", "OwnerTeamKey": 2, "group_weight": 0.15, "type_weight": 0.42, "BaseComplexity": "Medium", "DefaultPriority": "Standard", "ApprovalProbability": 0.12, "VendorDependencyProbability": 0.28, "FirstContactResolutionBaseProbability": 0.55},
        {"ServiceKey": 5, "ServiceCode": "BEN-02", "ServiceGroup": "Benefits", "RequestType": "Dependent Update", "OwnerTeamKey": 2, "group_weight": 0.15, "type_weight": 0.33, "BaseComplexity": "Medium", "DefaultPriority": "Standard", "ApprovalProbability": 0.18, "VendorDependencyProbability": 0.30, "FirstContactResolutionBaseProbability": 0.50},
        {"ServiceKey": 6, "ServiceCode": "BEN-03", "ServiceGroup": "Benefits", "RequestType": "Vendor Inquiry", "OwnerTeamKey": 2, "group_weight": 0.15, "type_weight": 0.25, "BaseComplexity": "High", "DefaultPriority": "Standard", "ApprovalProbability": 0.05, "VendorDependencyProbability": 0.72, "FirstContactResolutionBaseProbability": 0.34},
        {"ServiceKey": 7, "ServiceCode": "TNA-01", "ServiceGroup": "Time & Attendance", "RequestType": "Time Correction", "OwnerTeamKey": 1, "group_weight": 0.16, "type_weight": 0.44, "BaseComplexity": "Medium", "DefaultPriority": "Standard", "ApprovalProbability": 0.30, "VendorDependencyProbability": 0.01, "FirstContactResolutionBaseProbability": 0.54},
        {"ServiceKey": 8, "ServiceCode": "TNA-02", "ServiceGroup": "Time & Attendance", "RequestType": "Absence or Leave Registration", "OwnerTeamKey": 1, "group_weight": 0.16, "type_weight": 0.34, "BaseComplexity": "Medium", "DefaultPriority": "Standard", "ApprovalProbability": 0.35, "VendorDependencyProbability": 0.04, "FirstContactResolutionBaseProbability": 0.48},
        {"ServiceKey": 9, "ServiceCode": "TNA-03", "ServiceGroup": "Time & Attendance", "RequestType": "Overtime Query", "OwnerTeamKey": 1, "group_weight": 0.16, "type_weight": 0.22, "BaseComplexity": "Low", "DefaultPriority": "Low", "ApprovalProbability": 0.15, "VendorDependencyProbability": 0.01, "FirstContactResolutionBaseProbability": 0.70},
        {"ServiceKey": 10, "ServiceCode": "EDC-01", "ServiceGroup": "Employee Data Changes", "RequestType": "Personal or Contact Data", "OwnerTeamKey": 3, "group_weight": 0.19, "type_weight": 0.46, "BaseComplexity": "Low", "DefaultPriority": "Low", "ApprovalProbability": 0.05, "VendorDependencyProbability": 0.00, "FirstContactResolutionBaseProbability": 0.76},
        {"ServiceKey": 11, "ServiceCode": "EDC-02", "ServiceGroup": "Employee Data Changes", "RequestType": "Emergency or Dependent Data", "OwnerTeamKey": 3, "group_weight": 0.19, "type_weight": 0.30, "BaseComplexity": "Medium", "DefaultPriority": "Standard", "ApprovalProbability": 0.10, "VendorDependencyProbability": 0.00, "FirstContactResolutionBaseProbability": 0.64},
        {"ServiceKey": 12, "ServiceCode": "EDC-03", "ServiceGroup": "Employee Data Changes", "RequestType": "Position or Location Data", "OwnerTeamKey": 3, "group_weight": 0.19, "type_weight": 0.24, "BaseComplexity": "High", "DefaultPriority": "High", "ApprovalProbability": 0.65, "VendorDependencyProbability": 0.00, "FirstContactResolutionBaseProbability": 0.35},
        {"ServiceKey": 13, "ServiceCode": "DOC-01", "ServiceGroup": "HR Documents & Certificates", "RequestType": "Employment Certificate", "OwnerTeamKey": 2, "group_weight": 0.15, "type_weight": 0.48, "BaseComplexity": "Low", "DefaultPriority": "Low", "ApprovalProbability": 0.02, "VendorDependencyProbability": 0.00, "FirstContactResolutionBaseProbability": 0.82},
        {"ServiceKey": 14, "ServiceCode": "DOC-02", "ServiceGroup": "HR Documents & Certificates", "RequestType": "Reference or Confirmation Letter", "OwnerTeamKey": 2, "group_weight": 0.15, "type_weight": 0.28, "BaseComplexity": "Medium", "DefaultPriority": "Standard", "ApprovalProbability": 0.18, "VendorDependencyProbability": 0.00, "FirstContactResolutionBaseProbability": 0.60},
        {"ServiceKey": 15, "ServiceCode": "DOC-03", "ServiceGroup": "HR Documents & Certificates", "RequestType": "Document Copy", "OwnerTeamKey": 2, "group_weight": 0.15, "type_weight": 0.24, "BaseComplexity": "Low", "DefaultPriority": "Low", "ApprovalProbability": 0.01, "VendorDependencyProbability": 0.00, "FirstContactResolutionBaseProbability": 0.86},
        {"ServiceKey": 16, "ServiceCode": "ONB-01", "ServiceGroup": "Onboarding", "RequestType": "Pre-hire Documents", "OwnerTeamKey": 3, "group_weight": 0.10, "type_weight": 0.38, "BaseComplexity": "Medium", "DefaultPriority": "High", "ApprovalProbability": 0.15, "VendorDependencyProbability": 0.02, "FirstContactResolutionBaseProbability": 0.52},
        {"ServiceKey": 17, "ServiceCode": "ONB-02", "ServiceGroup": "Onboarding", "RequestType": "HR System Setup", "OwnerTeamKey": 3, "group_weight": 0.10, "type_weight": 0.34, "BaseComplexity": "High", "DefaultPriority": "High", "ApprovalProbability": 0.08, "VendorDependencyProbability": 0.18, "FirstContactResolutionBaseProbability": 0.38},
        {"ServiceKey": 18, "ServiceCode": "ONB-03", "ServiceGroup": "Onboarding", "RequestType": "Orientation Support", "OwnerTeamKey": 3, "group_weight": 0.10, "type_weight": 0.28, "BaseComplexity": "Low", "DefaultPriority": "Standard", "ApprovalProbability": 0.02, "VendorDependencyProbability": 0.00, "FirstContactResolutionBaseProbability": 0.78},
        {"ServiceKey": 19, "ServiceCode": "OFF-01", "ServiceGroup": "Offboarding", "RequestType": "Termination Documents", "OwnerTeamKey": 3, "group_weight": 0.07, "type_weight": 0.34, "BaseComplexity": "Medium", "DefaultPriority": "High", "ApprovalProbability": 0.25, "VendorDependencyProbability": 0.00, "FirstContactResolutionBaseProbability": 0.48},
        {"ServiceKey": 20, "ServiceCode": "OFF-02", "ServiceGroup": "Offboarding", "RequestType": "Final Pay Coordination", "OwnerTeamKey": 3, "group_weight": 0.07, "type_weight": 0.33, "BaseComplexity": "High", "DefaultPriority": "Critical", "ApprovalProbability": 0.40, "VendorDependencyProbability": 0.08, "FirstContactResolutionBaseProbability": 0.30},
        {"ServiceKey": 21, "ServiceCode": "OFF-03", "ServiceGroup": "Offboarding", "RequestType": "Asset or Access Clearance", "OwnerTeamKey": 3, "group_weight": 0.07, "type_weight": 0.33, "BaseComplexity": "High", "DefaultPriority": "High", "ApprovalProbability": 0.35, "VendorDependencyProbability": 0.20, "FirstContactResolutionBaseProbability": 0.32},
    ],
    "raw_issues": {
        "duplicate_case_rate": 0.008,
        "label_variant_rate": 0.015,
        "blank_channel_rate": 0.005,
        "whitespace_rate": 0.010,
        "mixed_boolean_rate": 0.020,
        "duplicate_event_rate": 0.005,
        "orphan_survey_rate": 0.003,
    },
}

