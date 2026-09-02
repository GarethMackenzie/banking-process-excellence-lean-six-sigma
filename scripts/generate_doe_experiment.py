"""Generate a randomized replicated 2^3 factorial synthetic experiment."""
from pathlib import Path
import itertools, json, argparse
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser(); p.add_argument('--seed',type=int,default=2718); p.add_argument('--replicates',type=int,default=12); a=p.parse_args(); rng=np.random.default_rng(a.seed)
 rows=[]
 run=1
 for rep in range(1,a.replicates+1):
  combos=list(itertools.product([-1,1],repeat=3)); rng.shuffle(combos)
  for A,B,C in combos:
   # Controlled effects with one mildly adverse interaction; not every effect is beneficial.
   cycle=4.6 -0.28*A -0.38*B -0.22*C -0.10*A*B +0.07*B*C + rng.normal(0,0.32)
   queue=max(0.2,1.4 -0.22*A -0.18*C -0.06*A*C + rng.normal(0,.16))
   rework_p=np.clip(.24 - .075*B - .025*C + .018*A*C, .03,.50)
   sla_fail=np.clip(.18 - .05*A - .07*B - .035*C + .018*B*C + rng.normal(0,.015),.01,.5)
   rows.append({"Run_ID":f"DOE-{run:03d}","Replicate":rep,"Staffing_Capacity":A,"Document_Prevalidation":B,"Routing_Strategy":C,"Total_Cycle_Time_Hours":max(cycle,0.5),"Queue_Time_Hours":queue,"Rework_Rate":rework_p,"SLA_Failure_Rate":sla_fail})
   run+=1
 df=pd.DataFrame(rows).sample(frac=1,random_state=a.seed).reset_index(drop=True); df.insert(1,'Randomized_Order',np.arange(1,len(df)+1))
 (ROOT/'data'/'doe').mkdir(parents=True,exist_ok=True); df.to_csv(ROOT/'data'/'doe'/'doe_experiment.csv',index=False)
 cell=df.groupby(['Staffing_Capacity','Document_Prevalidation','Routing_Strategy']).size(); balanced=cell.nunique()==1 and len(cell)==8
 (ROOT/'results'/'doe_manifest.json').write_text(json.dumps({"seed":a.seed,"replicates":a.replicates,"rows":len(df),"factorial_cells":len(cell),"cell_size":int(cell.iloc[0]),"balanced":bool(balanced)},indent=2))
 print(f"DOE rows: {len(df)} | balanced: {balanced}")
if __name__=='__main__': main()
