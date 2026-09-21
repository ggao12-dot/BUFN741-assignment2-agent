"""Month-end adjusted closes, no forward filling, common monthly observations."""
from __future__ import annotations
import pandas as pd
import numpy as np
import pandas_market_calendars as mcal
from src.validation import require, validate_returns


def monthly_returns(prices: pd.DataFrame, end_month: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    require(isinstance(prices.index, pd.DatetimeIndex), 'Prices require a DatetimeIndex')
    require(prices.index.is_unique and prices.columns.is_unique, 'Duplicate price dates/assets')
    require(prices.index.is_monotonic_increasing and len(prices) > 0, 'Empty or unsorted prices')
    observed = prices.to_numpy()[~pd.isna(prices.to_numpy())]
    require(np.isfinite(observed).all() and (observed > 0).all(), 'Invalid adjusted prices')
    end = pd.Period(end_month, freq='M')
    prices = prices.loc[:end.end_time].copy()
    require(len(prices) > 0, 'No prices through requested end month')
    # Exact scheduled closing session prevents stale month-end prices and partial months.
    sessions = mcal.get_calendar('NYSE').schedule(
        start_date=prices.index[0].to_period('M').start_time.date(),
        end_date=end.end_time.date()).index
    closing_sessions = pd.Series(sessions, index=sessions.to_period('M')).groupby(level=0).last()
    monthly = prices.reindex(pd.DatetimeIndex(closing_sessions.to_numpy()))
    monthly.index = closing_sessions.index
    monthly.index.name = 'month'
    returns = monthly.pct_change(fill_method=None)
    common = returns.dropna(how='any')
    require(not common.empty, 'No common monthly returns')
    # Leading inception gaps are expected; internal gaps are failures, not dropped months.
    aligned = returns.loc[common.index[0]:end]
    validate_returns(aligned)
    require(aligned.index[-1] == end, f'Missing required final month {end}')
    return monthly, aligned
