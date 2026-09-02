from pathlib import Path
import json
import numpy as np
import pandas as pd
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from src.config import SimulationConfig
from src.simulation import SLA_BY_COMPLEXITY

DF=pd.read_csv(ROOT/'data'/'interim'/'applications_true.csv',low_memory=False)
CAP=pd.read_csv(ROOT/'data'/'interim'/'capacity_schedule.csv')
CAL=pd.read_csv(ROOT/'data'/'interim'/'business_calendar.csv')

def test_exact_count(): assert len(DF)==100000
def test_unique_ids(): assert DF.Application_ID.is_unique
def test_fixed_complexity_thresholds():
    expected=np.where(DF.Complexity_Score<=29,'Low',np.where(DF.Complexity_Score<=49,'Medium','High'))
    assert np.all(expected==DF.Application_Complexity)
def test_risk_thresholds():
    expected=np.where(DF.Risk_Score<35,'Low',np.where(DF.Risk_Score<65,'Medium','High'))
    assert np.all(expected==DF.Risk_Tier)
def test_branch_calendar():
    d=DF.copy(); d.Application_Date=pd.to_datetime(d.Application_Date); cal=CAL.copy(); cal.Date=pd.to_datetime(cal.Date); lookup=cal.set_index('Date').Branch_Open
    b=d.Channel.eq('Branch'); assert d.loc[b,'Application_Date'].map(lookup).astype(bool).all()
def test_abandonment_censoring():
    a=DF.Abandonment_Flag.eq(1); assert DF.loc[a,['Approval_Timestamp','Activation_Timestamp']].isna().all().all()
def test_completed_has_activation():
    c=DF.Completed_Flag.eq(1); assert DF.loc[c,'Activation_Timestamp'].notna().all()
def test_no_negative_durations():
    cols=[c for c in DF.columns if c.endswith('_Minutes')]; assert (DF[cols]>=0).all().all()
def test_cost_reconciliation():
    assert np.allclose(DF.Total_COPQ,DF.Total_Internal_Failure_Cost+DF.Total_External_Failure_Cost)
def test_required_review_not_copq():
    assert np.allclose(DF.Total_Appraisal_Cost,DF.Required_Manual_Review_Cost)
def test_defect_count_explicit():
    cols=[c for c in DF.columns if c.endswith('_Defect')]; assert np.array_equal(DF.Defect_Count.to_numpy(),DF[cols].sum(axis=1).to_numpy())
def test_backlog_recursion():
    c=CAP.sort_values(['Branch_ID','Shift','Date'])
    for _,g in c.groupby(['Branch_ID','Shift']): assert np.allclose(g.Opening_Backlog.iloc[1:],g.Closing_Backlog.iloc[:-1],atol=.011)
def test_sla_utilization():
    c=DF.Completed_Flag.eq(1); assert np.allclose(DF.loc[c,'SLA_Utilization'].astype(float),DF.loc[c,'Time_To_Activation_Hours'].astype(float)/DF.loc[c,'SLA_Target_Hours'].astype(float))
def test_msa_balanced():
    m=pd.read_csv(ROOT/'data'/'msa'/'msa_study.csv'); assert len(m)==2*60*4*2; assert m.groupby(['Study_Phase','Study_Item_ID','Reviewer_ID']).Trial.nunique().eq(2).all()
def test_doe_balanced():
    d=pd.read_csv(ROOT/'data'/'doe'/'doe_experiment.csv'); sizes=d.groupby(['Staffing_Capacity','Document_Prevalidation','Routing_Strategy']).size(); assert len(sizes)==8 and sizes.nunique()==1
def test_dq_precision_recall():
    gt=pd.read_csv(ROOT/'data'/'interim'/'injected_issues_ground_truth.csv'); det=pd.read_csv(ROOT/'data'/'data_quality_issues.csv'); a=set(map(tuple,gt[['Application_ID','Issue_Type']].values)); b=set(map(tuple,det[['Application_ID','Issue_Type']].values)); assert a==b
def test_seed_results():
    s=pd.read_csv(ROOT/'results'/'seed_robustness.csv'); assert set(s.Seed)=={42,1,123,2026,8675309}; assert s.Rows.eq(100000).all()
