"""Separate covariance effects from complete-model expected-return effects."""
from __future__ import annotations
import numpy as np
import pandas as pd
from src.portfolio_optimizer import AnalysisResult, PortfolioOptimizer, ConstraintSpec
from src.validation import require


def compare_models(markowitz: AnalysisResult, sim: AnalysisResult, covariance_only: bool,
                   rf: float, spec: ConstraintSpec, options: dict) -> dict[str, pd.DataFrame]:
    require(markowitz.assets == sim.assets, 'Comparison asset order mismatch')
    if covariance_only:
        require(np.array_equal(markowitz.mean, sim.mean), 'Covariance-only comparison requires identical means')
    weights, metrics = [], []
    for name in ['GMV', 'tangency']:
        if name not in markowitz.portfolios.portfolio.values or name not in sim.portfolios.portfolio.values:
            continue
        m = markowitz.portfolios.set_index('portfolio').loc[name]
        s = sim.portfolios.set_index('portfolio').loc[name]
        for asset in markowitz.assets:
            weights.append(dict(portfolio=name, asset=asset, markowitz=m[f'w_{asset}'],
                                sim=s[f'w_{asset}'], sim_minus_markowitz=s[f'w_{asset}'] - m[f'w_{asset}']))
        for metric in ['mean_annual', 'sd_annual', 'sharpe_annual', 'gross_exposure']:
            metrics.append(dict(portfolio=name, metric=metric, markowitz=m[metric], sim=s[metric],
                                sim_minus_markowitz=s[metric] - m[metric]))
    # Solve both models at identical expected-return targets on their overlapping upper branches.
    # In complete-model comparisons these are model-specific expected returns, not forecasts
    # under one common probability model; interpret accordingly.
    m_branch, s_branch = markowitz.frontier.query('efficient'), sim.frontier.query('efficient')
    low = max(m_branch.target_monthly.min(), s_branch.target_monthly.min())
    high = min(m_branch.target_monthly.max(), s_branch.target_monthly.max())
    dominance = []
    tolerance = options.get('dominance_sd_tolerance', 1e-8)
    require(np.isfinite(tolerance) and tolerance > 0, 'Invalid dominance SD tolerance')
    if high >= low:
        mo = PortfolioOptimizer(markowitz.mean, markowitz.covariance, rf, spec, options)
        so = PortfolioOptimizer(sim.mean, sim.covariance, rf, spec, options)
        for target in np.linspace(low, high, 80):
            mw, sw = mo.minimum_variance(target), so.minimum_variance(target)
            m_sd = float(np.sqrt(12 * (mw @ markowitz.covariance @ mw)))
            s_sd = float(np.sqrt(12 * (sw @ sim.covariance @ sw)))
            dominance.append(dict(target_annual=12 * target, markowitz_sd_annual=m_sd,
                                  sim_sd_annual=s_sd, sim_minus_markowitz_sd=s_sd - m_sd,
                                  lower_volatility='TIE' if abs(s_sd - m_sd) <= tolerance else
                                  ('SIM' if s_sd < m_sd else 'MARKOWITZ'),
                                  sd_tolerance_annual=tolerance))
    return dict(weight_differences=pd.DataFrame(weights), metric_differences=pd.DataFrame(metrics),
                frontier_dominance=pd.DataFrame(dominance, columns=[
                    'target_annual', 'markowitz_sd_annual', 'sim_sd_annual',
                    'sim_minus_markowitz_sd', 'lower_volatility', 'sd_tolerance_annual']),
                means=pd.DataFrame(dict(asset=markowitz.assets, markowitz=markowitz.mean,
                                         sim=sim.mean, difference=sim.mean - markowitz.mean)))
