"""Deterministic commentary with explicitly separated modeling effects."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import yaml
from src.validation import require


def portfolio_lines(root: Path, summary: dict, names: list[str]) -> list[str]:
    lines = []
    for name in names:
        table = pd.read_csv(root / 'tables' / f'{name}_portfolios.csv').set_index('portfolio')
        tangency = summary['tangencies'][name]
        line = f"- {name}: GMV volatility {table.loc['GMV', 'sd_annual']:.2%}; "
        if tangency['status'] == 'NONATTAINED':
            line += (f"tangency NONATTAINED; annualized Sharpe supremum "
                     f"{tangency['sharpe_supremum_annual']:.3f}; no finite tangency weights, gross exposure or CAL.")
        else:
            line += (f"tangency Sharpe {table.loc['tangency', 'sharpe_annual']:.3f}; "
                     f"tangency gross exposure {table.loc['tangency', 'gross_exposure']:.3f}.")
        lines.append(line)
    return lines


def write_markowitz_report(root: Path, summary: dict) -> None:
    text = ['BUFN741 — Markowitz results', '',
            'Scope: Markowitz only. This document is not the complete multi-model assignment report.',
            f"Assignment completeness: {summary['completeness']}.", '']
    for name, sample in summary['samples'].items():
        text.append(f"- {name}: {sample['start']} through {sample['end']}, N={sample['N']}.")
    text += [''] + portfolio_lines(root, summary, [name for name in summary['results'] if name.startswith('markowitz_')])
    if summary['blocked_stages']:
        text += ['', 'Unavailable sections: SIM and its dependent comparisons/final report.',
                 summary['blocked_stages']['ff_data']['reason']]
    text += ['', 'All calculation inputs are monthly; displayed means, SDs and Sharpes are annualized.',
             'NONATTAINED is an economic outcome, not a failed solver point. The limiting Sharpe is not',
             'achieved by any finite fully invested portfolio. No attained CAL is drawn for that case.']
    (root / 'markowitz_report.md').write_text('\n'.join(text) + '\n')


def _weights(row: pd.Series, assets: list[str]) -> str:
    return ', '.join(f'{asset}={row[f"w_{asset}"]:.2%}' for asset in assets)


def render_sim_report(root: Path) -> str:
    """Render the SIM-only report from persisted, production-validated artifacts."""
    summary = json.loads((root / 'results_summary.json').read_text())
    require(summary['completeness'] == 'COMPLETE', 'SIM report requires complete SIM results')
    regressions = pd.read_csv(root / 'models' / 'sim_regressions.csv', index_col='asset',
                              float_precision='round_trip')
    assumptions = json.loads((root / 'models' / 'sim_assumptions.json').read_text())
    assets = regressions.index.tolist()
    means = np.load(root / 'models' / 'sim_complete_A_moments.npz')['mean']
    require(len(means) == len(assets), 'SIM report mean/asset length mismatch')
    policy = summary['sample_policy']

    text = ['BUFN741 — Single-Index Model results', '',
            'Scope: Single-Index Model only. This document is not the complete multi-model assignment report.',
            f"Assignment completeness: {summary['completeness']}.", '', 'Sample observations:',
            f"- ETF sample: {policy['etf_sample']['start']} through {policy['etf_sample']['end']}, "
            f"N={policy['etf_sample']['N']}.",
            f"- Available Fama–French RF sample: {policy['rf_sample']['start']} through "
            f"{policy['rf_sample']['end']}, N={policy['rf_sample']['N']}.",
            f"- SIM common sample: {policy['sim_common']['start']} through {policy['sim_common']['end']}, "
            f"N={policy['sim_common']['N']}.",
            f"- Markowitz comparison sample: {policy['markowitz_comparison']['start']} through "
            f"{policy['markowitz_comparison']['end']}, N={policy['markowitz_comparison']['N']}.",
            f"- Accepted RF trailing lag: {'yes' if policy['lag_accepted'] else 'no'}; "
            f"{policy['trailing_rf_lag_months']} month(s), configured maximum "
            f"{policy['max_trailing_rf_lag_months']}.", '',
            'SIM estimation summary', '',
            f"Expected-return method: {assumptions['expected_return_method']}; fixed annual RF "
            f"{12 * assumptions['fixed_rf_monthly']:.2%}; annual market risk premium "
            f"{12 * assumptions['market_premium_monthly']:.2%}.",
            'Displayed expected returns, alpha, residual risk, systematic variance and total variance are annualized. '
            'Beta, systematic variance share and R² are unitless.', '',
            '| Asset | Expected return | Alpha | Beta | Residual SD | Residual variance | Systematic variance | '
            'SIM total variance | Systematic share | R² |',
            '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for asset, expected_return in zip(assets, means):
        row = regressions.loc[asset]
        text.append(
            f"| {asset} | {12 * expected_return:.4%} | {row.alpha_annual:.4%} | {row.beta:.4f} | "
            f"{row.residual_sd_annual:.4%} | {row.residual_variance_annual:.8f} | "
            f"{row.systematic_variance_annual:.8f} | {row.total_variance_annual:.8f} | "
            f"{row.systematic_variance_share:.2%} | {row.r_squared:.4f} |")
    text += ['', 'SPY is the market asset: alpha=0, beta=1 and residual variance=0. '
             'SPY is not regressed on itself.',
             'R² is the saved single-factor fit diagnostic used here to rank how much asset variation is described '
             'by the market factor; no separate unsaved ranking statistic is inferred.', '',
             'SIM covariance structure', '',
             '`Sigma_SIM = beta beta\' Var(SPY - RF) + diag(residual variances)`', '',
             'The beta and covariance calculations use the same aligned SPY-minus-Fama–French-RF factor. '
             'Cross-asset covariance is generated only through common SPY market exposure; residual '
             'cross-covariances are assumed to be zero.']

    for label in 'ABC':
        name = f'sim_complete_{label}'
        portfolios = pd.read_csv(root / 'tables' / f'{name}_portfolios.csv',
                                 float_precision='round_trip').set_index('portfolio')
        tangency = json.loads((root / 'models' / f'{name}_tangency.json').read_text())
        gmv = portfolios.loc['GMV']
        text += ['', f'Specification {label}', '',
                 f"- GMV annualized expected return: {gmv.mean_annual:.4%}.",
                 f"- GMV annualized volatility: {gmv.sd_annual:.4%}.",
                 f"- GMV gross exposure: {gmv.gross_exposure:.6f}.",
                 f"- GMV weights: {_weights(gmv, assets)}.",
                 f"- Tangency status: {tangency['status']}."]
        if tangency['status'] == 'NONATTAINED':
            text += [f"- Tangency annualized expected return: not attained.",
                     f"- Tangency annualized volatility: not attained.",
                     f"- Annualized Sharpe supremum: {tangency['sharpe_supremum_annual']:.6f}.",
                     '- Tangency gross exposure: no finite value.',
                     '- Tangency weights: none; no finite tangency portfolio or attained CAL exists.']
        else:
            require(tangency['status'] == 'ATTAINED' and 'tangency' in portfolios.index,
                    f'{name}: invalid saved tangency state for SIM report')
            tangent = portfolios.loc['tangency']
            text += [f"- Tangency annualized expected return: {tangent.mean_annual:.4%}.",
                     f"- Tangency annualized volatility: {tangent.sd_annual:.4%}.",
                     f"- Tangency annualized Sharpe ratio: {tangent.sharpe_annual:.6f}.",
                     f"- Tangency gross exposure: {tangent.gross_exposure:.6f}.",
                     f"- Tangency weights: {_weights(tangent, assets)}."]

    non_market = regressions.drop(index='SPY')
    largest_betas = non_market.beta.sort_values(ascending=False).head(3)
    residual_risk = non_market.residual_sd_annual.sort_values(ascending=False).head(3)
    systematic_share = non_market.systematic_variance_share.sort_values(ascending=False).head(3)
    weakest_fit = non_market.r_squared.sort_values().head(3)
    diag = summary['diagnostics']['sim_complete_A']
    text += ['', 'SIM diagnostics', '',
             f"- Covariance validation: symmetric and PSD; minimum monthly eigenvalue "
             f"{min(diag['eigenvalues_monthly']):.10g}; condition number {diag['condition_number']:.4f}.",
             '- Largest non-market betas: ' + ', '.join(f'{a}={v:.4f}' for a, v in largest_betas.items()) + '.',
             '- Largest non-market residual risks (annualized SD): ' +
             ', '.join(f'{a}={v:.4%}' for a, v in residual_risk.items()) + '.',
             '- Largest non-market systematic variance shares: ' +
             ', '.join(f'{a}={v:.2%}' for a, v in systematic_share.items()) + '.',
             '- Assets least well described by SPY (lowest saved R²): ' +
             ', '.join(f'{a}={v:.4f}' for a, v in weakest_fit.items()) + '.']
    for label in 'ABC':
        hits = summary['diagnostics'][f'sim_complete_{label}']['bound_hits']
        description = ('none' if not hits else '; '.join(
            f"{hit['portfolio']} {hit['asset']}={hit['weight']:.6f}" for hit in hits))
        text.append(f'- Specification {label} binding constraints: {description}.')

    common = policy['sim_common']
    text += ['', 'Part 2 comparison context', '',
             'The covariance-only comparison uses an exactly identical expected-return vector on both sides.',
             f"Markowitz comparison and SIM estimates both use {common['start']} through {common['end']} "
             f"(N={common['N']}). Differences in that experiment therefore reflect covariance structure only. "
             'The complete comparison remains in the separate comparison tables and complete report.', '',
             'Methodological note', '',
             'All calculations use monthly units. Displayed expected returns and variances are multiplied by 12; '
             'volatilities and Sharpe ratios are multiplied by sqrt(12).',
             'Historical Fama–French RF observations are used for excess-return regressions. The configured fixed '
             f"{summary['rf_cal_annual_presentation']:.2%} annual RF is used for CAL and tangency calculations.",
             f"The {policy['trailing_rf_lag_months']}-month RF lag relative to Yahoo was accepted under the "
             'configured trailing-lag policy.']
    return '\n'.join(text) + '\n'


def write_sim_report(root: Path) -> None:
    (root / 'sim_report.md').write_text(render_sim_report(root))


def validate_sim_report(root: Path) -> None:
    path = root / 'sim_report.md'
    require(path.is_file(), 'Successful SIM analysis requires sim_report.md')
    require(path.read_text() == render_sim_report(root),
            'sim_report.md differs from authoritative saved SIM outputs')


def _comparison_portfolio_lines(root: Path, summary: dict, name: str,
                                model_label: str, assets: list[str]) -> list[str]:
    portfolios = pd.read_csv(root / 'tables' / f'{name}_portfolios.csv',
                             float_precision='round_trip').set_index('portfolio')
    tangency = json.loads((root / 'models' / f'{name}_tangency.json').read_text())
    gmv = portfolios.loc['GMV']
    hits = summary['diagnostics'][name]['bound_hits']
    hit_text = ('none' if not hits else '; '.join(
        f"{hit['portfolio']} {hit['asset']}={hit['weight']:.6f}" for hit in hits))
    lines = [f'**{model_label}**', '',
             f"- GMV annualized expected return: {gmv.mean_annual:.4%}.",
             f"- GMV annualized volatility: {gmv.sd_annual:.4%}.",
             f"- GMV gross exposure: {gmv.gross_exposure:.6f}.",
             f"- GMV weights: {_weights(gmv, assets)}.",
             f"- Tangency status: {tangency['status']}."]
    if tangency['status'] == 'NONATTAINED':
        lines += ['- Tangency annualized expected return: not attained.',
                  '- Tangency annualized volatility: not attained.',
                  f"- Annualized Sharpe supremum: {tangency['sharpe_supremum_annual']:.6f}.",
                  '- Tangency gross exposure: no finite value.',
                  '- Tangency weights: none; no finite tangency portfolio or attained CAL exists.']
    else:
        require(tangency['status'] == 'ATTAINED' and 'tangency' in portfolios.index,
                f'{name}: invalid saved tangency state for comparison report')
        tangent = portfolios.loc['tangency']
        lines += [f"- Tangency annualized expected return: {tangent.mean_annual:.4%}.",
                  f"- Tangency annualized volatility: {tangent.sd_annual:.4%}.",
                  f"- Tangency annualized Sharpe ratio: {tangent.sharpe_annual:.6f}.",
                  f"- Tangency gross exposure: {tangent.gross_exposure:.6f}.",
                  f"- Tangency weights: {_weights(tangent, assets)}."]
    lines.append(f'- Weights at or near bounds: {hit_text}.')
    return lines


def _frontier_summary(frame: pd.DataFrame) -> dict:
    require(len(frame) > 0, 'Comparison report requires common frontier targets')
    counts = frame.lower_volatility.value_counts().reindex(['MARKOWITZ', 'SIM', 'TIE'], fill_value=0)
    return dict(minimum=float(frame.sim_minus_markowitz_sd.min()),
                maximum=float(frame.sim_minus_markowitz_sd.max()),
                mean_absolute=float(frame.sim_minus_markowitz_sd.abs().mean()),
                counts={name: int(counts[name]) for name in counts.index},
                shares={name: float(counts[name] / len(frame)) for name in counts.index},
                tolerance=float(frame.sd_tolerance_annual.iloc[0]), N=len(frame))


def _weight_sensitivity_lines(frame: pd.DataFrame, portfolio: str, markowitz_hits: set,
                              sim_hits: set, tolerance: float) -> list[str]:
    rows = frame.loc[frame.portfolio == portfolio].copy()
    if rows.empty:
        return [f'**{portfolio} weight sensitivity:** unavailable because at least one tangency is NONATTAINED.'
                if portfolio == 'tangency' else '**GMV weight sensitivity:** unavailable.']
    rows['absolute_difference'] = rows.sim_minus_markowitz.abs()
    lines = [f'**{portfolio} weight sensitivity**', '',
             '| Asset | Markowitz | SIM | SIM − Markowitz | Absolute difference | Sign reversal | Bound status changed |',
             '|---|---:|---:|---:|---:|:---:|:---:|']
    for row in rows.itertuples():
        sign_reversal = abs(row.markowitz) > tolerance and abs(row.sim) > tolerance and row.markowitz * row.sim < 0
        bound_change = ((portfolio, row.asset) in markowitz_hits) != ((portfolio, row.asset) in sim_hits)
        lines.append(f'| {row.asset} | {row.markowitz:.4%} | {row.sim:.4%} | '
                     f'{row.sim_minus_markowitz:.4%} | {row.absolute_difference:.4%} | '
                     f'{"YES" if sign_reversal else "NO"} | {"YES" if bound_change else "NO"} |')
    largest = rows.sort_values('absolute_difference', ascending=False).head(3)
    lines += ['', '- Largest changes: ' + ', '.join(
        f'{row.asset}={row.absolute_difference:.4%}' for row in largest.itertuples()) + '.']
    return lines


def _matrix_lines(matrix: np.ndarray, assets: list[str]) -> list[str]:
    lines = ['| Asset | ' + ' | '.join(assets) + ' |',
             '|---|' + '|'.join(['---:'] * len(assets)) + '|']
    for asset, row in zip(assets, matrix):
        lines.append(f'| {asset} | ' + ' | '.join(f'{value:.8f}' for value in row) + ' |')
    return lines


def render_model_comparison_report(root: Path) -> str:
    """Render the cross-model report solely from validated saved artifacts."""
    summary = json.loads((root / 'results_summary.json').read_text())
    require(summary['completeness'] == 'COMPLETE' and summary['comparisons'],
            'Model comparison report requires completed comparisons')
    policy = summary['sample_policy']
    markowitz_sample, sim_sample = policy['markowitz_comparison'], policy['sim_common']
    require(markowitz_sample == sim_sample, 'Comparison report requires identical model samples')
    assets = markowitz_sample['assets']
    config = yaml.safe_load((root / 'config_snapshot.yaml').read_text())
    weight_tolerance = float(config['optimization']['constraint_tolerance'])
    experiments = [('covariance_only', 'sim_covariance_only',
                    'Experiment 1 — Covariance-model effect only'),
                   ('complete_model', 'sim_complete',
                    'Experiment 2 — Complete model comparison')]
    text = ['BUFN741 — Markowitz vs. Single-Index Model Comparison', '',
            'Scope: dedicated cross-model comparison report. It complements `markowitz_report.md` and '
            '`sim_report.md` and does not replace either model-specific report.', '',
            'Sample alignment', '',
            f"- Markowitz comparison sample: {markowitz_sample['start']} through {markowitz_sample['end']}, "
            f"N={markowitz_sample['N']}.",
            f"- SIM common sample: {sim_sample['start']} through {sim_sample['end']}, N={sim_sample['N']}.",
            'The direct comparison uses exactly the same observations for both models, so sample timing does not '
            'contaminate the model differences.', '',
            'All portfolio calculations use monthly units. Displayed expected returns, volatilities and Sharpe '
            f"ratios are annualized. CAL and tangency calculations use the configured fixed annual RF of "
            f"{summary['rf_cal_annual_presentation']:.2%}."]

    frontier_summaries, stability_values, weight_frames = {}, {}, {}
    for experiment, sim_prefix, heading in experiments:
        text += ['', heading, '']
        if experiment == 'covariance_only':
            text += ['Markowitz and SIM use an exactly identical expected-return vector. Markowitz uses the full '
                     'sample covariance matrix; SIM uses the single-index implied covariance matrix. Differences '
                     'in this experiment therefore reflect covariance structure only.']
        else:
            text += ['Markowitz uses its sample mean vector and full covariance matrix. SIM uses its model-implied '
                     'expected-return vector and SIM covariance matrix. Differences therefore combine expected-return '
                     'and covariance assumptions.']
        for label in 'ABC':
            markowitz_name, sim_name = f'markowitz_comparison_{label}', f'{sim_prefix}_{label}'
            means = pd.read_csv(root / 'tables' / f'comparison_{experiment}_{label}_means.csv',
                                float_precision='round_trip')
            if experiment == 'covariance_only':
                require(np.array_equal(means.markowitz.to_numpy(), means.sim.to_numpy()),
                        f'Comparison report: covariance-only means differ for {label}')
            text += ['', f'### Specification {label}', '']
            text += _comparison_portfolio_lines(root, summary, markowitz_name, 'Markowitz', assets)
            text += [''] + _comparison_portfolio_lines(root, summary, sim_name, 'SIM', assets)

            dominance = pd.read_csv(root / 'tables' / f'comparison_{experiment}_{label}_frontier_dominance.csv',
                                    float_precision='round_trip')
            frontier_summaries[(experiment, label)] = fs = _frontier_summary(dominance)
            text += ['', '**Common-target efficient-frontier comparison**', '',
                     f"The overlapping efficient ranges contain {fs['N']} identical expected-return targets. "
                     f"The annual-SD tie tolerance is {fs['tolerance']:.10g}.",
                     f"- Minimum SIM-minus-Markowitz volatility difference: {fs['minimum']:.6%}.",
                     f"- Maximum SIM-minus-Markowitz volatility difference: {fs['maximum']:.6%}.",
                     f"- Mean absolute volatility difference: {fs['mean_absolute']:.6%}.",
                     f"- MARKOWITZ: {fs['counts']['MARKOWITZ']} targets ({fs['shares']['MARKOWITZ']:.2%}).",
                     f"- SIM: {fs['counts']['SIM']} targets ({fs['shares']['SIM']:.2%}).",
                     f"- TIE: {fs['counts']['TIE']} targets ({fs['shares']['TIE']:.2%}).",
                     'These are pointwise classifications; no overall winner is assigned.', '',
                     '| Target return | Markowitz volatility | SIM volatility | SIM − Markowitz | Lower volatility |',
                     '|---:|---:|---:|---:|:---:|']
            for row in dominance.itertuples():
                text.append(f'| {row.target_annual:.4%} | {row.markowitz_sd_annual:.4%} | '
                            f'{row.sim_sd_annual:.4%} | {row.sim_minus_markowitz_sd:.4%} | '
                            f'{row.lower_volatility} |')

            differences = pd.read_csv(root / 'tables' / f'comparison_{experiment}_{label}_weight_differences.csv',
                                      float_precision='round_trip')
            weight_frames[(experiment, label)] = differences
            m_hits = {(item['portfolio'], item['asset']) for item in summary['diagnostics'][markowitz_name]['bound_hits']}
            s_hits = {(item['portfolio'], item['asset']) for item in summary['diagnostics'][sim_name]['bound_hits']}
            text += [''] + _weight_sensitivity_lines(differences, 'GMV', m_hits, s_hits, weight_tolerance)
            text += [''] + _weight_sensitivity_lines(differences, 'tangency', m_hits, s_hits, weight_tolerance)
            metrics = pd.read_csv(root / 'tables' / f'comparison_{experiment}_{label}_metric_differences.csv',
                                  float_precision='round_trip')
            gmv_gross = metrics.query("portfolio == 'GMV' and metric == 'gross_exposure'").iloc[0]
            text += ['', f"- GMV gross-exposure difference (SIM − Markowitz): "
                     f"{gmv_gross.sim_minus_markowitz:.6f}."]
            stability = pd.read_csv(root / 'tables' / f'comparison_{experiment}_{label}_weight_stability.csv',
                                    float_precision='round_trip').set_index('portfolio')
            stability_values[(experiment, label)] = stability

    markowitz_moments = np.load(root / 'models' / 'markowitz_comparison_A_moments.npz')
    sim_moments = np.load(root / 'models' / 'sim_complete_A_moments.npz')
    markowitz_cov, sim_cov = markowitz_moments['covariance'], sim_moments['covariance']
    covariance_difference = sim_cov - markowitz_cov
    markowitz_sd = np.sqrt(np.diag(markowitz_cov))
    sim_sd = np.sqrt(np.diag(sim_cov))
    markowitz_corr = markowitz_cov / np.outer(markowitz_sd, markowitz_sd)
    sim_corr = sim_cov / np.outer(sim_sd, sim_sd)
    covariance_rows = []
    correlation_rows = []
    for i, asset_i in enumerate(assets):
        for j in range(i, len(assets)):
            covariance_rows.append((asset_i, assets[j], markowitz_cov[i, j], sim_cov[i, j],
                                    covariance_difference[i, j]))
        for j in range(i + 1, len(assets)):
            correlation_rows.append((asset_i, assets[j], markowitz_corr[i, j], sim_corr[i, j],
                                     sim_corr[i, j] - markowitz_corr[i, j]))
    covariance_rows.sort(key=lambda row: abs(row[4]), reverse=True)
    correlation_rows.sort(key=lambda row: abs(row[4]), reverse=True)
    m_condition = summary['diagnostics']['markowitz_comparison_A']['condition_number']
    s_condition = summary['diagnostics']['sim_complete_A']['condition_number']
    text += ['', 'Covariance-structure comparison', '',
             'The full Markowitz covariance matrix retains every sample covariance. The SIM-implied covariance '
             'generates cross-asset covariance only through common SPY exposure and assumes zero residual '
             'cross-covariances.',
             f'- Markowitz covariance condition number: {m_condition:.6f}.',
             f'- SIM covariance condition number: {s_condition:.6f}.',
             f'- Monthly covariance-difference Frobenius norm: {np.linalg.norm(covariance_difference):.10g}.',
             f'- Maximum absolute monthly covariance discrepancy: {max(abs(row[4]) for row in covariance_rows):.10g}.', '',
             '**Full Markowitz covariance matrix (monthly)**', '']
    text += _matrix_lines(markowitz_cov, assets)
    text += ['', '**SIM-implied covariance matrix (monthly)**', '']
    text += _matrix_lines(sim_cov, assets)
    text += ['',
             '**Largest absolute covariance discrepancies (monthly covariance)**', '',
             '| Asset i | Asset j | Markowitz | SIM | SIM − Markowitz |',
             '|---|---|---:|---:|---:|']
    for asset_i, asset_j, markowitz_value, sim_value, difference in covariance_rows[:10]:
        text.append(f'| {asset_i} | {asset_j} | {markowitz_value:.10f} | {sim_value:.10f} | {difference:.10f} |')
    text += ['', '**Largest absolute correlation discrepancies**', '',
             '| Asset i | Asset j | Markowitz | SIM | SIM − Markowitz |',
             '|---|---|---:|---:|---:|']
    for asset_i, asset_j, markowitz_value, sim_value, difference in correlation_rows[:10]:
        text.append(f'| {asset_i} | {asset_j} | {markowitz_value:.6f} | {sim_value:.6f} | {difference:.6f} |')

    regressions = pd.read_csv(root / 'models' / 'sim_regressions.csv', index_col='asset',
                              float_precision='round_trip')
    weakest = regressions.drop(index='SPY').r_squared.sort_values().head(3)
    text += ['', 'Covariance Effect', '']
    for label in 'ABC':
        fs = frontier_summaries[('covariance_only', label)]
        text.append(f"- Specification {label}: MARKOWITZ {fs['counts']['MARKOWITZ']}, SIM "
                    f"{fs['counts']['SIM']}, TIE {fs['counts']['TIE']} across {fs['N']} common targets; "
                    f"mean absolute annual-volatility difference {fs['mean_absolute']:.6%}.")
    text += ['These differences isolate the covariance model because the saved expected-return vectors are exactly '
             'identical. The SIM restriction removes residual cross-asset covariance and retains only covariance '
             'transmitted through SPY beta exposure.', '', 'Additional Expected-Return Effect', '']
    for label in 'ABC':
        covariance_fs = frontier_summaries[('covariance_only', label)]
        complete_fs = frontier_summaries[('complete_model', label)]
        text.append(f"- Specification {label}: mean absolute frontier difference changes from "
                    f"{covariance_fs['mean_absolute']:.6%} in Experiment 1 to "
                    f"{complete_fs['mean_absolute']:.6%} in Experiment 2; the complete-model counts are "
                    f"MARKOWITZ {complete_fs['counts']['MARKOWITZ']}, SIM {complete_fs['counts']['SIM']}, "
                    f"TIE {complete_fs['counts']['TIE']}.")
    text += ['Experiment 2 changes the SIM expected-return vector in addition to its covariance matrix. Its '
             'increment relative to Experiment 1 is therefore the additional expected-return-model effect; it '
             'must not be interpreted as another covariance-only result.', '', 'Economic interpretation', '',
             '- Assets least naturally represented by SPY as the sole factor, based on the lowest saved R² values: ' +
             ', '.join(f'{asset}={value:.4f}' for asset, value in weakest.items()) + '.',
             '- The largest covariance and correlation discrepancies above identify the assets and pairs for which '
             'the single-index approximation departs most from the full sample covariance structure.']
    for experiment, _, heading in experiments:
        available = []
        for label in 'ABC':
            stability = stability_values[(experiment, label)]
            for portfolio in ['GMV', 'tangency']:
                row = stability.loc[portfolio]
                if row.status == 'AVAILABLE':
                    available.append((float(row.l1_distance), label, portfolio))
        largest = max(available) if available else None
        if largest:
            text.append(f'- {heading}: the largest available portfolio weight L1 change is '
                        f'{largest[0]:.6f} for Specification {largest[1]} {largest[2]}.')
        all_weights = pd.concat((weight_frames[(experiment, label)] for label in 'ABC'), ignore_index=True)
        if not all_weights.empty:
            largest_asset = all_weights.loc[all_weights.sim_minus_markowitz.abs().idxmax()]
            text.append(f'- {heading}: the most sensitive individual saved allocation is '
                        f'{largest_asset.asset} in the {largest_asset.portfolio} comparison, with an absolute '
                        f'weight change of {abs(largest_asset.sim_minus_markowitz):.4%}.')
        gmv_values = ', '.join(
            f"{label}={stability_values[(experiment, label)].loc['GMV', 'l1_distance']:.6f}" for label in 'ABC')
        gmv_a = float(stability_values[(experiment, 'A')].loc['GMV', 'l1_distance'])
        constraint_effect = ', '.join(
            f"{label} {'reduces' if float(stability_values[(experiment, label)].loc['GMV', 'l1_distance']) < gmv_a else 'amplifies'} "
            f"the difference relative to A" for label in 'BC')
        text.append(f'- {heading}: GMV weight L1 differences by constraint are {gmv_values}; {constraint_effect}.')
        tangency_available = [(label, stability_values[(experiment, label)].loc['tangency']) for label in 'ABC'
                              if stability_values[(experiment, label)].loc['tangency', 'status'] == 'AVAILABLE']
        if len(tangency_available) >= 2:
            baseline_label, baseline = tangency_available[0]
            comparisons = ', '.join(
                f"{label} {'reduces' if float(row.l1_distance) < float(baseline.l1_distance) else 'amplifies'} "
                f"the difference relative to {baseline_label}" for label, row in tangency_available[1:])
            text.append(f'- {heading}: for attained tangencies, {comparisons}.')
    text += ['Constraints can change which assets absorb covariance or mean-model differences. The bound-change '
             'columns and L1 distances above report that effect directly. Pointwise frontier crossings are retained, '
             'and the report deliberately assigns no overall model winner.']
    return '\n'.join(text) + '\n'


def write_model_comparison_report(root: Path) -> None:
    (root / 'model_comparison_report.md').write_text(render_model_comparison_report(root))


def validate_model_comparison_report(root: Path) -> None:
    path = root / 'model_comparison_report.md'
    require(path.is_file(), 'Completed model comparisons require model_comparison_report.md')
    require(path.read_text() == render_model_comparison_report(root),
            'model_comparison_report.md differs from authoritative saved comparison outputs')


def write_interpretation(root: Path, summary: dict) -> None:
    require(summary['completeness'] == 'COMPLETE', 'Complete report requires SIM and comparisons')
    text = ['BUFN741 Group Assignment 2', '==========================', '',
            'All estimation and optimization use monthly units. Annualized means are arithmetic, not CAGR.', '',
            'Sample observations:']
    for name, sample in summary['samples'].items():
        text.append(f"- {name}: {sample['start']} through {sample['end']}, N={sample['N']}.")
    policy = summary['sample_policy']
    text += ['', f"The ETF analysis sample ends {policy['etf_sample']['end']}; the Fama-French RF source ends "
             f"{policy['rf_sample']['end']}. The trailing RF lag is {policy['trailing_rf_lag_months']} month(s) "
             f"and was {'accepted' if policy['lag_accepted'] else 'not accepted'} under the configured "
             f"maximum of {policy['max_trailing_rf_lag_months']}.",
             f"SIM and every direct Markowitz/SIM comparison use the identical common sample "
             f"{policy['sim_common']['start']} through {policy['sim_common']['end']} "
             f"(N={policy['sim_common']['N']}). Main Markowitz results retain the full ETF endpoint."]
    text += ['', 'Comparison 1 (covariance-only) holds the sample mean vector exactly fixed. Changes in risk,',
             'weights and Sharpe therefore isolate the covariance-model effect.',
             'Comparison 2 (complete model) also replaces the means with the configured SIM expected returns.',
             'Its differences combine covariance and expected-return effects. Model-implied frontier dominance',
             'does not establish out-of-sample superiority.', '',
             'SPY has alpha=0, beta=1 and zero residual variance. Other residual variances use SSE/(N-2).',
             'SIM regression and covariance use the same SPY-minus-FF-RF factor and its sample variance.',
             'The fixed forecast RF is deterministic; SPY model risk equals the historical excess-factor variance.',
             'The historical regression RF series is distinct from the fixed CAL and SIM forecast RF assumptions.', '',
             f"Selected results (annualized): main Markowitz ends {policy['etf_sample']['end']}; "
             f"SIM ends {policy['sim_common']['end']}."]
    text += portfolio_lines(root, summary, ['markowitz_full_A', 'markowitz_full_B', 'markowitz_full_C',
                                            'sim_complete_A', 'sim_complete_B', 'sim_complete_C'])
    text += ['', 'CALs assume lending and borrowing at the same configured rate. Portfolio constraints apply to',
             'the risky tangency fund; allocations above 100% scale its holdings and need not satisfy its original bounds.',
             'Results are in-sample. Estimated means can make tangency weights unstable, especially with unlimited',
             'shorting. Inspect gross exposure, bound hits, eigenvalues, and weight-stability diagnostics.',
             'Pre/post covariance differences use monthly units and identical assets within each sample.',
             'Incremental diversification uses the same full-sample dates for every asset subset.',
             'With unchanged long-only rules, a larger opportunity set cannot worsen the true GMV or maximum Sharpe;',
             'small numerical differences should be evaluated against solver tolerances.']
    (root / 'interpretation.md').write_text('\n'.join(text) + '\n')
