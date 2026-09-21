"""Fail-closed input, moment, and portfolio validation."""
from __future__ import annotations

import numpy as np
import pandas as pd


class ValidationError(ValueError):
    """Required data or mathematical invariant was violated."""


class ExternalDataUnavailable(ValidationError):
    """A required external observation/source is unavailable, rather than invalid."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def validate_covariance(cov: np.ndarray, tolerance: float = 1e-10) -> np.ndarray:
    cov = np.asarray(cov, dtype=float)
    require(cov.ndim == 2 and cov.shape[0] == cov.shape[1], 'Covariance must be square')
    require(np.isfinite(cov).all(), 'Non-finite covariance')
    require(np.allclose(cov, cov.T, atol=tolerance, rtol=0), 'Asymmetric covariance')
    eigenvalues = np.linalg.eigvalsh(cov)
    require(eigenvalues.min() >= -tolerance, 'Covariance is not PSD')
    return eigenvalues


def validate_returns(frame: pd.DataFrame, min_n: int = 3) -> None:
    require(isinstance(frame.index, pd.PeriodIndex) and frame.index.freqstr == 'M',
            'Returns must have a monthly PeriodIndex')
    require(len(frame) >= min_n and len(frame.columns) > 0, 'Insufficient observations')
    require(frame.index.is_unique and frame.columns.is_unique, 'Duplicate observations/assets')
    require(frame.index.is_monotonic_increasing, 'Unsorted returns')
    require(np.isfinite(frame.to_numpy()).all(), 'Missing or non-finite aligned returns')
    require((frame.to_numpy() >= -1).all(), 'Simple returns below -100%')
    expected = pd.period_range(frame.index[0], frame.index[-1], freq='M')
    require(frame.index.equals(expected), 'Internal missing month in common sample')


def validate_weights(weights: np.ndarray, lower: np.ndarray, upper: np.ndarray,
                     tolerance: float = 1e-7, mean: np.ndarray | None = None,
                     target: float | None = None) -> None:
    require(np.isfinite(weights).all(), 'Non-finite weights')
    require(abs(weights.sum() - 1) <= tolerance, 'Weights do not sum to one')
    require(bool(np.all(weights >= lower - tolerance)), 'Lower bound violated')
    require(bool(np.all(weights <= upper + tolerance)), 'Upper bound violated')
    if target is not None:
        require(mean is not None and abs(weights @ mean - target) <= tolerance,
                'Frontier target return missed')
