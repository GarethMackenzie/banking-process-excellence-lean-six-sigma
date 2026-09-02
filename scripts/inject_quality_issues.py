"""Inject controlled source-system data-quality issues into the synthetic truth dataset."""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SEED = 4242
rng = np.random.default_rng(SEED)
INTERIM = ROOT / "data" / "interim"
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

parse_dates = [c for c in [
    "Application_Date", "Application_Received_Timestamp", "Identity_Verification_Start",
    "Identity_Verification_End", "Document_Validation_Start", "Document_Validation_End",
    "KYC_Start", "KYC_End", "Manual_Review_Start", "Manual_Review_End",
    "Approval_Timestamp", "Activation_Timestamp", "Abandonment_Timestamp"
]]
df = pd.read_csv(INTERIM / "applications_true.csv", parse_dates=parse_dates)
n = len(df)

plan = {
    "Duplicate_Application_ID": 400,
    "Missing_Channel": 300,
    "Invalid_Region": 300,
    "Negative_Processing_Time": 300,
    "Timestamp_Sequencing_Error": 300,
    "Incorrect_Capitalization": 300,
    "Whitespace_Contamination": 300,
    "Missing_Product_Type": 300,
    "Future_Application_Date": 200,
    "Invalid_SLA_Flag": 200,
    "Missing_Analyst_ID": 300,
}

# Use disjoint rows while respecting eligibility (e.g. completed rows for SLA corruption).
available = set(range(n))
buckets: dict[str, np.ndarray] = {}
def draw(issue: str, count: int, eligible=None):
    pool = np.array(sorted(available if eligible is None else (available & set(eligible))), dtype=int)
    if len(pool) < count:
        raise RuntimeError(f"Insufficient eligible rows for {issue}: {len(pool)} < {count}")
    chosen = rng.choice(pool, size=count, replace=False)
    available.difference_update(map(int, chosen))
    buckets[issue] = chosen

completed_idx = df.index[df["Completed_Flag"].eq(1)].tolist()
iv_idx = df.index[df["Identity_Verification_Start"].notna() & df["Identity_Verification_End"].notna()].tolist()
for issue, count in plan.items():
    if issue == "Invalid_SLA_Flag": draw(issue, count, completed_idx)
    elif issue == "Timestamp_Sequencing_Error": draw(issue, count, iv_idx)
    else: draw(issue, count)

raw = df.copy()
gt = []
def log(indices, issue):
    for i in indices:
        gt.append({"Application_ID": raw.at[i, "Application_ID"], "Issue_Type": issue})

idx = buckets["Duplicate_Application_ID"]
dup_rows = raw.loc[idx].copy(); log(idx, "Duplicate_Application_ID")

idx = buckets["Missing_Channel"]; raw.loc[idx, "Channel"] = np.nan; log(idx, "Missing_Channel")
idx = buckets["Invalid_Region"]
typo = {"Northern":"Norhtern","Southern":"Souhtern","Eastern":"Estern","Western":"Wsetern","Central":"Centrl"}
raw.loc[idx, "Region"] = raw.loc[idx, "Region"].map(typo); log(idx, "Invalid_Region")
idx = buckets["Negative_Processing_Time"]; raw.loc[idx, "Document_Validation_Minutes"] = -raw.loc[idx, "Document_Validation_Minutes"].abs(); log(idx, "Negative_Processing_Time")
idx = buckets["Timestamp_Sequencing_Error"]
tmp = raw.loc[idx, "Identity_Verification_Start"].copy(); raw.loc[idx, "Identity_Verification_Start"] = raw.loc[idx, "Identity_Verification_End"].values; raw.loc[idx, "Identity_Verification_End"] = tmp.values; log(idx, "Timestamp_Sequencing_Error")
idx = buckets["Incorrect_Capitalization"]
fields = np.array(["Channel","Region","Product_Type","Customer_Segment"]); chosen = rng.choice(fields, size=len(idx))
for f in fields:
    sub = idx[chosen == f]
    if len(sub): raw.loc[sub, f] = raw.loc[sub, f].astype(str).str.upper()
log(idx, "Incorrect_Capitalization")
idx = buckets["Whitespace_Contamination"]
fields2 = np.array(["Channel","Region","Product_Type"]); chosen2 = rng.choice(fields2, size=len(idx))
for f in fields2:
    sub = idx[chosen2 == f]
    if len(sub): raw.loc[sub, f] = "  " + raw.loc[sub, f].astype(str) + "  "
log(idx, "Whitespace_Contamination")
idx = buckets["Missing_Product_Type"]; raw.loc[idx, "Product_Type"] = np.nan; log(idx, "Missing_Product_Type")
idx = buckets["Future_Application_Date"]; raw.loc[idx, "Application_Date"] = pd.Timestamp("2026-09-01") + pd.to_timedelta(rng.integers(1, 90, len(idx)), unit="D"); log(idx, "Future_Application_Date")
idx = buckets["Invalid_SLA_Flag"]; raw.loc[idx, "SLA_Met_Flag"] = 2; log(idx, "Invalid_SLA_Flag")
idx = buckets["Missing_Analyst_ID"]; raw.loc[idx, "Analyst_ID"] = np.nan; log(idx, "Missing_Analyst_ID")

raw = pd.concat([raw, dup_rows], ignore_index=True)
raw.to_csv(RAW / "applications_raw.csv", index=False)
ground = pd.DataFrame(gt)
ground.insert(0, "Log_ID", [f"GT{i+1:05d}" for i in range(len(ground))])
ground.to_csv(INTERIM / "injected_issues_ground_truth.csv", index=False)
print(f"Truth rows: {n:,} | Raw rows: {len(raw):,} | Seeded issue events: {len(ground):,}")
print(ground["Issue_Type"].value_counts().to_string())
