"""Independent corruptions must fail the production gate before figures/reports."""
import json
import numpy as np
import pandas as pd
import pytest
from src.benchmark_portfolios import benchmark_table
from src.estimate_moments import estimate_moments, portfolio_metrics
from src.generate_tables import save_result, write_json
from src.portfolio_optimizer import ConstraintSpec, analyze
from src.validation import ValidationError
from workflow.orchestrator import validate_saved_results
from workflow.state_manager import RunState

NAME = 'markowitz_full_B'


@pytest.fixture(scope='module')
def accepted_result(returns):
    mean, cov = estimate_moments(returns)
    return analyze(mean, cov, list(returns.columns), .00375, ConstraintSpec('long_only'), {'points': 40}, {})


@pytest.fixture
def saved_result(tmp_path, config, accepted_result):
    state = RunState(tmp_path, config)
    root, result = state.path, accepted_result
    save_result(root, NAME, result)
    benchmarks = benchmark_table(result.assets, result.mean, result.covariance, .00375, config['constraints'], 1e-7)
    benchmarks.to_csv(root / 'tables' / f'{NAME}_benchmarks.csv', index=False)
    summary = dict(status='NUMERICAL_RESULTS_SAVED', results={NAME: result.portfolios.to_dict(orient='records')},
                   tangencies={NAME: result.tangency.to_dict()}, benchmarks={NAME: benchmarks.to_dict(orient='records')})
    write_json(root / 'results_summary.json', summary)
    yield state, config, result, benchmarks, summary
    state.close()


def validate(saved):
    state, config, result, benchmarks, summary = saved
    validate_saved_results(state.path, {NAME: result}, {NAME: ConstraintSpec('long_only')},
                           config, .00375, {NAME: benchmarks}, summary)


def test_unchanged_persisted_outputs_reconcile(saved_result):
    validate(saved_result)


@pytest.mark.parametrize('corruption', ['gmv_weights', 'gmv_label', 'variance', 'cal_risky', 'cal_cash',
                                       'cal_return', 'summary', 'benchmark', 'tangency_json', 'efficient_branch'])
def test_each_corruption_blocks_figures_and_report(saved_result, corruption):
    state, _, result, _, _ = saved_result
    root = state.path
    if corruption == 'summary':
        path = root / 'results_summary.json'
        payload = json.loads(path.read_text())
        payload['results'][NAME][0]['variance_monthly'] *= 2
        path.write_text(json.dumps(payload))
    elif corruption == 'tangency_json':
        path = root / 'models' / f'{NAME}_tangency.json'
        payload = json.loads(path.read_text())
        payload['weights'] = [1 / 8] * 8
        path.write_text(json.dumps(payload))
    else:
        suffix = ('cal' if corruption.startswith('cal_') else 'benchmarks' if corruption == 'benchmark'
                  else 'efficient_frontier' if corruption == 'efficient_branch' else 'portfolios')
        path = root / 'tables' / f'{NAME}_{suffix}.csv'
        table = pd.read_csv(path)
        if corruption in {'gmv_weights', 'benchmark'}:
            weights = np.array([.2, .1, .1, .1, .1, .1, .1, .2])
            # Deliberately keep all numeric columns internally consistent and feasible.
            for key, value in portfolio_metrics(weights, result.mean, result.covariance, .00375).items():
                table.loc[0, key] = value
            for asset, weight in zip(result.assets, weights):
                table.loc[0, f'w_{asset}'] = weight
        elif corruption == 'gmv_label':
            table.loc[0, 'portfolio'] = 'tangency'
        elif corruption == 'variance':
            table.loc[0, 'variance_monthly'] *= 2
        elif corruption == 'cal_risky':
            table.loc[100, 'risky_allocation'] = .2
        elif corruption == 'cal_cash':
            table.loc[100, 'cash_allocation'] = 99
        elif corruption == 'cal_return':
            table.loc[100, 'mean_annual'] = 9
        elif corruption == 'efficient_branch':
            table = table.iloc[1:]
        table.to_csv(path, index=False)
    with pytest.raises(ValidationError):
        with state.stage('output_validation'):
            validate(saved_result)
    assert state.state['stages']['output_validation']['status'] == 'FAILED'
    for stage in ['figures', 'markowitz_report', 'report']:
        assert state.state['stages'][stage]['status'] == 'SKIPPED'
    assert not list((root / 'figures').iterdir())
    assert not (root / 'interpretation.md').exists()
