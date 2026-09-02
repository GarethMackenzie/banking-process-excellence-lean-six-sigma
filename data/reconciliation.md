# Data Reconciliation

Portfolio demonstration using synthetic data only.

| Stage | Row Count |
|---|---:|
| Raw rows | 100,400 |
| Rows quarantined | 1,800 |
| Rows retained clean | 98,600 |
| Reconciliation | 100,400 == 100,400 |

Field-level corrections: **1,400**
Detection precision vs seeded ground truth: **100.00%**
Detection recall vs seeded ground truth: **100.00%**

## Quarantine reasons

| Reason | Rows |
|---|---:|
| Duplicate_Application_ID | 400 |
| Missing_Channel | 300 |
| Negative_Processing_Time | 300 |
| Timestamp_Sequencing_Error | 300 |
| Missing_Product_Type | 300 |
| Future_Application_Date | 200 |