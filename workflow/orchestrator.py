"""Ordered fail-closed assignment workflow; numerical outputs precede all plots."""
from __future__ import annotations
import importlib.metadata
import json
import logging
from pathlib import Path
import platform
import sys
import numpy as np
import pandas as pd
from src.benchmark_portfolios import ASSETS, benchmark_table
from src.comparison import compare_models
from src.data_download import load_yahoo_prices, load_fama_french, sha256
from src.diagnostics import largest_pairs, result_diagnostics, sample_changes, weight_stability
from src.estimate_moments import estimate_moments, monthly_rate, portfolio_metrics
from src.generate_tables import save_result, write_json, json_safe
from src.final_report import write_final_assignment_report, validate_final_assignment_report
from src.interpretation import (validate_model_comparison_report, validate_sim_report,
                                write_interpretation, write_markowitz_report,
                                write_model_comparison_report, write_sim_report)
from src.markowitz import run_markowitz
from src.portfolio_optimizer import ConstraintSpec, analyze
from src.process_returns import monthly_returns
from src.sample_manager import make_samples, sample_metadata, select_sim_common_sample
from src.single_index import fit_single_index
from src.validation import require, validate_weights, validate_covariance, ValidationError, ExternalDataUnavailable
from workflow.state_manager import RunState

LOG = logging.getLogger(__name__)


def git_commit(project_root: Path) -> str | None:
    """Read the current commit without invoking Git; return None for an unborn repository."""
    head = project_root / '.git' / 'HEAD'
    if not head.is_file():
        return None
    value = head.read_text().strip()
    if value.startswith('ref: '):
        ref = project_root / '.git' / value[5:]
        return ref.read_text().strip() if ref.is_file() else None
    return value or None


def validate_config(config: dict) -> None:
    tickers = config['assets']['tickers']
    require(len(tickers) == 8 and set(tickers) == set(ASSETS), 'Exactly the eight assignment assets are required')
    require(config['data']['provider'] == 'yahoo' and config['data']['price_field'] == 'Adj Close',
            'Assignment requires Yahoo adjusted prices')
    require(config['data']['frequency'] == 'monthly' and config['data']['common_sample'], 'Common monthly sample required')
    require(config['data']['end_month'] == '2026-08', 'Assignment requires final month August 2026')
    require(pd.Timestamp(config['data']['start_date']) < pd.Timestamp('2000-01-01'),
            'Download history must begin before all assignment ETF inception dates')
    require(config['samples']['full'] == {'start': 'common', 'end': '2026-08'}, 'Invalid full sample')
    require(config['samples']['pre_covid'] == {'start': 'common', 'end': '2019-12'}, 'Invalid pre-COVID sample')
    require(config['samples']['post_covid'] == {'start': '2020-01', 'end': '2026-08'}, 'Invalid post-COVID sample')
    require(set(config['constraints']) == {'A', 'B', 'C'}, 'Specifications A/B/C are required')
    for name, kind in [('A', 'unrestricted'), ('B', 'long_only'), ('C', 'bounded')]:
        require(config['constraints'][name]['type'] == kind, f'Invalid specification {name}')
        ConstraintSpec.from_config(config['constraints'][name]).bounds(8)
    require(config['subsample_analysis']['constraint'] in config['constraints'], 'Unknown subsample constraint')
    require(config.get('diversification', {}).get('constraint', 'B') in config['constraints'], 'Unknown diversification constraint')
    require(isinstance(config['sim'].get('allow_trailing_rf_lag'), bool),
            'sim.allow_trailing_rf_lag must be boolean')
    require(isinstance(config['sim'].get('max_trailing_rf_lag_months'), int) and
            config['sim']['max_trailing_rf_lag_months'] >= 0,
            'sim.max_trailing_rf_lag_months must be a nonnegative integer')
    require(config['outputs']['save_csv'] and config['outputs']['save_json'], 'CSV and JSON are required audit outputs')
    require(config['frontier']['points'] >= 20 and config['frontier']['target_range_padding'] >= 0, 'Invalid frontier settings')
    for key in ['constraint_tolerance', 'psd_tolerance', 'crosscheck_weight_tolerance', 'frontier_sharpe_tolerance',
                'tangency_existence_tolerance', 'dominance_sd_tolerance']:
        if key in config['optimization']:
            require(np.isfinite(config['optimization'][key]) and config['optimization'][key] > 0,
                    f'Invalid optimization tolerance {key}')


def reconcile_table(path: Path, expected: pd.DataFrame) -> pd.DataFrame:
    """Compare serialized values/labels/order with accepted authoritative results."""
    actual = pd.read_csv(path, float_precision='round_trip')
    expected = expected.reset_index(drop=True).copy()
    # CSV empty strings and missing fields both deserialize as NaN.
    for column in expected:
        expected[column] = expected[column].mask(expected[column].isna() | expected[column].eq(''), np.nan)
    try:
        pd.testing.assert_frame_equal(actual, expected, check_dtype=False,
                                      check_exact=False, atol=1e-12, rtol=1e-12)
    except AssertionError as exc:
        raise ValidationError(f'{path.name}: persisted output differs from authoritative result: {exc}') from exc
    return actual


def reconcile_json(path: Path, expected: dict) -> None:
    require(json.loads(path.read_text()) == json_safe(expected),
            f'{path.name}: persisted JSON differs from authoritative result')


def validate_saved_sim(root: Path, sim) -> None:
    """Reconcile every persisted input consumed by the SIM-only report."""
    regressions = pd.read_csv(root / 'models' / 'sim_regressions.csv', index_col='asset',
                              float_precision='round_trip')
    try:
        pd.testing.assert_frame_equal(regressions, sim.regressions, check_dtype=False,
                                      check_exact=False, atol=1e-12, rtol=1e-12)
    except AssertionError as exc:
        raise ValidationError(f'sim_regressions.csv differs from authoritative SIM result: {exc}') from exc
    residuals = pd.read_csv(root / 'models' / 'sim_residuals.csv', index_col=0,
                            float_precision='round_trip')
    require(residuals.columns.tolist() == sim.residuals.columns.tolist() and
            residuals.index.tolist() == sim.residuals.index.astype(str).tolist() and
            np.allclose(residuals.to_numpy(), sim.residuals.to_numpy(), atol=1e-12, rtol=1e-12),
            'sim_residuals.csv differs from authoritative SIM result')
    reconcile_json(root / 'models' / 'sim_assumptions.json', sim.assumptions)


def validate_saved_descriptive_diagnostics(root: Path, samples: dict, changes: dict,
                                           stability: pd.DataFrame) -> None:
    """Reconcile persisted descriptive inputs cited by the final report."""
    full_correlation = pd.read_csv(root / 'models' / 'full_sample_correlation.csv', index_col=0,
                                   float_precision='round_trip')
    try:
        pd.testing.assert_frame_equal(full_correlation, samples['full'].corr(), check_dtype=False,
                                      check_names=False, check_exact=False, atol=1e-12, rtol=1e-12)
    except AssertionError as exc:
        raise ValidationError(f'full_sample_correlation.csv differs from authoritative sample: {exc}') from exc
    reconcile_table(root / 'diagnostics' / 'full_correlations.csv',
                    largest_pairs(samples['full'].corr(), 'correlation', 28))
    for name in ['covariance_changes', 'correlation_changes', 'variance_changes']:
        reconcile_table(root / 'diagnostics' / f'{name}.csv', changes[name])
    reconcile_table(root / 'diagnostics' / 'pre_post_weight_stability.csv', stability)


def validate_saved_results(root: Path, results: dict, specifications: dict, config: dict, rf: float,
                           benchmarks: dict | None = None, summary: dict | None = None,
                           extra_tables: dict | None = None) -> None:
    for name, result in results.items():
        lower, upper = specifications[name].bounds(len(result.assets))
        moments = np.load(root / 'models' / f'{name}_moments.npz')
        require(np.array_equal(moments['mean'], result.mean) and np.array_equal(moments['covariance'], result.covariance),
                f'{name}: saved moments differ')
        require(moments['assets'].tolist() == result.assets, f'{name}: saved asset order differs')
        validate_covariance(moments['covariance'])
        for suffix in ['portfolios', 'frontier']:
            frame = pd.read_csv(root / 'tables' / f'{name}_{suffix}.csv', float_precision='round_trip')
            if suffix == 'frontier':
                require(frame.solver_status.eq('optimal').all(), 'Failed solver point in saved frontier')
            reconcile_table(root / 'tables' / f'{name}_{suffix}.csv', getattr(result, suffix))
            require(len(frame) == len(getattr(result, suffix)), f'{name}: output row count mismatch')
            for _, row in frame.iterrows():
                weights = row[[f'w_{a}' for a in result.assets]].to_numpy(dtype=float)
                validate_weights(weights, lower, upper, config['optimization']['constraint_tolerance'],
                                 result.mean, row.target_monthly if suffix == 'frontier' else None)
                if suffix == 'frontier':
                    require(row.solver_status == 'optimal', 'Failed solver point in saved frontier')
                for key, value in portfolio_metrics(weights, result.mean, result.covariance, rf).items():
                    require(np.isclose(row[key], value, atol=1e-10, rtol=1e-9), f'{name}: saved metric {key} mismatch')
        branch = reconcile_table(root / 'tables' / f'{name}_efficient_frontier.csv',
                                 result.frontier.loc[result.frontier.efficient])
        require(branch.efficient.all(), f'{name}: invalid efficient branch')
        cal = reconcile_table(root / 'tables' / f'{name}_cal.csv', result.cal)
        reconcile_json(root / 'models' / f'{name}_tangency.json', result.tangency.to_dict())
        if result.tangency.status == 'NONATTAINED':
            require(cal.empty and result.tangency.weights is None and
                    'tangency' not in result.portfolios.portfolio.values,
                    'NONATTAINED tangency must have no finite weights or CAL')
        else:
            require(result.tangency.status == 'ATTAINED', 'Unknown tangency status')
            tangent = portfolio_metrics(result.tangency.weights, result.mean, result.covariance, rf)
            require(np.isfinite(cal.to_numpy()).all(), 'Non-finite CAL')
            allocation = cal.risky_allocation.to_numpy()
            expected = dict(cash_allocation=1 - allocation,
                            mean_monthly=rf + allocation * (tangent['mean_monthly'] - rf),
                            sd_monthly=np.abs(allocation) * tangent['sd_monthly'])
            expected.update(mean_annual=12 * expected['mean_monthly'], sd_annual=np.sqrt(12) * expected['sd_monthly'])
            for key, values in expected.items():
                require(np.allclose(cal[key], values, atol=1e-10, rtol=1e-9), f'{name}: invalid CAL {key}')
    for name, expected in (benchmarks or {}).items():
        frame = reconcile_table(root / 'tables' / f'{name}_benchmarks.csv', expected)
        result = results[name]
        for _, row in frame.iterrows():
            weights = row[[f'w_{a}' for a in result.assets]].to_numpy(dtype=float)
            lower, upper = ConstraintSpec.from_config(config['constraints'][row.specification]).bounds(len(weights))
            # Budget is always mandatory; feasibility is assessed separately for each specification.
            validate_weights(weights, np.full(len(weights), -np.inf), np.full(len(weights), np.inf),
                             config['optimization']['constraint_tolerance'])
            try:
                validate_weights(weights, lower, upper, config['optimization']['constraint_tolerance'])
                feasible = True
            except ValidationError:
                feasible = False
            require(bool(row.feasible) == feasible, f'{name}: benchmark feasibility mismatch')
            for key, value in portfolio_metrics(weights, result.mean, result.covariance, rf).items():
                require(np.isclose(row[key], value, atol=1e-10, rtol=1e-9), f'{name}: benchmark {key} mismatch')
    for filename, expected in (extra_tables or {}).items():
        reconcile_table(root / 'tables' / filename, expected)
    if summary is not None:
        # Reconcile portfolio sections to the actual accepted calculations as well as the JSON bytes.
        require(json_safe(summary['results']) == json_safe({name: result.portfolios.to_dict(orient='records')
                for name, result in results.items()}), 'Authoritative summary portfolio mismatch')
        require(json_safe(summary['tangencies']) == json_safe({name: result.tangency.to_dict()
                for name, result in results.items()}), 'Authoritative summary tangency mismatch')
        if benchmarks is not None:
            require(json_safe(summary['benchmarks']) == json_safe({name: table.to_dict(orient='records')
                    for name, table in benchmarks.items()}), 'Authoritative summary benchmark mismatch')
        reconcile_json(root / 'results_summary.json', summary)


def run_assignment(config: dict, project_root: Path, resume: str | None = None) -> Path:
    state = RunState(project_root / config['outputs'].get('root', 'runs'), config, resume)
    root = state.path
    handlers = [logging.FileHandler(root / 'logs' / 'run.log'), logging.StreamHandler(sys.stderr)]
    logger = logging.getLogger()
    old_level = logger.level
    logger.setLevel(logging.INFO)
    for handler in handlers:
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s'))
        logger.addHandler(handler)
    try:
        LOG.info('Run %s, attempt %s', state.state['run_id'], state.state['attempt'])
        with state.stage('configuration'):
            validate_config(config)
            rf = monthly_rate(config['risk_free']['annual_rate'], config['risk_free']['monthly_conversion'])
            specs = {k: ConstraintSpec.from_config(v) for k, v in config['constraints'].items()}
            provenance = dict(python=platform.python_version(), platform=platform.platform(),
                              git_commit=git_commit(project_root),
                              packages={p: importlib.metadata.version(p) for p in [
                                  'numpy', 'pandas', 'scipy', 'cvxpy', 'clarabel', 'statsmodels',
                                  'yfinance', 'matplotlib', 'pandas_market_calendars']},
                              source_sha256={str(p.relative_to(project_root)): sha256(p)
                                             for folder in ['src', 'workflow']
                                             for p in sorted((project_root / folder).glob('*.py'))})
            write_json(root / 'diagnostics' / 'environment.json', provenance)
        with state.stage('yahoo_data'):
            prices = load_yahoo_prices(config, project_root, root / 'data' / 'raw')
        with state.stage('input_validation'):
            monthly_prices, returns = monthly_returns(prices, config['data']['end_month'])
            samples = make_samples(returns, config['samples'])
            for name, sample in samples.items():
                LOG.info('%s sample: %s', name, sample_metadata(sample))
                sample.to_csv(root / 'data' / f'returns_{name}.csv', float_format='%.17g')
            monthly_prices.to_csv(root / 'data' / 'adjusted_monthly_prices.csv', float_format='%.17g')
        with state.stage('markowitz_full'):
            results, result_specs, result_samples = {}, {}, {}
            full = samples['full']
            mean, cov = estimate_moments(full)
            for label, spec in specs.items():
                name = f'markowitz_full_{label}'
                LOG.info('Optimizing %s', name)
                results[name] = analyze(mean, cov, list(full.columns), rf, spec, config['frontier'], config['optimization'])
                result_specs[name] = spec
                result_samples[name] = sample_metadata(full)
        with state.stage('markowitz_subsamples'):
            sub_label = config['subsample_analysis']['constraint']
            for sample in ['pre_covid', 'post_covid']:
                name = f'markowitz_{sample}_{sub_label}'
                LOG.info('Optimizing %s', name)
                results[name] = run_markowitz(samples[sample], rf, specs[sub_label],
                                              config['frontier'], config['optimization'])
                result_specs[name] = specs[sub_label]
                result_samples[name] = sample_metadata(samples[sample])
        with state.stage('diversification'):
            diversification = []
            div_label = config.get('diversification', {}).get('constraint', 'B')
            for universe, assets in [('equities', ASSETS[:3]), ('equities_bonds', ASSETS[:5]),
                                     ('equities_bonds_gold', ASSETS[:6]), ('all_assets', ASSETS)]:
                try:
                    specs[div_label].bounds(len(assets))
                except ValidationError as exc:
                    diversification.append(dict(universe=universe, specification=div_label, status='SKIPPED', reason=str(exc)))
                    continue
                name = f'diversification_{universe}_{div_label}'
                results[name] = run_markowitz(full[assets], rf, specs[div_label],
                                              config['frontier'], config['optimization'])
                result_specs[name] = specs[div_label]
                result_samples[name] = sample_metadata(full[assets])
                table = results[name].portfolios.set_index('portfolio')
                diversification.append(dict(universe=universe, specification=div_label, status='PASSED', reason='',
                                            gmv_sd_annual=table.loc['GMV', 'sd_annual'],
                                            tangency_status=results[name].tangency.status,
                                            tangency_sharpe_annual=None if 'tangency' not in table.index else
                                            table.loc['tangency', 'sharpe_annual'],
                                            sharpe_supremum_annual=results[name].tangency.to_dict()['sharpe_supremum_annual'],
                                            **sample_metadata(full[assets])))
        sim, comparisons = None, {}
        with state.stage('ff_data', allow_external_block=True):
            ff_rf = load_fama_french(config, project_root, root / 'data' / 'raw')
            sim_selection = select_sim_common_sample(
                full, ff_rf,
                config['sim']['allow_trailing_rf_lag'],
                config['sim']['max_trailing_rf_lag_months'])
            sim_returns, sim_rf = sim_selection.returns, sim_selection.risk_free
            ff_stage = state.state['stages']['ff_data']
            ff_stage.update(trailing_rf_lag_months=sim_selection.trailing_rf_lag_months,
                            lag_accepted=sim_selection.lag_accepted,
                            sim_common_start=str(sim_returns.index[0]),
                            sim_common_end=str(sim_returns.index[-1]),
                            sim_common_N=len(sim_returns))
            if sim_selection.trailing_rf_lag_months:
                warning = (f'Accepted trailing Fama-French RF lag of '
                           f'{sim_selection.trailing_rf_lag_months} month(s); SIM and direct model comparisons '
                           f'use {sim_returns.index[0]} through {sim_returns.index[-1]} (N={len(sim_returns)}).')
                ff_stage['warning'] = warning
                LOG.warning(warning)
            ff_rf.to_csv(root / 'data' / 'fama_french_rf_available.csv', float_format='%.17g')
            sim_rf.to_csv(root / 'data' / 'regression_rf_sim_common.csv', float_format='%.17g')
            sim_returns.to_csv(root / 'data' / 'returns_sim_common.csv', float_format='%.17g')
            sim_returns.to_csv(root / 'data' / 'returns_markowitz_comparison.csv', float_format='%.17g')
        sim_ready = state.state['stages']['ff_data']['status'] == 'PASSED'
        if sim_ready:
            with state.stage('sim'):
                comparison_mean, comparison_cov = estimate_moments(sim_returns)
                sim = fit_single_index(sim_returns, sim_rf, config['sim'])
                for label, spec in specs.items():
                    comparison_name = f'markowitz_comparison_{label}'
                    LOG.info('Optimizing %s', comparison_name)
                    results[comparison_name] = analyze(
                        comparison_mean, comparison_cov, list(sim_returns.columns), rf, spec,
                        config['frontier'], config['optimization'])
                    result_specs[comparison_name] = spec
                    result_samples[comparison_name] = sample_metadata(sim_returns)
                    for prefix, model_mean in [('sim_covariance_only', comparison_mean.copy()),
                                               ('sim_complete', sim.means)]:
                        name = f'{prefix}_{label}'
                        LOG.info('Optimizing %s', name)
                        results[name] = analyze(model_mean, sim.covariance, list(sim_returns.columns), rf, spec,
                                                config['frontier'], config['optimization'])
                        result_specs[name] = spec
                        result_samples[name] = sample_metadata(sim_returns)
            with state.stage('comparisons'):
                for label in specs:
                    for comparison, sim_prefix in [('covariance_only', 'sim_covariance_only'), ('complete_model', 'sim_complete')]:
                        name = f'{comparison}_{label}'
                        comparisons[name] = compare_models(results[f'markowitz_comparison_{label}'], results[f'{sim_prefix}_{label}'],
                                                           comparison == 'covariance_only', rf, specs[label], config['optimization'])
                        comparisons[name]['weight_stability'] = weight_stability(
                            results[f'markowitz_comparison_{label}'], results[f'{sim_prefix}_{label}'])
        else:
            LOG.warning('SIM blocked: %s', state.state['stages']['ff_data']['reason'])
            state.block_dependency('sim', 'ff_data')
            state.block_dependency('comparisons', 'sim')
            state.block_dependency('report', 'comparisons')
        with state.stage('numerical_outputs'):
            benchmark_tables, diagnostics, extra_tables = {}, {}, {}
            for name, result in results.items():
                diagnostics[name] = result_diagnostics(result, result_specs[name], config['optimization']['constraint_tolerance'])
                if not name.startswith('diversification'):
                    benchmark_tables[name] = benchmark_table(result.assets, result.mean, result.covariance, rf,
                                                             config['constraints'], config['optimization']['constraint_tolerance'])
            changes = sample_changes(samples['pre_covid'], samples['post_covid'])
            stability = weight_stability(results[f'markowitz_pre_covid_{sub_label}'], results[f'markowitz_post_covid_{sub_label}'])
            for name, result in results.items():
                save_result(root, name, result)
                write_json(root / 'diagnostics' / f'{name}_diagnostics.json', diagnostics[name])
            for name, table in benchmark_tables.items():
                table.to_csv(root / 'tables' / f'{name}_benchmarks.csv', index=False)
            for name, tables in comparisons.items():
                for suffix, table in tables.items():
                    table.to_csv(root / 'tables' / f'comparison_{name}_{suffix}.csv', index=False)
                    extra_tables[f'comparison_{name}_{suffix}.csv'] = table
            for name, table in changes.items():
                table.to_csv(root / 'diagnostics' / f'{name}.csv', index=name.endswith('matrix'))
            for name, sample in samples.items():
                largest_pairs(sample.corr(), 'correlation', 28).to_csv(root / 'diagnostics' / f'{name}_correlations.csv', index=False)
                sample.cov().to_csv(root / 'models' / f'{name}_sample_covariance_monthly.csv')
                sample.corr().to_csv(root / 'models' / f'{name}_sample_correlation.csv')
                asset_statistics = pd.DataFrame(dict(mean_monthly=sample.mean(), variance_monthly=sample.var(ddof=1),
                                  sd_monthly=sample.std(ddof=1), mean_annual=12 * sample.mean(),
                                  variance_annual=12 * sample.var(ddof=1),
                                  sd_annual=np.sqrt(12) * sample.std(ddof=1))).rename_axis('asset').reset_index()
                asset_statistics.to_csv(root / 'tables' / f'{name}_asset_statistics.csv', index=False)
                extra_tables[f'{name}_asset_statistics.csv'] = asset_statistics
            stability.to_csv(root / 'diagnostics' / 'pre_post_weight_stability.csv', index=False)
            diversification_table = pd.DataFrame(diversification)
            # Store asset lists as explicit JSON strings, rather than Python repr in CSV.
            if 'assets' in diversification_table:
                diversification_table['assets'] = diversification_table.assets.map(
                    lambda value: json.dumps(value) if isinstance(value, list) else None)
            diversification_table.to_csv(root / 'tables' / 'diversification.csv', index=False)
            extra_tables['diversification.csv'] = diversification_table
            sample_periods = pd.DataFrame([
                dict(analysis=name, start=metadata['start'], end=metadata['end'], N=metadata['N'],
                     assets=json.dumps(metadata['assets']))
                for name, metadata in result_samples.items()
            ])
            sample_periods.to_csv(root / 'tables' / 'analysis_sample_periods.csv', index=False)
            extra_tables['analysis_sample_periods.csv'] = sample_periods
            if sim is not None:
                sim.regressions.to_csv(root / 'models' / 'sim_regressions.csv')
                sim.residuals.to_csv(root / 'models' / 'sim_residuals.csv')
                write_json(root / 'models' / 'sim_assumptions.json', sim.assumptions)
            base_samples = {name: sample_metadata(s) for name, s in samples.items()}
            if sim_ready:
                base_samples.update(etf_sample=sim_selection.metadata['etf_sample'],
                                    rf_sample=sim_selection.metadata['rf_sample'],
                                    sim_common=sim_selection.metadata['sim_common'],
                                    markowitz_comparison=sim_selection.metadata['markowitz_comparison'])
            summary = dict(run_id=state.state['run_id'], status='NUMERICAL_RESULTS_SAVED',
                           samples=base_samples,
                           sample_policy=None if not sim_ready else sim_selection.metadata,
                           result_samples=result_samples,
                           rf_cal_monthly=rf, rf_cal_annual_presentation=12 * rf,
                           completeness='COMPLETE' if sim_ready else 'PARTIAL',
                           blocked_stages={name: details for name, details in state.state['stages'].items()
                                           if details['status'].startswith('BLOCKED_')},
                           sim_assumptions=None if sim is None else sim.assumptions, diversification=diversification,
                           comparisons={} if not sim_ready else {
                               'covariance_only': 'Identical sample means; full covariance versus SIM covariance',
                               'complete_model': 'Sample means/full covariance versus SIM means/SIM covariance'},
                           results={name: result.portfolios.to_dict(orient='records') for name, result in results.items()},
                           tangencies={name: result.tangency.to_dict() for name, result in results.items()},
                           benchmarks={name: table.to_dict(orient='records') for name, table in benchmark_tables.items()},
                           diagnostics=diagnostics)
            write_json(root / 'results_summary.json', summary)
        with state.stage('output_validation'):
            validate_saved_results(root, results, result_specs, config, rf, benchmark_tables, summary, extra_tables)
            validate_saved_descriptive_diagnostics(root, samples, changes, stability)
            if sim_ready:
                validate_saved_sim(root, sim)
            for label in specs if sim_ready else []:
                table = pd.read_csv(root / 'tables' / f'comparison_covariance_only_{label}_means.csv', float_precision='round_trip')
                require(np.array_equal(table.markowitz.to_numpy(), table.sim.to_numpy()), 'Saved covariance-only means differ')
            if sim_ready:
                write_sim_report(root)
                validate_sim_report(root)
                write_model_comparison_report(root)
                validate_model_comparison_report(root)
            manifest = {str(p.relative_to(root)): sha256(p) for folder in ['data', 'models', 'tables', 'diagnostics']
                        for p in sorted((root / folder).rglob('*')) if p.is_file()}
            write_json(root / 'diagnostics' / 'artifact_manifest.json', manifest)
        with state.stage('figures'):
            if config['outputs']['save_figures']:
                from src.generate_figures import frontier_figure, diversification_figure
                dpi = config['outputs']['dpi']
                full_period = result_samples['markowitz_full_A']
                comparison_period = result_samples.get('markowitz_comparison_A')
                full_note = f"{full_period['start']} to {full_period['end']}, N={full_period['N']}"
                frontier_figure(root, {f'markowitz_full_{label}': label for label in specs},
                                'markowitz_constraints', f'Markowitz — constraint specifications\n{full_note}', dpi)
                for label in specs:
                    for prefix in ['markowitz_full', 'sim_complete']:
                        name = f'{prefix}_{label}'
                        if name not in results:
                            continue
                        benchmarks = benchmark_tables[name].query('specification == @label')
                        period = result_samples[name]
                        note = f"{period['start']} to {period['end']}, N={period['N']}"
                        frontier_figure(root, {name: label}, name,
                                        f'{prefix.replace("_", " ")} — {label}\n{note}', dpi, benchmarks)
                    for comparison, prefix in [('covariance_only', 'sim_covariance_only'), ('complete_model', 'sim_complete')]:
                        if not sim_ready:
                            continue
                        note = (f"{comparison_period['start']} to {comparison_period['end']}, "
                                f"N={comparison_period['N']}")
                        frontier_figure(root, {f'markowitz_comparison_{label}': 'Markowitz comparison sample',
                                               f'{prefix}_{label}': 'SIM'},
                                        f'comparison_{comparison}_{label}',
                                        f'{comparison.replace("_", " ")} — {label}\n{note}', dpi)
                pre = result_samples[f'markowitz_pre_covid_{sub_label}']
                post = result_samples[f'markowitz_post_covid_{sub_label}']
                frontier_figure(root, {f'markowitz_pre_covid_{sub_label}': 'Pre-COVID', f'markowitz_post_covid_{sub_label}': 'Post-COVID'},
                                'pre_post_comparison',
                                f"Pre/post COVID — specification {sub_label}\npre {pre['start']}–{pre['end']} (N={pre['N']}); "
                                f"post {post['start']}–{post['end']} (N={post['N']})", dpi)
                diversification_figure(root, dpi)
            else:
                LOG.info('Figures disabled by configuration')
        with state.stage('markowitz_report'):
            summary['status'] = 'PASSED' if sim_ready else 'PARTIAL'
            write_json(root / 'results_summary.json', summary)
            reconcile_json(root / 'results_summary.json', summary)
            write_markowitz_report(root, summary)
        if sim_ready:
            with state.stage('report'):
                write_interpretation(root, summary)
                write_final_assignment_report(root)
                validate_final_assignment_report(root)
        state.complete()
        LOG.info('Run %s: %s', state.state['status'], root)
        return root
    except BaseException:
        LOG.exception('Run FAILED: %s (downstream stages skipped)', root)
        raise
    finally:
        for handler in handlers:
            logger.removeHandler(handler)
            handler.close()
        logger.setLevel(old_level)
        state.close()
