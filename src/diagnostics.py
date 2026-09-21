"""Descriptive diagnostics calculated independently of plotting."""
from __future__ import annotations
import numpy as np
import pandas as pd
from src.portfolio_optimizer import AnalysisResult, ConstraintSpec


def largest_pairs(matrix: pd.DataFrame, value_name: str = 'value', top: int = 15) -> pd.DataFrame:
    rows = [dict(asset_i=matrix.index[i], asset_j=matrix.columns[j], **{value_name: float(matrix.iloc[i, j])})
            for i in range(len(matrix)) for j in range(i + 1, len(matrix))]
    frame = pd.DataFrame(rows)
    return frame.loc[frame[value_name].abs().sort_values(ascending=False).index].head(top).reset_index(drop=True)


def sample_changes(pre: pd.DataFrame, post: pd.DataFrame) -> dict[str, pd.DataFrame]:
    cov_change, corr_change = post.cov() - pre.cov(), post.corr() - pre.corr()
    # Include diagonal variance changes in addition to off-diagonal covariance changes.
    variance = pd.DataFrame(dict(asset=pre.columns, pre_variance=np.diag(pre.cov()),
                                  post_variance=np.diag(post.cov()), change=np.diag(cov_change)))
    return dict(covariance_changes=largest_pairs(cov_change, 'change', 28),
                correlation_changes=largest_pairs(corr_change, 'change', 28),
                variance_changes=variance, covariance_change_matrix=cov_change,
                correlation_change_matrix=corr_change)


def result_diagnostics(result: AnalysisResult, spec: ConstraintSpec, tolerance: float) -> dict:
    lower, upper = spec.bounds(len(result.assets))
    bound_hits = []
    for _, row in result.portfolios.iterrows():
        for i, asset in enumerate(result.assets):
            w = row[f'w_{asset}']
            if abs(w - lower[i]) <= tolerance * 10 or abs(w - upper[i]) <= tolerance * 10:
                bound_hits.append(dict(portfolio=row.portfolio, asset=asset, weight=float(w)))
    eigenvalues = np.linalg.eigvalsh(result.covariance)
    w = result.portfolios.set_index('portfolio')[[f'w_{a}' for a in result.assets]]
    return dict(eigenvalues_monthly=eigenvalues.tolist(), condition_number=float(eigenvalues.max() / eigenvalues.min()),
                bound_hits=bound_hits, gross_exposure=result.portfolios.set_index('portfolio').gross_exposure.to_dict(),
                tangency_status=result.tangency.status,
                gmv_tangency_weight_l1_distance=None if 'tangency' not in w.index else
                float(np.abs(w.loc['GMV'] - w.loc['tangency']).sum()))


def weight_stability(left: AnalysisResult, right: AnalysisResult) -> pd.DataFrame:
    rows = []
    for portfolio in ['GMV', 'tangency']:
        if portfolio not in left.portfolios.portfolio.values or portfolio not in right.portfolios.portfolio.values:
            rows.append(dict(portfolio=portfolio, status='NONATTAINED', l1_distance=None,
                             l2_distance=None, max_absolute_change=None))
            continue
        a = left.portfolios.set_index('portfolio').loc[portfolio]
        b = right.portfolios.set_index('portfolio').loc[portfolio]
        delta = np.array([b[f'w_{x}'] - a[f'w_{x}'] for x in left.assets])
        rows.append(dict(portfolio=portfolio, status='AVAILABLE', l1_distance=float(np.abs(delta).sum()),
                         l2_distance=float(np.linalg.norm(delta)), max_absolute_change=float(np.abs(delta).max())))
    return pd.DataFrame(rows)
