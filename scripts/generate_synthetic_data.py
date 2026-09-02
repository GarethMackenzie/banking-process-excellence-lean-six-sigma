"""Generate the canonical synthetic Apex Retail Bank onboarding dataset."""
from __future__ import annotations
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import SimulationConfig
from src.simulation import run_simulation


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--n-applications", type=int, default=100_000)
    p.add_argument("--start-date", default="2024-01-01")
    p.add_argument("--end-date", default="2026-08-31")
    p.add_argument("--output-dir", default=str(ROOT))
    return p.parse_args()


def main():
    args = parse_args()
    cfg = SimulationConfig(seed=args.seed, n_applications=args.n_applications, start_date=args.start_date, end_date=args.end_date)
    df, paths = run_simulation(cfg, Path(args.output_dir))
    completed = df[df["Completed_Flag"].eq(1)]
    print(f"Generated exactly {len(df):,} synthetic applications")
    print(f"Completed: {len(completed):,} | Abandoned: {df['Abandonment_Flag'].sum():,}")
    print(f"Median activation time: {completed['Time_To_Activation_Hours'].median():.2f} h")
    print(f"SLA compliance: {completed['SLA_Met_Flag'].astype(float).mean()*100:.2f}%")
    print(f"FPY: {df['First_Pass_Yield_Flag'].mean()*100:.2f}% | Rework: {df['Rework_Flag'].mean()*100:.2f}%")
    print(f"Mean COPQ/app: R{df['Total_COPQ'].mean():.2f} | Appraisal/app: R{df['Total_Appraisal_Cost'].mean():.2f}")
    print(f"Saved canonical truth -> {paths['applications']}")


if __name__ == "__main__":
    main()
