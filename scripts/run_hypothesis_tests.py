from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy import stats
ROOT=Path(__file__).resolve().parents[1]
df=pd.read_csv(ROOT/'data'/'clean'/'applications_clean.csv', low_memory=False)
comp=df[df.Completed_Flag.eq(1)].copy()
# Manual review cycle-time association
x=comp.loc[comp.Manual_Review_Flag.eq(1),'Time_To_Activation_Hours']; y=comp.loc[comp.Manual_Review_Flag.eq(0),'Time_To_Activation_Hours']
u,p=stats.mannwhitneyu(x,y,alternative='two-sided')
# Rank-biserial effect size from U
rbc=2*u/(len(x)*len(y)) - 1
# Channel differences
channels=[g.Time_To_Activation_Hours.values for _,g in comp.groupby('Channel')]
h,p_kw=stats.kruskal(*channels)
# Rework association with channel
ct=pd.crosstab(df.Channel,df.Rework_Flag); chi2,p_chi,dof,exp=stats.chi2_contingency(ct)
res={"manual_review_mannwhitney":{"u":float(u),"p_value":float(p),"rank_biserial":float(rbc),"median_review":float(x.median()),"median_no_review":float(y.median())},"channel_kruskal":{"h":float(h),"p_value":float(p_kw)},"rework_by_channel_chi_square":{"chi2":float(chi2),"p_value":float(p_chi),"dof":int(dof)}}
(ROOT/'results'/'hypothesis_tests.json').write_text(json.dumps(res,indent=2))
(ROOT/'dmaic'/'03_analyze'/'hypothesis-testing.md').write_text(f"# Hypothesis Testing\n\nAll tests use the synthetic clean dataset. Non-normal cycle-time distributions motivate rank-based tests.\n\n- Manual review vs no review: Mann–Whitney p={p:.3g}, rank-biserial effect={rbc:.3f}; medians {x.median():.2f} h vs {y.median():.2f} h. This is an **association**, not a causal estimate.\n- Channel cycle-time differences: Kruskal–Wallis p={p_kw:.3g}.\n- Rework by channel: chi-square p={p_chi:.3g}.\n")
print(json.dumps(res,indent=2))
