from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
df=pd.read_csv(ROOT/'data'/'clean'/'applications_clean.csv', low_memory=False)
items=[
 ('Document submission','Incomplete documentation','Rework / delay','Documentation completeness defect','Submission checks',7,'Documentation_Completeness_Defect',5,'Pre-validation at submission'),
 ('Document validation','Poor document quality','Repeat validation','Document quality defect','Manual validation',6,'Document_Quality_Defect',5,'Automated quality prompt + checklist'),
 ('Identity verification','Identity mismatch','Exception handling','Identity verification defect','Identity matching rules',9,'Identity_Verification_Defect',4,'Standardized escalation path'),
 ('KYC screening','Processing defect','Rework / control delay','KYC processing defect','Reviewer checks',9,'KYC_Processing_Defect',4,'Checklist + peer review for exceptions'),
 ('Data capture','Incorrect captured data','Correction / rework','Data capture defect','Field validation',6,'Data_Capture_Defect',5,'Input validation and standard fields'),
]
rows=[]
for step,mode,effect,cause,control,sev,col,det,action in items:
 occ=max(1,min(10,int(round(df[col].mean()*20))))
 rpn=sev*occ*det; post_occ=max(1,occ-2); post_det=max(1,det-1)
 rows.append([step,mode,effect,cause,control,sev,occ,det,rpn,action,sev,post_occ,post_det,sev*post_occ*post_det])
cols=['Process Step','Failure Mode','Effect','Cause','Current Control','Severity','Occurrence','Detection','RPN','Recommended Action','Post-Improvement S','Post-Improvement O','Post-Improvement D','Residual RPN']
out=pd.DataFrame(rows,columns=cols).sort_values('RPN',ascending=False); out.to_csv(ROOT/'results'/'fmea.csv',index=False)
lines=['# Process FMEA','', 'Severity and detection ratings are transparent synthetic scoring assumptions; occurrence is linked to generated defect prevalence. RPN is a prioritization aid, not a substitute for judgement.','', '| Process step | Failure mode | S | O | D | RPN | Recommended action | Residual RPN |','|---|---|---:|---:|---:|---:|---|---:|']
for r in out.itertuples(index=False): lines.append(f"| {r[0]} | {r[1]} | {r[5]} | {r[6]} | {r[7]} | {r[8]} | {r[9]} | {r[13]} |")
(ROOT/'dmaic'/'03_analyze'/'fmea.md').write_text('\n'.join(lines))
print(out[['Process Step','RPN','Residual RPN']].to_string(index=False))
