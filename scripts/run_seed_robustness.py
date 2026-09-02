"""Run five full canonical-size simulations in isolated subprocesses to avoid memory accumulation."""
from pathlib import Path
import json, subprocess, sys
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
seeds=[42,1,123,2026,8675309]
rows=[]
for seed in seeds:
    cp=subprocess.run([sys.executable,str(ROOT/'scripts'/'seed_metrics_once.py'),'--seed',str(seed)],cwd=ROOT,capture_output=True,text=True,check=True)
    rows.append(json.loads(cp.stdout.strip().splitlines()[-1]))
out=pd.DataFrame(rows); out.to_csv(ROOT/'results'/'seed_robustness.csv',index=False)
keys=['Median_Activation_Hours','P90_Activation_Hours','SLA_Compliance','FPY','Rework','COPQ_Per_App']; summary={k:float(out[k].std(ddof=1)/abs(out[k].mean())) for k in keys}
headers=list(out.columns);md=['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|']
for _,r in out.iterrows(): md.append('| '+' | '.join(f'{r[h]:.4f}' if isinstance(r[h],(float,np.floating)) else str(r[h]) for h in headers)+' |')
lines=['# Multi-Seed Robustness','', 'Five full 100,000-application simulations were generated independently in isolated processes. The goal is structural stability, not identical results.','']+md+['','## Relative seed variability','','| Metric | CV across seeds |','|---|---:|']+[f'| {k} | {v*100:.2f}% |' for k,v in summary.items()]+['','Major baseline conclusions are structurally robust when direction and order of magnitude persist across seeds.']
(ROOT/'docs'/'seed-robustness.md').write_text('\n'.join(lines));print(out.to_string(index=False));print(summary)
