# Cost of Quality and COPQ Methodology

All Rand values are simulated assumptions.

## Classification

- **Prevention cost:** fixed synthetic prevention investment per application.
- **Appraisal / required-control cost:** required risk/KYC manual review. This is necessary control activity and is **not COPQ**.
- **Internal failure cost:** defect-driven review, rework, repeat processing and simulated expedited handling.
- **External failure cost:** complaint handling and abandonment opportunity cost.
- **COPQ:** internal failure + external failure only.
- **Total Cost of Quality:** prevention + appraisal + COPQ.

The separation prevents the methodological error of labelling every legitimate KYC review as poor quality. `results/simulation_parameters.json` contains the unit-cost assumptions and the test suite reconciles each total.
