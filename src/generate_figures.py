"""Presentation only: all inputs are persisted, precomputed numerical tables."""
from __future__ import annotations
import os
import json
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR', '/tmp/bufn741-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import pandas as pd

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                     'axes.spines.top': False, 'axes.spines.right': False,
                     'savefig.bbox': 'tight', 'axes.grid': True, 'grid.alpha': .2})


def frontier_figure(root: Path, names: dict[str, str], filename: str, title: str, dpi: int,
                    benchmarks: pd.DataFrame | None = None) -> None:
    fig, ax = plt.subplots(figsize=(8, 5.5), layout='constrained')
    for name, label in names.items():
        frontier = pd.read_csv(root / 'tables' / f'{name}_frontier.csv')
        upper = frontier.loc[frontier.efficient]
        cal = pd.read_csv(root / 'tables' / f'{name}_cal.csv')
        portfolios = pd.read_csv(root / 'tables' / f'{name}_portfolios.csv')
        line, = ax.plot(upper.sd_annual, upper.mean_annual, label=label, linewidth=2)
        ax.plot(frontier.sd_annual, frontier.mean_annual, color=line.get_color(), alpha=.25, linewidth=1)
        if not cal.empty:
            ax.plot(cal.sd_annual, cal.mean_annual, '--', color=line.get_color(), linewidth=1, label=f'{label} CAL')
        else:
            status = json.loads((root / 'models' / f'{name}_tangency.json').read_text())['status']
            ax.plot([], [], color=line.get_color(), linestyle='', label=f'{label}: tangency {status}')
        for _, row in portfolios.iterrows():
            ax.scatter(row.sd_annual, row.mean_annual, marker='*' if row.portfolio == 'tangency' else 'o',
                       s=80, color=line.get_color(), zorder=4)
    if benchmarks is not None:
        for _, row in benchmarks.loc[benchmarks.feasible].drop_duplicates('benchmark').iterrows():
            ax.scatter(row.sd_annual, row.mean_annual, marker='x', color='black', s=35)
            ax.annotate(row.benchmark.replace('_', '/'), (row.sd_annual, row.mean_annual),
                        xytext=(4, 5), textcoords='offset points', fontsize=8)
    ax.set(xlabel='Annualized standard deviation', ylabel='Annualized arithmetic expected return', title=title)
    ax.xaxis.set_major_formatter(PercentFormatter(1))
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.legend(fontsize=8, loc='best')
    for extension in ['png', 'pdf']:
        fig.savefig(root / 'figures' / f'{filename}.{extension}', dpi=dpi)
    plt.close(fig)


def diversification_figure(root: Path, dpi: int) -> None:
    table = pd.read_csv(root / 'tables' / 'diversification.csv').query("status == 'PASSED'")
    if table.empty:
        return
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), layout='constrained')
    for ax, column, title in zip(axes, ['gmv_sd_annual', 'tangency_sharpe_annual'],
                               ['GMV annual volatility', 'Tangency annual Sharpe']):
        ax.bar(table.universe, table[column], color='#286a91')
        ax.set_title(title)
        ax.tick_params(axis='x', rotation=25, labelsize=8)
    axes[0].yaxis.set_major_formatter(PercentFormatter(1))
    for extension in ['png', 'pdf']:
        fig.savefig(root / 'figures' / f'diversification.{extension}', dpi=dpi)
    plt.close(fig)
