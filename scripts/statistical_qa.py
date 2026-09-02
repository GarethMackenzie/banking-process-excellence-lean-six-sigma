from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.stats import skew
ROOT=Path(__file__).resolve().parents[1]
df=pd.read_csv(ROOT/'data'/'clean'/'applications_clean.csv',low_memory=False)
comp=df[df.Completed_Flag.eq(1)]
checks=[]
def add(name,status,detail): checks.append({'check':name,'status':'PASS' if status else 'WARN','detail':detail})
cycle=comp.Time_To_Activation_Hours.astype(float)
add('cycle_time_right_skew',skew(cycle)>0.5,f'skew={skew(cycle):.3f}')
add('cycle_time_tail_finite',np.isfinite(cycle).all(),f'max={cycle.max():.2f}')
for c in ['Channel','Risk_Tier','Application_Complexity']:
    vc=df[c].value_counts(normalize=True); add(f'nondegenerate_{c}',len(vc)>1 and vc.max()<.98,str(vc.round(3).to_dict()))
# Distinct predictor correlation matrix.
cols=['Opening_Backlog','Queue_Length_At_Arrival','Complexity_Score','Risk_Score','Defect_Count','Available_Staff','System_Downtime_Minutes']
# Pandas may expose a read-only view here under newer NumPy versions; make an
# explicit writable copy before clearing the diagonal for the distinct-predictor check.
corr=df[cols].corr(numeric_only=True).abs()
corr_values=corr.to_numpy(copy=True)
np.fill_diagonal(corr_values,0)
maxcorr=float(corr_values.max()); loc=np.unravel_index(np.argmax(corr_values),corr_values.shape)
add('no_unexpected_near_duplicate_predictors',maxcorr<.95,f'max |r|={maxcorr:.3f} between {corr.index[loc[0]]} and {corr.columns[loc[1]]}')
add('backlog_increases_queue_time',df[['Opening_Backlog','Queue_Time_Minutes']].corr().iloc[0,1]>0.15,f"r={df[['Opening_Backlog','Queue_Time_Minutes']].corr().iloc[0,1]:.3f}")
add('defects_increase_rework',df.loc[df.Defect_Count>0,'Rework_Flag'].mean()>df.loc[df.Defect_Count==0,'Rework_Flag'].mean(),f"rates={df.loc[df.Defect_Count>0,'Rework_Flag'].mean():.3f}/{df.loc[df.Defect_Count==0,'Rework_Flag'].mean():.3f}")
add('abandonment_censoring',df.loc[df.Abandonment_Flag.eq(1),['Approval_Timestamp','Activation_Timestamp']].isna().all().all(),'abandoned rows have no approval/activation')
add('cost_nonnegative',(df[['Total_COPQ','Total_Appraisal_Cost','Total_Cost_of_Quality']]>=0).all().all(),'all cost fields nonnegative')
seed_path=ROOT/'results'/'seed_robustness.csv'
if seed_path.exists():
    sr=pd.read_csv(seed_path); cv=float(sr.FPY.std()/sr.FPY.mean()); add('seed_stability_fpy',cv<.03,f'CV={cv:.3%}')
else: add('seed_stability_fpy',False,'seed robustness not run')
status='PASS' if all(c['status']=='PASS' for c in checks) else 'WARN'
res={'overall':status,'checks':checks}; (ROOT/'results'/'statistical_qa.json').write_text(json.dumps(res,indent=2)); print(json.dumps(res,indent=2))
