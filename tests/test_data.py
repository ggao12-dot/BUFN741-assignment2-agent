import numpy as np
import pandas as pd
import pytest
from src.data_download import load_data, parse_fama_french, check_cache, write_manifest
from src.process_returns import monthly_returns
from src.sample_manager import make_samples, select_sim_common_sample
from src.validation import ValidationError
from conftest import PROJECT, make_zip


def test_offline_cache_and_returns(offline_fixture, returns, monkeypatch):
    config, _, _, _, _ = offline_fixture
    def no_network(*args, **kwargs):
        pytest.fail('Offline mode attempted network')
    monkeypatch.setattr('requests.Session.get', no_network)
    import yfinance
    monkeypatch.setattr(yfinance, 'download', no_network)
    prices, rf, _ = load_data(config, PROJECT)
    _, actual = monthly_returns(prices, '2026-08')
    np.testing.assert_allclose(actual.to_numpy(), returns.to_numpy(), atol=1e-14)
    assert actual.index[0] == pd.Period('2006-05')
    assert actual.index[-1] == pd.Period('2026-08')
    samples = make_samples(actual, config['samples'])
    assert samples['pre_covid'].index[-1] == pd.Period('2019-12')
    assert samples['post_covid'].index[0] == pd.Period('2020-01')
    assert len(samples['full']) == len(samples['pre_covid']) + len(samples['post_covid'])
    assert rf.index.equals(actual.index)


def test_first_common_month_is_derived(offline_fixture):
    _, prices, _, _, _ = offline_fixture
    prices.iloc[:7, -1] = np.nan
    _, actual = monthly_returns(prices, '2026-08')
    assert actual.index[0] == prices.index[8].to_period('M')


@pytest.mark.parametrize('kind', ['missing_price', 'missing_month', 'partial_final_month', 'duplicate', 'negative'])
def test_bad_prices_fail(offline_fixture, kind):
    _, prices, _, _, _ = offline_fixture
    prices = prices.copy()
    if kind == 'missing_price':
        prices.iloc[20, 0] = np.nan
    elif kind == 'missing_month':
        prices = prices.drop(prices.index[20])
    elif kind == 'partial_final_month':
        prices.index = prices.index[:-1].append(pd.DatetimeIndex([prices.index[-1] - pd.Timedelta(days=3)]))
    elif kind == 'duplicate':
        prices = pd.concat([prices, prices.iloc[[-1]]])
    else:
        prices.iloc[10, 0] = -1
    with pytest.raises(ValidationError):
        monthly_returns(prices, '2026-08')


def test_cache_corruption_fails_offline(offline_fixture):
    config, _, _, yahoo, _ = offline_fixture
    yahoo.write_text(yahoo.read_text() + '\n')
    with pytest.raises(ValidationError, match='checksum'):
        load_data(config, PROJECT)


def test_load_data_preserves_trailing_ff_endpoint(offline_fixture):
    config, _, rf, _, ff = offline_fixture
    ff.write_bytes(make_zip(rf.iloc[:-1]))
    write_manifest(ff, 'synthetic truncated fixture')
    _, loaded_rf, _ = load_data(config, PROJECT)
    assert loaded_rf.index[-1] == pd.Period('2026-07')


@pytest.mark.parametrize('lag', [1, 2])
def test_allowed_trailing_rf_lag_uses_common_intersection(returns, lag):
    rf = pd.Series(.003, index=returns.index[:-lag], name='RF')
    selection = select_sim_common_sample(returns, rf, True, 2)
    assert selection.trailing_rf_lag_months == lag
    assert selection.lag_accepted
    assert selection.returns.index.equals(returns.index[:-lag])
    assert selection.risk_free.index.equals(returns.index[:-lag])
    assert selection.metadata['sim_common']['N'] == len(returns) - lag
    assert selection.metadata['markowitz_comparison'] == selection.metadata['sim_common']


def test_trailing_rf_lag_above_tolerance_fails(returns):
    rf = pd.Series(.003, index=returns.index[:-3], name='RF')
    with pytest.raises(ValidationError, match='trails ETF returns by 3 months'):
        select_sim_common_sample(returns, rf, True, 2)


def test_internal_rf_gap_is_fatal(returns):
    rf = pd.Series(.003, index=returns.index.delete(50), name='RF')
    with pytest.raises(ValidationError, match='Internal Fama-French RF gaps'):
        select_sim_common_sample(returns, rf, True, 2)


def test_trailing_lag_must_be_explicitly_allowed(returns):
    rf = pd.Series(.003, index=returns.index[:-1], name='RF')
    with pytest.raises(ValidationError, match='allowed=False'):
        select_sim_common_sample(returns, rf, False, 2)


def test_ff_parser_percent_conversion_and_annual_exclusion():
    rf = pd.Series([.003, .004], index=pd.period_range('2026-07', periods=2, freq='M'))
    parsed = parse_fama_french(make_zip(rf))
    np.testing.assert_allclose(parsed, rf)
    assert len(parsed) == 2


def test_corrupted_ff_is_validation_failure_not_external_block(offline_fixture):
    from src.data_download import load_fama_french
    from src.validation import ExternalDataUnavailable
    config, _, _, _, ff = offline_fixture
    ff.write_bytes(ff.read_bytes() + b'corrupted')
    with pytest.raises(ValidationError, match='checksum') as exc:
        load_fama_french(config, PROJECT)
    assert not isinstance(exc.value, ExternalDataUnavailable)
