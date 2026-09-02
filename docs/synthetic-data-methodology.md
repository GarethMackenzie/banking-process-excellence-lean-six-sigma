# Synthetic Data Methodology

Apex Retail Bank is fictional. The canonical generator creates exactly 100,000 applications from 2024-01-01 through 2026-08-31 using a deterministic seed. It combines stable business rules with stochastic variation, including seasonality, branch/channel operating rules, right-skewed service times, recursive backlog, staffing shocks, outages, defect opportunities and abandonment.

The pipeline deliberately separates **process truth** from **source-system data quality erosion**. A second script injects controlled defects into a copy of the truth dataset. The validator does not read the injection ground truth; reconciliation later compares detected events with the hidden log to measure precision and recall honestly.

Synthetic assumptions are not calibrated to a real bank and should not be used to estimate actual operational performance.
