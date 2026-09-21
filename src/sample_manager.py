"""Select complete, identical observations for each explicitly configured sample."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd
from src.validation import require, validate_returns


def make_samples(returns: pd.DataFrame, specs: dict) -> dict[str, pd.DataFrame]:
    validate_returns(returns)
    result = {}
    for name, spec in specs.items():
        start = returns.index[0] if spec['start'] == 'common' else pd.Period(spec['start'], freq='M')
        end = pd.Period(spec['end'], freq='M')
        sample = returns.loc[start:end].copy()
        validate_returns(sample, min_n=max(3, len(returns.columns) + 1))
        require(sample.index[0] == start and sample.index[-1] == end,
                f'{name}: required boundary month missing')
        result[name] = sample
    return result


def sample_metadata(frame: pd.DataFrame) -> dict:
    return dict(start=str(frame.index[0]), end=str(frame.index[-1]), N=len(frame),
                assets=list(frame.columns))


def series_metadata(series: pd.Series) -> dict:
    require(isinstance(series.index, pd.PeriodIndex) and series.index.freqstr == 'M',
            'Series metadata requires a monthly PeriodIndex')
    require(len(series) > 0, 'Cannot describe an empty monthly series')
    return dict(start=str(series.index[0]), end=str(series.index[-1]), N=len(series),
                name=str(series.name or 'value'))


def month_difference(later: pd.Period, earlier: pd.Period) -> int:
    return (later.year - earlier.year) * 12 + later.month - earlier.month


@dataclass(frozen=True)
class SIMSampleSelection:
    returns: pd.DataFrame
    risk_free: pd.Series
    trailing_rf_lag_months: int
    lag_accepted: bool
    metadata: dict


def select_sim_common_sample(returns: pd.DataFrame, rf: pd.Series,
                             allow_trailing_rf_lag: bool,
                             max_trailing_rf_lag_months: int) -> SIMSampleSelection:
    """Return the longest contiguous ETF/RF intersection under the trailing-lag policy.

    A later ETF endpoint is permitted only as a trailing source lag. Missing RF months
    inside the overlapping interval are data errors and are never repaired or skipped.
    """
    validate_returns(returns, min_n=max(3, len(returns.columns) + 1))
    require(isinstance(rf.index, pd.PeriodIndex) and rf.index.freqstr == 'M',
            'Fama-French RF must have a monthly PeriodIndex')
    require(rf.index.is_unique and rf.index.is_monotonic_increasing,
            'Fama-French RF months must be unique and sorted')
    require(len(rf) > 0 and np.isfinite(rf.to_numpy()).all(), 'Invalid Fama-French RF observations')
    require(isinstance(max_trailing_rf_lag_months, int) and max_trailing_rf_lag_months >= 0,
            'max_trailing_rf_lag_months must be a nonnegative integer')

    missing_anywhere = pd.period_range(rf.index[0], rf.index[-1], freq='M').difference(rf.index)
    require(len(missing_anywhere) == 0,
            f'Internal Fama-French RF gaps: {list(map(str, missing_anywhere))}')

    start = max(returns.index[0], rf.index[0])
    end = min(returns.index[-1], rf.index[-1])
    require(start <= end, 'ETF returns and Fama-French RF have no common monthly observations')
    expected = pd.period_range(start, end, freq='M')
    missing = expected.difference(rf.index)
    require(len(missing) == 0, f'Internal Fama-French RF gaps: {list(map(str, missing))}')

    lag = max(0, month_difference(returns.index[-1], rf.index[-1]))
    accepted = lag == 0 or (allow_trailing_rf_lag and lag <= max_trailing_rf_lag_months)
    require(accepted,
            f'Fama-French RF trails ETF returns by {lag} months; allowed={allow_trailing_rf_lag}, '
            f'maximum={max_trailing_rf_lag_months}')

    common_returns = returns.loc[expected].copy()
    common_rf = rf.reindex(expected).copy()
    validate_returns(common_returns, min_n=max(3, len(returns.columns) + 1))
    require(common_rf.notna().all(), 'Fama-French RF alignment introduced missing observations')
    metadata = dict(
        etf_sample=sample_metadata(returns),
        rf_sample=series_metadata(rf),
        sim_common=sample_metadata(common_returns),
        markowitz_comparison=sample_metadata(common_returns),
        trailing_rf_lag_months=lag,
        lag_accepted=accepted,
        allow_trailing_rf_lag=bool(allow_trailing_rf_lag),
        max_trailing_rf_lag_months=max_trailing_rf_lag_months,
    )
    return SIMSampleSelection(common_returns, common_rf, lag, accepted, metadata)
