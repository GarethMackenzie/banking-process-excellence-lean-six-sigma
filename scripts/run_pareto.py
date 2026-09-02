from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
df=pd.read_csv(ROOT/'data'/'clean'/'applications_clean.csv',low_memory=False)
cols=[c for c in df.columns if c.endswith('_Defect')]
labels={c:c.replace('_Defect','').replace('_',' ') for c in cols}
counts=pd.Series({labels[c]:int(df[c].sum()) for c in cols}).sort_values(ascending=False)
out=counts.rename('Count').reset_index(); out.columns=['Defect','Count']; out['Percent']=out.Count/out.Count.sum(); out['Cumulative_Percent']=out.Percent.cumsum(); out.to_csv(ROOT/'results'/'defect_pareto.csv',index=False)
lines=['# Pareto Analysis','', 'Defect categories are explicit opportunity failures; rework is intentionally excluded because it is an outcome.','', '| Defect | Count | Share | Cumulative |','|---|---:|---:|---:|']
for r in out.itertuples(): lines.append(f"| {r.Defect} | {r.Count:,} | {r.Percent*100:.1f}% | {r.Cumulative_Percent*100:.1f}% |")
(ROOT/'dmaic'/'03_analyze'/'pareto-analysis.md').write_text('\n'.join(lines))
print(out.to_string(index=False))
