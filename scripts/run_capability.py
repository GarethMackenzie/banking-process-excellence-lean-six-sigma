from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy import stats
ROOT=Path(__file__).resolve().parents[1]
df=pd.read_csv(ROOT/'data'/'clean'/'applications_clean.csv', low_memory=False)
comp=df[df.Completed_Flag.eq(1)].copy()
rows=[]
for tier,g in comp.groupby('Application_Complexity'):
 x=g.Time_To_Activation_Hours.astype(float).values; usl=float(g.SLA_Target_Hours.iloc[0]); mean=float(np.mean(x)); sd=float(np.std(x,ddof=1)); skew=float(stats.skew(x)); yield_rate=float(np.mean(x<=usl));
 # Diagnostic normal Ppu shown only as a rejected/secondary reference.
 ppu_normal=(usl-mean)/(3*sd) if sd>0 else np.nan
 # Primary non-normal one-sided capability is empirical yield + tail quantiles.
 q95=float(np.quantile(x,.95)); q99=float(np.quantile(x,.99)); margin_p99=usl-q99
 rows.append({"Complexity":tier,"n":len(g),"USL_hours":usl,"mean_hours":mean,"median_hours":float(np.median(x)),"skewness":skew,"observed_yield":yield_rate,"p95_hours":q95,"p99_hours":q99,"p99_margin_hours":margin_p99,"normal_ppu_diagnostic_only":ppu_normal})
out=pd.DataFrame(rows).sort_values('USL_hours'); out.to_csv(ROOT/'results'/'capability_by_tier.csv',index=False)
method="Cycle time is right-skewed and SLA specifications differ by complexity tier. The primary capability evidence is therefore one-sided empirical conformance and tail percentiles within homogeneous SLA groups. A normal-theory Ppu is retained only as a diagnostic reference and is not the primary capability conclusion."
(ROOT/'docs'/'capability-methodology.md').write_text("# Process Capability Methodology\n\n"+method+"\n\n**Control limits are not specification limits.** Stability is assessed separately with SPC before capability is interpreted.\n")
lines=["# Process Capability — MEASURE","",method,"","| Complexity | n | USL | Yield | Median | P95 | P99 | P99 margin |","|---|---:|---:|---:|---:|---:|---:|---:|"]
for r in out.itertuples(): lines.append(f"| {r.Complexity} | {r.n:,} | {r.USL_hours:.0f} h | {r.observed_yield*100:.2f}% | {r.median_hours:.2f} | {r.p95_hours:.2f} | {r.p99_hours:.2f} | {r.p99_margin_hours:.2f} h |")
(ROOT/'dmaic'/'02_measure'/'process-capability.md').write_text('\n'.join(lines))
print(out.to_string(index=False))
