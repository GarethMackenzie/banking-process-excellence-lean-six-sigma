"""Generate a balanced synthetic categorical MSA before and after standardization."""
from pathlib import Path
import argparse,json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--seed',type=int,default=314);p.add_argument('--items',type=int,default=60);p.add_argument('--reviewers',type=int,default=4);p.add_argument('--trials',type=int,default=2);a=p.parse_args();rng=np.random.default_rng(a.seed)
 classes=np.array(['ACCEPT','REWORK_REQUIRED','MANUAL_REVIEW_REQUIRED']);refs=np.tile(classes,int(np.ceil(a.items/3)))[:a.items];rng.shuffle(refs)
 phases={'Baseline':np.linspace(.86,.93,a.reviewers),'Post_Standardization':np.linspace(.95,.98,a.reviewers)};rows=[]
 for phase,accs in phases.items():
  for item in range(a.items):
   for r in range(a.reviewers):
    # reviewer-specific stable bias keeps the study realistic; higher post-standardization accuracy reflects clarified definitions/training.
    for trial in range(1,a.trials+1):
     ref=refs[item]; acc=float(accs[r] - (0.015 if trial==2 and phase=='Baseline' else 0))
     rating=ref if rng.random()<acc else rng.choice(classes[classes!=ref])
     rows.append({'Study_Phase':phase,'Study_Item_ID':f'MSA-{item+1:03d}','Application_ID':f'STUDY-APX-{item+1:03d}','Reviewer_ID':f'REV-{r+1:02d}','Trial':trial,'Reference_Classification':ref,'Reviewer_Classification':rating})
 out=pd.DataFrame(rows);(ROOT/'data'/'msa').mkdir(parents=True,exist_ok=True);out.to_csv(ROOT/'data'/'msa'/'msa_study.csv',index=False)
 (ROOT/'results'/'msa_manifest.json').write_text(json.dumps({'seed':a.seed,'items_per_phase':a.items,'reviewers':a.reviewers,'trials':a.trials,'phases':list(phases),'rows':len(out),'balanced':len(out)==len(phases)*a.items*a.reviewers*a.trials},indent=2));print(f'MSA study rows: {len(out)}')
if __name__=='__main__':main()
