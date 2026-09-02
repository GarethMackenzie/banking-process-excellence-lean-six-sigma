"""Correct or quarantine independently detected source-system data-quality issues."""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"; RAW=DATA/"raw"; CLEAN=DATA/"clean"; QUAR=DATA/"quarantine"
CLEAN.mkdir(parents=True, exist_ok=True); QUAR.mkdir(parents=True, exist_ok=True)
raw=pd.read_csv(RAW/"applications_raw.csv")
issues=pd.read_csv(DATA/"data_quality_issues.csv")
# Index lookup without deprecated groupby.apply.
id_to_idx={k:list(v) for k,v in raw.groupby("Application_ID", sort=False).groups.items()}
def indexes(app, typ):
    vals=id_to_idx.get(app,[])
    return vals[1:] if typ=="Duplicate_Application_ID" else vals
quarantine_types={"Duplicate_Application_ID","Missing_Channel","Missing_Product_Type","Negative_Processing_Time","Timestamp_Sequencing_Error","Future_Application_Date"}
q=set(); reason={}
for r in issues.itertuples():
    if r.Issue_Type in quarantine_types or str(r.Resolution).startswith("Quarantine"):
        for i in indexes(r.Application_ID,r.Issue_Type): q.add(i); reason.setdefault(i,[]).append(r.Issue_Type)
q=sorted(q)
quarantined=raw.loc[q].copy(); quarantined["Quarantine_Reason"]=[", ".join(reason.get(i,[])) for i in q]
clean=raw.drop(index=q).copy(); corrections=[]
VALID={"Channel":["Digital App","Branch","Call Centre","Broker Referral"],"Region":["Northern","Southern","Eastern","Western","Central"],"Product_Type":["Transactional Account","Savings Account","Credit Card","Personal Loan","Business Account"],"Customer_Segment":["Retail Mass Market","Retail Affluent","Small Business","Student","Private Banking"]}
for r in issues.itertuples():
    if not str(r.Resolution).startswith("Correct"): continue
    idx=[i for i in indexes(r.Application_ID,r.Issue_Type) if i in clean.index]
    for i in idx:
        if r.Issue_Type=="Incorrect_Capitalization":
            for field, vals in VALID.items():
                val=clean.at[i,field]
                if isinstance(val,str):
                    lower={x.lower():x for x in vals}
                    if val.lower() in lower and val not in vals and val==val.strip(): clean.at[i,field]=lower[val.lower()]; corrections.append((r.Application_ID,field,r.Issue_Type))
        elif r.Issue_Type=="Whitespace_Contamination":
            for field in ["Channel","Region","Product_Type"]:
                val=clean.at[i,field]
                if isinstance(val,str) and val!=val.strip(): clean.at[i,field]=val.strip(); corrections.append((r.Application_ID,field,r.Issue_Type))
        elif r.Issue_Type=="Invalid_Region" and pd.notna(r.Corrected_Value): clean.at[i,"Region"]=r.Corrected_Value; corrections.append((r.Application_ID,"Region",r.Issue_Type))
        elif r.Issue_Type=="Missing_Analyst_ID": clean.at[i,"Analyst_ID"]="UNKNOWN-ANALYST"; corrections.append((r.Application_ID,"Analyst_ID",r.Issue_Type))
        elif r.Issue_Type=="Invalid_SLA_Flag":
            if clean.at[i,"Completed_Flag"]==1:
                clean.at[i,"SLA_Met_Flag"]=int(float(clean.at[i,"Time_To_Activation_Hours"]) <= float(clean.at[i,"SLA_Target_Hours"]))
                corrections.append((r.Application_ID,"SLA_Met_Flag",r.Issue_Type))
clean=clean.reset_index(drop=True)
clean.to_csv(CLEAN/"applications_clean.csv",index=False); quarantined.to_csv(QUAR/"applications_quarantine.csv",index=False)
assert len(raw)==len(clean)+len(quarantined)
# Validate detection against hidden injection ground truth only after detection/build; validator never reads it.
gt=pd.read_csv(DATA/"interim"/"injected_issues_ground_truth.csv")
truth=set(map(tuple,gt[["Application_ID","Issue_Type"]].itertuples(index=False,name=None)))
detected=set(map(tuple,issues[["Application_ID","Issue_Type"]].itertuples(index=False,name=None)))
precision=len(truth&detected)/max(len(detected),1); recall=len(truth&detected)/max(len(truth),1)
recon=["# Data Reconciliation","","Portfolio demonstration using synthetic data only.","", "| Stage | Row Count |","|---|---:|",f"| Raw rows | {len(raw):,} |",f"| Rows quarantined | {len(quarantined):,} |",f"| Rows retained clean | {len(clean):,} |",f"| Reconciliation | {len(quarantined)+len(clean):,} == {len(raw):,} |","",f"Field-level corrections: **{len(corrections):,}**",f"Detection precision vs seeded ground truth: **{precision*100:.2f}%**",f"Detection recall vs seeded ground truth: **{recall*100:.2f}%**","","## Quarantine reasons","","| Reason | Rows |","|---|---:|"]
for reason_name,count in quarantined["Quarantine_Reason"].value_counts().items(): recon.append(f"| {reason_name} | {count:,} |")
(DATA/"reconciliation.md").write_text("\n".join(recon))
print(f"Raw: {len(raw):,} | Quarantined: {len(quarantined):,} | Clean: {len(clean):,} | Corrections: {len(corrections):,}")
print(f"Detection precision: {precision:.3f} | recall: {recall:.3f}")
