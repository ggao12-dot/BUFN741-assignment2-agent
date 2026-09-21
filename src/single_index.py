"""Monthly excess-return OLS, SPY identity, and total-return SIM covariance."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.stattools import durbin_watson, jarque_bera
from src.validation import require, validate_returns, validate_covariance


@dataclass
class SingleIndexResult:
    means: np.ndarray
    covariance: np.ndarray
    regressions: pd.DataFrame
    residuals: pd.DataFrame
    market_variance: float
    assumptions: dict


def fit_single_index(returns: pd.DataFrame, rf: pd.Series, config: dict) -> SingleIndexResult:
    validate_returns(returns)
    require(rf.index.is_unique and returns.index.isin(rf.index).all(), 'Missing monthly regression RF')
    rf = rf.reindex(returns.index)
    require(np.isfinite(rf.to_numpy()).all(), 'Non-finite regression RF')
    market = config.get('market', 'SPY')
    require(market == 'SPY' and market in returns, 'Assignment market proxy must be SPY')
    market_excess = returns[market] - rf
    require(market_excess.var() > 1e-14, 'Constant market excess returns')
    x = sm.add_constant(market_excess.rename('market_excess'))
    # The exact excess-return factor used for beta also determines systematic risk.
    market_variance = float(market_excess.var(ddof=1))
    rows, residuals = [], pd.DataFrame(index=returns.index)
    for asset in returns.columns:
        if asset == market:
            row = dict(asset=asset, alpha_monthly=0.0, beta=1.0, residual_variance_monthly=0.0,
                       r_squared=1.0, adjusted_r_squared=1.0, N=len(returns), df_resid=None,
                       alpha_se=None, beta_se=None, alpha_t=None, beta_t=None,
                       alpha_p=None, beta_p=None, durbin_watson=None, jb_p=None, fitted=False)
            residuals[asset] = 0.0
        else:
            fitted = sm.OLS(returns[asset] - rf, x, missing='raise').fit()
            residuals[asset] = fitted.resid
            row = dict(asset=asset, alpha_monthly=float(fitted.params.iloc[0]),
                       beta=float(fitted.params.iloc[1]), residual_variance_monthly=float(fitted.mse_resid),
                       r_squared=float(fitted.rsquared), adjusted_r_squared=float(fitted.rsquared_adj),
                       N=int(fitted.nobs), df_resid=int(fitted.df_resid),
                       alpha_se=float(fitted.bse.iloc[0]), beta_se=float(fitted.bse.iloc[1]),
                       alpha_t=float(fitted.tvalues.iloc[0]), beta_t=float(fitted.tvalues.iloc[1]),
                       alpha_p=float(fitted.pvalues.iloc[0]), beta_p=float(fitted.pvalues.iloc[1]),
                       durbin_watson=float(durbin_watson(fitted.resid)),
                       jb_p=float(jarque_bera(fitted.resid)[1]), fitted=True)
        row['residual_sd_monthly'] = np.sqrt(row['residual_variance_monthly'])
        row['systematic_variance_monthly'] = row['beta'] ** 2 * market_variance
        row['total_variance_monthly'] = row['systematic_variance_monthly'] + row['residual_variance_monthly']
        row['alpha_annual'] = 12 * row['alpha_monthly']
        row['residual_variance_annual'] = 12 * row['residual_variance_monthly']
        row['residual_sd_annual'] = np.sqrt(12) * row['residual_sd_monthly']
        row['systematic_variance_annual'] = 12 * row['systematic_variance_monthly']
        row['total_variance_annual'] = 12 * row['total_variance_monthly']
        rows.append(row)
    table = pd.DataFrame(rows).set_index('asset')
    beta = table.beta.to_numpy()
    covariance = np.outer(beta, beta) * market_variance + np.diag(table.residual_variance_monthly)
    validate_covariance(covariance)
    method = config.get('expected_return_method', 'alpha_beta_premium')
    fixed_rf = config.get('annual_fixed_risk_free_rate', 0.045) / 12
    premium = config.get('annual_market_risk_premium', 0.06) / 12
    if method == 'alpha_beta_premium':
        means = fixed_rf + table.alpha_monthly.to_numpy() + beta * premium
    elif method == 'sample_mean':
        means = returns.mean().to_numpy()
    elif method == 'beta_premium':
        means = fixed_rf + beta * premium
    else:
        raise ValueError(f'Unknown SIM expected-return method: {method}')
    assumptions = dict(expected_return_method=method, fixed_rf_monthly=fixed_rf,
                       market_premium_monthly=premium, covariance_market_variance='SPY minus aligned FF RF, ddof=1',
                       residual_variance='OLS SSE/(N-2)', residual_cross_covariances='assumed zero',
                       regression_rf='Fama-French monthly RF, aligned without dropping observations')
    return SingleIndexResult(means, covariance, table, residuals, market_variance, assumptions)
