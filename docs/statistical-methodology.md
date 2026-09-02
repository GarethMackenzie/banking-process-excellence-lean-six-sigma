# Statistical Methodology

The analysis follows question → variable type → assumptions → method → effect / uncertainty → business interpretation.

- Right-skewed cycle times use rank-based hypothesis tests where appropriate.
- Regression models `log1p(time to activation)` with HC3 robust covariance and reports VIF; mediators are deliberately excluded from the driver model.
- Capability is evaluated within homogeneous SLA groups and does not rely on aggregate normal Cp/Cpk.
- MSA uses repeated categorical ratings with a reference standard; continuous Gage R&R is not misapplied.
- DOE is a separate randomized replicated 2³ design, not a relabelled observational analysis.
- SPC separates control limits from customer specifications and reports false alarms / missed seeded events.
- Baseline observational language uses “associated with”, not causal language. Intervention language is reserved for the randomized synthetic experiment/pilot.
