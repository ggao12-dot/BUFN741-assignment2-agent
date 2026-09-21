"""Auditable raw downloads, checksummed caches, and strictly offline reuse."""
from __future__ import annotations
import hashlib
import fcntl
import io
import json
import logging
import re
import shutil
import time
import zipfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
import requests
from src.validation import require, ValidationError, ExternalDataUnavailable
from src.process_returns import monthly_returns

LOG = logging.getLogger(__name__)
FF_URL = 'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_CSV.zip'


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cache_paths(config: dict, root: Path) -> tuple[Path, Path]:
    settings = dict(tickers=config['assets']['tickers'], start=config['data']['start_date'],
                    end=config['data']['end_month'], field='Adj Close', interval='1d', version=1)
    key = hashlib.sha256(json.dumps(settings, sort_keys=True).encode()).hexdigest()[:16]
    raw = root / config['data']['raw_dir']
    return raw / f'yahoo_{key}.csv', raw / 'F-F_Research_Data_Factors_CSV.zip'


def write_manifest(path: Path, source: str, **extra: object) -> None:
    manifest = dict(source=source, sha256=sha256(path),
                    retrieved_at=datetime.now(timezone.utc).isoformat(), **extra)
    path.with_suffix(path.suffix + '.json').write_text(json.dumps(manifest, indent=2))


def check_cache(path: Path) -> dict:
    metadata = json.loads(path.with_suffix(path.suffix + '.json').read_text())
    require(metadata['sha256'] == sha256(path), f'Cache checksum mismatch: {path}')
    return metadata


def read_prices(path: Path, tickers: list[str]) -> pd.DataFrame:
    raw = pd.read_csv(path, header=[0, 1], index_col=0, parse_dates=True)
    require('Adj Close' in raw.columns.get_level_values(0), 'Yahoo Adj Close missing')
    prices = raw['Adj Close'].reindex(columns=tickers)
    prices.index = pd.DatetimeIndex(prices.index).tz_localize(None).normalize()
    return prices


def parse_fama_french(payload: bytes) -> pd.Series:
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        names = [name for name in archive.namelist() if name.lower().endswith('.csv')]
        require(len(names) == 1, 'Unexpected Fama-French ZIP contents')
        lines = archive.read(names[0]).decode('utf-8-sig').splitlines()
    rows = [line.strip().split(',') for line in lines if re.match(r'^\s*\d{6}\s*,', line)]
    require(bool(rows) and all(len(row) == 5 for row in rows), 'Invalid monthly FF rows')
    index = pd.PeriodIndex([f'{r[0].strip()[:4]}-{r[0].strip()[4:]}' for r in rows], freq='M')
    result = pd.Series([float(r[4]) / 100 for r in rows], index=index, name='RF')
    require(result.index.is_unique and result.index.is_monotonic_increasing, 'Invalid FF month index')
    require(result.notna().all() and result.abs().lt(1).all(), 'Invalid FF risk-free observations')
    return result


def load_data(config: dict, root: Path, snapshot_dir: Path | None = None) -> tuple[pd.DataFrame, pd.Series, list[Path]]:
    """Load both independent sources without imposing a shared endpoint policy."""
    return (load_yahoo_prices(config, root, snapshot_dir), load_fama_french(config, root, snapshot_dir),
            list(cache_paths(config, root)))


@contextmanager
def _cache_snapshot(config: dict, root: Path, snapshot_dir: Path | None, source_index: int):
    """Serialize cache updates and snapshot only the source requested by this stage."""
    yahoo, ff = cache_paths(config, root)
    yahoo.parent.mkdir(parents=True, exist_ok=True)
    with (yahoo.parent / '.download.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            yield
        finally:
            # Preserve available raw evidence even when final-month validation fails.
            if snapshot_dir is not None:
                snapshot_dir.mkdir(parents=True, exist_ok=True)
                for source in [(yahoo, ff)[source_index]]:
                    for path in [source, source.with_suffix(source.suffix + '.json')]:
                        if path.exists():
                            shutil.copy2(path, snapshot_dir / path.name)
            fcntl.flock(lock, fcntl.LOCK_UN)


def load_yahoo_prices(config: dict, root: Path, snapshot_dir: Path | None = None) -> pd.DataFrame:
    with _cache_snapshot(config, root, snapshot_dir, 0):
        return _load_prices(config, root)


def load_fama_french(config: dict, root: Path, snapshot_dir: Path | None = None) -> pd.Series:
    with _cache_snapshot(config, root, snapshot_dir, 1):
        return _load_fama_french(config, root)


def _load_prices(config: dict, root: Path) -> pd.DataFrame:
    yahoo_path, ff_path = cache_paths(config, root)
    yahoo_path.parent.mkdir(parents=True, exist_ok=True)
    options = config['data']
    offline, cache = options.get('offline', False), options.get('cache', True)
    tickers = config['assets']['tickers']
    prices = None
    if cache or offline:
        try:
            check_cache(yahoo_path)
            prices = read_prices(yahoo_path, tickers)
            monthly_returns(prices, options['end_month'])
            LOG.info('Reusing validated Yahoo cache %s', yahoo_path)
        except (OSError, ValueError, KeyError) as exc:
            if offline:
                raise ValidationError(f'Offline Yahoo cache unavailable/invalid: {exc}') from exc
            LOG.info('Yahoo cache unavailable/invalid: %s', exc)
            prices = None
    if prices is None:
        import yfinance as yf
        yf.set_tz_cache_location(str(yahoo_path.parent / '.yfinance'))
        end = (pd.Period(options['end_month'], freq='M') + 1).start_time.strftime('%Y-%m-%d')
        for attempt in range(3):
            raw = yf.download(tickers, start=options['start_date'], end=end, interval='1d',
                              auto_adjust=False, actions=True, progress=False, threads=False,
                              timeout=30, group_by='column', multi_level_index=True)
            if raw is not None and not raw.empty:
                # Preserve returned OHLC, adjusted closes, volume and corporate actions.
                temp = yahoo_path.with_suffix('.download.csv')
                raw.to_csv(temp)
                candidate = read_prices(temp, tickers)
                monthly_returns(candidate, options['end_month'])
                temp.replace(yahoo_path)
                write_manifest(yahoo_path, 'Yahoo Finance via yfinance', tickers=tickers,
                               start=options['start_date'], end_exclusive=end,
                               yfinance_version=yf.__version__, auto_adjust=False)
                prices = candidate
                break
            if attempt < 2:
                time.sleep(2 ** attempt)
        require(prices is not None, 'Yahoo download returned no usable adjusted-price data')
    return prices


def _load_fama_french(config: dict, root: Path) -> pd.Series:
    _, ff_path = cache_paths(config, root)
    options = config['data']
    offline, cache = options.get('offline', False), options.get('cache', True)
    rf = None
    if cache or offline:
        try:
            check_cache(ff_path)
            rf = parse_fama_french(ff_path.read_bytes())
        except FileNotFoundError as exc:
            if offline:
                raise ExternalDataUnavailable(f'Offline Fama-French cache unavailable: {exc}') from exc
            LOG.info('Fama-French cache unavailable: %s', exc)
            rf = None
        if rf is not None:
            LOG.info('Reusing validated Fama-French cache %s ending %s', ff_path, rf.index[-1])
    if rf is None:
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        try:
            with requests.Session() as session:
                session.mount('https://', HTTPAdapter(max_retries=Retry(total=3, backoff_factor=1)))
                response = session.get(FF_URL, timeout=(15, 60))
                response.raise_for_status()
        except requests.RequestException as exc:
            raise ExternalDataUnavailable(f'Fama-French source unavailable: {exc}') from exc
        rf = parse_fama_french(response.content)
        temp = ff_path.with_suffix('.download.zip')
        temp.write_bytes(response.content)
        temp.replace(ff_path)
        write_manifest(ff_path, FF_URL, last_month=str(rf.index[-1]), units='percent in raw; decimal parsed')
    return rf
