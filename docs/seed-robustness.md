# Multi-Seed Robustness

Five full 100,000-application simulations were generated independently in isolated processes. The goal is structural stability, not identical results.

| Seed | Rows | Median_Activation_Hours | P90_Activation_Hours | SLA_Compliance | SLA_Utilization_Median | FPY | Rework | Manual_Review | Abandonment | Complaint | COPQ_Per_App | Appraisal_Per_App | PCE | Risk_Low | Risk_Medium | Risk_High | Complexity_Low | Complexity_Medium | Complexity_High |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 42.0000 | 100000.0000 | 3.4340 | 5.8213 | 0.9791 | 0.3905 | 0.6493 | 0.2204 | 0.0714 | 0.0063 | 0.0163 | 19.3013 | 2.0673 | 0.3428 | 0.8913 | 0.0766 | 0.0321 | 0.7728 | 0.1577 | 0.0695 |
| 1.0000 | 100000.0000 | 3.3866 | 5.6443 | 0.9800 | 0.3845 | 0.6456 | 0.2209 | 0.0722 | 0.0059 | 0.0165 | 19.1316 | 2.1042 | 0.3486 | 0.8922 | 0.0738 | 0.0340 | 0.7719 | 0.1579 | 0.0701 |
| 123.0000 | 100000.0000 | 3.4499 | 6.0972 | 0.9748 | 0.3917 | 0.6485 | 0.2201 | 0.0733 | 0.0067 | 0.0176 | 19.3960 | 2.1105 | 0.3377 | 0.8920 | 0.0748 | 0.0332 | 0.7702 | 0.1593 | 0.0705 |
| 2026.0000 | 100000.0000 | 3.4227 | 5.7966 | 0.9789 | 0.3879 | 0.6470 | 0.2226 | 0.0719 | 0.0058 | 0.0162 | 19.2242 | 2.0894 | 0.3441 | 0.8922 | 0.0742 | 0.0337 | 0.7719 | 0.1579 | 0.0702 |
| 8675309.0000 | 100000.0000 | 3.3623 | 5.5799 | 0.9804 | 0.3816 | 0.6453 | 0.2219 | 0.0731 | 0.0059 | 0.0167 | 19.2826 | 2.1186 | 0.3517 | 0.8897 | 0.0765 | 0.0339 | 0.7701 | 0.1580 | 0.0720 |

## Relative seed variability

| Metric | CV across seeds |
|---|---:|
| Median_Activation_Hours | 1.05% |
| P90_Activation_Hours | 3.46% |
| SLA_Compliance | 0.23% |
| FPY | 0.27% |
| Rework | 0.47% |
| COPQ_Per_App | 0.51% |

Major baseline conclusions are structurally robust when direction and order of magnitude persist across seeds.