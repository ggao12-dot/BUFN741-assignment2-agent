"""Economic edge cases and invariants identified by the repository audit."""
from itertools import combinations, product
import numpy as np
import pytest
from scipy.optimize import linprog
from src.portfolio_optimizer import analytical_tangency, analyze, ConstraintSpec, PortfolioOptimizer
from src.estimate_moments import estimate_moments
from src.comparison import compare_models
from src.validation import validate_weights, ValidationError


@pytest.mark.parametrize('rf,status', [(0.0, 'ATTAINED'), (.003, 'NONATTAINED'), (.006, 'NONATTAINED')])
def test_unrestricted_tangency_sign_and_boundary(rf, status):
    mean, cov = np.array([.002, .004]), np.eye(2) * .001
    result = analytical_tangency(mean, cov, rf)
    assert result.status == status
    if status == 'ATTAINED':
        expected = np.linalg.solve(cov, mean - rf)
        np.testing.assert_allclose(result.weights, expected / expected.sum())
    else:
        assert result.weights is None and result.gross_exposure is None
        assert result.sharpe_supremum_monthly == pytest.approx(np.sqrt(.002))
        assert 'mu_GMV <= rf' in result.reason
    if rf == .003:
        assert result.coefficients['h'] == pytest.approx(0, abs=1e-12)


def test_sharpe_supremum_is_limit_not_finite_tangency():
    mean, cov, rf = np.array([.002, .004]), np.eye(2) * .001, .006
    result = analytical_tangency(mean, cov, rf)
    sharpes = []
    for leverage in [10, 100, 1000, 10000]:
        w = np.array([.5 - leverage, .5 + leverage])
        sharpes.append((w @ mean - rf) / np.sqrt(w @ cov @ w))
    assert np.all(np.diff(sharpes) > 0)
    assert max(sharpes) < result.sharpe_supremum_monthly
    assert sharpes[-1] == pytest.approx(result.sharpe_supremum_monthly, rel=.001)


def test_nonattained_analysis_never_invokes_slsqp(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail('SLSQP must not fabricate finite NONATTAINED weights')
    monkeypatch.setattr(PortfolioOptimizer, 'tangency', forbidden)
    result = analyze(np.array([.002, .004]), np.eye(2) * .001, ['X', 'Y'], .006,
                     ConstraintSpec('unrestricted'), {'points': 40}, {})
    assert result.tangency.status == 'NONATTAINED'
    assert result.portfolios.portfolio.tolist() == ['GMV']
    assert len(result.frontier) == 40 and result.cal.empty
    assert result.checks['frontier_analytical_max_weight_error'] < 2e-4


def test_zero_discriminant_boundary_preserves_degenerate_frontier():
    result = analyze(np.array([.003, .003]), np.eye(2) * .001, ['X', 'Y'], .003,
                     ConstraintSpec('unrestricted'), {'points': 40}, {})
    assert result.tangency.status == 'NONATTAINED'
    assert result.tangency.sharpe_supremum_monthly == pytest.approx(0, abs=1e-8)
    assert len(result.frontier) == 1 and len(result.portfolios) == 1


@pytest.fixture(scope='module')
def comparison_result(returns):
    mu, cov = estimate_moments(returns)
    return analyze(mu, cov, list(returns.columns), .00375, ConstraintSpec('long_only'), {'points': 40}, {})


def test_identical_models_are_only_ties(comparison_result):
    frame = compare_models(comparison_result, comparison_result, True, .00375,
                           ConstraintSpec('long_only'), {})['frontier_dominance']
    assert len(frame) == 80
    assert frame.lower_volatility.eq('TIE').all()
    assert frame.sim_minus_markowitz_sd.eq(0).all()


@pytest.mark.parametrize('scale,expected', [(1 + 1e-9, 'TIE'), (1 - 1e-9, 'TIE'),
                                           (1.01, 'MARKOWITZ'), (.99, 'SIM')])
def test_near_ties_and_pointwise_differences(comparison_result, scale, expected):
    from dataclasses import replace
    other = replace(comparison_result, covariance=comparison_result.covariance * scale)
    frame = compare_models(comparison_result, other, True, .00375,
                           ConstraintSpec('long_only'), {'dominance_sd_tolerance': 1e-8})['frontier_dominance']
    assert frame.lower_volatility.eq(expected).all()
    assert frame.sd_tolerance_annual.eq(1e-8).all()
    assert 'winner' not in frame.columns


def test_specification_c_negative_holdings_geometry():
    # Maximize a common negative margin for every candidate set of three shorts.
    for negative_assets in combinations(range(8), 3):
        a = np.zeros((3, 9))
        for row, asset in enumerate(negative_assets):
            a[row, asset] = a[row, 8] = 1
        result = linprog([0] * 8 + [-1], A_ub=a, b_ub=np.zeros(3),
                         A_eq=[[1] * 8 + [0]], b_eq=[1], bounds=[(-.2, .2)] * 8 + [(0, None)])
        assert result.success and result.x[-1] <= 1e-10
    weights = np.array([.2] * 6 + [-.1, -.1])
    validate_weights(weights, *ConstraintSpec('bounded', -.2, .2).bounds(8))
    assert (weights < 0).sum() == 2


def test_specification_c_maximum_gross_exposure():
    # ||w||_1 = max over sign vectors s of s'w; enumerate all sign LPs.
    maxima = []
    for signs in product([-1, 1], repeat=8):
        result = linprog(-np.array(signs), A_eq=np.ones((1, 8)), b_eq=[1], bounds=[(-.2, .2)] * 8)
        assert result.success
        maxima.append(-result.fun)
    assert max(maxima) == pytest.approx(1.4, abs=1e-10)


def test_specification_c_equal_weight_and_three_asset_feasibility():
    spec = ConstraintSpec('bounded', -.2, .2)
    validate_weights(np.ones(8) / 8, *spec.bounds(8))
    with pytest.raises(ValidationError, match='Infeasible'):
        spec.bounds(3)
