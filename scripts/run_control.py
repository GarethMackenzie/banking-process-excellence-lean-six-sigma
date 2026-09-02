from pathlib import Path
import json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
rng=np.random.default_rng(1212)
pilot=json.loads((ROOT/'results'/'pilot_results.json').read_text())
weeks=pd.date_range('2026-09-07',periods=26,freq='W-MON')
center=pilot['pilot_median_hours']
vals=rng.normal(center,0.11,len(weeks))
# One transparent special-cause disruption to demonstrate reaction-plan logic.
vals[17]+=0.55
mr=np.abs(np.diff(vals[:12])); sigma=mr.mean()/1.128; ucl=center+3*sigma; lcl=max(0,center-3*sigma)
signal=(vals>ucl)|(vals<lcl)
out=pd.DataFrame({'Week':weeks,'Median_Activation_Hours':vals,'Center_Line':center,'UCL':ucl,'LCL':lcl,'SPC_Signal':signal})
out.to_csv(ROOT/'results'/'control_period.csv',index=False)
res={'weeks':len(out),'center_line':float(center),'ucl':float(ucl),'lcl':float(lcl),'signal_weeks':int(signal.sum()),'sustainment_median':float(np.median(vals)),'improvement_persisted':bool(np.median(vals)<pilot['baseline_median_hours'])}
(ROOT/'results'/'control_results.json').write_text(json.dumps(res,indent=2))
(ROOT/'dmaic'/'05_control'/'control-plan.md').write_text("# Control Plan\n\n| CTQ | Specification / target | Frequency | Owner role | Control method | Reaction |\n|---|---|---|---|---|---|\n| Time to activation | Tiered SLA; monitor SLA utilization | Weekly | Process Excellence Lead | I-chart / weekly median | Investigate special-cause signal; verify capacity and outages |\n| First Pass Yield | Maintain pilot baseline or better | Weekly | Quality Lead | P chart | Pareto defects; verify document pre-validation |\n| Rework | Maintain pilot baseline or better | Weekly | Operations Manager | P chart | Root-cause review and corrective action |\n| Backlog | No sustained run above center line | Daily | Capacity Manager | Queue dashboard | Reallocate approved capacity |\n| Measurement agreement | Study threshold documented | Quarterly | Quality Assurance | Attribute agreement study | Retrain / clarify operational definitions |\n\nThe control plan preserves required KYC controls; it does not trade control effectiveness for speed.\n")
(ROOT/'dmaic'/'05_control'/'reaction-plan.md').write_text("# Reaction Plan\n\n1. Confirm the signal is not a data-quality or measurement issue.\n2. Review special-cause evidence: outage, staffing, reviewer availability, demand surge.\n3. Contain backlog using approved capacity-routing rules without bypassing KYC controls.\n4. Record cause, action, owner and closure date.\n5. Re-establish limits only after a verified stable process shift; never move limits merely to hide poor performance.\n")
print(json.dumps(res,indent=2))
