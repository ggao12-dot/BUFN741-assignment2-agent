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
    assert (root / 'interpretation.md').exists()
    assert list((root / 'tables').glob('comparison_*'))


def test_unknown_resume_does_not_create_run(tmp_path, config):
    with pytest.raises(ValidationError, match='Unknown run'):
        RunState(tmp_path, config, 'nonexistent')
    assert not (tmp_path / 'nonexistent').exists()
