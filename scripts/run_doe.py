from pathlib import Path
import json
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm
ROOT=Path(__file__).resolve().parents[1]
df=pd.read_csv(ROOT/'data'/'doe'/'doe_experiment.csv')
model=smf.ols('Total_Cycle_Time_Hours ~ Staffing_Capacity * Document_Prevalidation * Routing_Strategy',data=df).fit()
anova=anova_lm(model,typ=2)
coef={k:float(v) for k,v in model.params.items()}
means=df.groupby(['Staffing_Capacity','Document_Prevalidation','Routing_Strategy']).Total_Cycle_Time_Hours.mean().reset_index(); best=means.loc[means.Total_Cycle_Time_Hours.idxmin()].to_dict()
res={"r_squared":float(model.rsquared),"coefficients":coef,"best_observed_configuration":{k:(float(v) if isinstance(v,(float,int)) else v) for k,v in best.items()},"anova_p_values":{str(k):float(v) for k,v in anova['PR(>F)'].dropna().items()}}
(ROOT/'results'/'doe_results.json').write_text(json.dumps(res,indent=2))
(ROOT/'dmaic'/'04_improve'/'doe.md').write_text("# Design of Experiments\n\nA separate randomized, replicated **2³ full factorial** experiment tests staffing capacity, document pre-validation, and routing strategy. Baseline transactions are observational and are not labelled as DOE.\n\n"+f"Model R²: **{model.rsquared:.3f}**. Best observed factor combination: staffing={best['Staffing_Capacity']:+.0f}, pre-validation={best['Document_Prevalidation']:+.0f}, routing={best['Routing_Strategy']:+.0f}, mean cycle time={best['Total_Cycle_Time_Hours']:.2f} h.\n\nSee `results/doe_results.json` for fitted coefficients and ANOVA p-values. Results are synthetic experimental evidence, not workplace outcomes.\n")
print(json.dumps(res,indent=2))
