"""Deterministic commentary with explicitly separated modeling effects."""
from __future__ import annotations
from pathlib import Path
import pandas as pd
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
