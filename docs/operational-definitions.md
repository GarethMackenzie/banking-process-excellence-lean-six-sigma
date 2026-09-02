# Operational Definitions

| Measure | Start | Stop | Unit | Population / rule |
|---|---|---|---|---|
| Time to approval | Application received | Approval timestamp | elapsed hours | Completed applications only |
| Time to activation | Application received | Activation timestamp | elapsed hours | **Primary customer-facing CTQ**, completed applications only |
| Time to abandonment | Application received | Abandonment timestamp | elapsed hours | Abandoned applications only; downstream events are censored |
| SLA utilization | n/a | n/a | ratio | Time to activation / governed SLA target |
| First Pass Yield | intake | completion / abandonment | binary | 1 only when no defined defect opportunity fails and no rework occurs |
| Rework | identified correction | corrected state | count / binary | Outcome, not a defect opportunity |
| COPQ | process observation | outcome | Rand | Internal + external failure cost only; required control/appraisal is excluded |

### Calendar convention

Application intake is calendar-time based. Digital intake may occur 24/7; Branch intake is permitted only when the synthetic business calendar marks the branch open. The primary CTQ is **calendar elapsed time to activation**, not business-hours-only processing time. This is explicit so specifications and capability are interpreted consistently.

### SLA specifications

Low complexity = 8 h, Medium = 16 h, High = 24 h. These are synthetic policy inputs, not tuned to hit a target compliance rate. Aggregate compliance is therefore descriptive only; capability is evaluated within homogeneous SLA groups.
