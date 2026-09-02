import argparse,json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from src.config import SimulationConfig
from src.simulation import generate_calendar,generate_branches,generate_analysts,generate_special_causes,generate_application_context,generate_capacity_schedule,simulate_process,validate_truth
p=argparse.ArgumentParser();p.add_argument('--seed',type=int,required=True);a=p.parse_args();seed=a.seed
cfg=SimulationConfig(seed=seed,n_applications=100000);rng=np.random.default_rng(seed)
cal=generate_calendar(cfg,rng);branches=generate_branches(cfg,rng);events=generate_special_causes(cfg,cal,branches,rng);analysts=generate_analysts(cfg,branches,rng);context=generate_application_context(cfg,cal,branches,events,rng);cap=generate_capacity_schedule(cfg,context,cal,branches,events,rng);df=simulate_process(cfg,context,cap,analysts,events,rng)
probs=validate_truth(df,cfg,cal,cap)
if probs: raise AssertionError(probs)
c=df[df.Completed_Flag.eq(1)];va=df.Identity_Verification_Minutes+df.Document_Validation_Minutes+df.KYC_Processing_Minutes+df.Manual_Review_Minutes;tot=va+df.Queue_Time_Minutes+df.KYC_Batch_Wait_Minutes+df.Manual_Review_Queue_Wait_Minutes+df.Rework_Minutes
r={'Seed':seed,'Rows':len(df),'Median_Activation_Hours':float(c.Time_To_Activation_Hours.median()),'P90_Activation_Hours':float(c.Time_To_Activation_Hours.quantile(.9)),'SLA_Compliance':float(c.SLA_Met_Flag.astype(float).mean()),'SLA_Utilization_Median':float(c.SLA_Utilization.median()),'FPY':float(df.First_Pass_Yield_Flag.mean()),'Rework':float(df.Rework_Flag.mean()),'Manual_Review':float(df.Manual_Review_Flag.mean()),'Abandonment':float(df.Abandonment_Flag.mean()),'Complaint':float(df.Customer_Complaint_Flag.mean()),'COPQ_Per_App':float(df.Total_COPQ.mean()),'Appraisal_Per_App':float(df.Total_Appraisal_Cost.mean()),'PCE':float(va.sum()/tot.sum()),'Risk_Low':float((df.Risk_Tier=='Low').mean()),'Risk_Medium':float((df.Risk_Tier=='Medium').mean()),'Risk_High':float((df.Risk_Tier=='High').mean()),'Complexity_Low':float((df.Application_Complexity=='Low').mean()),'Complexity_Medium':float((df.Application_Complexity=='Medium').mean()),'Complexity_High':float((df.Application_Complexity=='High').mean())}
print(json.dumps(r))
