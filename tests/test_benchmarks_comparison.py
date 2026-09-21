import numpy as np
import pytest
from src.benchmark_portfolios import benchmark_weights, benchmark_table
from src.comparison import compare_models
from src.estimate_moments import estimate_moments
from src.portfolio_optimizer import AnalysisResult, ConstraintSpec, analyze
from src.validation import ValidationError


def test_benchmark_weights_and_separate_feasibility(returns, config):
    weights = benchmark_weights(list(returns.columns))
    for w in weights.values():
        assert w.sum() == pytest.approx(1)
    np.testing.assert_allclose(weights['60_40'], [.2] * 5 + [0] * 3)
    assert weights['40_30_30'][:3].sum() == pytest.approx(.4)
    assert weights['40_30_30'][3:5].sum() == pytest.approx(.3)
    assert weights['40_30_30'][5:].sum() == pytest.approx(.3)
    mean, cov = estimate_moments(returns)
    table = benchmark_table(list(returns.columns), mean, cov, .00375, config['constraints'], 1e-7)
    assert table.feasible.all()  # All three specified benchmarks happen to satisfy A/B/C.
    config['constraints']['C']['upper'] = .15
    table = benchmark_table(list(returns.columns), mean, cov, .00375, config['constraints'], 1e-7)
    assert not table.query("benchmark == '60_40' and specification == 'C'").feasible.iloc[0]
    assert table.query("benchmark == '60_40' and specification == 'B'").feasible.iloc[0]


def test_covariance_only_rejects_different_means(returns):
    mean, cov = estimate_moments(returns)
    result = analyze(mean, cov, list(returns.columns), .00375, ConstraintSpec('long_only'), {'points': 40}, {})
    changed = AnalysisResult(result.assets, mean + .001, cov, result.portfolios, result.frontier, result.cal, result.checks)
    with pytest.raises(ValidationError, match='identical means'):
        compare_models(result, changed, True, .00375, ConstraintSpec('long_only'), {})
