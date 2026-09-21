from __future__ import annotations
import copy
import io
from pathlib import Path
import zipfile
import numpy as np
import pandas as pd
import pandas_market_calendars as mcal
import pytest
import yaml
from src.benchmark_portfolios import ASSETS
from src.data_download import cache_paths, write_manifest

PROJECT = Path(__file__).resolve().parents[1]


@pytest.fixture
def config():
    return yaml.safe_load((PROJECT / 'config' / 'assignment2.yaml').read_text())


@pytest.fixture(scope='session')
def returns():
    rng = np.random.default_rng(741)
    index = pd.period_range('2006-05', '2026-08', freq='M')
    market = rng.normal(0, .045, len(index))
    market -= market.mean()
    beta = np.array([1, .9, 1.2, -.1, .1, .2, .6, .45])
    residuals = rng.normal(size=(len(index), 8)) * [.0, .025, .035, .022, .012, .04, .07, .04]
    residuals -= residuals.mean(axis=0)
    means = np.array([.012, .011, .013, .006, .0055, .008, .009, .009])
    return pd.DataFrame(means + np.outer(market, beta) + residuals, index=index, columns=ASSETS)


def make_zip(rf: pd.Series) -> bytes:
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w') as archive:
        lines = ['Synthetic test fixture, NEVER real market data', ',Mkt-RF,SMB,HML,RF']
        lines.extend(f'{p.year}{p.month:02d},1.0,0.0,0.0,{v * 100:.12g}' for p, v in rf.items())
        lines += ['', ' Annual Factors: January-December', '2025,1,2,3,4']
        archive.writestr('F-F_Research_Data_Factors.csv', '\n'.join(lines))
    return stream.getvalue()


@pytest.fixture
def offline_fixture(tmp_path, config, returns):
    config = copy.deepcopy(config)
    config['data']['raw_dir'] = str(tmp_path / 'raw')
    config['data']['offline'] = True
    config['outputs']['root'] = str(tmp_path / 'runs')
    index = pd.period_range(returns.index[0] - 1, returns.index[-1], freq='M')
    sessions = mcal.get_calendar('NYSE').schedule(index[0].start_time.date(), index[-1].end_time.date()).index
    last = pd.Series(sessions, index=sessions.to_period('M')).groupby(level=0).last()
    values = np.vstack([np.ones(8), np.cumprod(1 + returns.to_numpy(), axis=0)]) * 100
    prices = pd.DataFrame(values, index=pd.DatetimeIndex(last.to_numpy()), columns=ASSETS)
    raw = pd.concat({'Adj Close': prices, 'Close': prices}, axis=1)
    yahoo, ff = cache_paths(config, PROJECT)
    yahoo.parent.mkdir(parents=True)
    raw.to_csv(yahoo)
    write_manifest(yahoo, 'SYNTHETIC PYTEST FIXTURE — NOT YAHOO DATA')
    rf = pd.Series(.003 + .0004 * np.sin(np.arange(len(returns)) / 8), index=returns.index)
    ff.write_bytes(make_zip(rf))
    write_manifest(ff, 'SYNTHETIC PYTEST FIXTURE — NOT FAMA-FRENCH DATA')
    return config, prices, rf, yahoo, ff
