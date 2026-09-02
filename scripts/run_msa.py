from pathlib import Path
import json,numpy as np,pandas as pd
from statsmodels.stats.inter_rater import fleiss_kappa
ROOT=Path(__file__).resolve().parents[1];df=pd.read_csv(ROOT/'data'/'msa'/'msa_study.csv')
def assess(d):
 acc=(d.Reviewer_Classification==d.Reference_Classification).mean();within=d.groupby(['Reviewer_ID','Study_Item_ID']).Reviewer_Classification.nunique().eq(1).mean();between=d.groupby(['Study_Item_ID','Trial']).Reviewer_Classification.nunique().eq(1).mean();classes=sorted(d.Reference_Classification.unique());counts=[]
 for _,g in d.groupby(['Study_Item_ID','Trial']):counts.append([int((g.Reviewer_Classification==c).sum()) for c in classes])
 kap=float(fleiss_kappa(np.array(counts)));rev=d.assign(Correct=d.Reviewer_Classification==d.Reference_Classification).groupby('Reviewer_ID').Correct.mean().to_dict();return {'agreement_to_reference':float(acc),'within_appraiser_repeatability':float(within),'between_appraiser_unanimous_agreement':float(between),'fleiss_kappa':kap,'reviewer_accuracy':{k:float(v) for k,v in rev.items()}}
base=assess(df[df.Study_Phase.eq('Baseline')]);post=assess(df[df.Study_Phase.eq('Post_Standardization')]);res=dict(base);res['baseline']=base;res['post_standardization']=post;res['agreement_gain_pp']=(post['agreement_to_reference']-base['agreement_to_reference'])*100
(ROOT/'results'/'msa_results.json').write_text(json.dumps(res,indent=2));(ROOT/'dmaic'/'02_measure'/'measurement-system-analysis.md').write_text(f'''# Measurement System Analysis

Synthetic categorical Attribute Agreement Analysis uses 60 items, four reviewers and two repeated trials per phase.

| Phase | Agreement to reference | Within-appraiser repeatability | Between-appraiser unanimous agreement | Fleiss' kappa |
|---|---:|---:|---:|---:|
| Baseline | {base['agreement_to_reference']*100:.1f}% | {base['within_appraiser_repeatability']*100:.1f}% | {base['between_appraiser_unanimous_agreement']*100:.1f}% | {base['fleiss_kappa']:.3f} |
| Post-standardization | {post['agreement_to_reference']*100:.1f}% | {post['within_appraiser_repeatability']*100:.1f}% | {post['between_appraiser_unanimous_agreement']*100:.1f}% | {post['fleiss_kappa']:.3f} |

The baseline study is treated as a measurement-system finding rather than ignored. The simulated response is clearer operational definitions and reviewer standardization, followed by a repeated study. This is a methodological demonstration, not a claim about real reviewers.
''');print(json.dumps(res,indent=2))
