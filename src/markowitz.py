"""Sample-moment Markowitz model."""
from __future__ import annotations
import pandas as pd
from src.estimate_moments import estimate_moments
from src.portfolio_optimizer import AnalysisResult, ConstraintSpec, analyze


def run_markowitz(returns: pd.DataFrame, rf: float, spec: ConstraintSpec,
                  frontier: dict, optimization: dict) -> AnalysisResult:
    mean, cov = estimate_moments(returns)
    return analyze(mean, cov, list(returns.columns), rf, spec, frontier, optimization)
