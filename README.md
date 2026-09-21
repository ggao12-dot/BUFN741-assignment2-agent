# BUFN741 Assignment 2 analytical harness

Deterministic Markowitz and Single-Index Model portfolio analysis for SPY, EFA,
EEM, TLT, AGG, GLD, USO and DBC. Python 3.10+; Linux/macOS (run locking uses
`fcntl`). No LLM API or credentials are required.

## Install and run

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run_assignment.py --config config/assignment2.yaml
```

The configured ETF endpoint is **August 2026**. Main Markowitz analysis uses that
complete common ETF sample. SIM uses the longest contiguous intersection of ETF
returns and Fama–French RF, and direct Markowitz/SIM comparisons re-estimate the
Markowitz moments on that exact same intersection. A trailing RF release lag is
accepted only when `sim.allow_trailing_rf_lag` is true and it does not exceed
`sim.max_trailing_rf_lag_months` (defaults: true and 2). The accepted lag is
recorded as a warning in state, metadata and the report. Internal RF gaps and
lags beyond the configured tolerance are fatal. No RF is substituted.

With the September 20, 2026 sources, main Markowitz ends August 2026 while SIM
and all direct model comparisons end July 2026. This is a complete run, not a
blocked one. A wholly unavailable FF source can still produce a `PARTIAL` run;
the CLI exits 0 for complete, 2 for partial external dependency, and 1 for an
invalid source, sample-policy violation, or solver failure.

Valid raw caches are reused automatically. Offline execution makes no download:

```bash
python run_assignment.py --config config/assignment2.yaml --offline
python run_assignment.py --config config/assignment2.yaml --resume RUN_ID
python -m pytest -q
```

`data.offline: true` is equivalent to `--offline`. `data.cache: false` refreshes
downloads on online runs; raw sources are still retained for auditing. Download
failures and corrupt sources are logged. Missing/incomplete FF is an external
block; corrupted FF data still fails validation and is not treated as an external block.
All relative data/output paths resolve against the project directory. An absolute
`data.raw_dir` or `outputs.root` supports a separate cache or output volume.

Each normal invocation creates a new run ID. Resume requires an existing explicit
ID and matching configuration (offline mode may change). It archives the previous
attempt under `attempts/NNN/` and replays every stage. This conservative resume
policy avoids mixing outputs across attempts; it does not skip completed work.
An OS lock prevents concurrent execution against the same run ID.

## Data and sample conventions

- Yahoo daily OHLC, adjusted closes, volume and corporate actions are downloaded
  from January 1990 with `auto_adjust=False`. The exclusive download end is
  September 1, 2026. All returned fields are preserved in the raw CSV.
- Monthly adjusted prices are selected at the exact last NYSE session of each
  month using `pandas_market_calendars`. Simple total returns are
  `adjusted_price[t] / adjusted_price[t-1] - 1`. No prices or returns are forward
  filled. Adjusted prices reflect Yahoo's dividend/split adjustments.
- The first complete monthly return across all eight assets is derived from the
  data. Pre-inception gaps are trimmed; any internal missing month, missing
  month-end close, invalid price or incomplete final month is an error.
- Full sample: first common return through August 2026. Pre-COVID: first common
  return through December 2019. Post-COVID: January 2020 through August 2026.
  Exact start/end/N are saved for every sample. Every asset subset in incremental
  diversification uses these same full-sample observations.
- Historical Fama–French RF is read from the monthly rows of the original ZIP's
  CSV and converted from percent to decimal. Annual summary rows are excluded.
  The raw ZIP is preserved. A permitted trailing release lag shortens only the
  SIM/direct-comparison intersection. Internal gaps never cause silent trimming.
- Raw caches have SHA-256 manifests and retrieval metadata. Successful runs copy
  the raw files and manifests into their own `data/raw/` directory.

Source documentation: [yfinance download](https://ranaroussi.github.io/yfinance/reference/api/yfinance.download.html),
[Fama–French factors](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/f-f_factors.html),
[CVXPY solvers](https://www.cvxpy.org/tutorial/solvers/index.html).

## Numerical conventions

Calculations use monthly arithmetic means and sample covariance (`ddof=1`).
Presentation uses `12*mean`, `12*variance`, `sqrt(12)*SD`, and
`sqrt(12)*monthly_Sharpe`. Annualized arithmetic means are not CAGR. Portfolio
gross exposure is `sum(abs(weights))`.

The CAL rate defaults to `0.045/12`. Set `risk_free.monthly_conversion` to
`compound` to use `(1+annual_rate)**(1/12)-1`; the summary reports the actual
monthly rate and its arithmetic annual presentation. This fixed CAL rate is
distinct from the historical regression RF observations.

The optimizer supports:

| Specification | Budget constraint | Asset bounds |
|---|---|---|
| A | weights sum to one | unrestricted long/short |
| B | weights sum to one | nonnegative |
| C | weights sum to one | -0.20 to +0.20 by default |

GMV and target-return portfolios use CVXPY/CLARABEL, with variance scaling for
numerical conditioning and tight solver tolerances. A result must have status
`optimal` and pass independent budget, bound and target checks; `optimal_inaccurate`
is rejected. A failed frontier point aborts the entire analytical stage. No
failed points appear in saved frontier files.

The default frontier contains 200 points across both branches, including GMV
and the constrained return extrema. Specification A has an unbounded mathematical
frontier; its saved finite range spans the asset means, GMV and analytical
tangency when attained, with configurable padding. The efficient branch is saved separately.
Constrained extrema come from validated linear programs.

Tangency uses direct SLSQP maximization of monthly Sharpe with an analytic gradient
and multiple feasible starts (equal weight, GMV and the grid's best portfolio).
Every accepted solution must pass success/constraint checks. Its Sharpe must
agree with the independently solved dense upper frontier within the configured
monthly tolerance. Increase `frontier.points` if that cross-check fails.
Specification A also checks GMV, every frontier point and tangency against
closed-form matrix solutions. No short-sale bounds are introduced for A.

The engine fails explicitly on singular covariance and never silently regularizes.
For unrestricted tangency it calculates `A=1'Σ⁻¹1`, `B=1'Σ⁻¹μ`, `C=μ'Σ⁻¹μ`,
`D=A*C-B²`, and `h=B-rf*A`. If `h > tangency_existence_tolerance` (default 1e-12),
the conventional analytical weights are checked against SLSQP. Otherwise the
economic outcome is `NONATTAINED`, with monthly Sharpe supremum `sqrt(D/A)`.
No SLSQP approximation, finite weights, gross exposure, or attained CAL is saved
for that outcome. GMV/frontiers and other specifications continue normally.
Per-model `models/*_tangency.json` and `results_summary.json` store the status,
reason, coefficients, supremum and null weights/exposure. Portfolio CSVs contain
only actual finite portfolios; the CAL CSV is header-only when nonattained.
Plots retain the efficient frontier and GMV and label the missing tangency.
A positive-excess finite tangency is required for constrained attained CALs.

CAL tables include risky allocations 0–150%, cash weights, risk and expected
return. Lending/borrowing is assumed available at the same rate. A/B/C constraints
apply to the risky fund, and may not hold for its scaled holdings when combined
with borrowing. Figures mark GMV with a circle and tangency with a star.

## Single-Index Model and comparisons

Non-SPY regressions use monthly excess returns:

```text
r_i - historical_RF = alpha_i + beta_i * (r_SPY - historical_RF) + residual_i
```

SPY is assigned alpha=0, beta=1, residual variance=0 and is never regressed.
Residual variance is OLS `SSE/(N-2)`. Regression exports include alpha, beta,
residual variance/SD, systematic and total implied variance, coefficient standard
errors/t-statistics/p-values, R²/adjusted R², N, residual degrees of freedom,
Durbin–Watson and Jarque–Bera p-values. Diagnostics do not correct for serial
correlation or heteroskedasticity; OLS coefficient standard errors are conventional.

Define the monthly factor once as `factor = SPY - aligned_FF_RF`. Both regressions
and SIM covariance use that exact factor:
`Sigma_SIM = outer(beta,beta)*Var(factor, ddof=1) + diag(residual_variances)`.
Thus SPY's SIM variance is the excess-factor variance, not raw SPY variance.
The fixed forecast RF is deterministic, so adding it does not change this model
covariance. Residual cross-covariances are assumed zero. This convention replaces
the original raw-SPY-variance convention following the methodological audit.

`sim.expected_return_method` supports:

- `alpha_beta_premium` (default): `fixed_RF/12 + monthly_alpha + beta*premium/12`.
- `beta_premium`: omits alpha from the preceding forecast.
- `sample_mean`: uses historical arithmetic sample means.

Default annual fixed RF is 4.5%, annual market risk premium is 6%. These SIM
forecast assumptions always use division by 12, independently of CAL conversion.
For the default model SPY's expected return is `(0.045+0.06)/12`.

**Covariance-only comparison** uses identical sample means for Markowitz and SIM,
validated before and after serialization. **Complete-model comparison** uses
sample means/full covariance versus configured SIM means/SIM covariance. The
former isolates covariance effects; the latter combines covariance and mean
effects. Both include weight/metric differences and frontier volatility
differences at identical targets over overlapping efficient return ranges.
Complete-model targets use each model's own expectations; apparent dominance
does not imply realized performance superiority.
Pointwise differences retain crossings; there is no overall winner. The
`lower_volatility` column is `MARKOWITZ`, `SIM`, or `TIE`, with an explicit absolute
annual-SD tolerance `optimization.dominance_sd_tolerance` (default 1e-8).

Benchmarks are equal weight, 60/40 (20% in each equity/bond ETF), and 40/30/30
with equal weights within each asset class. Each is checked separately under
each specification and valued under each model's moments. All three happen to
be feasible under default A/B/C. Infeasible benchmarks remain labeled in the
tables and are excluded from constraint-specific plots.

Subsample Markowitz comparison defaults to B; configure
`subsample_analysis.constraint`. The pre/post chart shares one set of axes.
`diversification.constraint` also defaults to B. It compares equities, equities
plus bonds, equities plus bonds plus gold, and all assets. Infeasible subsets
(e.g. three assets with a 20% upper bound) are recorded as `SKIPPED` with a reason.

## Outputs and workflow

```text
config/assignment2.yaml
src/                       reusable calculations, validation, I/O and plotting
workflow/                  orchestration and run state
tests/                     unit, failure-injection and offline CLI integration tests
data/raw/                  checksummed downloaded sources
data/processed/            reserved for optional shared derived exports
runs/<run_id>/
  state.json               atomic stage status and failure reason
  config_snapshot.yaml
  logs/run.log
  data/                    aligned samples, RF, monthly prices, copied raw sources
  models/                  exact NPZ moments, CSV moments, regressions and residuals
  tables/                  portfolios, frontiers, CALs, benchmarks, comparisons, sample-period map
  figures/                 PNG and vector PDF
  diagnostics/             checks, correlations, changes, eigenvalues, bounds and exposures
  results_summary.json     machine-readable metrics, assumptions and sample metadata
  interpretation.md        deterministic quantitative narrative
  markowitz_report.md      available Markowitz results, explicitly scoped/partial
```

The stages are configuration, Yahoo data, input validation, Markowitz full sample,
Markowitz subsamples, diversification, FF data, SIM, comparisons, numerical outputs,
output validation, figures, Markowitz report, and complete report. Missing external
FF data blocks only its dependencies; actual validation/solver failures mark the
stage `FAILED` and every pending downstream stage `SKIPPED`. Figures read saved
tables and contain no optimization logic. Output validation reconciles saved
weights, labels, order and metrics against accepted in-memory results, including
benchmarks and comparison tables. It independently recomputes portfolio metrics,
feasibility and full CAL identities, checks nonattained tangency metadata, and
reconciles the summary JSON before accepting figures or reports. Successful
numerical artifacts have a SHA-256 manifest.
Environment/package versions and source hashes are recorded for reproducibility.
CSV/JSON are mandatory audit outputs; figures may be disabled.

Diagnostics include all asset-pair correlations sorted by magnitude, covariance
and correlation changes, diagonal variance changes, bound hits, gross exposure,
eigenvalues/condition numbers, common-target frontier differences, and GMV versus
tangency weight stability across models and periods. These are descriptive,
in-sample diagnostics; there is no claim of out-of-sample forecasting ability.

## Testing

```bash
python -m pytest -q
```

Tests cover mathematical identities, constrained and analytical optimization,
alignment and inception handling, annualization, SIM variance identities,
missing/corrupt data, benchmark feasibility, state isolation/resume, solver
failure propagation, and saved-file integrity. The full CLI integration test
uses explicitly labeled **synthetic** Yahoo-shaped and FF-shaped caches in a
temporary directory, produces all numerical outputs and figures, and checks their
contents. No synthetic data is inserted into the real assignment cache. Tests
are deterministic and do not require network access.
Audit regression tests cover positive/negative/zero tangency normalizers, the
Sharpe supremum, partial runs with missing FF, exact excess-factor variance,
independent output corruptions, comparison ties, and Specification C geometry
(at most two strictly negative holdings, maximum gross exposure 1.40).
