from pathlib import Path
import json
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
ROOT=Path(__file__).resolve().parents[1]
rng=np.random.default_rng(9090)
base=pd.read_csv(ROOT/'data'/'clean'/'applications_clean.csv')
base=base[base.Completed_Flag.eq(1)].sample(n=min(20000,int((base.Completed_Flag.eq(1)).sum())),random_state=9090).copy()
doe=pd.read_csv(ROOT/'data'/'doe'/'doe_experiment.csv')
model=smf.ols('Total_Cycle_Time_Hours ~ Staffing_Capacity * Document_Prevalidation * Routing_Strategy',data=doe).fit()
combos=doe.groupby(['Staffing_Capacity','Document_Prevalidation','Routing_Strategy']).agg(cycle=('Total_Cycle_Time_Hours','mean'),rework=('Rework_Rate','mean')).reset_index()
standard=combos[(combos.Staffing_Capacity==-1)&(combos.Document_Prevalidation==-1)&(combos.Routing_Strategy==-1)].iloc[0]
best=combos.loc[combos.cycle.idxmin()]
cycle_ratio=float(best.cycle/standard.cycle)
cycle_delta=float(best.cycle-standard.cycle)
rework_ratio=float(best.rework/standard.rework)
pilot_cycle=np.maximum(.25,base.Time_To_Activation_Hours.to_numpy()*cycle_ratio+rng.normal(0,.18,len(base)))
pilot_rework=rng.binomial(1,np.clip(base.Rework_Flag.to_numpy()*rework_ratio + (1-base.Rework_Flag.to_numpy())*.03*rework_ratio,0,.8))
# Conservative failure-cost scaling: internal failure component tracks rework improvement; external cost unchanged except complaints tied to SLA.
slat=base.SLA_Target_Hours.to_numpy(float); pilot_sla=(pilot_cycle<=slat); base_sla=base.SLA_Met_Flag.astype(float).to_numpy()
pilot_internal=base.Total_Internal_Failure_Cost.to_numpy()*np.where(base.Rework_Flag.to_numpy()==1,rework_ratio,0.85)
pilot_external=base.Total_External_Failure_Cost.to_numpy()*np.where(pilot_sla,0.85,1.0)
pilot_copq=pilot_internal+pilot_external
u,p=stats.mannwhitneyu(base.Time_To_Activation_Hours,pilot_cycle,alternative='two-sided')
res={"sample_size":len(base),"selected_configuration":{"Staffing_Capacity":int(best.Staffing_Capacity),"Document_Prevalidation":int(best.Document_Prevalidation),"Routing_Strategy":int(best.Routing_Strategy)},"doe_cycle_delta_hours":cycle_delta,"doe_cycle_ratio":cycle_ratio,"baseline_median_hours":float(base.Time_To_Activation_Hours.median()),"pilot_median_hours":float(np.median(pilot_cycle)),"baseline_sla":float(np.mean(base_sla)),"pilot_sla":float(np.mean(pilot_sla)),"baseline_rework":float(base.Rework_Flag.mean()),"pilot_rework":float(np.mean(pilot_rework)),"baseline_copq_per_app":float(base.Total_COPQ.mean()),"pilot_copq_per_app":float(np.mean(pilot_copq)),"mann_whitney_p_value":float(p),"median_cycle_change_pct":float((np.median(pilot_cycle)/base.Time_To_Activation_Hours.median()-1)*100),"copq_change_pct":float((np.mean(pilot_copq)/base.Total_COPQ.mean()-1)*100)}
(ROOT/'results'/'pilot_results.json').write_text(json.dumps(res,indent=2))
(ROOT/'dmaic'/'04_improve'/'pilot-analysis.md').write_text(f"# Improvement Pilot\n\nThe pilot is a **synthetic intervention simulation** selected from the randomized DOE, not a claim of real operational savings.\n\n| Metric | Baseline sample | Pilot | Change |\n|---|---:|---:|---:|\n| Median activation time | {res['baseline_median_hours']:.2f} h | {res['pilot_median_hours']:.2f} h | {res['median_cycle_change_pct']:.1f}% |\n| SLA compliance | {res['baseline_sla']*100:.2f}% | {res['pilot_sla']*100:.2f}% | {(res['pilot_sla']-res['baseline_sla'])*100:.2f} pp |\n| Rework | {res['baseline_rework']*100:.2f}% | {res['pilot_rework']*100:.2f}% | {(res['pilot_rework']-res['baseline_rework'])*100:.2f} pp |\n| COPQ/app | R{res['baseline_copq_per_app']:.2f} | R{res['pilot_copq_per_app']:.2f} | {res['copq_change_pct']:.1f}% |\n\nMann–Whitney p={p:.3g}. Statistical significance is reported alongside practical change; this is a controlled synthetic scenario, not a real bank outcome.\n")
print(json.dumps(res,indent=2))
