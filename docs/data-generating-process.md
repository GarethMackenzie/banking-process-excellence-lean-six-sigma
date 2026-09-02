# Data-Generating Process

The simulation intentionally distinguishes drivers, mediators and outcomes.

```text
Business calendar + channel rules
            ↓
Application arrivals → branch/shift demand
            ↓
Staffing / absences / outages → effective capacity
            ↓
Opening backlog → queue position → queue wait ─────────────┐
                                                           ↓
Product / ownership / EDD factors → risk score → required review → review wait
                                                           ↓
Defined defect opportunities → rework → additional processing → failure cost
                                                           ↓
                                        time to approval → activation CTQ
                                                           ↓
                                   SLA / complaint / abandonment outcomes
```

`Queue_Time_Minutes` is a mediator of capacity/backlog effects, so it is not blindly included with upstream capacity variables in the root-cause regression. Risk represents control complexity, not misconduct. Special-cause labels are stored separately and are not inputs to SPC detection.
