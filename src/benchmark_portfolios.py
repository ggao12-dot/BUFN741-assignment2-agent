"""Assignment benchmarks and independent constraint feasibility."""
from __future__ import annotations
import numpy as np
import pandas as pd
from src.portfolio_optimizer import ConstraintSpec
from src.estimate_moments import portfolio_metrics
from src.validation import validate_weights, ValidationError, require

ASSETS = ['SPY', 'EFA', 'EEM', 'TLT', 'AGG', 'GLD', 'USO', 'DBC']


def benchmark_weights(assets: list[str]) -> dict[str, np.ndarray]:
    require(set(assets) == set(ASSETS), 'Benchmarks require all eight assignment assets')
    sixty = dict(zip(ASSETS, [.2, .2, .2, .2, .2, 0, 0, 0]))
    balanced = dict(zip(ASSETS, [.4 / 3] * 3 + [.3 / 2] * 2 + [.3 / 3] * 3))
    return {'equal_weight': np.full(8, 1 / 8),
            '60_40': np.array([sixty[a] for a in assets]),
            '40_30_30': np.array([balanced[a] for a in assets])}


def benchmark_table(assets: list[str], mean: np.ndarray, cov: np.ndarray, rf: float,
                    constraints: dict, tolerance: float) -> pd.DataFrame:
    rows = []
    for name, weights in benchmark_weights(assets).items():
        for label, config in constraints.items():
            lower, upper = ConstraintSpec.from_config(config).bounds(len(assets))
            try:
                validate_weights(weights, lower, upper, tolerance)
                feasible, reason = True, ''
            except ValidationError as exc:
                feasible, reason = False, str(exc)
            rows.append(dict(benchmark=name, specification=label, feasible=feasible,
                             infeasibility_reason=reason, **portfolio_metrics(weights, mean, cov, rf),
                             **{f'w_{a}': float(w) for a, w in zip(assets, weights)}))
    return pd.DataFrame(rows)
