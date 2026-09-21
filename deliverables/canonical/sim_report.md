BUFN741 — Single-Index Model results

Scope: Single-Index Model only. This document is not the complete multi-model assignment report.
Assignment completeness: COMPLETE.

Sample observations:
- ETF sample: 2006-05 through 2026-08, N=244.
- Available Fama–French RF sample: 1926-07 through 2026-07, N=1201.
- SIM common sample: 2006-05 through 2026-07, N=243.
- Markowitz comparison sample: 2006-05 through 2026-07, N=243.
- Accepted RF trailing lag: yes; 1 month(s), configured maximum 2.

SIM estimation summary

Expected-return method: alpha_beta_premium; fixed annual RF 4.50%; annual market risk premium 6.00%.
Displayed expected returns, alpha, residual risk, systematic variance and total variance are annualized. Beta, systematic variance share and R² are unitless.

| Asset | Expected return | Alpha | Beta | Residual SD | Residual variance | Systematic variance | SIM total variance | Systematic share | R² |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SPY | 10.5000% | 0.0000% | 1.0000 | 0.0000% | 0.00000000 | 0.02316264 | 0.02316264 | 100.00% | 1.0000 |
| EFA | 5.6298% | -4.6827% | 0.9687 | 8.5602% | 0.00732766 | 0.02173752 | 0.02906518 | 74.79% | 0.7487 |
| EEM | 5.9789% | -4.7095% | 1.0314 | 13.8083% | 0.01906703 | 0.02464036 | 0.04370739 | 56.38% | 0.5648 |
| TLT | 7.1859% | 3.1193% | -0.0722 | 13.8341% | 0.01913816 | 0.00012082 | 0.01925899 | 0.63% | 0.0063 |
| AGG | 5.7680% | 0.8264% | 0.0736 | 4.4178% | 0.00195165 | 0.00012546 | 0.00207711 | 6.04% | 0.0606 |
| GLD | 12.6337% | 7.6054% | 0.0880 | 17.1535% | 0.02942424 | 0.00017957 | 0.02960381 | 0.61% | 0.0061 |
| USO | 0.1277% | -9.2351% | 0.8105 | 35.8208% | 0.12831285 | 0.01521437 | 0.14352722 | 10.60% | 0.1064 |
| DBC | 4.3474% | -3.4073% | 0.5424 | 16.9215% | 0.02863374 | 0.00681565 | 0.03544939 | 19.23% | 0.1929 |

SPY is the market asset: alpha=0, beta=1 and residual variance=0. SPY is not regressed on itself.
R² is the saved single-factor fit diagnostic used here to rank how much asset variation is described by the market factor; no separate unsaved ranking statistic is inferred.

SIM covariance structure

`Sigma_SIM = beta beta' Var(SPY - RF) + diag(residual variances)`

The beta and covariance calculations use the same aligned SPY-minus-Fama–French-RF factor. Cross-asset covariance is generated only through common SPY market exposure; residual cross-covariances are assumed to be zero.

Specification A

- GMV annualized expected return: 6.1950%.
- GMV annualized volatility: 4.1558%.
- GMV gross exposure: 1.015161.
- GMV weights: SPY=-0.47%, EFA=0.74%, EEM=-0.28%, TLT=9.68%, AGG=81.98%, GLD=5.35%, USO=0.26%, DBC=2.76%.
- Tangency status: ATTAINED.
- Tangency annualized expected return: 14.2855%.
- Tangency annualized volatility: 9.9851%.
- Tangency annualized Sharpe ratio: 0.980009.
- Tangency gross exposure: 3.194688.
- Tangency weights: SPY=123.65%, EFA=-65.11%, EEM=-25.17%, TLT=16.61%, AGG=43.14%, GLD=26.34%, USO=-7.33%, DBC=-12.12%.

Specification B

- GMV annualized expected return: 6.2208%.
- GMV annualized volatility: 4.1563%.
- GMV gross exposure: 1.000000.
- GMV weights: SPY=0.00%, EFA=0.20%, EEM=0.00%, TLT=9.69%, AGG=81.85%, GLD=5.34%, USO=0.23%, DBC=2.68%.
- Tangency status: ATTAINED.
- Tangency annualized expected return: 8.6236%.
- Tangency annualized volatility: 6.2319%.
- Tangency annualized Sharpe ratio: 0.661691.
- Tangency gross exposure: 1.000000.
- Tangency weights: SPY=20.43%, EFA=0.00%, EEM=0.00%, TLT=15.35%, AGG=39.88%, GLD=24.34%, USO=0.00%, DBC=0.00%.

Specification C

- GMV annualized expected return: 8.0949%.
- GMV annualized volatility: 7.3849%.
- GMV gross exposure: 1.010240.
- GMV weights: SPY=20.00%, EFA=5.63%, EEM=-0.51%, TLT=20.00%, AGG=20.00%, GLD=20.00%, USO=1.33%, DBC=13.56%.
- Tangency status: ATTAINED.
- Tangency annualized expected return: 8.5016%.
- Tangency annualized volatility: 7.7914%.
- Tangency annualized Sharpe ratio: 0.513588.
- Tangency gross exposure: 1.095368.
- Tangency weights: SPY=20.00%, EFA=11.29%, EEM=4.21%, TLT=20.00%, AGG=20.00%, GLD=20.00%, USO=-4.77%, DBC=9.28%.

SIM diagnostics

- Covariance validation: symmetric and PSD; minimum monthly eigenvalue 0.0001606137659; condition number 82.9328.
- Largest non-market betas: EEM=1.0314, EFA=0.9687, USO=0.8105.
- Largest non-market residual risks (annualized SD): USO=35.8208%, GLD=17.1535%, DBC=16.9215%.
- Largest non-market systematic variance shares: EFA=74.79%, EEM=56.38%, DBC=19.23%.
- Assets least well described by SPY (lowest saved R²): GLD=0.0061, TLT=0.0063, AGG=0.0606.
- Specification A binding constraints: none.
- Specification B binding constraints: GMV SPY=0.000000; GMV EEM=0.000000; tangency EFA=0.000000; tangency EEM=0.000000; tangency USO=0.000000; tangency DBC=0.000000.
- Specification C binding constraints: GMV SPY=0.200000; GMV TLT=0.200000; GMV AGG=0.200000; GMV GLD=0.200000; tangency SPY=0.200000; tangency TLT=0.200000; tangency AGG=0.200000; tangency GLD=0.200000.

Part 2 comparison context

The covariance-only comparison uses an exactly identical expected-return vector on both sides.
Markowitz comparison and SIM estimates both use 2006-05 through 2026-07 (N=243). Differences in that experiment therefore reflect covariance structure only. The complete comparison remains in the separate comparison tables and complete report.

Methodological note

All calculations use monthly units. Displayed expected returns and variances are multiplied by 12; volatilities and Sharpe ratios are multiplied by sqrt(12).
Historical Fama–French RF observations are used for excess-return regressions. The configured fixed 4.50% annual RF is used for CAL and tangency calculations.
The 1-month RF lag relative to Yahoo was accepted under the configured trailing-lag policy.
