from pathlib import Path
import json
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor
from scipy.stats import skew
ROOT=Path(__file__).resolve().parents[1]
df=pd.read_csv(ROOT/'data'/'clean'/'applications_clean.csv', low_memory=False)
df=df[df.Completed_Flag.eq(1)].copy()
df['log_cycle']=np.log1p(df.Time_To_Activation_Hours)
# Pre-process / early-process drivers only; queue time itself is intentionally excluded as a mediator.
formula='log_cycle ~ Complexity_Score + Risk_Score + Required_Manual_Review_Flag + Defect_Count + Opening_Backlog + System_Downtime_Minutes + C(Channel)'
model=smf.ols(formula,data=df).fit(cov_type='HC3')
num=df[['Complexity_Score','Risk_Score','Required_Manual_Review_Flag','Defect_Count','Opening_Backlog','System_Downtime_Minutes']].dropna().astype(float)
# Add constant manually for VIF; report predictors only.
X=np.column_stack([np.ones(len(num)),num.values])
vif={c:float(variance_inflation_factor(X,i+1)) for i,c in enumerate(num.columns)}
resid_skew=float(skew(model.resid))
res={"formula":formula,"n":int(model.nobs),"r_squared":float(model.rsquared),"adj_r_squared":float(model.rsquared_adj),"robust_covariance":"HC3","residual_skewness":resid_skew,"max_vif":float(max(vif.values())),"vif":vif,"coefficients":{k:float(v) for k,v in model.params.items()},"p_values":{k:float(v) for k,v in model.pvalues.items()}}
(ROOT/'results'/'regression_results.json').write_text(json.dumps(res,indent=2))
(ROOT/'dmaic'/'03_analyze'/'regression-analysis.md').write_text(f"# Regression Analysis\n\nThe model explains **log time-to-activation** using pre-process and early-process drivers. Queue-time components are intentionally excluded because they are mediators of staffing/capacity/backlog effects. HC3 robust standard errors are used.\n\n- n = {int(model.nobs):,}\n- R² = {model.rsquared:.3f}\n- Adjusted R² = {model.rsquared_adj:.3f}\n- Maximum VIF = {max(vif.values()):.2f}\n- Residual skewness = {resid_skew:.2f}\n\nCoefficients are interpreted as conditional associations in the observational baseline, not causal effects. See `results/regression_results.json`.\n")
print(json.dumps({k:res[k] for k in ['n','r_squared','adj_r_squared','max_vif','residual_skewness']},indent=2))
