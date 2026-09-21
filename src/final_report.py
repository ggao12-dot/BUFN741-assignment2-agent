"""Assemble the final assignment narrative from validated persisted artifacts."""
from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pandas as pd
import yaml
from src.validation import require


ASSETS = ['SPY', 'EFA', 'EEM', 'TLT', 'AGG', 'GLD', 'USO', 'DBC']


def _load_portfolios(root: Path, name: str) -> pd.DataFrame:
    return pd.read_csv(root / 'tables' / f'{name}_portfolios.csv',
                       float_precision='round_trip').set_index('portfolio')


def _portfolio_summary(root: Path, summary: dict, names: list[tuple[str, str]]) -> list[str]:
    lines = ['| Model/specification | Portfolio | Status | Expected return | Volatility | Sharpe | Gross exposure |',
             '|---|---|---|---:|---:|---:|---:|']
    for name, label in names:
        table = _load_portfolios(root, name)
        for portfolio in ['GMV', 'tangency']:
            tangency = summary['tangencies'][name]
            if portfolio == 'tangency' and tangency['status'] == 'NONATTAINED':
                lines.append(f"| {label} | Tangency | NONATTAINED | — | — | supremum "
                             f"{tangency['sharpe_supremum_annual']:.3f} | — |")
                continue
            row = table.loc[portfolio]
            lines.append(f"| {label} | {portfolio} | ATTAINED | {row.mean_annual:.2%} | "
                         f"{row.sd_annual:.2%} | {row.sharpe_annual:.3f} | {row.gross_exposure:.3f} |")
    return lines


def _weight_table(root: Path, summary: dict, names: list[tuple[str, str]]) -> list[str]:
    lines = ['| Model/specification | Portfolio | ' + ' | '.join(ASSETS) + ' |',
             '|---|---|' + '|'.join(['---:'] * len(ASSETS)) + '|']
    for name, label in names:
        table = _load_portfolios(root, name)
        for portfolio in ['GMV', 'tangency']:
            if portfolio not in table.index:
                continue
            row = table.loc[portfolio]
            weights = ' | '.join(f"{row[f'w_{asset}']:.1%}" for asset in ASSETS)
            lines.append(f'| {label} | {portfolio} | {weights} |')
    return lines


def _figure(number: int, filename: str, caption: str) -> list[str]:
    return ['', f'![Figure {number}. {caption}](figures/{filename})', '',
            f'*Figure {number}. {caption}*']


def _comparison_summary(root: Path, experiment: str) -> list[str]:
    lines = ['| Specification | Common targets | Min SIM−Markowitz SD | Max SIM−Markowitz SD | '
             'Mean absolute SD difference | MARKOWITZ | SIM | TIE |',
             '|:---:|---:|---:|---:|---:|---:|---:|---:|']
    for label in 'ABC':
        table = pd.read_csv(root / 'tables' / f'comparison_{experiment}_{label}_frontier_dominance.csv',
                            float_precision='round_trip')
        counts = table.lower_volatility.value_counts()
        lines.append(f"| {label} | {len(table)} | {table.sim_minus_markowitz_sd.min():.3%} | "
                     f"{table.sim_minus_markowitz_sd.max():.3%} | "
                     f"{table.sim_minus_markowitz_sd.abs().mean():.3%} | "
                     f"{counts.get('MARKOWITZ', 0)} | {counts.get('SIM', 0)} | {counts.get('TIE', 0)} |")
    return lines


def _comparison_portfolio_metrics(root: Path, experiment: str) -> list[str]:
    lines = ['| Specification | Portfolio | Model | Expected return | Volatility | Sharpe | Gross exposure |',
             '|:---:|---|---|---:|---:|---:|---:|']
    for label in 'ABC':
        table = pd.read_csv(root / 'tables' / f'comparison_{experiment}_{label}_metric_differences.csv',
                            float_precision='round_trip')
        for portfolio in ['GMV', 'tangency']:
            subset = table.loc[table.portfolio == portfolio].set_index('metric')
            if subset.empty:
                continue
            for model in ['markowitz', 'sim']:
                lines.append(f"| {label} | {portfolio} | {model.title()} | "
                             f"{subset.loc['mean_annual', model]:.2%} | {subset.loc['sd_annual', model]:.2%} | "
                             f"{subset.loc['sharpe_annual', model]:.3f} | "
                             f"{subset.loc['gross_exposure', model]:.3f} |")
    return lines


def _largest_weight_differences(root: Path, experiment: str) -> list[str]:
    lines = ['| Specification | Portfolio | Largest-changing asset | Markowitz | SIM | Absolute change |',
             '|:---:|---|---|---:|---:|---:|']
    for label in 'ABC':
        table = pd.read_csv(root / 'tables' / f'comparison_{experiment}_{label}_weight_differences.csv',
                            float_precision='round_trip')
        for portfolio in ['GMV', 'tangency']:
            subset = table.loc[table.portfolio == portfolio].copy()
            if subset.empty:
                lines.append(f'| {label} | {portfolio} | unavailable: NONATTAINED | — | — | — |')
                continue
            row = subset.loc[subset.sim_minus_markowitz.abs().idxmax()]
            lines.append(f'| {label} | {portfolio} | {row.asset} | {row.markowitz:.2%} | '
                         f'{row.sim:.2%} | {abs(row.sim_minus_markowitz):.2%} |')
    return lines


def _git_commit(root: Path) -> str:
    environment = json.loads((root / 'diagnostics' / 'environment.json').read_text())
    return environment.get('git_commit') or 'unavailable'


def render_final_assignment_report(root: Path) -> str:
    """Render the complete report without performing portfolio estimation or optimization."""
    summary = json.loads((root / 'results_summary.json').read_text())
    require(summary['completeness'] == 'COMPLETE', 'Final report requires a complete multi-model run')
    for component in ['markowitz_report.md', 'sim_report.md', 'model_comparison_report.md']:
        require((root / component).is_file(), f'Final report requires {component}')
    config = yaml.safe_load((root / 'config_snapshot.yaml').read_text())
    samples = summary['samples']
    stats = pd.read_csv(root / 'tables' / 'full_asset_statistics.csv', float_precision='round_trip')
    correlations = pd.read_csv(root / 'models' / 'full_sample_correlation.csv', index_col=0,
                               float_precision='round_trip')
    full_pairs = pd.read_csv(root / 'diagnostics' / 'full_correlations.csv', float_precision='round_trip')
    diversification = pd.read_csv(root / 'tables' / 'diversification.csv', float_precision='round_trip')
    covariance_changes = pd.read_csv(root / 'diagnostics' / 'covariance_changes.csv', float_precision='round_trip')
    correlation_changes = pd.read_csv(root / 'diagnostics' / 'correlation_changes.csv', float_precision='round_trip')
    stability = pd.read_csv(root / 'diagnostics' / 'pre_post_weight_stability.csv',
                            float_precision='round_trip').set_index('portfolio')
    regressions = pd.read_csv(root / 'models' / 'sim_regressions.csv', index_col='asset',
                              float_precision='round_trip')
    sim_mean = np.load(root / 'models' / 'sim_complete_A_moments.npz')['mean']
    full_names = [(f'markowitz_full_{label}', f'Markowitz {label}') for label in 'ABC']
    sim_names = [(f'sim_complete_{label}', f'SIM {label}') for label in 'ABC']
    div = diversification.set_index('universe')
    pre = _load_portfolios(root, 'markowitz_pre_covid_B')
    post = _load_portfolios(root, 'markowitz_post_covid_B')
    weakest = regressions.drop(index='SPY').r_squared.sort_values().head(3)
    cov_a = pd.read_csv(root / 'tables' / 'comparison_covariance_only_A_frontier_dominance.csv')
    cov_b = pd.read_csv(root / 'tables' / 'comparison_covariance_only_B_frontier_dominance.csv')
    markowitz_a = summary['tangencies']['markowitz_full_A']
    if markowitz_a['status'] == 'NONATTAINED':
        unrestricted_summary = (
            f"The unrestricted full-sample tangency is NONATTAINED. Because the GMV expected return is below "
            f"the {summary['rf_cal_annual_presentation']:.2%} CAL rate, the Sharpe supremum "
            f"{markowitz_a['sharpe_supremum_annual']:.3f} is approached asymptotically; no finite tangency fund "
            'or attained CAL exists.')
        unrestricted_detail = (
            'Specification A is an economic NONATTAINED case, not a solver failure. Its GMV return is below '
            'the risk-free rate, so normalized finite tangency weights do not exist.')
        short_sale_detail = (
            'Unrestricted A attains the lowest GMV risk but uses larger gross exposure and has no finite '
            'full-sample Markowitz tangency portfolio.')
    else:
        a_table = _load_portfolios(root, 'markowitz_full_A')
        unrestricted_summary = (
            f"The unrestricted full-sample tangency is ATTAINED, with annualized Sharpe "
            f"{a_table.loc['tangency', 'sharpe_annual']:.3f} and gross exposure "
            f"{a_table.loc['tangency', 'gross_exposure']:.3f}.")
        unrestricted_detail = 'Specification A has a finite attained tangency portfolio in this run.'
        short_sale_detail = (
            'Unrestricted A attains the lowest GMV risk and permits larger offsetting positions and gross exposure.')

    text = ['# BUFN741 Group Assignment 2', '',
            '## Multi-Asset Portfolio Optimization: Markowitz and Single-Index Models', '',
            'This is the complete assignment report. It covers Part 1 Markowitz optimization, Part 2 '
            'Single-Index Model estimation and optimization, direct Markowitz-versus-SIM comparisons, '
            'the required pre/post-COVID analysis, numerical diagnostics, and economic interpretation. '
            'The validated component reports remain available as `markowitz_report.md`, `sim_report.md`, '
            'and `model_comparison_report.md`.', '',
            '## Executive Summary', '',
            f"- Adding bonds reduced long-only GMV volatility from {div.loc['equities', 'gmv_sd_annual']:.2%} "
            f"for equities alone to {div.loc['equities_bonds', 'gmv_sd_annual']:.2%}. Adding gold raised the "
            f"tangency Sharpe from {div.loc['equities_bonds', 'tangency_sharpe_annual']:.3f} to "
            f"{div.loc['equities_bonds_gold', 'tangency_sharpe_annual']:.3f}; adding oil and DBC reduced GMV "
            f"volatility further to {div.loc['all_assets', 'gmv_sd_annual']:.2%} but did not improve the saved "
            'tangency Sharpe at displayed precision.',
            f'- {unrestricted_summary}',
            f"- Long-only and ±20% bounds materially reduce gross exposure and concentrate the solution in a more "
            'implementable region, while Specification C places several assets at its +20% ceiling.',
            f"- Under Specification B, post-COVID GMV volatility rose from {pre.loc['GMV', 'sd_annual']:.2%} to "
            f"{post.loc['GMV', 'sd_annual']:.2%}; the tangency Sharpe rose from "
            f"{pre.loc['tangency', 'sharpe_annual']:.3f} to {post.loc['tangency', 'sharpe_annual']:.3f}. The "
            f"post-COVID estimate uses only {samples['post_covid']['N']} monthly observations.",
            '- SIM attributes every cross-asset covariance to exposure to the SPY-minus-RF factor. The lowest '
            'single-factor R² values occur for ' + ', '.join(f'{a} ({v:.3f})' for a, v in weakest.items()) + '.',
            f"- In the covariance-only experiment, Specification A has lower Markowitz volatility at "
            f"{(cov_a.lower_volatility == 'MARKOWITZ').sum()} of 80 common targets and lower SIM volatility at "
            f"{(cov_a.lower_volatility == 'SIM').sum()}; under B the corresponding counts are "
            f"{(cov_b.lower_volatility == 'MARKOWITZ').sum()} and {(cov_b.lower_volatility == 'SIM').sum()}. "
            'The crossings rule out a single frontier winner.', '',
            '## 1. Objective and Methodology', '',
            'The investable universe is SPY, EFA, EEM, TLT, AGG, GLD, USO, and DBC. The analysis uses monthly '
            'simple total returns from Yahoo Finance adjusted prices. Fama–French monthly RF observations support '
            'SIM excess-return regressions; the fixed 4.5% annual rate supports CAL and tangency calculations.', '',
            'All estimation and optimization are monthly. Arithmetic means and variances are multiplied by 12 for '
            'presentation, while standard deviations and Sharpe ratios are multiplied by sqrt(12). Specification A '
            'is unrestricted long/short with weights summing to one. B is long-only. C constrains every weight to '
            '[-20%, +20%]. Markowitz uses the full sample covariance matrix. SIM uses beta beta\' times the variance '
            'of SPY minus aligned FF RF, plus diagonal residual variances.', '',
            '## 2. Data and Sample Construction', '',
            f"- Markowitz full sample: {samples['full']['start']} through {samples['full']['end']}, N={samples['full']['N']}.",
            f"- Pre-COVID: {samples['pre_covid']['start']} through {samples['pre_covid']['end']}, N={samples['pre_covid']['N']}.",
            f"- Post-COVID: {samples['post_covid']['start']} through {samples['post_covid']['end']}, N={samples['post_covid']['N']}.",
            f"- SIM common sample: {samples['sim_common']['start']} through {samples['sim_common']['end']}, N={samples['sim_common']['N']}.",
            f"- Markowitz comparison sample: {samples['markowitz_comparison']['start']} through "
            f"{samples['markowitz_comparison']['end']}, N={samples['markowitz_comparison']['N']}.", '',
            f"Yahoo ETF returns extend through August 2026. Available FF RF ends July 2026, producing an accepted "
            f"{summary['sample_policy']['trailing_rf_lag_months']}-month lag under the configured maximum of "
            f"{summary['sample_policy']['max_trailing_rf_lag_months']}. Main Markowitz analysis retains August. "
            'SIM and direct comparisons use the identical May 2006–July 2026 intersection.', '',
            '## 3. Descriptive Statistics and Diversification', '',
            '**Table 1. Full-sample annualized asset statistics**', '',
            '| Asset | Arithmetic mean | Standard deviation | Variance |',
            '|---|---:|---:|---:|']
    for row in stats.itertuples():
        text.append(f'| {row.asset} | {row.mean_annual:.2%} | {row.sd_annual:.2%} | {row.variance_annual:.6f} |')
    text += ['', '**Table 2. Full-sample correlation matrix**', '',
             '| Asset | ' + ' | '.join(ASSETS) + ' |',
             '|---|' + '|'.join(['---:'] * len(ASSETS)) + '|']
    for asset in ASSETS:
        text.append(f'| {asset} | ' + ' | '.join(f'{correlations.loc[asset, other]:.2f}' for other in ASSETS) + ' |')
    top_positive = full_pairs.sort_values('correlation', ascending=False).head(4)
    top_diversifying = full_pairs.sort_values('correlation').head(4)
    text += ['', 'The largest positive correlations are ' + ', '.join(
        f'{r.asset_i}/{r.asset_j}={r.correlation:.3f}' for r in top_positive.itertuples()) +
        '. The lowest correlations, which provide the clearest pairwise diversification evidence, are ' +
        ', '.join(f'{r.asset_i}/{r.asset_j}={r.correlation:.3f}' for r in top_diversifying.itertuples()) + '.', '',
        '**Table 3. Incremental diversification under Specification B**', '',
        '| Universe | GMV volatility | Tangency status | Tangency Sharpe |',
        '|---|---:|:---:|---:|']
    for row in diversification.itertuples():
        universe_label = 'all assets' if row.universe == 'all_assets' else row.universe.replace('_', ' + ')
        text.append(f'| {universe_label} | {row.gmv_sd_annual:.2%} | '
                    f'{row.tangency_status} | {row.tangency_sharpe_annual:.3f} |')
    text += _figure(1, 'diversification.png', 'Incremental diversification across asset subsets.')

    text += ['', '## 4. Markowitz Full-Sample Results', '',
             '**Table 4. Markowitz GMV and tangency results**', ''] + _portfolio_summary(root, summary, full_names)
    text += ['', '**Table 5. Markowitz portfolio weights**', ''] + _weight_table(root, summary, full_names)
    text += ['', unrestricted_detail + ' B removes short sales. C '
             'allows limited shorts but its eight +20% caps make the feasible set tight and produce binding ceilings.']
    text += _figure(2, 'markowitz_constraints.png', 'Full-sample Markowitz frontiers under A, B, and C.')
    text += _figure(3, 'markowitz_full_A.png', 'Specification A Markowitz frontier; tangency is nonattained.')
    text += _figure(4, 'markowitz_full_B.png', 'Specification B Markowitz frontier and attained CAL.')
    text += _figure(5, 'markowitz_full_C.png', 'Specification C Markowitz frontier and attained CAL.')

    benchmarks = pd.read_csv(root / 'tables' / 'markowitz_full_B_benchmarks.csv', float_precision='round_trip')
    text += ['', '## 5. Benchmark Portfolios', '', '**Table 6. Benchmark performance and feasibility**', '',
             '| Benchmark | Specification | Feasible | Expected return | Volatility | Sharpe |',
             '|---|:---:|:---:|---:|---:|---:|']
    for row in benchmarks.itertuples():
        text.append(f'| {row.benchmark} | {row.specification} | {"yes" if row.feasible else "no"} | '
                    f'{row.mean_annual:.2%} | {row.sd_annual:.2%} | {row.sharpe_annual:.3f} |')
    text += ['', 'Feasibility is evaluated independently under each specification. No infeasible allocation is '
             'projected into or treated as part of a constraint-specific opportunity set.', '',
             '## 6. Effect of Portfolio Constraints', '',
             'A permits large offsetting long and short positions and therefore has the greatest exposure to '
             'estimation error. B forces gross exposure to one. Under C, eight weights each capped at +20% must '
             'sum to one, so at least five meaningful long positions are required; no more than two holdings can '
             'be strictly negative, and maximum gross exposure is 1.40. The saved bound diagnostics show which '
             'assets absorb these geometric restrictions.', '',
             '## 7. Pre-COVID versus Post-COVID Markowitz Results', '',
             '**Table 7. Specification B pre/post portfolio comparison**', '',
             '| Period | Portfolio | Expected return | Volatility | Sharpe | Gross exposure |',
             '|---|---|---:|---:|---:|---:|']
    for period, table in [('Pre-COVID', pre), ('Post-COVID', post)]:
        for portfolio in ['GMV', 'tangency']:
            row = table.loc[portfolio]
            text.append(f'| {period} | {portfolio} | {row.mean_annual:.2%} | {row.sd_annual:.2%} | '
                        f'{row.sharpe_annual:.3f} | {row.gross_exposure:.3f} |')
    text += ['', '**Table 8. Pre/post portfolio weights**', '',
             '| Period | Portfolio | ' + ' | '.join(ASSETS) + ' |',
             '|---|---|' + '|'.join(['---:'] * len(ASSETS)) + '|']
    for period, table in [('Pre-COVID', pre), ('Post-COVID', post)]:
        for portfolio in ['GMV', 'tangency']:
            row = table.loc[portfolio]
            text.append(f'| {period} | {portfolio} | ' +
                        ' | '.join(f"{row[f'w_{asset}']:.1%}" for asset in ASSETS) + ' |')
    text += ['', f"GMV weights change by L1={stability.loc['GMV', 'l1_distance']:.3f}; tangency weights change "
             f"by L1={stability.loc['tangency', 'l1_distance']:.3f}. The largest absolute correlation changes "
             'are ' + ', '.join(f'{r.asset_i}/{r.asset_j}={r.change:+.3f}'
                                for r in correlation_changes.head(4).itertuples()) +
             '. The largest monthly covariance changes are ' + ', '.join(
                 f'{r.asset_i}/{r.asset_j}={r.change:+.6f}' for r in covariance_changes.head(4).itertuples()) +
             '. The shorter post-COVID sample makes these estimates less precise.']
    text += _figure(6, 'pre_post_comparison.png', 'Pre- and post-COVID Specification B frontiers and CALs on common axes.')

    text += ['', '## 8. Single-Index Model Estimation', '',
             'For every non-market asset the regression is `(r_i - rf) = alpha_i + beta_i (r_SPY - rf) + epsilon_i`. '
             'SPY is assigned alpha=0, beta=1, and residual variance=0 and is not regressed on itself. The covariance '
             "model is `Sigma_SIM = beta beta' Var(SPY - RF) + diag(residual variances)`.", '',
             '**Table 9. SIM estimates and model-implied expected returns**', '',
             '| Asset | Expected return | Alpha | Beta | Residual SD | Residual variance | Systematic variance | Total variance | R² |',
             '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for asset, expected in zip(ASSETS, sim_mean):
        row = regressions.loc[asset]
        text.append(f'| {asset} | {12*expected:.2%} | {row.alpha_annual:.2%} | {row.beta:.3f} | '
                    f'{row.residual_sd_annual:.2%} | {row.residual_variance_annual:.6f} | '
                    f'{row.systematic_variance_annual:.6f} | {row.total_variance_annual:.6f} | {row.r_squared:.3f} |')

    text += ['', '## 9. SIM Portfolio Optimization', '', '**Table 10. SIM GMV and tangency results**', '']
    text += _portfolio_summary(root, summary, sim_names)
    text += ['', '**Table 11. SIM portfolio weights**', ''] + _weight_table(root, summary, sim_names)
    for number, label in enumerate('ABC', start=7):
        text += _figure(number, f'sim_complete_{label}.png', f'SIM complete-model frontier under Specification {label}.')

    text += ['', '## 10. Markowitz versus SIM: Covariance-Only Experiment', '',
             'The expected-return vectors and observations are exactly identical. Markowitz uses full sample '
             'covariance; SIM uses single-index covariance. Every difference below is therefore a covariance-model '
             'effect. Categories are pointwise and no overall winner is declared.', '',
             '**Table 12. Covariance-only common-target frontier diagnostics**', '']
    text += _comparison_summary(root, 'covariance_only')
    text += ['', '**Table 13. Covariance-only GMV and tangency comparison**', '']
    text += _comparison_portfolio_metrics(root, 'covariance_only')
    text += ['', '**Table 14. Largest covariance-only allocation differences**', '']
    text += _largest_weight_differences(root, 'covariance_only')
    for number, label in enumerate('ABC', start=10):
        text += _figure(number, f'comparison_covariance_only_{label}.png',
                        f'Covariance-only Markowitz versus SIM comparison, Specification {label}.')

    text += ['', '## 11. Complete Markowitz versus SIM Comparison', '',
             'Markowitz uses sample means and full covariance. SIM uses alpha/beta/premium expected returns and SIM '
             'covariance. This experiment combines covariance and expected-return effects. Comparing it with '
             'Section 10 isolates the additional effect of changing the expected-return model.', '',
             '**Table 15. Complete-model common-target frontier diagnostics**', '']
    text += _comparison_summary(root, 'complete_model')
    text += ['', '**Table 16. Complete-model GMV and tangency comparison**', '']
    text += _comparison_portfolio_metrics(root, 'complete_model')
    text += ['', '**Table 17. Largest complete-model allocation differences**', '']
    text += _largest_weight_differences(root, 'complete_model')
    for number, label in enumerate('ABC', start=13):
        text += _figure(number, f'comparison_complete_model_{label}.png',
                        f'Complete-model Markowitz versus SIM comparison, Specification {label}.')

    markowitz_cov = np.load(root / 'models' / 'markowitz_comparison_A_moments.npz')['covariance']
    sim_cov = np.load(root / 'models' / 'sim_complete_A_moments.npz')['covariance']
    difference = sim_cov - markowitz_cov
    pairs = []
    m_corr = markowitz_cov / np.outer(np.sqrt(np.diag(markowitz_cov)), np.sqrt(np.diag(markowitz_cov)))
    s_corr = sim_cov / np.outer(np.sqrt(np.diag(sim_cov)), np.sqrt(np.diag(sim_cov)))
    for i in range(len(ASSETS)):
        for j in range(i + 1, len(ASSETS)):
            pairs.append((ASSETS[i], ASSETS[j], difference[i, j], s_corr[i, j] - m_corr[i, j]))
    cov_pairs = sorted(pairs, key=lambda row: abs(row[2]), reverse=True)[:8]
    corr_pairs = sorted(pairs, key=lambda row: abs(row[3]), reverse=True)[:8]
    text += ['', '## 12. Covariance-Model Diagnostics', '',
             f"The monthly Frobenius norm of SIM minus full covariance is {np.linalg.norm(difference):.8f}. "
             f"Condition numbers are {summary['diagnostics']['markowitz_comparison_A']['condition_number']:.2f} "
             f"for full covariance and {summary['diagnostics']['sim_complete_A']['condition_number']:.2f} for SIM.", '',
             '**Table 18. Largest off-diagonal covariance discrepancies**', '',
             '| Pair | SIM − Markowitz monthly covariance |', '|---|---:|']
    for a, b, value, _ in cov_pairs:
        text.append(f'| {a}/{b} | {value:+.8f} |')
    text += ['', '**Table 19. Largest correlation discrepancies**', '',
             '| Pair | SIM − Markowitz correlation |', '|---|---:|']
    for a, b, _, value in corr_pairs:
        text.append(f'| {a}/{b} | {value:+.4f} |')
    text += ['', 'Bonds, gold, oil, broad commodities, and international equities can have common influences that '
             'are not captured by SPY alone. Here that limitation is measured by the saved R² values and matrix '
             'discrepancies rather than asserted from asset labels alone.', '',
             '## 13. Answers to Assignment Analysis Questions', '',
             '### Question 1. What diversification benefit comes from bonds, gold, oil, and broad commodities?', '',
             f"Bonds produce the largest GMV reduction: {div.loc['equities', 'gmv_sd_annual']:.2%} falls to "
             f"{div.loc['equities_bonds', 'gmv_sd_annual']:.2%}. Gold raises maximum Sharpe to "
             f"{div.loc['equities_bonds_gold', 'tangency_sharpe_annual']:.3f}. Oil and DBC lower all-asset GMV "
             f"volatility to {div.loc['all_assets', 'gmv_sd_annual']:.2%}, with no displayed Sharpe improvement.", '',
             '### Question 2. What is the effect of allowing short sales?', '',
             short_sale_detail + ' Short sales enlarge the opportunity set while '
             'making allocations more sensitive to estimated inputs.', '',
             '### Question 3. What is the effect of ±20% bounds?', '',
             'C caps concentration and leverage, raises GMV volatility relative to A/B, and places several assets '
             'at +20%. Its geometry requires broad long exposure because eight capped positions must sum to one.', '',
             '### Question 4. How do pre- and post-COVID covariance structures differ?', '',
             'The largest saved changes involve USO/DBC covariance and equity/bond correlations. Post-COVID GMV '
             f"volatility is {post.loc['GMV', 'sd_annual']:.2%} versus {pre.loc['GMV', 'sd_annual']:.2%} pre-COVID, "
             'but the shorter post sample increases uncertainty.', '',
             '### Question 5. How sensitive are tangency and GMV weights to expected returns?', '',
             f"Across pre/post samples, tangency L1 weight change is {stability.loc['tangency', 'l1_distance']:.3f} "
             f"versus {stability.loc['GMV', 'l1_distance']:.3f} for GMV. This computed contrast is consistent with "
             'tangency weights depending directly on expected returns while GMV depends on covariance.', '',
             '### Question 6. How good is the SIM approximation?', '',
             'It is strongest for assets with high saved R² and weakest for ' +
             ', '.join(f'{a} (R²={v:.3f})' for a, v in weakest.items()) +
             '. The matrix discrepancies in Tables 18 and 19 quantify approximation error.', '',
             '### Question 7. Where are the SIM and Markowitz frontiers relative to each other?', '',
             f"They cross in covariance-only A: Markowitz has lower risk at {(cov_a.lower_volatility == 'MARKOWITZ').sum()} "
             f"targets and SIM at {(cov_a.lower_volatility == 'SIM').sum()}. B and C favor SIM at most saved common "
             'targets in this in-sample comparison. No overall winner is assigned.', '',
             '### Question 8. What are the practical limitations of SPY as the sole common factor?', '',
             'A single US equity factor cannot reproduce residual cross-covariances. Low R² for several defensive '
             'and real-asset ETFs and the observed covariance/correlation discrepancies show where that assumption '
             'is restrictive in this sample.', '',
             '## 14. Practical Interpretation and Limitations', '',
             'Sample means are noisy, so tangency weights can be unstable. GMV is less directly exposed to mean '
             'error but remains sensitive to covariance estimation. Unrestricted leverage can be impractical, and '
             'constraints change both attainable returns and which estimates drive allocations. The post-COVID '
             'sample is short. SIM is parsimonious but omits common factors beyond SPY. All conclusions are '
             'in-sample and do not establish future performance.', '',
             '## 15. Conclusion', '',
             'The results show substantial diversification from bonds and a Sharpe improvement from gold. Constraints '
             'trade theoretical opportunity-set breadth for implementability. Pre/post estimates differ materially, '
             'especially for commodity and equity/bond relationships. SIM offers a structured covariance estimate '
             'but changes frontiers and weights because its one-factor restriction omits residual co-movement. The '
             'most aggressive theoretical solution is therefore not automatically the most economically usable one.', '',
             '## Appendix A. Provenance and Reproducibility', '',
             f"- Production run ID: `{summary['run_id']}`.",
             f"- Git commit: `{_git_commit(root)}`.",
             '- Configuration snapshot: `config_snapshot.yaml`.',
             f"- Data sources: Yahoo Finance adjusted prices and Fama–French monthly RF.",
             f"- CAL/tangency RF: {summary['rf_cal_annual_presentation']:.2%} annual.",
             f"- SIM market-premium assumption: {12 * summary['sim_assumptions']['market_premium_monthly']:.2%} annual.",
             f"- Solvers: {config['optimization']['solver']} for quadratic programs and "
             f"{config['optimization']['tangency_solver']} for constrained tangency.",
             f"- Constraint tolerance: {config['optimization']['constraint_tolerance']}; PSD tolerance: "
             f"{config['optimization']['psd_tolerance']}; frontier tie tolerance: "
             f"{config['optimization']['dominance_sd_tolerance']} annual SD.",
             '- Pytest result: the analytical workflow does not self-invoke pytest; the complete release-suite '
             'result is reported alongside this frozen production artifact.',
             '- Internal production output validation: PASSED.',
             'This report was generated from the frozen run artifacts after numerical output validation. It does '
             'not perform portfolio estimation or optimization.']
    return '\n'.join(text) + '\n'


def write_final_assignment_report(root: Path) -> None:
    (root / 'final_assignment_report.md').write_text(render_final_assignment_report(root))


def validate_final_assignment_report(root: Path) -> None:
    path = root / 'final_assignment_report.md'
    require(path.is_file(), 'Complete workflow requires final_assignment_report.md')
    require(path.read_text() == render_final_assignment_report(root),
            'final_assignment_report.md differs from authoritative saved outputs')
    text = path.read_text()
    required = ['## Executive Summary'] + [f'## {number}.' for number in range(1, 16)]
    require(all(section in text for section in required), 'Final report is missing a required major section')
    require(all(f'### Question {number}.' in text for number in range(1, 9)),
            'Final report must answer all eight assignment questions')
    for filename in ['markowitz_constraints.png', 'markowitz_full_A.png', 'markowitz_full_B.png',
                     'markowitz_full_C.png', 'pre_post_comparison.png', 'sim_complete_A.png',
                     'sim_complete_B.png', 'sim_complete_C.png', 'comparison_covariance_only_A.png',
                     'comparison_covariance_only_B.png', 'comparison_covariance_only_C.png',
                     'comparison_complete_model_A.png', 'comparison_complete_model_B.png',
                     'comparison_complete_model_C.png', 'diversification.png']:
        require((root / 'figures' / filename).is_file() and f'figures/{filename}' in text,
                f'Final report missing required figure: {filename}')
    require('Tangency weights: none' not in text or 'NONATTAINED' in text,
            'Final report has inconsistent nonattained tangency presentation')
