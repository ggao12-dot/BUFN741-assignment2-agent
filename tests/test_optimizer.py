import numpy as np
import pytest
from src.estimate_moments import estimate_moments
from src.portfolio_optimizer import (PortfolioOptimizer, ConstraintSpec, analyze,
                                     analytical_gmv, analytical_tangency, OptimizationError)
from src.validation import ValidationError


@pytest.fixture(scope='module', params=['unrestricted', 'long_only', 'bounded'])
def optimized(request, returns):
    mean, cov = estimate_moments(returns)
    spec = ConstraintSpec(request.param, -.2, .2)
    options = dict(constraint_tolerance=1e-7, solver='CLARABEL', tangency_solver='SLSQP')
    result = analyze(mean, cov, list(returns.columns), .00375, spec, {'points': 200}, options)
    return result, spec


def test_every_portfolio_and_frontier_satisfies_constraints(optimized):
    result, spec = optimized
    lower, upper = spec.bounds(8)
    for table in [result.portfolios, result.frontier]:
        weights = table[[f'w_{a}' for a in result.assets]].to_numpy()
        np.testing.assert_allclose(weights.sum(axis=1), 1, atol=1e-7)
        assert (weights >= lower - 1e-7).all()
        assert (weights <= upper + 1e-7).all()
    weights = result.frontier[[f'w_{a}' for a in result.assets]].to_numpy()
    np.testing.assert_allclose(weights @ result.mean, result.frontier.target_monthly, atol=1e-7)
    assert result.frontier.solver_status.eq('optimal').all()


def test_tangency_independent_frontier_check(optimized):
    result, _ = optimized
    tangent = result.portfolios.set_index('portfolio').loc['tangency']
    grid = result.frontier.query('efficient').sharpe_monthly.max()
    assert -.0000001 <= tangent.sharpe_monthly - grid <= .005
    assert np.isclose(result.cal.iloc[0].mean_monthly, .00375)
    at_one = result.cal.iloc[100]
    assert at_one.mean_monthly == pytest.approx(tangent.mean_monthly)
    assert at_one.sd_monthly == pytest.approx(tangent.sd_monthly)


def test_gmv_is_minimum_and_upper_branch(optimized):
    result, _ = optimized
    gmv = result.portfolios.set_index('portfolio').loc['GMV']
    assert (result.frontier.variance_monthly >= gmv.variance_monthly - 1e-10).all()
    assert (result.frontier.query('efficient').mean_monthly >= gmv.mean_monthly - 1e-10).all()


def test_unrestricted_numerical_agrees_analytical(returns):
    mean, cov = estimate_moments(returns)
    optimizer = PortfolioOptimizer(mean, cov, .00375, ConstraintSpec('unrestricted'))
    gmv = optimizer.minimum_variance()
    tangent, _ = optimizer.tangency([np.ones(8) / 8, gmv])
    np.testing.assert_allclose(gmv, analytical_gmv(cov), atol=1e-7)
    np.testing.assert_allclose(tangent, analytical_tangency(mean, cov, .00375).weights, atol=2e-4)


def test_infeasible_target_and_bounds_fail(returns):
    mean, cov = estimate_moments(returns)
    optimizer = PortfolioOptimizer(mean, cov, .00375, ConstraintSpec('long_only'))
    with pytest.raises(OptimizationError):
        optimizer.minimum_variance(float(mean.max() + .1))
    with pytest.raises(ValidationError):
        ConstraintSpec('bounded', -.2, .2).bounds(3)


def test_failed_solver_point_aborts_frontier(monkeypatch, returns):
    mean, cov = estimate_moments(returns)
    original = PortfolioOptimizer.minimum_variance
    calls = 0

    def fail(self, target=None):
        nonlocal calls
        calls += 1
        if calls == 5:
            raise OptimizationError('injected failed frontier point')
        return original(self, target)

    monkeypatch.setattr(PortfolioOptimizer, 'minimum_variance', fail)
    with pytest.raises(OptimizationError, match='injected'):
        analyze(mean, cov, list(returns.columns), .00375, ConstraintSpec('long_only'), {'points': 20}, {})


def test_unknown_solver_rejected(returns):
    mean, cov = estimate_moments(returns)
    optimizer = PortfolioOptimizer(mean, cov, .00375, ConstraintSpec('long_only'), {'solver': 'DOES_NOT_EXIST'})
    with pytest.raises(OptimizationError):
        optimizer.minimum_variance()


def test_failed_slsqp_is_never_accepted(monkeypatch, returns):
    from scipy.optimize import OptimizeResult
    mean, cov = estimate_moments(returns)
    optimizer = PortfolioOptimizer(mean, cov, .00375, ConstraintSpec('long_only'))
    monkeypatch.setattr('src.portfolio_optimizer.minimize', lambda *a, **k: OptimizeResult(
        success=False, x=np.ones(8) / 8, message='iteration limit', nit=2000, fun=-100))
    with pytest.raises(OptimizationError, match='All tangency solves failed'):
        optimizer.tangency([np.ones(8) / 8])


def test_success_status_with_invalid_weights_is_rejected(monkeypatch, returns):
    from scipy.optimize import OptimizeResult
    mean, cov = estimate_moments(returns)
    optimizer = PortfolioOptimizer(mean, cov, .00375, ConstraintSpec('long_only'))
    monkeypatch.setattr('src.portfolio_optimizer.minimize', lambda *a, **k: OptimizeResult(
        success=True, x=np.ones(8), message='success', nit=1, fun=-1))
    with pytest.raises(OptimizationError, match='All tangency solves failed'):
        optimizer.tangency([np.ones(8) / 8])
