# Remediation Audit

| Issue | Remediation | Validation |
|---|---|---|
| Required review incorrectly counted as COPQ | Split Cost of Quality into prevention, appraisal, internal failure and external failure | Cost reconciliation tests |
| Abandonment after completed stages | Terminal abandonment stages and timestamp censoring | Abandonment tests |
| Ambiguous onboarding duration | Separate approval and activation CTQs | Operational definitions + tests |
| Quantile-based complexity | Fixed score thresholds | Cross-seed rule test |
| Same-period backlog only | Recursive branch × shift backlog | Capacity reconciliation |
| Coarse staffing | Branch × shift effective FTE/capacity schedule | Grain QA |
| Queue variables duplicated | Distinct backlog, queue length and queue position | Correlation QA |
| Rework counted as defect | Six explicit defect opportunities; rework is outcome | Defect-count reconciliation |
| MSA absent | Separate balanced Attribute Agreement study | MSA manifest/results |
| DOE absent | Separate randomized replicated 2³ factorial | DOE manifest/results |
| Special causes discarded | Ground-truth event manifest | SPC evaluation |
| Weekend branch intake | Business-calendar-aware channel assignment | Calendar test |
| Customer segment drove risk | Governed process/control risk factors only | Risk-threshold test |
| Random analyst IDs | Synthetic analyst dimension and qualified assignment | Analyst integrity QA |
| Day-level outage treatment | Explicit outage intervals and stage-overlap delay | Event/capacity QA |
| Approximate canonical row count | Exact multinomial allocation to 100,000 | Row-count test |
| Monolithic generator | Modular `src/` simulation + CLI wrapper | Import/CLI/compile tests |
| Missing reproducibility manifests | Generation and parameter manifests + hashes | QA |
| No seed robustness | Five 100k simulations | `seed_robustness.csv` |
