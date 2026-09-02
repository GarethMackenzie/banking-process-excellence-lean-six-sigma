"""Independent validation rules for the defect-bearing raw onboarding extract."""
from __future__ import annotations
from difflib import get_close_matches
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
DATA = ROOT / "data"
VALID = {
    "Channel": ["Digital App", "Branch", "Call Centre", "Broker Referral"],
    "Region": ["Northern", "Southern", "Eastern", "Western", "Central"],
    "Product_Type": ["Transactional Account", "Savings Account", "Credit Card", "Personal Loan", "Business Account"],
    "Customer_Segment": ["Retail Mass Market", "Retail Affluent", "Small Business", "Student", "Private Banking"],
}
raw = pd.read_csv(RAW / "applications_raw.csv", parse_dates=["Application_Date","Identity_Verification_Start","Identity_Verification_End"])
issues=[]

def add(app, typ, sev, original, corrected, resolution, rule):
    issues.append({"Issue_ID": f"DQ{len(issues)+1:05d}", "Application_ID": app, "Issue_Type":typ, "Severity":sev,
                   "Original_Value":original, "Corrected_Value":corrected, "Resolution":resolution, "Detected_By":rule})

for i in raw.index[raw["Application_ID"].duplicated(keep="first")]:
    add(raw.at[i,"Application_ID"],"Duplicate_Application_ID","Critical",raw.at[i,"Application_ID"],np.nan,"Quarantine duplicate occurrence, retain first","duplicate_check")
for field, sev in [("Channel","High"),("Product_Type","High"),("Analyst_ID","Medium")]:
    for i in raw.index[raw[field].isna()]:
        correction = "UNKNOWN-ANALYST" if field=="Analyst_ID" else np.nan
        resolution = "Correct: impute placeholder 'UNKNOWN-ANALYST'" if field=="Analyst_ID" else "Quarantine (required analytical field missing)"
        add(raw.at[i,"Application_ID"],f"Missing_{field}",sev,np.nan,correction,resolution,f"missing[{field}]")
# Invalid region excluding pure case/whitespace variants.
canon={v.lower():v for v in VALID["Region"]}
norm=raw["Region"].astype(str).str.strip().str.lower()
mask=raw["Region"].notna() & ~norm.isin(canon)
for i in raw.index[mask]:
    bad=str(raw.at[i,"Region"]); match=get_close_matches(bad.strip().lower(), list(canon), n=1, cutoff=.6)
    if match: add(raw.at[i,"Application_ID"],"Invalid_Region","Medium",bad,canon[match[0]],"Correct: fuzzy-matched to canonical region","domain[Region]")
    else: add(raw.at[i,"Application_ID"],"Invalid_Region","Medium",bad,np.nan,"Quarantine (unresolved invalid region)","domain[Region]")
for i in raw.index[raw["Document_Validation_Minutes"] < 0]:
    add(raw.at[i,"Application_ID"],"Negative_Processing_Time","Critical",raw.at[i,"Document_Validation_Minutes"],np.nan,"Quarantine (duration integrity violation)","range[Document_Validation_Minutes]")
mask=raw["Identity_Verification_End"].notna() & raw["Identity_Verification_Start"].notna() & (raw["Identity_Verification_End"] < raw["Identity_Verification_Start"])
for i in raw.index[mask]:
    add(raw.at[i,"Application_ID"],"Timestamp_Sequencing_Error","Critical","end before start",np.nan,"Quarantine (cannot safely infer true order)","sequence[Identity_Verification]")
for field, values in VALID.items():
    lower={v.lower():v for v in values}; series=raw[field].astype(str)
    mask=raw[field].notna() & series.str.lower().isin(lower) & series.eq(series.str.strip()) & ~series.isin(values)
    for i in raw.index[mask]: add(raw.at[i,"Application_ID"],"Incorrect_Capitalization","Low",raw.at[i,field],lower[str(raw.at[i,field]).lower()],"Correct: canonical casing",f"format[{field}]")
for field in ["Channel","Region","Product_Type"]:
    series=raw[field].astype(str); mask=raw[field].notna() & ~series.eq(series.str.strip()) & series.str.strip().isin(VALID[field])
    for i in raw.index[mask]: add(raw.at[i,"Application_ID"],"Whitespace_Contamination","Low",repr(raw.at[i,field]),str(raw.at[i,field]).strip(),"Correct: strip whitespace",f"format[{field}]")
for i in raw.index[raw["Application_Date"] > pd.Timestamp("2026-09-01")]:
    add(raw.at[i,"Application_ID"],"Future_Application_Date","Critical",raw.at[i,"Application_Date"],np.nan,"Quarantine (date beyond extraction date)","temporal[Application_Date]")
mask=raw["Completed_Flag"].eq(1) & ~raw["SLA_Met_Flag"].isin([0,1])
for i in raw.index[mask]: add(raw.at[i,"Application_ID"],"Invalid_SLA_Flag","Critical",raw.at[i,"SLA_Met_Flag"],"recompute","Correct: recompute from activation time and SLA target","domain[SLA_Met_Flag]")

out=pd.DataFrame(issues)
out.to_csv(DATA / "data_quality_issues.csv", index=False)
print(f"Raw rows scanned: {len(raw):,} | Issues detected: {len(out):,}")
print(out["Issue_Type"].value_counts().to_string())
