# Baseline Performance — MEASURE Phase

> Portfolio demonstration using synthetic data only. Financial values and process outcomes are simulated.

Clean analytical records: **98,600**; completed applications used for activation-time/SLA metrics: **97,978**.

## CTQ scorecard

| Metric | Baseline |
|---|---:|
| Median time to activation | 3.43 h |
| P90 time to activation | 5.82 h |
| SLA compliance (completed only) | 97.90% |
| Median SLA utilization | 0.391 |
| First Pass Yield | 64.96% |
| Rework rate | 22.02% |
| Abandonment rate | 0.63% |
| Process Cycle Efficiency | 34.28% |
| COPQ per application | R19.28 |
| Required-control appraisal cost per application | R2.07 |

## Defect opportunity model

Unit = one onboarding application. Explicit opportunities per unit = **6** (Documentation_Completeness_Defect, Document_Quality_Defect, Identity_Verification_Defect, Data_Capture_Defect, KYC_Processing_Defect, Product_Information_Defect). Rework is an outcome and is not counted as a defect opportunity.

DPU = **0.2982**, DPO = **0.0497**, DPMO = **49,692**. The sigma estimate (**3.15**) is retained only as an approximate portfolio teaching metric; capability is assessed separately and does not assume normality.

## Interpretation

The strongest baseline quality signal is FPY of **65.0%** with rework at **22.0%**. Aggregate SLA compliance is high and should not be used as the sole improvement headline because SLA specifications differ by governed complexity tier.