# Regression Analysis

The model explains **log time-to-activation** using pre-process and early-process drivers. Queue-time components are intentionally excluded because they are mediators of staffing/capacity/backlog effects. HC3 robust standard errors are used.

- n = 97,978
- R² = 0.660
- Adjusted R² = 0.660
- Maximum VIF = 3.25
- Residual skewness = 0.81

Coefficients are interpreted as conditional associations in the observational baseline, not causal effects. See `results/regression_results.json`.
