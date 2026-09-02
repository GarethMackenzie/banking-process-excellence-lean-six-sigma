"""Orchestrate the canonical local project build."""
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
CMDS=[
 ['scripts/generate_synthetic_data.py','--seed','42','--n-applications','100000'],
 ['scripts/inject_quality_issues.py'],['scripts/validate_data.py'],['scripts/build_clean_data.py'],['scripts/calculate_baseline.py'],
 ['scripts/generate_msa_study.py'],['scripts/run_msa.py'],['scripts/generate_doe_experiment.py'],['scripts/run_doe.py'],
 ['scripts/run_hypothesis_tests.py'],['scripts/run_regression.py'],['scripts/run_capability.py'],['scripts/run_pareto.py'],['scripts/run_spc.py'],['scripts/run_pilot.py'],['scripts/run_control.py'],['scripts/build_fmea.py'],
 ['scripts/run_seed_robustness.py'],
]
for cmd in CMDS:
    print('>',sys.executable,*cmd); subprocess.run([sys.executable,*cmd],cwd=ROOT,check=True)
subprocess.run([sys.executable,'-m','pytest','-q'],cwd=ROOT,check=True)
subprocess.run([sys.executable,'scripts/statistical_qa.py'],cwd=ROOT,check=True)
subprocess.run([sys.executable,'scripts/qa_project.py'],cwd=ROOT,check=True)
