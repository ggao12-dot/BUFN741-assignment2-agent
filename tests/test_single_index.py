import numpy as np
import pandas as pd
import pytest
from src.single_index import fit_single_index
from src.validation import ValidationError


def test_sim_identities_and_regressions(returns):
    rf = pd.Series(.003 + .0004 * np.sin(np.arange(len(returns))), index=returns.index)
    result = fit_single_index(returns, rf, {})
    spy = result.regressions.loc['SPY']
    assert spy.alpha_monthly == 0 and spy.beta == 1 and spy.residual_variance_monthly == 0
    assert not spy.fitted
    beta = result.regressions.beta.to_numpy()
    systematic = np.outer(beta, beta) * (returns.SPY - rf).var(ddof=1)
    off = ~np.eye(8, dtype=bool)
    np.testing.assert_allclose(result.covariance[off], systematic[off], rtol=0, atol=1e-16)
    np.testing.assert_allclose(np.diag(result.covariance), beta ** 2 * result.market_variance + result.regressions.residual_variance_monthly,
                               rtol=0, atol=1e-16)
    np.testing.assert_allclose(
        result.regressions.systematic_variance_share,
        result.regressions.systematic_variance_monthly / result.regressions.total_variance_monthly)
    np.testing.assert_allclose(result.covariance, result.covariance.T, atol=1e-16)
    assert np.linalg.eigvalsh(result.covariance).min() >= 0
    np.testing.assert_allclose(result.means, .045 / 12 + result.regressions.alpha_monthly + beta * .06 / 12)
    assert result.means[0] == .045 / 12 + .06 / 12
    for asset in returns.columns[1:]:
        regression = result.regressions.loc[asset]
        x = np.column_stack([np.ones(len(returns)), returns.SPY - rf])
        expected = np.linalg.lstsq(x, returns[asset] - rf, rcond=None)[0]
        np.testing.assert_allclose([regression.alpha_monthly, regression.beta], expected)
        assert regression.residual_variance_monthly == pytest.approx(np.sum(result.residuals[asset] ** 2) / (len(returns) - 2))
        assert abs(result.residuals[asset].sum()) < 1e-10


@pytest.mark.parametrize('method', ['sample_mean', 'beta_premium'])
def test_configurable_means(returns, method):
    rf = pd.Series(.003, index=returns.index)
    sim = fit_single_index(returns, rf, {'expected_return_method': method})
    expected = returns.mean() if method == 'sample_mean' else .045 / 12 + sim.regressions.beta * .06 / 12
    np.testing.assert_allclose(sim.means, expected)


def test_missing_rf_fails_without_trimming(returns):
    with pytest.raises(ValidationError, match='Missing monthly'):
        fit_single_index(returns, pd.Series(.003, index=returns.index[:-1]), {})


def test_sim_uses_exact_excess_factor_variance(returns):
    # Correlation with SPY makes substituting raw-SPY variance visibly wrong.
    rf = .002 + .2 * (returns.SPY - returns.SPY.mean())
    result = fit_single_index(returns, rf, {})
    factor_variance = (returns.SPY - rf).var(ddof=1)
    beta = result.regressions.beta.to_numpy()
    expected = np.outer(beta, beta) * factor_variance + np.diag(result.regressions.residual_variance_monthly)
    np.testing.assert_allclose(result.covariance, expected, rtol=0, atol=1e-16)
    assert result.market_variance == factor_variance
    assert result.market_variance != pytest.approx(returns.SPY.var(ddof=1))
    assert result.covariance[0, 0] == factor_variance
