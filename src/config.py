from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass(frozen=True)
class SimulationConfig:
    seed: int = 42
    n_applications: int = 100_000
    start_date: str = "2024-01-01"
    end_date: str = "2026-08-31"
    config_version: str = "2.0.0"
    n_branches: int = 60
    n_analysts: int = 180
    capacity_per_fte: float = 8.5
    public_holiday_rate: float = 0.025
    outage_event_count: int = 28
    volume_spike_event_count: int = 12
    staffing_shock_event_count: int = 22
    reviewer_shortage_event_count: int = 14

    @property
    def parameters(self):
        return asdict(self)

ROOT = Path(__file__).resolve().parents[1]
