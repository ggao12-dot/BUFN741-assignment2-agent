import numpy as np
import pytest
from src.estimate_moments import estimate_moments, portfolio_metrics, monthly_rate
from src.portfolio_optimizer import analytical_gmv, analytical_tangency, analytical_frontier
from src.validation import validate_covariance, validate_weights, ValidationError


def test_annualization_and_gross_exposure(returns):
    mean, cov = estimate_moments(returns)
    weights = np.array([.4, -.2, .1, .1, .2, .1, .1, .2])
    metrics = portfolio_metrics(weights, mean, cov, .045 / 12)
    assert metrics['gross_exposure'] == pytest.approx(1.4)
    assert metrics['mean_annual'] == pytest.approx(12 * metrics['mean_monthly'])
    assert metrics['variance_annual'] == pytest.approx(12 * metrics['variance_monthly'])
    assert metrics['sd_annual'] == pytest.approx(np.sqrt(12) * metrics['sd_monthly'])
    assert metrics['sharpe_annual'] == pytest.approx(np.sqrt(12) * metrics['sharpe_monthly'])
    assert monthly_rate(.045) == .045 / 12
    assert (1 + monthly_rate(.045, 'compound')) ** 12 == pytest.approx(1.045)


def test_analytical_identities(returns):
    mean, cov = estimate_moments(returns)
    gmv = analytical_gmv(cov)
    assert gmv.sum() == pytest.approx(1)
    assert np.ptp(cov @ gmv) < 1e-14
    tangent = analytical_tangency(mean, cov, .00375).weights
    excess = mean - .00375
    assert tangent.sum() == pytest.approx(1)
    assert (tangent @ excess) ** 2 / (tangent @ cov @ tangent) == pytest.approx(excess @ np.linalg.solve(cov, excess))
    frontier = analytical_frontier(mean, cov, .009)
    assert frontier.sum() == pytest.approx(1)
    assert frontier @ mean == pytest.approx(.009)


@pytest.mark.parametrize('cov', [np.array([[1., 2.], [0., 1.]]), np.array([[1., 2.], [2., 1.]]), np.array([[np.nan]])])
def test_bad_covariance_rejected(cov):
    with pytest.raises(ValidationError):
        validate_covariance(cov)


def test_psd_tolerance():
    validate_covariance(np.diag([1., -1e-12]), 1e-10)
    validate_covariance(np.ones((2, 2)))


def test_invalid_weight_rejected():
    with pytest.raises(ValidationError):
        validate_weights(np.array([.2, .2]), np.zeros(2), np.ones(2))


def test_nonattained_unrestricted_tangency_is_not_mislabeled():
    result = analytical_tangency(np.array([.001, .002]), np.eye(2), .01)
    assert result.status == 'NONATTAINED'
    assert result.weights is None and result.gross_exposure is None
