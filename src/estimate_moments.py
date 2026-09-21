"""Monthly arithmetic moments and explicitly labeled presentation units."""
from __future__ import annotations
import numpy as np
import pandas as pd
from src.validation import require, validate_returns, validate_covariance


def monthly_rate(annual: float, convention: str = 'simple') -> float:
    require(np.isfinite(annual), 'Non-finite risk-free rate')
    if convention == 'simple':
        return annual / 12
    require(convention == 'compound' and annual > -1, 'Invalid monthly conversion')
    return (1 + annual) ** (1 / 12) - 1


def estimate_moments(returns: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    validate_returns(returns)
    mean, cov = returns.mean().to_numpy(), returns.cov(ddof=1).to_numpy()
    validate_covariance(cov)
    return mean, cov


def portfolio_metrics(weights: np.ndarray, mean: np.ndarray, cov: np.ndarray,
                      rf: float) -> dict[str, float]:
    variance = float(weights @ cov @ weights)
    require(variance > 0, 'Portfolio variance must be positive')
    ret, sd = float(weights @ mean), float(np.sqrt(variance))
    sharpe = (ret - rf) / sd
    return dict(mean_monthly=ret, variance_monthly=variance, sd_monthly=sd,
                sharpe_monthly=sharpe, mean_annual=12 * ret,
                variance_annual=12 * variance, sd_annual=np.sqrt(12) * sd,
                sharpe_annual=np.sqrt(12) * sharpe,
                gross_exposure=float(np.abs(weights).sum()))
