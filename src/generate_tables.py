"""Serialization of already calculated numerical results."""
from __future__ import annotations
import json
import os
from pathlib import Path
import numpy as np
import pandas as pd
from src.portfolio_optimizer import AnalysisResult


def json_safe(value: object) -> object:
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, np.ndarray)):
        return [json_safe(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, (float, np.floating)):
        return float(value) if np.isfinite(value) else None
    return value


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    with temp.open('w') as handle:
        json.dump(json_safe(value), handle, indent=2, allow_nan=False)
        handle.flush()
        os.fsync(handle.fileno())
    temp.replace(path)


def save_result(root: Path, name: str, result: AnalysisResult) -> None:
    for label, table in [('portfolios', result.portfolios), ('frontier', result.frontier),
                         ('efficient_frontier', result.frontier.loc[result.frontier.efficient]), ('cal', result.cal)]:
        table.to_csv(root / 'tables' / f'{name}_{label}.csv', index=False, float_format='%.17g')
    pd.DataFrame(result.covariance, index=result.assets, columns=result.assets).to_csv(
        root / 'models' / f'{name}_covariance_monthly.csv', float_format='%.17g')
    pd.Series(result.mean, index=result.assets, name='mean_monthly').to_csv(
        root / 'models' / f'{name}_means_monthly.csv', float_format='%.17g')
    np.savez_compressed(root / 'models' / f'{name}_moments.npz',
                        mean=result.mean, covariance=result.covariance, assets=result.assets)
    write_json(root / 'diagnostics' / f'{name}_optimization_checks.json', result.checks)
    write_json(root / 'models' / f'{name}_tangency.json', result.tangency.to_dict())
