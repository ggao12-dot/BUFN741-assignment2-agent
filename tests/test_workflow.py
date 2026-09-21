import copy
import json
from pathlib import Path
import subprocess
import sys
import numpy as np
import pandas as pd
import pytest
import yaml
from src.data_download import sha256
from src.interpretation import (render_model_comparison_report, render_sim_report,
                                validate_model_comparison_report, validate_sim_report)
from src.final_report import (render_final_assignment_report,
                              validate_final_assignment_report,
                              write_final_assignment_report)
from src.validation import ValidationError
from workflow.orchestrator import run_assignment
from workflow.state_manager import RunState, STAGES
from conftest import PROJECT


def test_unique_runs_and_explicit_resume(tmp_path, config):
    first = RunState(tmp_path, config)
    run_id = first.state['run_id']
    first.close()
    second = RunState(tmp_path, config)
    assert second.state['run_id'] != run_id
    second.close()
    resumed = RunState(tmp_path, config, run_id)
    assert resumed.state['attempt'] == 2
    assert (resumed.path / 'attempts' / '001' / 'state.json').exists()
    assert all(s['status'] == 'PENDING' for s in resumed.state['stages'].values())
    resumed.close()


def test_resume_mismatch_and_concurrent_run_rejected(tmp_path, config):
    first = RunState(tmp_path, config)
    run_id = first.state['run_id']
    with pytest.raises(RuntimeError, match='active'):
        RunState(tmp_path, config, run_id)
    first.close()
    changed = copy.deepcopy(config)
    changed['risk_free']['annual_rate'] = .05
    with pytest.raises(ValidationError, match='differs'):
        RunState(tmp_path, changed, run_id)
    with pytest.raises(ValidationError, match='Invalid run ID'):
        RunState(tmp_path, config, '../escape')


def test_fail_closed_on_missing_cache(tmp_path, config):
    config['data'].update(offline=True, raw_dir=str(tmp_path / 'empty_cache'))
    config['outputs']['root'] = str(tmp_path / 'runs')
    with pytest.raises(ValidationError):
        run_assignment(config, PROJECT)
    root = next((tmp_path / 'runs').iterdir())
    state = json.loads((root / 'state.json').read_text())
    assert state['status'] == 'FAILED'
    assert state['stages']['yahoo_data']['status'] == 'FAILED'
    for stage in STAGES[2:]:
        assert state['stages'][stage]['status'] == 'SKIPPED'
    assert not list((root / 'figures').iterdir())
    assert not (root / 'results_summary.json').exists()


def test_full_offline_cli_and_output_integrity(offline_fixture, tmp_path):
    config, _, _, _, _ = offline_fixture
    path = tmp_path / 'synthetic_assignment.yaml'
    path.write_text(yaml.safe_dump(config))
    result = subprocess.run([sys.executable, str(PROJECT / 'run_assignment.py'), '--config', str(path), '--offline'],
                            capture_output=True, text=True, timeout=180)
    assert result.returncode == 0, result.stdout + result.stderr
    root = next(Path(config['outputs']['root']).iterdir())
    state = json.loads((root / 'state.json').read_text())
    summary = json.loads((root / 'results_summary.json').read_text())
    assert state['status'] == summary['status'] == 'PASSED'
    assert all(s['status'] == 'PASSED' for s in state['stages'].values())
    assert summary['samples']['full']['start'] == '2006-05'
    assert summary['samples']['full']['end'] == '2026-08'
    assert summary['samples']['full']['N'] == 244
    assert len(summary['results']) == 18
    assert len(list((root / 'figures').glob('*.png'))) == 15
    assert len(list((root / 'figures').glob('*.pdf'))) == 15
    assert (root / 'interpretation.md').stat().st_size > 500
    sim_report_path = root / 'sim_report.md'
    assert sim_report_path.stat().st_size > 2000
    sim_report = sim_report_path.read_text()
    assert sim_report.startswith('BUFN741 — Single-Index Model results')
    assert 'Scope: Single-Index Model only' in sim_report
    assert 'SIM common sample: 2006-05 through 2026-08, N=244' in sim_report
    assert 'SPY is the market asset: alpha=0, beta=1 and residual variance=0' in sim_report
    assert 'SPY is not regressed on itself' in sim_report
    assert 'Expected return' in sim_report and 'Alpha' in sim_report and 'Beta' in sim_report
    assert 'Residual SD' in sim_report and 'SIM covariance structure' in sim_report
    assert 'symmetric and PSD' in sim_report
    for label in 'ABC':
        assert f'Specification {label}' in sim_report
        table = pd.read_csv(root / 'tables' / f'sim_complete_{label}_portfolios.csv').set_index('portfolio')
        gmv = table.loc['GMV']
        assert f'GMV annualized expected return: {gmv.mean_annual:.4%}' in sim_report
        assert f'GMV annualized volatility: {gmv.sd_annual:.4%}' in sim_report
    regressions = pd.read_csv(root / 'models' / 'sim_regressions.csv', index_col='asset')
    means = np.load(root / 'models' / 'sim_complete_A_moments.npz')['mean']
    efa = regressions.loc['EFA']
    assert f'| EFA | {12 * means[1]:.4%} | {efa.alpha_annual:.4%} | {efa.beta:.4f} |' in sim_report
    validate_sim_report(root)

    comparison_report_path = root / 'model_comparison_report.md'
    assert comparison_report_path.stat().st_size > 10000
    comparison_report = comparison_report_path.read_text()
    assert comparison_report.startswith('BUFN741 — Markowitz vs. Single-Index Model Comparison')
    assert '`markowitz_report.md`' in comparison_report and '`sim_report.md`' in comparison_report
    assert 'Markowitz comparison sample: 2006-05 through 2026-08, N=244' in comparison_report
    assert 'SIM common sample: 2006-05 through 2026-08, N=244' in comparison_report
    assert 'Experiment 1 — Covariance-model effect only' in comparison_report
    assert 'Experiment 2 — Complete model comparison' in comparison_report
    assert 'exactly identical expected-return vector' in comparison_report
    assert 'Full Markowitz covariance matrix (monthly)' in comparison_report
    assert 'SIM-implied covariance matrix (monthly)' in comparison_report
    assert 'Monthly covariance-difference Frobenius norm' in comparison_report
    for label in 'ABC':
        assert comparison_report.count(f'### Specification {label}') == 2
    assert all(category in comparison_report for category in ['MARKOWITZ:', 'SIM:', 'TIE:'])

    dominance = pd.read_csv(root / 'tables' / 'comparison_covariance_only_A_frontier_dominance.csv')
    counts = dominance.lower_volatility.value_counts()
    assert f"Minimum SIM-minus-Markowitz volatility difference: {dominance.sim_minus_markowitz_sd.min():.6%}" in comparison_report
    assert f"Mean absolute volatility difference: {dominance.sim_minus_markowitz_sd.abs().mean():.6%}" in comparison_report
    assert f"TIE: {counts.get('TIE', 0)} targets ({counts.get('TIE', 0) / len(dominance):.2%})" in comparison_report
    differences = pd.read_csv(root / 'tables' / 'comparison_complete_model_B_weight_differences.csv')
    spy_gmv = differences.query("portfolio == 'GMV' and asset == 'SPY'").iloc[0]
    expected_weight_row = (f'| SPY | {spy_gmv.markowitz:.4%} | {spy_gmv.sim:.4%} | '
                           f'{spy_gmv.sim_minus_markowitz:.4%} | {abs(spy_gmv.sim_minus_markowitz):.4%} |')
    assert expected_weight_row in comparison_report
    validate_model_comparison_report(root)

    final_report_path = root / 'final_assignment_report.md'
    final_report = final_report_path.read_text()
    assert final_report.startswith('# BUFN741 Group Assignment 2')
    assert '## Multi-Asset Portfolio Optimization: Markowitz and Single-Index Models' in final_report
    assert 'Markowitz full sample: 2006-05 through 2026-08, N=244' in final_report
    assert 'SIM common sample: 2006-05 through 2026-08, N=244' in final_report
    assert all(f'## {number}.' in final_report for number in range(1, 16))
    assert all(f'### Question {number}.' in final_report for number in range(1, 9))
    assert 'expected-return vectors and observations are exactly identical' in final_report
    assert final_report.count('![') == 15
    validate_final_assignment_report(root)

    # Re-rendering the final report cannot alter any analytical artifact.
    analytical = [path for folder in ['data', 'models', 'tables', 'diagnostics', 'figures']
                  for path in (root / folder).rglob('*') if path.is_file()]
    before = {path: sha256(path) for path in analytical}
    write_final_assignment_report(root)
    assert before == {path: sha256(path) for path in analytical}

    original_final_report = final_report_path.read_text()
    final_report_path.write_text(original_final_report + '\ncorrupted final statistic: 999\n')
    with pytest.raises(ValidationError, match='differs from authoritative'):
        validate_final_assignment_report(root)
    final_report_path.write_text(original_final_report)
    required_figure = root / 'figures' / 'markowitz_constraints.png'
    hidden_figure = required_figure.with_suffix('.png.hidden')
    required_figure.rename(hidden_figure)
    with pytest.raises(ValidationError, match='missing required figure'):
        validate_final_assignment_report(root)
    hidden_figure.rename(required_figure)

    # NONATTAINED status removes the corresponding finite weight row.
    full_a_tangency_path = root / 'models' / 'markowitz_full_A_tangency.json'
    original_full_a_tangency = full_a_tangency_path.read_text()
    full_a_tangency = json.loads(original_full_a_tangency)
    full_a_tangency.update(status='NONATTAINED', weights=None, gross_exposure=None,
                           sharpe_supremum_annual=0.6,
                           sharpe_supremum_monthly=0.6 / np.sqrt(12))
    full_a_tangency_path.write_text(json.dumps(full_a_tangency))
    summary_path = root / 'results_summary.json'
    original_summary = summary_path.read_text()
    nonattained_summary = json.loads(original_summary)
    nonattained_summary['tangencies']['markowitz_full_A'] = full_a_tangency
    summary_path.write_text(json.dumps(nonattained_summary))
    full_a_portfolio_path = root / 'tables' / 'markowitz_full_A_portfolios.csv'
    original_full_a_portfolios = full_a_portfolio_path.read_text()
    full_a_portfolios = pd.read_csv(full_a_portfolio_path)
    full_a_portfolios.loc[full_a_portfolios.portfolio != 'tangency'].to_csv(full_a_portfolio_path, index=False)
    nonattained_final = render_final_assignment_report(root)
    markowitz_weights = nonattained_final.split('**Table 5. Markowitz portfolio weights**', 1)[1].split(
        '![Figure 2.', 1)[0]
    assert '| Markowitz A | tangency |' not in markowitz_weights
    assert 'Tangency | NONATTAINED' in nonattained_final
    full_a_tangency_path.write_text(original_full_a_tangency)
    full_a_portfolio_path.write_text(original_full_a_portfolios)
    summary_path.write_text(original_summary)
    for name in summary['results']:
        frame = pd.read_csv(root / 'tables' / f'{name}_frontier.csv')
        assert frame.solver_status.eq('optimal').all()
        assert len(frame) >= 200
        weights = frame.filter(regex='^w_').to_numpy()
        np.testing.assert_allclose(weights.sum(axis=1), 1, atol=1e-7)
    for label in 'ABC':
        means = pd.read_csv(root / 'tables' / f'comparison_covariance_only_{label}_means.csv')
        np.testing.assert_array_equal(means.markowitz, means.sim)
    manifest = json.loads((root / 'diagnostics' / 'artifact_manifest.json').read_text())
    assert len(manifest) > 100
    for relative, digest in manifest.items():
        assert sha256(root / relative) == digest
    diversification = pd.read_csv(root / 'tables' / 'diversification.csv')
    assert (np.diff(diversification.gmv_sd_annual) <= 1e-7).all()
    assert (np.diff(diversification.tangency_sharpe_annual) >= -1e-7).all()
    assert not (PROJECT / 'workflow_state.json').exists()

    # The production validator detects both report corruption and inconsistent saved report inputs.
    original_report = sim_report_path.read_text()
    sim_report_path.write_text(original_report + '\ncorrupted value: 999\n')
    with pytest.raises(ValidationError, match='differs from authoritative'):
        validate_sim_report(root)
    sim_report_path.write_text(original_report)
    regression_path = root / 'models' / 'sim_regressions.csv'
    original_regressions = regression_path.read_text()
    corrupted = pd.read_csv(regression_path)
    corrupted.loc[corrupted.asset == 'EFA', 'beta'] = 999
    corrupted.to_csv(regression_path, index=False)
    with pytest.raises(ValidationError, match='differs from authoritative'):
        validate_sim_report(root)
    regression_path.write_text(original_regressions)

    original_comparison_report = comparison_report_path.read_text()
    comparison_report_path.write_text(original_comparison_report + '\ncorrupted comparison: 999\n')
    with pytest.raises(ValidationError, match='differs from authoritative'):
        validate_model_comparison_report(root)
    comparison_report_path.write_text(original_comparison_report)
    frontier_path = root / 'tables' / 'comparison_covariance_only_A_frontier_dominance.csv'
    original_frontier = frontier_path.read_text()
    corrupted_frontier = pd.read_csv(frontier_path)
    corrupted_frontier.loc[0, 'lower_volatility'] = 'TIE'
    corrupted_frontier.to_csv(frontier_path, index=False)
    with pytest.raises(ValidationError, match='differs from authoritative'):
        validate_model_comparison_report(root)
    frontier_path.write_text(original_frontier)

    # A nonattained model contributes no fabricated finite tangency comparison.
    comparison_tangency_path = root / 'models' / 'markowitz_comparison_A_tangency.json'
    comparison_tangency = json.loads(comparison_tangency_path.read_text())
    comparison_tangency.update(status='NONATTAINED', weights=None, gross_exposure=None,
                               sharpe_supremum_annual=0.4,
                               sharpe_supremum_monthly=0.4 / np.sqrt(12))
    comparison_tangency_path.write_text(json.dumps(comparison_tangency))
    comparison_portfolio_path = root / 'tables' / 'markowitz_comparison_A_portfolios.csv'
    comparison_portfolios = pd.read_csv(comparison_portfolio_path)
    comparison_portfolios.loc[comparison_portfolios.portfolio != 'tangency'].to_csv(
        comparison_portfolio_path, index=False)
    rendered_comparison = render_model_comparison_report(root)
    covariance_a = rendered_comparison.split('### Specification A', 1)[1].split('### Specification B', 1)[0]
    markowitz_a = covariance_a.split('**Markowitz**', 1)[1].split('**SIM**', 1)[0]
    assert 'Tangency status: NONATTAINED' in markowitz_a
    assert 'Tangency weights: none; no finite tangency portfolio' in markowitz_a
    assert 'Tangency weights: SPY=' not in markowitz_a

    # NONATTAINED rendering must never infer or fabricate finite tangency weights.
    tangency_path = root / 'models' / 'sim_complete_A_tangency.json'
    tangency = json.loads(tangency_path.read_text())
    tangency.update(status='NONATTAINED', weights=None, gross_exposure=None,
                    sharpe_supremum_annual=0.5, sharpe_supremum_monthly=0.5 / np.sqrt(12))
    tangency_path.write_text(json.dumps(tangency))
    portfolio_path = root / 'tables' / 'sim_complete_A_portfolios.csv'
    portfolios = pd.read_csv(portfolio_path)
    portfolios.loc[portfolios.portfolio != 'tangency'].to_csv(portfolio_path, index=False)
    rendered = render_sim_report(root)
    specification_a = rendered.split('Specification A', 1)[1].split('Specification B', 1)[0]
    assert 'Tangency status: NONATTAINED' in specification_a
    assert 'Tangency weights: none; no finite tangency portfolio' in specification_a
    assert 'Tangency weights: SPY=' not in specification_a


def test_failed_frontier_produces_no_saved_frontier(offline_fixture, monkeypatch):
    config, _, _, _, _ = offline_fixture
    from src.portfolio_optimizer import OptimizationError
    def failed(*args, **kwargs):
        raise OptimizationError('injected solver failure')
    monkeypatch.setattr('src.portfolio_optimizer.PortfolioOptimizer.minimum_variance', failed)
    with pytest.raises(OptimizationError, match='injected'):
        run_assignment(config, PROJECT)
    root = next(Path(config['outputs']['root']).iterdir())
    state = json.loads((root / 'state.json').read_text())
    assert state['stages']['markowitz_full']['status'] == 'FAILED'
    assert state['stages']['figures']['status'] == 'SKIPPED'
    assert not list((root / 'tables').glob('*frontier*'))
    assert not list((root / 'figures').iterdir())


def test_corrupted_output_blocks_plots_and_report(offline_fixture, monkeypatch):
    config, _, _, _, _ = offline_fixture
    config['frontier']['points'] = 40
    from workflow.orchestrator import save_result
    def corrupt(root, name, result):
        save_result(root, name, result)
        if name == 'markowitz_full_A':
            path = root / 'tables' / f'{name}_frontier.csv'
            table = pd.read_csv(path)
            table.loc[0, 'solver_status'] = 'failed'
            table.to_csv(path, index=False)
    monkeypatch.setattr('workflow.orchestrator.save_result', corrupt)
    with pytest.raises(ValidationError, match='Failed solver point'):
        run_assignment(config, PROJECT)
    root = next(Path(config['outputs']['root']).iterdir())
    state = json.loads((root / 'state.json').read_text())
    assert state['stages']['output_validation']['status'] == 'FAILED'
    assert state['stages']['figures']['status'] == 'SKIPPED'
    assert state['stages']['report']['status'] == 'SKIPPED'
    assert not list((root / 'figures').iterdir())
    assert not (root / 'interpretation.md').exists()
    assert not (root / 'sim_report.md').exists()
    assert not (root / 'model_comparison_report.md').exists()
    assert not (root / 'final_assignment_report.md').exists()


def test_corrupted_sim_report_input_fails_output_validation(offline_fixture, monkeypatch):
    config, _, _, _, _ = offline_fixture
    config['frontier']['points'] = 40
    from workflow import orchestrator
    original_validation = orchestrator.validate_saved_results

    def corrupt_after_numerical_reconciliation(*args, **kwargs):
        original_validation(*args, **kwargs)
        root = args[0]
        path = root / 'models' / 'sim_regressions.csv'
        table = pd.read_csv(path)
        table.loc[table.asset == 'EFA', 'beta'] = 999
        table.to_csv(path, index=False)

    monkeypatch.setattr(orchestrator, 'validate_saved_results', corrupt_after_numerical_reconciliation)
    with pytest.raises(ValidationError, match='sim_regressions.csv differs'):
        run_assignment(config, PROJECT)
    root = next(Path(config['outputs']['root']).iterdir())
    state = json.loads((root / 'state.json').read_text())
    assert state['stages']['output_validation']['status'] == 'FAILED'
    for stage in ['figures', 'markowitz_report', 'report']:
        assert state['stages'][stage]['status'] == 'SKIPPED'
    assert not (root / 'sim_report.md').exists()
    assert not list((root / 'figures').iterdir())


def test_corrupted_comparison_report_input_fails_output_validation(offline_fixture, monkeypatch):
    config, _, _, _, _ = offline_fixture
    config['frontier']['points'] = 40
    from workflow import orchestrator
    original_validation = orchestrator.validate_saved_results

    def corrupt_before_numerical_reconciliation(*args, **kwargs):
        root = args[0]
        path = root / 'tables' / 'comparison_covariance_only_A_frontier_dominance.csv'
        table = pd.read_csv(path)
        table.loc[0, 'lower_volatility'] = 'CORRUPTED'
        table.to_csv(path, index=False)
        original_validation(*args, **kwargs)

    monkeypatch.setattr(orchestrator, 'validate_saved_results', corrupt_before_numerical_reconciliation)
    with pytest.raises(ValidationError, match='persisted output differs'):
        run_assignment(config, PROJECT)
    root = next(Path(config['outputs']['root']).iterdir())
    state = json.loads((root / 'state.json').read_text())
    assert state['stages']['output_validation']['status'] == 'FAILED'
    for stage in ['figures', 'markowitz_report', 'report']:
        assert state['stages'][stage]['status'] == 'SKIPPED'
    assert not (root / 'model_comparison_report.md').exists()
    assert not list((root / 'figures').iterdir())


def test_one_month_rf_lag_runs_sim_on_intersection(offline_fixture):
    config, _, rf, _, ff = offline_fixture
    config['frontier']['points'] = 80
    from conftest import make_zip
    from src.data_download import write_manifest
    ff.write_bytes(make_zip(rf.iloc[:-1]))
    write_manifest(ff, 'synthetic incomplete fixture')
    root = run_assignment(config, PROJECT)
    assert (root / 'data' / 'raw' / ff.name).read_bytes() == ff.read_bytes()
    state = json.loads((root / 'state.json').read_text())
    assert state['status'] == 'PASSED'
    for stage in ['yahoo_data', 'input_validation', 'markowitz_full', 'markowitz_subsamples',
                  'diversification', 'ff_data', 'sim', 'comparisons', 'numerical_outputs',
                  'output_validation', 'figures', 'markowitz_report', 'report']:
        assert state['stages'][stage]['status'] == 'PASSED'
    assert state['stages']['ff_data']['trailing_rf_lag_months'] == 1
    assert state['stages']['ff_data']['lag_accepted'] is True
    assert 'Accepted trailing' in state['stages']['ff_data']['warning']
    summary = json.loads((root / 'results_summary.json').read_text())
    assert summary['status'] == 'PASSED' and summary['comparisons']
    assert summary['samples']['full']['end'] == '2026-08'
    assert summary['samples']['sim_common']['end'] == '2026-07'
    assert summary['samples']['sim_common']['N'] == 243
    assert summary['samples']['markowitz_comparison'] == summary['samples']['sim_common']
    assert summary['sample_policy']['trailing_rf_lag_months'] == 1
    assert summary['sample_policy']['lag_accepted'] is True
    np.testing.assert_array_equal(
        pd.read_csv(root / 'data' / 'returns_sim_common.csv', index_col=0).to_numpy(),
        pd.read_csv(root / 'data' / 'returns_markowitz_comparison.csv', index_col=0).to_numpy())
    for label in 'ABC':
        comparison_means = pd.read_csv(root / 'models' / f'markowitz_comparison_{label}_means_monthly.csv', index_col=0)
        covariance_only_means = pd.read_csv(root / 'models' / f'sim_covariance_only_{label}_means_monthly.csv', index_col=0)
        np.testing.assert_array_equal(comparison_means.to_numpy(), covariance_only_means.to_numpy())
    periods = pd.read_csv(root / 'tables' / 'analysis_sample_periods.csv').set_index('analysis')
    assert periods.loc['markowitz_full_A', 'end'] == '2026-08'
    assert periods.loc['markowitz_comparison_A', 'end'] == '2026-07'
    assert periods.loc['sim_complete_A', 'end'] == '2026-07'
    assert (root / 'markowitz_report.md').exists()
    sim_report = (root / 'sim_report.md').read_text()
    assert 'SIM common sample: 2006-05 through 2026-07, N=243' in sim_report
    assert 'Markowitz comparison sample: 2006-05 through 2026-07, N=243' in sim_report
    assert 'Accepted RF trailing lag: yes; 1 month(s)' in sim_report
    comparison_report = (root / 'model_comparison_report.md').read_text()
    assert 'Markowitz comparison sample: 2006-05 through 2026-07, N=243' in comparison_report
    assert 'SIM common sample: 2006-05 through 2026-07, N=243' in comparison_report
    assert 'exactly identical expected-return vector' in comparison_report
    final_report = (root / 'final_assignment_report.md').read_text()
    assert 'Markowitz comparison sample: 2006-05 through 2026-07, N=243' in final_report
    assert 'SIM common sample: 2006-05 through 2026-07, N=243' in final_report
    assert (root / 'interpretation.md').exists()
    assert list((root / 'tables').glob('comparison_*'))


def test_unknown_resume_does_not_create_run(tmp_path, config):
    with pytest.raises(ValidationError, match='Unknown run'):
        RunState(tmp_path, config, 'nonexistent')
    assert not (tmp_path / 'nonexistent').exists()
