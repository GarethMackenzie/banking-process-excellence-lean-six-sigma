# Project Walkthrough

## 30 seconds
This project shows how I use Lean Six Sigma with data rather than treating it as a certificate. I defined a synthetic retail-bank onboarding process, validated the measurement system, quantified process capability and variation, tested root-cause hypotheses, ran a randomized factorial experiment, simulated a pilot and then established a control plan with SPC.

## 60 seconds
The project starts with 100,000 reproducible synthetic applications and a separate source-data quality layer. DEFINE establishes the CTQs and process map. MEASURE separates activation time from approval time, uses six explicit defect opportunities and runs an Attribute Agreement study. ANALYZE uses Pareto, non-parametric testing, regression and FMEA while separating observational association from causality. IMPROVE uses a randomized 2³ DOE rather than calling historical data an experiment. CONTROL then monitors sustainment and documents reaction rules. Required KYC review is treated as appraisal cost, not COPQ.

## 2-minute technical walkthrough
Open with the repository architecture and synthetic-data disclosure. Show the exact 100k canonical manifest and multi-seed robustness. Walk through the recursive branch/shift backlog, operational definitions and abandonment censoring. Then show MSA, capability-by-tier, Pareto/regression/FMEA, randomized DOE, pilot metrics and the control plan. Finish with QA: deterministic generation, quality-detection precision/recall, pytest, statistical QA and the master QA report.
