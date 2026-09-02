# Root-Cause Evidence Hierarchy

| Suspected driver | Mechanism | Evidence | Status / limitation |
|---|---|---|---|
| Required manual review | Additional controlled review and waiting | Review vs no-review median difference; rank-based test in `hypothesis-testing.md` | Strong association; legitimate control work, not automatically waste |
| Defects | Rework / repeat processing | Defect rate → rework relationship; Pareto + regression | Supported synthetic mechanism |
| Opening backlog | Waiting before active work | Positive queue-time correlation and regression coefficient | Supported upstream process driver |
| System outages | Stage delay / capacity loss | Event manifest + process overlap logic | Local effect; portfolio SPC can dilute signals |
| Channel | Submission-quality/process mix | Kruskal/chi-square evidence | Association; may proxy other process characteristics |

Fishbone hypotheses are treated as hypotheses until supported by data; appearing on a diagram is not evidence of root cause.
