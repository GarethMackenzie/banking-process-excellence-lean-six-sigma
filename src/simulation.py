from __future__ import annotations

import hashlib
import json
import math
import platform
import time
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from .config import ROOT, SimulationConfig

REGIONS = ["Northern", "Southern", "Eastern", "Western", "Central"]
SHIFTS = ["Morning", "Afternoon", "Evening"]
PRODUCTS = ["Transactional Account", "Savings Account", "Credit Card", "Personal Loan", "Business Account"]
SEGMENTS = ["Retail Mass Market", "Retail Affluent", "Small Business", "Student", "Private Banking"]
CHANNELS = ["Digital App", "Branch", "Call Centre", "Broker Referral"]

COSTS = {
    "prevention_per_application": 4.00,
    "required_manual_review": 45.00,
    "defect_driven_review": 45.00,
    "rework_per_cycle": 35.00,
    "repeat_processing_per_cycle": 20.00,
    "complaint": 80.00,
    "abandonment": 150.00,
    "expedited_handling": 60.00,
}

SLA_BY_COMPLEXITY = {"Low": 8.0, "Medium": 16.0, "High": 24.0}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _lognormal(rng: np.random.Generator, median: np.ndarray | float, sigma: float, size: int) -> np.ndarray:
    median_arr = np.maximum(np.asarray(median, dtype=float), 0.1)
    return rng.lognormal(np.log(median_arr), sigma=sigma, size=size)


def generate_calendar(cfg: SimulationConfig, rng: np.random.Generator) -> pd.DataFrame:
    dates = pd.date_range(cfg.start_date, cfg.end_date, freq="D")
    cal = pd.DataFrame({"Date": dates})
    cal["Day_Of_Week"] = cal["Date"].dt.day_name()
    cal["Is_Weekend"] = cal["Date"].dt.weekday >= 5
    weekday_idx = cal.index[~cal["Is_Weekend"]].to_numpy()
    n_holidays = max(1, int(round(len(weekday_idx) * cfg.public_holiday_rate)))
    holiday_idx = rng.choice(weekday_idx, size=n_holidays, replace=False)
    cal["Is_Public_Holiday"] = False
    cal.loc[holiday_idx, "Is_Public_Holiday"] = True
    cal["Is_Business_Day"] = (~cal["Is_Weekend"]) & (~cal["Is_Public_Holiday"])
    cal["Branch_Open"] = cal["Is_Business_Day"]
    cal["Call_Centre_Open"] = ~cal["Is_Public_Holiday"]
    cal["Digital_Available"] = True
    cal["Operating_Start"] = "08:00"
    cal["Operating_End"] = "17:00"
    return cal


def generate_branches(cfg: SimulationConfig, rng: np.random.Generator) -> pd.DataFrame:
    branch_ids = [f"BR-{i:03d}" for i in range(1, cfg.n_branches + 1)]
    regions = [REGIONS[(i - 1) % len(REGIONS)] for i in range(1, cfg.n_branches + 1)]
    size_band = rng.choice(["Small", "Medium", "Large"], size=cfg.n_branches, p=[0.35, 0.45, 0.20])
    acquisition_weight = np.where(size_band == "Large", 1.8, np.where(size_band == "Medium", 1.15, 0.65))
    return pd.DataFrame({
        "Branch_ID": branch_ids,
        "Region": regions,
        "Branch_Size": size_band,
        "Acquisition_Weight": acquisition_weight,
    })


def generate_analysts(cfg: SimulationConfig, branches: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    for i in range(cfg.n_analysts):
        b = branches.iloc[i % len(branches)]
        shift = SHIFTS[(i // len(branches)) % len(SHIFTS)]
        skill = rng.choice(["Standard", "Advanced", "Specialist"], p=[0.55, 0.30, 0.15])
        experience = rng.choice(["0-2 years", "3-5 years", "6+ years"], p=[0.35, 0.40, 0.25])
        authority = {"Standard": "Standard KYC", "Advanced": "Enhanced KYC", "Specialist": "EDD / Complex"}[skill]
        rows.append({
            "Analyst_ID": f"AN-{i+1:04d}",
            "Home_Branch": b["Branch_ID"],
            "Primary_Shift": shift,
            "Skill_Level": skill,
            "Experience_Band": experience,
            "KYC_Authority_Level": authority,
            "Employment_Status": "Active",
        })
    return pd.DataFrame(rows)


def _exact_arrival_counts(cfg: SimulationConfig, cal: pd.DataFrame, rng: np.random.Generator, events: pd.DataFrame | None = None) -> np.ndarray:
    day_index = np.arange(len(cal))
    month = cal["Date"].dt.month.to_numpy()
    seasonal = 1.0 + 0.16 * np.sin(2 * np.pi * (month - 2) / 12.0)
    growth = 1.0 + 0.30 * (day_index / max(1, len(cal) - 1))
    day_factor = np.where(cal["Is_Business_Day"].to_numpy(), 1.0, 0.20)
    weights = np.maximum(seasonal * growth * day_factor, 0.01)
    if events is not None and not events.empty:
        surges = events.loc[events["Event_Type"].eq("Regional Demand Surge")]
        date_to_idx = {pd.Timestamp(d).date(): i for i, d in enumerate(cal["Date"])}
        for r in surges.itertuples():
            i = date_to_idx.get(pd.Timestamp(r.Start_Timestamp).date())
            if i is not None:
                weights[i] *= float(r.Magnitude)
    probs = weights / weights.sum()
    return rng.multinomial(cfg.n_applications, probs)


def _channel_probs(is_business_day: bool, call_open: bool) -> tuple[list[str], list[float]]:
    if is_business_day:
        return CHANNELS, [0.46, 0.29, 0.15, 0.10]
    if call_open:
        return ["Digital App", "Call Centre"], [0.84, 0.16]
    return ["Digital App"], [1.0]


def generate_application_context(cfg: SimulationConfig, cal: pd.DataFrame, branches: pd.DataFrame, events: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    counts = _exact_arrival_counts(cfg, cal, rng, events)
    app_dates = np.repeat(cal["Date"].to_numpy(), counts)
    n = len(app_dates)
    assert n == cfg.n_applications
    df = pd.DataFrame({"Application_Date": pd.to_datetime(app_dates)})
    df["Application_ID"] = [f"APX{1000000+i:07d}" for i in range(n)]
    df["Application_Month"] = df["Application_Date"].dt.to_period("M").astype(str)

    cal_lookup = cal.set_index("Date")
    is_bus = df["Application_Date"].map(cal_lookup["Is_Business_Day"]).astype(bool)
    call_open = df["Application_Date"].map(cal_lookup["Call_Centre_Open"]).astype(bool)
    channels = []
    for b, c in zip(is_bus.to_numpy(), call_open.to_numpy()):
        vals, probs = _channel_probs(bool(b), bool(c))
        channels.append(rng.choice(vals, p=probs))
    df["Channel"] = channels

    df["Customer_Segment"] = rng.choice(SEGMENTS, size=n, p=[0.52, 0.20, 0.15, 0.09, 0.04])
    df["Product_Type"] = rng.choice(PRODUCTS, size=n, p=[0.34, 0.22, 0.19, 0.15, 0.10])
    df["Region"] = rng.choice(REGIONS, size=n, p=[0.24, 0.19, 0.17, 0.21, 0.19])

    branch_by_region = {r: branches.loc[branches["Region"].eq(r)].copy() for r in REGIONS}
    assigned = []
    for r in df["Region"]:
        sub = branch_by_region[r]
        p = sub["Acquisition_Weight"].to_numpy(float)
        p = p / p.sum()
        assigned.append(rng.choice(sub["Branch_ID"].to_numpy(), p=p))
    df["Branch_ID"] = assigned

    shift_probs = {
        "Digital App": [0.30, 0.35, 0.35],
        "Call Centre": [0.32, 0.43, 0.25],
        "Branch": [0.48, 0.47, 0.05],
        "Broker Referral": [0.40, 0.45, 0.15],
    }
    df["Shift"] = [rng.choice(SHIFTS, p=shift_probs[c]) for c in df["Channel"]]

    # Arrival clock respects channel operating patterns.
    hour = np.empty(n)
    for ch in CHANNELS:
        mask = df["Channel"].eq(ch).to_numpy()
        m = mask.sum()
        if m == 0:
            continue
        if ch == "Digital App":
            hour[mask] = rng.uniform(0, 24, m)
        elif ch == "Branch":
            hour[mask] = rng.uniform(8, 16.75, m)
        elif ch == "Call Centre":
            hour[mask] = rng.uniform(7, 21, m)
        else:
            hour[mask] = rng.uniform(8, 18, m)
    df["Application_Received_Timestamp"] = df["Application_Date"] + pd.to_timedelta(hour, unit="h")

    # Stable process/control risk features. Customer segment is not used in risk scoring.
    product_risk = df["Product_Type"].map({
        "Savings Account": 1, "Transactional Account": 1, "Credit Card": 2,
        "Personal Loan": 2, "Business Account": 3,
    }).astype(int)
    df["Product_Risk_Class"] = product_risk
    df["Ownership_Complexity_Flag"] = ((df["Product_Type"].eq("Business Account")) & (rng.random(n) < 0.55)).astype(int)
    df["Identity_Exception_History_Flag"] = rng.binomial(1, 0.035, n)
    df["Source_Channel_Risk"] = df["Channel"].map({"Digital App": 2, "Branch": 1, "Call Centre": 2, "Broker Referral": 2}).astype(int)
    df["Enhanced_Due_Diligence_Flag"] = ((product_risk.eq(3)) & (rng.random(n) < 0.30) | (df["Ownership_Complexity_Flag"].eq(1) & (rng.random(n) < 0.40))).astype(int)
    verification_noise = rng.normal(0, 5, n)
    risk_score = (
        8 + 10 * (product_risk - 1) + 18 * df["Ownership_Complexity_Flag"]
        + 24 * df["Enhanced_Due_Diligence_Flag"]
        + 22 * df["Identity_Exception_History_Flag"]
        + 7 * (df["Source_Channel_Risk"] - 1) + verification_noise
    )
    df["Verification_Risk_Score"] = np.clip(risk_score, 0, 100).round(1)
    df["Risk_Score"] = df["Verification_Risk_Score"]
    df["Risk_Tier"] = pd.cut(df["Risk_Score"], bins=[-np.inf, 34.999, 64.999, np.inf], labels=["Low", "Medium", "High"]).astype(str)

    df["Products_Requested"] = rng.choice([1, 2, 3], size=n, p=[0.72, 0.22, 0.06])
    base_docs = df["Product_Type"].map({
        "Transactional Account": 3, "Savings Account": 3, "Credit Card": 4,
        "Personal Loan": 5, "Business Account": 7,
    }).astype(int)
    df["Documents_Required"] = (base_docs + (df["Products_Requested"] - 1) + 2 * df["Ownership_Complexity_Flag"] + df["Enhanced_Due_Diligence_Flag"]).astype(int)

    # Stable operational complexity score and fixed bands.
    complexity = (
        10 + 8 * (df["Products_Requested"] - 1)
        + 3 * np.maximum(df["Documents_Required"] - 3, 0)
        + 14 * df["Ownership_Complexity_Flag"]
        + 10 * df["Enhanced_Due_Diligence_Flag"]
        + 8 * (df["Product_Risk_Class"] - 1)
    )
    df["Complexity_Score"] = complexity.astype(int)
    df["Application_Complexity"] = pd.cut(complexity, bins=[-np.inf, 29, 49, np.inf], labels=["Low", "Medium", "High"]).astype(str)

    return df


def generate_special_causes(cfg: SimulationConfig, cal: pd.DataFrame, branches: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    business_dates = cal.loc[cal["Is_Business_Day"], "Date"].to_numpy()
    events = []
    event_id = 1

    def add_events(event_type: str, count: int, magnitude_range: tuple[float, float], affected_process: str, expected: str, duration_hours: tuple[float, float]):
        nonlocal event_id
        for d in rng.choice(business_dates, size=min(count, len(business_dates)), replace=False):
            b = rng.choice(branches["Branch_ID"].to_numpy())
            s = rng.choice(SHIFTS)
            if s == "Morning": start_h = rng.uniform(8, 10)
            elif s == "Afternoon": start_h = rng.uniform(12, 15)
            else: start_h = rng.uniform(17, 20)
            duration = rng.uniform(*duration_hours)
            start = pd.Timestamp(d) + pd.to_timedelta(start_h, unit="h")
            end = start + pd.to_timedelta(duration, unit="h")
            events.append({
                "Event_ID": f"SC{event_id:04d}", "Start_Timestamp": start, "End_Timestamp": end,
                "Branch_ID": b, "Shift": s, "Event_Type": event_type,
                "Magnitude": round(float(rng.uniform(*magnitude_range)), 3),
                "Affected_Process": affected_process, "Expected_Direction": expected,
            })
            event_id += 1

    add_events("System Outage", cfg.outage_event_count, (0.45, 1.0), "Verification / KYC", "Increase cycle time", (0.5, 3.5))
    add_events("Low Staffing Event", cfg.staffing_shock_event_count, (0.25, 0.55), "Capacity", "Increase backlog", (7, 9))
    add_events("Senior Reviewer Shortage", cfg.reviewer_shortage_event_count, (0.25, 0.50), "Manual Review", "Increase review wait", (7, 9))
    add_events("Regional Demand Surge", cfg.volume_spike_event_count, (1.5, 2.2), "Intake", "Increase backlog", (7, 9))
    return pd.DataFrame(events).sort_values("Start_Timestamp").reset_index(drop=True)


def generate_capacity_schedule(cfg: SimulationConfig, context: pd.DataFrame, cal: pd.DataFrame, branches: pd.DataFrame, events: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    grid = pd.MultiIndex.from_product([cal["Date"], branches["Branch_ID"], SHIFTS], names=["Date", "Branch_ID", "Shift"]).to_frame(index=False)
    branch_meta = branches.set_index("Branch_ID")
    grid["Region"] = grid["Branch_ID"].map(branch_meta["Region"])
    grid["Branch_Size"] = grid["Branch_ID"].map(branch_meta["Branch_Size"])

    arrivals = context.groupby(["Application_Date", "Branch_ID", "Shift"]).size().rename("New_Arrivals")
    grid = grid.merge(arrivals, how="left", left_on=["Date", "Branch_ID", "Shift"], right_index=True)
    grid["New_Arrivals"] = grid["New_Arrivals"].fillna(0).astype(int)

    base = grid["Branch_Size"].map({"Small": 0.10, "Medium": 0.18, "Large": 0.28}).to_numpy(float)
    shift_mult = grid["Shift"].map({"Morning": 1.00, "Afternoon": 1.00, "Evening": 0.55}).to_numpy(float)
    monday = (grid["Date"].dt.weekday == 0).to_numpy()
    scheduled = np.maximum(0.05, base * shift_mult - 0.02 * monday + rng.normal(0, 0.025, len(grid)))
    grid["Scheduled_Staff"] = np.round(scheduled, 2)
    absence_rate = np.clip(rng.beta(1.5, 18, len(grid)), 0, 0.45)
    grid["Absence_Count"] = np.round(grid["Scheduled_Staff"] * absence_rate, 2)
    grid["Training_FTE"] = np.where(rng.random(len(grid)) < 0.015, np.minimum(0.08, grid["Scheduled_Staff"]), 0.0)
    grid["Available_Staff"] = np.maximum(grid["Scheduled_Staff"] - grid["Absence_Count"] - grid["Training_FTE"], 0.05).round(2)
    grid["Senior_Reviewer_Count"] = np.maximum(0, np.round(grid["Available_Staff"] * rng.uniform(0.15, 0.35, len(grid)), 2))
    grid["KYC_Specialist_Count"] = np.maximum(0, np.round(grid["Available_Staff"] * rng.uniform(0.18, 0.42, len(grid)), 2))

    event_key = {(pd.Timestamp(r.Start_Timestamp).normalize(), r.Branch_ID, r.Shift, r.Event_Type): r for r in events.itertuples()}
    low_staff_mult = np.ones(len(grid))
    reviewer_mult = np.ones(len(grid))
    outage_min = np.zeros(len(grid))
    for i, r in enumerate(grid.itertuples()):
        keybase = (pd.Timestamp(r.Date), r.Branch_ID, r.Shift)
        e = event_key.get((*keybase, "Low Staffing Event"))
        if e is not None:
            low_staff_mult[i] = max(0.25, 1 - float(e.Magnitude))
        e2 = event_key.get((*keybase, "Senior Reviewer Shortage"))
        if e2 is not None:
            reviewer_mult[i] = max(0.25, 1 - float(e2.Magnitude))
        e3 = event_key.get((*keybase, "System Outage"))
        if e3 is not None:
            outage_min[i] = (pd.Timestamp(e3.End_Timestamp) - pd.Timestamp(e3.Start_Timestamp)).total_seconds() / 60
    grid["Available_Staff"] = (grid["Available_Staff"].to_numpy() * low_staff_mult).round(2)
    grid["Senior_Reviewer_Count"] = (grid["Senior_Reviewer_Count"].to_numpy() * reviewer_mult).round(2)
    grid["System_Downtime_Minutes"] = np.round(outage_min, 1)
    grid["Effective_FTE"] = np.maximum(grid["Available_Staff"] - grid["System_Downtime_Minutes"] / (8 * 60), 0.05).round(2)
    grid["Capacity_Per_FTE"] = cfg.capacity_per_fte
    grid["Nominal_Capacity"] = (grid["Scheduled_Staff"] * cfg.capacity_per_fte).round(2)
    grid["Effective_Capacity"] = np.maximum(grid["Effective_FTE"] * cfg.capacity_per_fte, 0.10).round(2)

    # Recursive backlog within each branch/shift across calendar dates.
    grid = grid.sort_values(["Branch_ID", "Shift", "Date"]).reset_index(drop=True)
    opening = np.zeros(len(grid), dtype=float)
    processed = np.zeros(len(grid), dtype=float)
    closing = np.zeros(len(grid), dtype=float)
    for (_, _), idx in grid.groupby(["Branch_ID", "Shift"], sort=False).groups.items():
        prev = 0.0
        for i in idx:
            opening[i] = prev
            available = opening[i] + grid.at[i, "New_Arrivals"]
            processed[i] = min(available, grid.at[i, "Effective_Capacity"])
            closing[i] = max(available - processed[i], 0.0)
            prev = closing[i]
    grid["Opening_Backlog"] = np.round(opening, 2)
    grid["Processed_Count"] = np.round(processed, 2)
    grid["Closing_Backlog"] = np.round(closing, 2)
    return grid


def _assign_analysts(df: pd.DataFrame, analysts: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    analyst_groups = {(b, s): g for (b, s), g in analysts.groupby(["Home_Branch", "Primary_Shift"])}
    ids, workload = [], []
    counters: dict[tuple[str, str, str], int] = {}
    for row in df.itertuples():
        g = analyst_groups.get((row.Branch_ID, row.Shift))
        if g is None or g.empty:
            g = analysts.loc[analysts["Home_Branch"].eq(row.Branch_ID)]
        # High-risk / EDD require at least Advanced when possible.
        if row.Risk_Tier == "High" or row.Enhanced_Due_Diligence_Flag == 1:
            qualified = g.loc[g["Skill_Level"].isin(["Advanced", "Specialist"])]
            if not qualified.empty:
                g = qualified
        selected = g.iloc[int(rng.integers(0, len(g)))]
        aid = selected["Analyst_ID"]
        key = (str(row.Application_Date.date()), row.Shift, aid)
        current = counters.get(key, 0)
        ids.append(aid)
        workload.append(current)
        counters[key] = current + 1
    df["Analyst_ID"] = ids
    df["Analyst_Workload_At_Assignment"] = workload
    return df


def _event_overlap_minutes(starts: pd.Series, ends: pd.Series, branch: pd.Series, shift: pd.Series, events: pd.DataFrame, event_type: str) -> np.ndarray:
    result = np.zeros(len(starts), dtype=float)
    e = events.loc[events["Event_Type"].eq(event_type)]
    if e.empty:
        return result
    keyed = {(r.Branch_ID, r.Shift, pd.Timestamp(r.Start_Timestamp).date()): (pd.Timestamp(r.Start_Timestamp), pd.Timestamp(r.End_Timestamp)) for r in e.itertuples()}
    for i, (s, en, b, sh) in enumerate(zip(starts, ends, branch, shift)):
        if pd.isna(s) or pd.isna(en):
            continue
        pair = keyed.get((b, sh, pd.Timestamp(s).date()))
        if pair is None:
            continue
        es, ee = pair
        overlap = max(pd.Timedelta(0), min(pd.Timestamp(en), ee) - max(pd.Timestamp(s), es))
        result[i] = overlap.total_seconds() / 60
    return result


def simulate_process(cfg: SimulationConfig, context: pd.DataFrame, capacity: pd.DataFrame, analysts: pd.DataFrame, events: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    df = context.copy()
    cap_cols = ["Date", "Branch_ID", "Shift", "Opening_Backlog", "Closing_Backlog", "Effective_Capacity", "Available_Staff", "Senior_Reviewer_Count", "KYC_Specialist_Count", "System_Downtime_Minutes"]
    df = df.merge(capacity[cap_cols], how="left", left_on=["Application_Date", "Branch_ID", "Shift"], right_on=["Date", "Branch_ID", "Shift"]).drop(columns=["Date"])

    # Queue length and queue position are distinct: opening queue plus within-period arrival rank.
    df["Arrival_Rank_In_Shift"] = df.groupby(["Application_Date", "Branch_ID", "Shift"]).cumcount() + 1
    df["Queue_Length_At_Arrival"] = np.floor(df["Opening_Backlog"] + df["Arrival_Rank_In_Shift"] - 1).astype(int)
    df["Queue_Position_At_Arrival"] = np.maximum(df["Queue_Length_At_Arrival"] + 1, 1).astype(int)

    n = len(df)
    # Explicit defect opportunities. Rework is downstream, not counted as a defect opportunity.
    complex_mult = df["Application_Complexity"].map({"Low": 0.0, "Medium": 0.04, "High": 0.10}).to_numpy(float)
    digital = df["Channel"].eq("Digital App").to_numpy(float)
    df["Documentation_Completeness_Defect"] = rng.binomial(1, np.clip(0.10 + 0.08 * digital + complex_mult, 0.01, 0.55))
    df["Document_Quality_Defect"] = rng.binomial(1, np.clip(0.045 + 0.04 * digital + 0.5 * complex_mult, 0.01, 0.40))
    df["Identity_Verification_Defect"] = rng.binomial(1, np.clip(0.018 + 0.045 * (df["Risk_Tier"].eq("High")) + 0.025 * df["Identity_Exception_History_Flag"], 0.005, 0.35))
    df["Data_Capture_Defect"] = rng.binomial(1, np.clip(0.018 + 0.02 * df["Channel"].eq("Call Centre").to_numpy(float), 0.005, 0.20))
    df["KYC_Processing_Defect"] = rng.binomial(1, np.clip(0.012 + 0.035 * df["Enhanced_Due_Diligence_Flag"].to_numpy(float), 0.005, 0.20))
    df["Product_Information_Defect"] = rng.binomial(1, np.clip(0.015 + 0.025 * (df["Products_Requested"].to_numpy() > 1), 0.005, 0.20))
    defect_cols = ["Documentation_Completeness_Defect", "Document_Quality_Defect", "Identity_Verification_Defect", "Data_Capture_Defect", "KYC_Processing_Defect", "Product_Information_Defect"]
    df["Defect_Count"] = df[defect_cols].sum(axis=1).astype(int)
    df["Missing_Document_Flag"] = df["Documentation_Completeness_Defect"]
    df["Document_Error_Flag"] = df["Document_Quality_Defect"]
    df["Identity_Mismatch_Flag"] = df["Identity_Verification_Defect"]
    missing_count = np.minimum(df["Documentation_Completeness_Defect"] * rng.integers(1, 3, n), np.maximum(df["Documents_Required"] - 1, 1))
    df["Documents_Submitted"] = (df["Documents_Required"] - missing_count).clip(lower=1).astype(int)

    rework_lambda = np.clip(0.12 + 0.55 * df["Defect_Count"].to_numpy(), 0.05, 3.0)
    df["Rework_Count"] = rng.poisson(rework_lambda)
    df["Rework_Flag"] = (df["Rework_Count"] > 0).astype(int)
    df["Rework_Minutes"] = np.round(df["Rework_Count"] * rng.uniform(20, 50, n), 1)

    required_review = ((df["Risk_Tier"].eq("High")) | (df["Enhanced_Due_Diligence_Flag"].eq(1))).astype(int)
    defect_review = ((required_review.eq(0)) & (df["Defect_Count"] >= 2)).astype(int)
    df["Required_Manual_Review_Flag"] = required_review
    df["Defect_Driven_Review_Flag"] = defect_review
    df["Manual_Review_Flag"] = ((required_review == 1) | (defect_review == 1)).astype(int)
    df["Exception_Flag"] = ((df["Manual_Review_Flag"] == 1) | (df["Defect_Count"] >= 2)).astype(int)

    df = _assign_analysts(df, analysts, rng)

    # Process times. Queue component uses recursive backlog and queue position.
    capacity_ratio = np.maximum(df["Effective_Capacity"].to_numpy(), 0.1)
    queue_median = 12 + 16 * df["Opening_Backlog"].to_numpy() + 4.5 * np.sqrt(df["Queue_Position_At_Arrival"].to_numpy()) + 15 / capacity_ratio
    df["Queue_Time_Minutes"] = np.round(_lognormal(rng, queue_median, 0.45, n), 1)

    cmult = df["Application_Complexity"].map({"Low": 1.0, "Medium": 1.3, "High": 1.7}).to_numpy(float)
    df["Identity_Verification_Minutes"] = np.round(_lognormal(rng, 14 * cmult + 18 * df["Identity_Verification_Defect"], 0.38, n), 1)
    df["Document_Validation_Minutes"] = np.round(_lognormal(rng, 18 * cmult + 20 * df["Documentation_Completeness_Defect"] + 14 * df["Document_Quality_Defect"], 0.42, n), 1)
    df["KYC_Batch_Wait_Minutes"] = np.round(_lognormal(rng, 45 + 6 * df["Opening_Backlog"].to_numpy() + 8 * df["Risk_Score"].to_numpy() / 20, 0.48, n), 1)
    df["KYC_Processing_Minutes"] = np.round(_lognormal(rng, 20 * cmult + 0.25 * df["Risk_Score"].to_numpy(), 0.38, n), 1)
    reviewer_scarcity = np.maximum(0.2, df["Senior_Reviewer_Count"].to_numpy())
    mr_wait_med = 50 + 20 * df["Opening_Backlog"].to_numpy() + 55 / reviewer_scarcity + 90 * df["Risk_Tier"].eq("High").to_numpy(float)
    mr_wait = _lognormal(rng, mr_wait_med, 0.55, n)
    df["Manual_Review_Queue_Wait_Minutes"] = np.where(df["Manual_Review_Flag"].eq(1), np.round(mr_wait, 1), 0.0)
    mr_proc = _lognormal(rng, 50 * cmult + 0.20 * df["Risk_Score"].to_numpy(), 0.42, n)
    df["Manual_Review_Minutes"] = np.where(df["Manual_Review_Flag"].eq(1), np.round(mr_proc, 1), 0.0)

    # Build preliminary stage times to evaluate actual outage overlap.
    received = pd.to_datetime(df["Application_Received_Timestamp"])
    iv_start = received + pd.to_timedelta(df["Queue_Time_Minutes"], unit="m")
    iv_end0 = iv_start + pd.to_timedelta(df["Identity_Verification_Minutes"], unit="m")
    outage_iv = _event_overlap_minutes(iv_start, iv_end0, df["Branch_ID"], df["Shift"], events, "System Outage")
    df["Identity_Verification_Minutes"] += np.round(outage_iv, 1)
    iv_end = iv_start + pd.to_timedelta(df["Identity_Verification_Minutes"], unit="m")

    dv_start = iv_end
    dv_end0 = dv_start + pd.to_timedelta(df["Document_Validation_Minutes"], unit="m")
    outage_dv = _event_overlap_minutes(dv_start, dv_end0, df["Branch_ID"], df["Shift"], events, "System Outage")
    df["Document_Validation_Minutes"] += np.round(outage_dv, 1)
    dv_end = dv_start + pd.to_timedelta(df["Document_Validation_Minutes"], unit="m")

    kyc_start = dv_end + pd.to_timedelta(df["KYC_Batch_Wait_Minutes"], unit="m")
    kyc_end0 = kyc_start + pd.to_timedelta(df["KYC_Processing_Minutes"], unit="m")
    outage_kyc = _event_overlap_minutes(kyc_start, kyc_end0, df["Branch_ID"], df["Shift"], events, "System Outage")
    df["KYC_Processing_Minutes"] += np.round(outage_kyc, 1)
    kyc_end = kyc_start + pd.to_timedelta(df["KYC_Processing_Minutes"], unit="m")

    mr_start = kyc_end + pd.to_timedelta(df["Manual_Review_Queue_Wait_Minutes"], unit="m")
    mr_end = mr_start + pd.to_timedelta(df["Manual_Review_Minutes"], unit="m")
    approval0 = mr_end + pd.to_timedelta(df["Rework_Minutes"], unit="m")
    activation0 = approval0 + pd.to_timedelta(rng.uniform(5, 45, n), unit="m")

    expected_hours = (activation0 - received).dt.total_seconds() / 3600
    # Abandonment is a process event, with probability increasing with wait/defects.
    logit = -5.4 + 0.055 * np.maximum(expected_hours - 12, 0) + 0.32 * df["Defect_Count"].to_numpy() + 0.18 * df["Queue_Length_At_Arrival"].to_numpy()
    abandon_p = 1 / (1 + np.exp(-np.clip(logit, -12, 8)))
    abandon = rng.random(n) < np.clip(abandon_p, 0.002, 0.25)
    stages = np.array(["",] * n, dtype=object)
    # Only manual-review cases can abandon awaiting manual review.
    base_stage_choices = np.array(["Document Submission", "Verification", "Awaiting KYC"])
    for i in np.flatnonzero(abandon):
        if df.at[i, "Manual_Review_Flag"] == 1:
            stages[i] = rng.choice(["Document Submission", "Verification", "Awaiting KYC", "Awaiting Manual Review"], p=[0.20, 0.20, 0.30, 0.30])
        else:
            stages[i] = rng.choice(base_stage_choices, p=[0.30, 0.25, 0.45])
    df["Abandonment_Flag"] = abandon.astype(int)
    df["Application_Abandoned_Flag"] = df["Abandonment_Flag"]
    df["Completed_Flag"] = (~abandon).astype(int)
    df["Application_Status"] = np.where(abandon, "Abandoned", "Completed")
    df["Abandonment_Stage"] = np.where(abandon, stages, "")

    # Populate stage timestamps and explicitly censor downstream stages after abandonment.
    df["Identity_Verification_Start"] = iv_start
    df["Identity_Verification_End"] = iv_end
    df["Document_Validation_Start"] = dv_start
    df["Document_Validation_End"] = dv_end
    df["KYC_Start"] = kyc_start
    df["KYC_End"] = kyc_end
    df["Manual_Review_Start"] = pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns]")
    df["Manual_Review_End"] = pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns]")
    review_mask = df["Manual_Review_Flag"].eq(1)
    df.loc[review_mask, "Manual_Review_Start"] = mr_start[review_mask]
    df.loc[review_mask, "Manual_Review_End"] = mr_end[review_mask]

    abandon_ts = pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns]")
    mask = df["Abandonment_Stage"].eq("Document Submission")
    abandon_ts.loc[mask] = received[mask] + (iv_start[mask] - received[mask]) / 2
    mask_v = df["Abandonment_Stage"].eq("Verification")
    abandon_ts.loc[mask_v] = iv_start[mask_v] + (iv_end[mask_v] - iv_start[mask_v]) / 2
    mask_k = df["Abandonment_Stage"].eq("Awaiting KYC")
    abandon_ts.loc[mask_k] = dv_end[mask_k] + (kyc_start[mask_k] - dv_end[mask_k]) / 2
    mask_m = df["Abandonment_Stage"].eq("Awaiting Manual Review")
    abandon_ts.loc[mask_m] = kyc_end[mask_m] + (mr_start[mask_m] - kyc_end[mask_m]) / 2
    df["Abandonment_Timestamp"] = abandon_ts

    # Censor timestamps after the abandonment stage.
    for i in np.flatnonzero(abandon):
        stage = stages[i]
        if stage == "Document Submission":
            for c in ["Identity_Verification_Start", "Identity_Verification_End", "Document_Validation_Start", "Document_Validation_End", "KYC_Start", "KYC_End", "Manual_Review_Start", "Manual_Review_End"]:
                df.at[i, c] = pd.NaT
        elif stage == "Verification":
            for c in ["Identity_Verification_End", "Document_Validation_Start", "Document_Validation_End", "KYC_Start", "KYC_End", "Manual_Review_Start", "Manual_Review_End"]:
                df.at[i, c] = pd.NaT
        elif stage == "Awaiting KYC":
            for c in ["KYC_Start", "KYC_End", "Manual_Review_Start", "Manual_Review_End"]:
                df.at[i, c] = pd.NaT
        elif stage == "Awaiting Manual Review":
            for c in ["Manual_Review_Start", "Manual_Review_End"]:
                df.at[i, c] = pd.NaT

    df["Approval_Timestamp"] = pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns]")
    df["Activation_Timestamp"] = pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns]")
    complete = df["Completed_Flag"].eq(1)
    df.loc[complete, "Approval_Timestamp"] = approval0[complete]
    df.loc[complete, "Activation_Timestamp"] = activation0[complete]
    df["Time_To_Approval_Hours"] = np.where(complete, (df["Approval_Timestamp"] - received).dt.total_seconds() / 3600, np.nan)
    df["Time_To_Activation_Hours"] = np.where(complete, (df["Activation_Timestamp"] - received).dt.total_seconds() / 3600, np.nan)
    df["Elapsed_Time_To_Abandonment_Hours"] = np.where(abandon, (df["Abandonment_Timestamp"] - received).dt.total_seconds() / 3600, np.nan)
    df["Elapsed_Process_Hours"] = np.where(complete, df["Time_To_Activation_Hours"], df["Elapsed_Time_To_Abandonment_Hours"])
    # Legacy alias is now explicitly activation-based for completed cases and elapsed-to-abandonment otherwise.
    df["Total_Onboarding_Hours"] = df["Elapsed_Process_Hours"]

    df["SLA_Target_Hours"] = df["Application_Complexity"].map(SLA_BY_COMPLEXITY).astype(float)
    df["SLA_Utilization"] = np.where(complete, df["Time_To_Activation_Hours"] / df["SLA_Target_Hours"], np.nan)
    df["SLA_Margin_Hours"] = np.where(complete, df["SLA_Target_Hours"] - df["Time_To_Activation_Hours"], np.nan)
    df["SLA_Met_Flag"] = pd.Series(np.where(complete, (df["Time_To_Activation_Hours"] <= df["SLA_Target_Hours"]).astype(int), np.nan), dtype="Float64")
    df["First_Pass_Yield_Flag"] = ((df["Defect_Count"] == 0) & (df["Rework_Count"] == 0)).astype(int)

    # Customer outcomes based on actual observed elapsed process time.
    complaint_p = np.clip(0.01 + 0.05 * np.nan_to_num(1 - df["SLA_Met_Flag"].astype(float), nan=0) + 0.025 * df["Rework_Flag"] + 0.015 * df["Abandonment_Flag"], 0.005, 0.35)
    df["Customer_Complaint_Flag"] = rng.binomial(1, complaint_p)

    # Cost of Quality: required control is appraisal; only failure costs enter COPQ.
    df["Prevention_Cost"] = COSTS["prevention_per_application"]
    df["Required_Manual_Review_Cost"] = df["Required_Manual_Review_Flag"] * COSTS["required_manual_review"]
    df["Defect_Driven_Review_Cost"] = df["Defect_Driven_Review_Flag"] * COSTS["defect_driven_review"]
    df["Rework_Cost"] = df["Rework_Count"] * COSTS["rework_per_cycle"]
    df["Repeat_Processing_Cost"] = df["Rework_Count"] * COSTS["repeat_processing_per_cycle"]
    df["Complaint_Cost"] = df["Customer_Complaint_Flag"] * COSTS["complaint"]
    df["Abandonment_Cost"] = df["Abandonment_Flag"] * COSTS["abandonment"]
    expedited = (complete & (df["SLA_Utilization"].fillna(0) > 0.90) & (rng.random(n) < 0.10)).astype(int)
    df["Expedited_Handling_Cost"] = expedited * COSTS["expedited_handling"]
    df["Total_Prevention_Cost"] = df["Prevention_Cost"]
    df["Total_Appraisal_Cost"] = df["Required_Manual_Review_Cost"]
    df["Total_Internal_Failure_Cost"] = df[["Defect_Driven_Review_Cost", "Rework_Cost", "Repeat_Processing_Cost", "Expedited_Handling_Cost"]].sum(axis=1)
    df["Total_External_Failure_Cost"] = df[["Complaint_Cost", "Abandonment_Cost"]].sum(axis=1)
    df["Total_COPQ"] = df["Total_Internal_Failure_Cost"] + df["Total_External_Failure_Cost"]
    df["Total_Cost_of_Quality"] = df["Total_Prevention_Cost"] + df["Total_Appraisal_Cost"] + df["Total_COPQ"]
    # Compatibility aliases for legacy downstream scripts.
    df["COPQ_Rework_Cost"] = df["Rework_Cost"]
    df["COPQ_Manual_Review_Cost"] = df["Defect_Driven_Review_Cost"]
    df["COPQ_Complaint_Cost"] = df["Complaint_Cost"]
    df["COPQ_Abandonment_Cost"] = df["Abandonment_Cost"]

    return df.sort_values("Application_Received_Timestamp").reset_index(drop=True)


def validate_truth(df: pd.DataFrame, cfg: SimulationConfig, cal: pd.DataFrame, capacity: pd.DataFrame) -> list[str]:
    problems = []
    if len(df) != cfg.n_applications:
        problems.append(f"row count {len(df)} != {cfg.n_applications}")
    if not df["Application_ID"].is_unique:
        problems.append("Application_ID is not unique")
    if (df.filter(regex="_Minutes$").select_dtypes(include=[np.number]) < 0).any().any():
        problems.append("negative duration found")
    # Branch channel only on branch-open days.
    open_map = cal.set_index("Date")["Branch_Open"]
    branch_rows = df["Channel"].eq("Branch")
    if branch_rows.any() and (~df.loc[branch_rows, "Application_Date"].map(open_map).astype(bool)).any():
        problems.append("branch application on closed day")
    # Abandoned records cannot have approval or activation.
    abandoned = df["Abandonment_Flag"].eq(1)
    if df.loc[abandoned, ["Approval_Timestamp", "Activation_Timestamp"]].notna().any().any():
        problems.append("abandoned record has approval/activation")
    completed = df["Completed_Flag"].eq(1)
    if df.loc[completed, ["Approval_Timestamp", "Activation_Timestamp"]].isna().any().any():
        problems.append("completed record missing approval/activation")
    if (df.loc[completed, "Activation_Timestamp"] < df.loc[completed, "Approval_Timestamp"]).any():
        problems.append("activation before approval")
    # Cost reconciliation.
    lhs = df["Total_COPQ"]
    rhs = df["Total_Internal_Failure_Cost"] + df["Total_External_Failure_Cost"]
    if not np.allclose(lhs, rhs):
        problems.append("COPQ reconciliation failed")
    if not np.allclose(df["Total_Cost_of_Quality"], df["Total_Prevention_Cost"] + df["Total_Appraisal_Cost"] + df["Total_COPQ"]):
        problems.append("Cost of Quality reconciliation failed")
    # Recursive backlog reconciliation.
    cap = capacity.sort_values(["Branch_ID", "Shift", "Date"])
    for (_, _), g in cap.groupby(["Branch_ID", "Shift"], sort=False):
        if len(g) > 1 and not np.allclose(g["Opening_Backlog"].iloc[1:].to_numpy(), g["Closing_Backlog"].iloc[:-1].to_numpy(), atol=0.01):
            problems.append("backlog carry-forward reconciliation failed")
            break
    return problems


def write_outputs(cfg: SimulationConfig, df: pd.DataFrame, cal: pd.DataFrame, branches: pd.DataFrame, analysts: pd.DataFrame, capacity: pd.DataFrame, events: pd.DataFrame, runtime_seconds: float, output_root: Path = ROOT) -> dict[str, Path]:
    interim = output_root / "data" / "interim"
    sample_dir = output_root / "data" / "sample"
    results = output_root / "results"
    for d in [interim, sample_dir, results]:
        d.mkdir(parents=True, exist_ok=True)
    paths = {
        "applications": interim / "applications_true.csv",
        "calendar": interim / "business_calendar.csv",
        "branches": interim / "branch_dimension.csv",
        "analysts": interim / "analyst_dimension.csv",
        "capacity": interim / "capacity_schedule.csv",
        "events": interim / "special_cause_manifest.csv",
    }
    df.to_csv(paths["applications"], index=False)
    cal.to_csv(paths["calendar"], index=False)
    branches.to_csv(paths["branches"], index=False)
    analysts.to_csv(paths["analysts"], index=False)
    capacity.to_csv(paths["capacity"], index=False)
    events.to_csv(paths["events"], index=False)
    # Stable inspectable sample, not random across reruns.
    df.head(min(5000, len(df))).to_csv(sample_dir / "applications_sample.csv", index=False)

    manifest = {
        "seed": cfg.seed,
        "target_rows": cfg.n_applications,
        "actual_rows": len(df),
        "date_range": [cfg.start_date, cfg.end_date],
        "python_version": platform.python_version(),
        "numpy_version": np.__version__,
        "pandas_version": pd.__version__,
        "configuration_version": cfg.config_version,
        "runtime_seconds": round(runtime_seconds, 3),
        "row_count": len(df),
        "column_count": df.shape[1],
        "output_hashes": {k: _sha256(v) for k, v in paths.items()},
    }
    (results / "generation_manifest.json").write_text(json.dumps(manifest, indent=2))
    params = asdict(cfg) | {"sla_by_complexity_hours": SLA_BY_COMPLEXITY, "cost_assumptions_rand": COSTS, "complexity_thresholds": {"Low": "<=29", "Medium": "30-49", "High": ">=50"}, "risk_thresholds": {"Low": "<35", "Medium": "35-64.999", "High": ">=65"}}
    (results / "simulation_parameters.json").write_text(json.dumps(params, indent=2))
    return paths


def run_simulation(cfg: SimulationConfig, output_root: Path = ROOT) -> tuple[pd.DataFrame, dict[str, Path]]:
    started = time.perf_counter()
    rng = np.random.default_rng(cfg.seed)
    cal = generate_calendar(cfg, rng)
    branches = generate_branches(cfg, rng)
    events = generate_special_causes(cfg, cal, branches, rng)
    analysts = generate_analysts(cfg, branches, rng)
    context = generate_application_context(cfg, cal, branches, events, rng)
    capacity = generate_capacity_schedule(cfg, context, cal, branches, events, rng)
    df = simulate_process(cfg, context, capacity, analysts, events, rng)
    problems = validate_truth(df, cfg, cal, capacity)
    if problems:
        raise AssertionError("Truth validation failed: " + "; ".join(problems))
    runtime = time.perf_counter() - started
    paths = write_outputs(cfg, df, cal, branches, analysts, capacity, events, runtime, output_root)
    return df, paths
