"""Compute MEASURE-phase baseline from the corrected clean synthetic dataset."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.stats import norm

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"/"clean"/"applications_clean.csv"; OUT=ROOT/"dmaic"/"02_measure"; OUT.mkdir(parents=True,exist_ok=True)
df=pd.read_csv(DATA, low_memory=False)
completed=df[df["Completed_Flag"].eq(1)].copy()
cycle=completed["Time_To_Activation_Hours"].astype(float)
defect_cols=[c for c in df.columns if c.endswith("_Defect")]
opportunities=len(defect_cols)
total_defects=df[defect_cols].sum().sum(); dpu=total_defects/len(df); dpo=dpu/opportunities; dpmo=dpo*1e6; sigma=norm.ppf(1-min(max(dpo,1e-9),1-1e-9))+1.5
va=(df["Identity_Verification_Minutes"]+df["Document_Validation_Minutes"]+df["KYC_Processing_Minutes"]+df["Manual_Review_Minutes"])
nva=(df["Queue_Time_Minutes"]+df["KYC_Batch_Wait_Minutes"]+df["Manual_Review_Queue_Wait_Minutes"]+df["Rework_Minutes"])
pce=va.sum()/(va.sum()+nva.sum())
metrics={
 "clean_rows":len(df),"completed_rows":len(completed),"median_activation_hours":cycle.median(),"mean_activation_hours":cycle.mean(),"p90_activation_hours":cycle.quantile(.90),"p95_activation_hours":cycle.quantile(.95),
 "sla_compliance":completed["SLA_Met_Flag"].astype(float).mean(),"sla_utilization_median":completed["SLA_Utilization"].median(),"fpy":df["First_Pass_Yield_Flag"].mean(),"rework_rate":df["Rework_Flag"].mean(),"manual_review_rate":df["Manual_Review_Flag"].mean(),"abandonment_rate":df["Abandonment_Flag"].mean(),"complaint_rate":df["Customer_Complaint_Flag"].mean(),"pce":pce,"dpu":dpu,"dpo":dpo,"dpmo":dpmo,"sigma_estimate":sigma,
 "copq_per_app":df["Total_COPQ"].mean(),"appraisal_per_app":df["Total_Appraisal_Cost"].mean(),"coq_per_app":df["Total_Cost_of_Quality"].mean(),"total_copq":df["Total_COPQ"].sum()
}
(ROOT/"results"/"baseline_metrics.json").write_text(json.dumps({k:float(v) if isinstance(v,(np.floating,float)) else int(v) if isinstance(v,(np.integer,int)) else v for k,v in metrics.items()},indent=2))
lines=["# Baseline Performance — MEASURE Phase","","> Portfolio demonstration using synthetic data only. Financial values and process outcomes are simulated.","",f"Clean analytical records: **{len(df):,}**; completed applications used for activation-time/SLA metrics: **{len(completed):,}**.","","## CTQ scorecard","","| Metric | Baseline |","|---|---:|",f"| Median time to activation | {metrics['median_activation_hours']:.2f} h |",f"| P90 time to activation | {metrics['p90_activation_hours']:.2f} h |",f"| SLA compliance (completed only) | {metrics['sla_compliance']*100:.2f}% |",f"| Median SLA utilization | {metrics['sla_utilization_median']:.3f} |",f"| First Pass Yield | {metrics['fpy']*100:.2f}% |",f"| Rework rate | {metrics['rework_rate']*100:.2f}% |",f"| Abandonment rate | {metrics['abandonment_rate']*100:.2f}% |",f"| Process Cycle Efficiency | {metrics['pce']*100:.2f}% |",f"| COPQ per application | R{metrics['copq_per_app']:.2f} |",f"| Required-control appraisal cost per application | R{metrics['appraisal_per_app']:.2f} |","","## Defect opportunity model","",f"Unit = one onboarding application. Explicit opportunities per unit = **{opportunities}** ({', '.join(defect_cols)}). Rework is an outcome and is not counted as a defect opportunity.","",f"DPU = **{dpu:.4f}**, DPO = **{dpo:.4f}**, DPMO = **{dpmo:,.0f}**. The sigma estimate (**{sigma:.2f}**) is retained only as an approximate portfolio teaching metric; capability is assessed separately and does not assume normality.","","## Interpretation","",f"The strongest baseline quality signal is FPY of **{metrics['fpy']*100:.1f}%** with rework at **{metrics['rework_rate']*100:.1f}%**. Aggregate SLA compliance is high and should not be used as the sole improvement headline because SLA specifications differ by governed complexity tier."]
(OUT/"baseline-performance.md").write_text("\n".join(lines))
print(json.dumps(metrics,indent=2,default=float))
