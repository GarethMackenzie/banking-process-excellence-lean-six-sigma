# Banking Process Excellence Analytics

### Lean Six Sigma DMAIC Optimization of Retail Customer Onboarding & KYC Operations

> **Portfolio demonstration using synthetic data only.** Apex Retail Bank is fictional. No real customer, banking, KYC, identity, employee, employer-confidential or production data is used.

An end-to-end process-excellence case study showing how data can move from **operational definition → measurement validation → statistical diagnosis → controlled experiment → pilot improvement → sustained control**.

## Executive scorecard

| Metric | Baseline | Synthetic pilot | Change |
|---|---:|---:|---:|
| Median time to activation | 3.44 h | 2.35 h | -31.7% |
| SLA compliance | 97.84% | 99.25% | 1.41 pp |
| Rework rate | 22.34% | 10.96% | -11.38 pp |
| COPQ / application | R18.66 | R8.96 | -52.0% |

These are **simulated portfolio results**, not workplace achievements or expected real-bank savings.

## Business problem

The generated baseline shows a process with **65.0% First Pass Yield**, **22.0% rework**, median activation time of **3.43 hours**, and P90 of **5.82 hours**. Aggregate SLA compliance is 97.90%, but SLA targets differ by complexity tier, so the improvement case is intentionally anchored on **quality-at-source, rework and process variation**, not a misleading aggregate SLA headline.

## DMAIC approach

**DEFINE** — project charter, SIPOC, VOC/CTQ, process map, value-stream logic and Lean waste hypotheses.  
**MEASURE** — exact operational definitions, explicit defect opportunities, baseline metrics, Attribute Agreement Analysis and non-normal capability treatment.  
**ANALYZE** — Pareto, hypothesis tests, HC3 regression, process-dependency map and FMEA.  
**IMPROVE** — separate randomized replicated 2³ factorial DOE, solution prioritization and a synthetic pilot.  
**CONTROL** — SPC, control plan, reaction plan and a 26-week synthetic sustainment period.

## Engineering depth

- Exact **100,000-application** canonical simulation, seed 42.
- Business-calendar-aware channel intake.
- Stable rule-based complexity and risk tiers, not sample quantiles.
- Recursive **Date × Branch × Shift** backlog/capacity state.
- Explicit special-cause manifest independent of SPC detection.
- Abandonment censoring prevents impossible downstream timestamps.
- Cost of Quality separates required-control appraisal from failure-related COPQ.
- Six explicit defect opportunities; rework is modelled as an outcome.
- Five-seed robustness study using 100,000 applications per seed.
- Controlled data-quality corruption → independent detection → correction/quarantine → reconciliation.
- Pytest, statistical QA, master QA and GitHub Actions.

## Measurement and statistical evidence

- MSA agreement to reference improves from **87.7%** (Fleiss' κ **0.681**) to **95.8%** (κ **0.875**) after a simulated standardization response, demonstrating that measurement-system findings trigger action rather than being ignored.
- Regression R²: **0.660**, maximum VIF **3.25**. Queue-time components are excluded from the root-cause regression because they are mediators of capacity/backlog effects.
- DOE R²: **0.712** using a randomized replicated full factorial design.
- SPC reports both signals and detection limitations. Local special-cause detection is **18.4%** (14 of 76 seeded events) with a **1.38%** local-state false-alarm rate; no result is hidden or tuned against event labels.

## Cost of Quality

Baseline mean failure-related COPQ is **R19.28/application** while legitimate required-control appraisal cost is separately reported at **R2.07/application**. Required KYC/manual review is not automatically treated as poor quality.

## Reproducibility

```bash
python -m venv .venv
# activate the environment for your OS
python -m pip install -r requirements.txt
python scripts/generate_synthetic_data.py --seed 42 --n-applications 100000
python scripts/inject_quality_issues.py
python scripts/validate_data.py
python scripts/build_clean_data.py
python scripts/calculate_baseline.py
python scripts/generate_msa_study.py
python scripts/run_msa.py
python scripts/generate_doe_experiment.py
python scripts/run_doe.py
python scripts/run_hypothesis_tests.py
python scripts/run_regression.py
python scripts/run_capability.py
python scripts/run_pareto.py
python scripts/run_spc.py
python scripts/run_pilot.py
python scripts/run_control.py
python scripts/build_fmea.py
python -m pytest -q
python scripts/statistical_qa.py
python scripts/qa_project.py
```

Full generated CSVs are intentionally ignored by Git because they are reproducible. `data/sample/` provides an inspectable sample; manifests and analytical results remain tracked.

## Repository map

```text
src/                 modular synthetic process simulation
scripts/             reproducible DMAIC and QA pipeline
tests/               process, statistical and integrity tests
dmaic/               DEFINE → MEASURE → ANALYZE → IMPROVE → CONTROL evidence
docs/                methodology, definitions, limitations and interview guide
results/              tracked metrics, manifests and QA evidence
sql/                  process-analysis SQL examples
data/sample/          small inspectable synthetic sample
.github/workflows/    automated CI quality gate
```

## Responsible interpretation

Risk tiers represent synthetic **review/control complexity**, not wrongdoing. Analyst data is fictional and supports workload/capacity analysis, not punitive employee ranking. Baseline observational associations are not labelled causal. Stronger intervention language is reserved for the separately randomized DOE and synthetic pilot.

## Author

**Gareth Andrew Mackenzie**  
Lean Six Sigma · Data Analytics · Python · SQL · Process Excellence · Banking Operations Analytics
