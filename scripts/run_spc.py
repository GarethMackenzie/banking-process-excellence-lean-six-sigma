from pathlib import Path
import json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
# 1) Classical portfolio SPC: weekly median activation time using I-MR limits.
df=pd.read_csv(ROOT/'data'/'clean'/'applications_clean.csv',parse_dates=['Application_Date'],low_memory=False)
comp=df[df.Completed_Flag.eq(1)].copy(); comp['Week']=comp.Application_Date.dt.to_period('W').apply(lambda p:p.start_time)
weekly=comp.groupby('Week').agg(Median_Cycle_Hours=('Time_To_Activation_Hours','median'),Rework_Rate=('Rework_Flag','mean'),n=('Application_ID','size')).reset_index()
k=max(20,int(len(weekly)*.60)); base=weekly.Median_Cycle_Hours.iloc[:k].to_numpy(); mr=np.abs(np.diff(base)); sigma=mr.mean()/1.128; center=float(base.mean()); ucl=center+3*sigma; lcl=max(0,center-3*sigma)
weekly['I_Signal']=(weekly.Median_Cycle_Hours>ucl)|(weekly.Median_Cycle_Hours<lcl)
# 2) Local ground-truth evaluation: event labels are used only AFTER independent thresholds are calculated.
cap=pd.read_csv(ROOT/'data'/'interim'/'capacity_schedule.csv',parse_dates=['Date'])
events=pd.read_csv(ROOT/'data'/'interim'/'special_cause_manifest.csv',parse_dates=['Start_Timestamp','End_Timestamp'])
local=[]
for (branch,shift),g0 in cap.groupby(['Branch_ID','Shift'],sort=False):
    g=g0.sort_values('Date').copy(); kb=max(30,int(len(g)*.60)); b=g.iloc[:kb]
    # Empirical extreme-state thresholds are appropriate for zero-inflated/non-normal queue/capacity measures.
    backlog_hi=float(b.Closing_Backlog.quantile(.995)); cap_lo=float(b.Effective_Capacity.quantile(.005)); reviewers_lo=float(b.Senior_Reviewer_Count.quantile(.005))
    sig=(g.Closing_Backlog>backlog_hi) | (g.Effective_Capacity<cap_lo)
    # Reviewer count is only informative when the baseline distribution is not structurally zero.
    if b.Senior_Reviewer_Count.gt(0).mean()>.25:
        sig = sig | (g.Senior_Reviewer_Count<reviewers_lo)
    for r,s in zip(g.itertuples(),sig): local.append({'Date':r.Date,'Branch_ID':branch,'Shift':shift,'Local_State_Signal':bool(s)})
local=pd.DataFrame(local); signal_keys=set((r.Date.date(),r.Branch_ID,r.Shift) for r in local.loc[local.Local_State_Signal].itertuples())
related=set(); detected=[]; lags=[]
for e in events.itertuples():
    d=pd.Timestamp(e.Start_Timestamp).date(); k0=(d,e.Branch_ID,e.Shift); k1=((pd.Timestamp(d)+pd.Timedelta(days=1)).date(),e.Branch_ID,e.Shift); related.update([k0,k1]); ok=k0 in signal_keys or k1 in signal_keys; detected.append(ok); lags.append(0 if k0 in signal_keys else 1 if k1 in signal_keys else None)
false_keys=[k for k in signal_keys if k not in related]
false_rate=len(false_keys)/len(local)
weekly.to_csv(ROOT/'results'/'spc_weekly.csv',index=False); local.to_csv(ROOT/'results'/'spc_local_state.csv',index=False)
res={'weekly_i_chart_center':center,'weekly_i_chart_ucl':float(ucl),'weekly_i_chart_lcl':float(lcl),'weekly_i_chart_signals':int(weekly.I_Signal.sum()),'seeded_events':len(events),'events_detected_local_state':int(sum(detected)),'event_detection_rate':float(np.mean(detected)),'missed_events':int(len(events)-sum(detected)),'local_false_alarm_group_days':len(false_keys),'local_false_alarm_rate':float(false_rate),'median_detection_lag_days':float(np.median([x for x in lags if x is not None])) if any(x is not None for x in lags) else None}
(ROOT/'results'/'spc_results.json').write_text(json.dumps(res,indent=2))
(ROOT/'dmaic'/'05_control'/'spc-monitoring.md').write_text(f"# SPC Monitoring\n\nThe primary control chart is a weekly Individuals chart on median time-to-activation; sigma is estimated from the baseline moving range. Because seeded special causes are local to a branch/shift and can be diluted in a portfolio median, a separate **ground-truth validation** uses independently derived extreme-state thresholds for zero-inflated branch/shift backlog and capacity variables. Event labels are never used to set thresholds.\n\n- Weekly I-chart center: **{center:.2f} h**, UCL **{ucl:.2f} h**, LCL **{lcl:.2f} h**\n- Weekly I-chart signal weeks: **{int(weekly.I_Signal.sum())}**\n- Seeded events: **{len(events)}**\n- Local event detections on event day or next day: **{sum(detected)} ({np.mean(detected)*100:.1f}%)**\n- Local-state false-alarm rate: **{false_rate*100:.2f}% of branch/shift/days**\n\nDetection performance is reported honestly rather than tuned against event labels. Control limits and customer SLA specifications remain conceptually separate.\n")
print(json.dumps(res,indent=2))
