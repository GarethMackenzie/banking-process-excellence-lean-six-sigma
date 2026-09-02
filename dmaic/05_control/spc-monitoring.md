# SPC Monitoring

The primary control chart is a weekly Individuals chart on median time-to-activation; sigma is estimated from the baseline moving range. Because seeded special causes are local to a branch/shift and can be diluted in a portfolio median, a separate **ground-truth validation** uses independently derived extreme-state thresholds for zero-inflated branch/shift backlog and capacity variables. Event labels are never used to set thresholds.

- Weekly I-chart center: **3.41 h**, UCL **3.55 h**, LCL **3.27 h**
- Weekly I-chart signal weeks: **19**
- Seeded events: **76**
- Local event detections on event day or next day: **14 (18.4%)**
- Local-state false-alarm rate: **1.38% of branch/shift/days**

Detection performance is reported honestly rather than tuned against event labels. Control limits and customer SLA specifications remain conceptually separate.
