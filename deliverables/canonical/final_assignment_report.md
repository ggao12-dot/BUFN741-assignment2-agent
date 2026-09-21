# BUFN741 Group Assignment 2

## Multi-Asset Portfolio Optimization: Markowitz and Single-Index Models

This is the complete assignment report. It covers Part 1 Markowitz optimization, Part 2 Single-Index Model estimation and optimization, direct Markowitz-versus-SIM comparisons, the required pre/post-COVID analysis, numerical diagnostics, and economic interpretation. The validated component reports remain available as `markowitz_report.md`, `sim_report.md`, and `model_comparison_report.md`.

## Executive Summary

- Adding bonds reduced long-only GMV volatility from 15.17% for equities alone to 4.53%. Adding gold raised the tangency Sharpe from 0.475 to 0.568; adding oil and DBC reduced GMV volatility further to 4.29% but did not improve the saved tangency Sharpe at displayed precision.
- The unrestricted full-sample tangency is NONATTAINED. Because the GMV expected return is below the 4.50% CAL rate, the Sharpe supremum 1.051 is approached asymptotically; no finite tangency fund or attained CAL exists.
- Long-only and ±20% bounds materially reduce gross exposure and concentrate the solution in a more implementable region, while Specification C places several assets at its +20% ceiling.
- Under Specification B, post-COVID GMV volatility rose from 3.50% to 5.36%; the tangency Sharpe rose from 0.520 to 0.980. The post-COVID estimate uses only 80 monthly observations.
- SIM attributes every cross-asset covariance to exposure to the SPY-minus-RF factor. The lowest single-factor R² values occur for GLD (0.006), TLT (0.006), AGG (0.061).
- In the covariance-only experiment, Specification A has lower Markowitz volatility at 33 of 80 common targets and lower SIM volatility at 47; under B the corresponding counts are 2 and 78. The crossings rule out a single frontier winner.

## 1. Objective and Methodology

The investable universe is SPY, EFA, EEM, TLT, AGG, GLD, USO, and DBC. The analysis uses monthly simple total returns from Yahoo Finance adjusted prices. Fama–French monthly RF observations support SIM excess-return regressions; the fixed 4.5% annual rate supports CAL and tangency calculations.

All estimation and optimization are monthly. Arithmetic means and variances are multiplied by 12 for presentation, while standard deviations and Sharpe ratios are multiplied by sqrt(12). Specification A is unrestricted long/short with weights summing to one. B is long-only. C constrains every weight to [-20%, +20%]. Markowitz uses the full sample covariance matrix. SIM uses beta beta' times the variance of SPY minus aligned FF RF, plus diagonal residual variances.

## 2. Data and Sample Construction

- Markowitz full sample: 2006-05 through 2026-08, N=244.
- Pre-COVID: 2006-05 through 2019-12, N=164.
- Post-COVID: 2020-01 through 2026-08, N=80.
- SIM common sample: 2006-05 through 2026-07, N=243.
- Markowitz comparison sample: 2006-05 through 2026-07, N=243.

Yahoo ETF returns extend through August 2026. Available FF RF ends July 2026, producing an accepted 1-month lag under the configured maximum of 2. Main Markowitz analysis retains August. SIM and direct comparisons use the identical May 2006–July 2026 intersection.

## 3. Descriptive Statistics and Diversification

**Table 1. Full-sample annualized asset statistics**

| Asset | Arithmetic mean | Standard deviation | Variance |
|---|---:|---:|---:|
| SPY | 11.71% | 15.19% | 0.023064 |
| EFA | 6.69% | 17.02% | 0.028971 |
| EEM | 7.43% | 20.88% | 0.043617 |
| TLT | 4.03% | 13.81% | 0.019067 |
| AGG | 3.19% | 4.54% | 0.002057 |
| GLD | 10.55% | 17.30% | 0.029932 |
| USO | 0.66% | 37.76% | 0.142614 |
| DBC | 3.93% | 18.81% | 0.035384 |

**Table 2. Full-sample correlation matrix**

| Asset | SPY | EFA | EEM | TLT | AGG | GLD | USO | DBC |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SPY | 1.00 | 0.87 | 0.75 | -0.08 | 0.25 | 0.08 | 0.33 | 0.44 |
| EFA | 0.87 | 1.00 | 0.86 | -0.04 | 0.33 | 0.19 | 0.37 | 0.50 |
| EEM | 0.75 | 0.86 | 1.00 | -0.05 | 0.29 | 0.31 | 0.35 | 0.52 |
| TLT | -0.08 | -0.04 | -0.05 | 1.00 | 0.83 | 0.26 | -0.36 | -0.32 |
| AGG | 0.25 | 0.33 | 0.29 | 0.83 | 1.00 | 0.37 | -0.20 | -0.09 |
| GLD | 0.08 | 0.19 | 0.31 | 0.26 | 0.37 | 1.00 | 0.04 | 0.30 |
| USO | 0.33 | 0.37 | 0.35 | -0.36 | -0.20 | 0.04 | 1.00 | 0.85 |
| DBC | 0.44 | 0.50 | 0.52 | -0.32 | -0.09 | 0.30 | 0.85 | 1.00 |

The largest positive correlations are SPY/EFA=0.865, EFA/EEM=0.858, USO/DBC=0.851, TLT/AGG=0.831. The lowest correlations, which provide the clearest pairwise diversification evidence, are TLT/USO=-0.356, TLT/DBC=-0.323, AGG/USO=-0.197, AGG/DBC=-0.088.

**Table 3. Incremental diversification under Specification B**

| Universe | GMV volatility | Tangency status | Tangency Sharpe |
|---|---:|:---:|---:|
| equities | 15.17% | ATTAINED | 0.475 |
| equities + bonds | 4.53% | ATTAINED | 0.475 |
| equities + bonds + gold | 4.53% | ATTAINED | 0.568 |
| all assets | 4.29% | ATTAINED | 0.568 |

![Figure 1. Incremental diversification across asset subsets.](../figures/diversification.png)

*Figure 1. Incremental diversification across asset subsets.*

## 4. Markowitz Full-Sample Results

**Table 4. Markowitz GMV and tangency results**

| Model/specification | Portfolio | Status | Expected return | Volatility | Sharpe | Gross exposure |
|---|---|---|---:|---:|---:|---:|
| Markowitz A | GMV | ATTAINED | 2.49% | 2.83% | -0.712 | 2.007 |
| Markowitz A | Tangency | NONATTAINED | — | — | supremum 1.051 | — |
| Markowitz B | GMV | ATTAINED | 3.17% | 4.29% | -0.309 | 1.000 |
| Markowitz B | tangency | ATTAINED | 11.27% | 11.92% | 0.568 | 1.000 |
| Markowitz C | GMV | ATTAINED | 6.64% | 7.94% | 0.270 | 1.388 |
| Markowitz C | tangency | ATTAINED | 8.40% | 11.46% | 0.340 | 1.366 |

**Table 5. Markowitz portfolio weights**

| Model/specification | Portfolio | SPY | EFA | EEM | TLT | AGG | GLD | USO | DBC |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Markowitz A | GMV | 3.5% | -12.5% | -2.7% | -32.5% | 142.6% | -2.6% | 0.2% | 4.0% |
| Markowitz B | GMV | 0.0% | 0.0% | 0.0% | 0.0% | 94.0% | 0.0% | 1.7% | 4.3% |
| Markowitz B | tangency | 62.1% | 0.0% | 0.0% | 0.0% | 0.0% | 37.9% | 0.0% | 0.0% |
| Markowitz C | GMV | 20.0% | 20.0% | -17.6% | 20.0% | 20.0% | 19.4% | -1.9% | 20.0% |
| Markowitz C | tangency | 20.0% | 20.0% | 13.1% | 19.5% | 5.7% | 20.0% | -18.3% | 20.0% |

Specification A is an economic NONATTAINED case, not a solver failure. Its GMV return is below the risk-free rate, so normalized finite tangency weights do not exist. B removes short sales. C allows limited shorts but its eight +20% caps make the feasible set tight and produce binding ceilings.

![Figure 2. Full-sample Markowitz frontiers under A, B, and C.](../figures/markowitz_constraints.png)

*Figure 2. Full-sample Markowitz frontiers under A, B, and C.*

![Figure 3. Specification A Markowitz frontier; tangency is nonattained.](../figures/markowitz_full_A.png)

*Figure 3. Specification A Markowitz frontier; tangency is nonattained.*

![Figure 4. Specification B Markowitz frontier and attained CAL.](../figures/markowitz_full_B.png)

*Figure 4. Specification B Markowitz frontier and attained CAL.*

![Figure 5. Specification C Markowitz frontier and attained CAL.](../figures/markowitz_full_C.png)

*Figure 5. Specification C Markowitz frontier and attained CAL.*

## 5. Benchmark Portfolios

**Table 6. Benchmark performance and feasibility**

| Benchmark | Specification | Feasible | Expected return | Volatility | Sharpe |
|---|:---:|:---:|---:|---:|---:|
| equal_weight | A | yes | 6.02% | 11.68% | 0.130 |
| equal_weight | B | yes | 6.02% | 11.68% | 0.130 |
| equal_weight | C | yes | 6.02% | 11.68% | 0.130 |
| 60_40 | A | yes | 6.61% | 10.70% | 0.197 |
| 60_40 | B | yes | 6.61% | 10.70% | 0.197 |
| 60_40 | C | yes | 6.61% | 10.70% | 0.197 |
| 40_30_30 | A | yes | 6.04% | 10.87% | 0.142 |
| 40_30_30 | B | yes | 6.04% | 10.87% | 0.142 |
| 40_30_30 | C | yes | 6.04% | 10.87% | 0.142 |

Feasibility is evaluated independently under each specification. No infeasible allocation is projected into or treated as part of a constraint-specific opportunity set.

## 6. Effect of Portfolio Constraints

A permits large offsetting long and short positions and therefore has the greatest exposure to estimation error. B forces gross exposure to one. Under C, eight weights each capped at +20% must sum to one, so at least five meaningful long positions are required; no more than two holdings can be strictly negative, and maximum gross exposure is 1.40. The saved bound diagnostics show which assets absorb these geometric restrictions.

## 7. Pre-COVID versus Post-COVID Markowitz Results

**Table 7. Specification B pre/post portfolio comparison**

| Period | Portfolio | Expected return | Volatility | Sharpe | Gross exposure |
|---|---|---:|---:|---:|---:|
| Pre-COVID | GMV | 4.09% | 3.50% | -0.116 | 1.000 |
| Pre-COVID | tangency | 8.68% | 8.04% | 0.520 | 1.000 |
| Post-COVID | GMV | 2.44% | 5.36% | -0.384 | 1.000 |
| Post-COVID | tangency | 16.19% | 11.94% | 0.980 | 1.000 |

**Table 8. Pre/post portfolio weights**

| Period | Portfolio | SPY | EFA | EEM | TLT | AGG | GLD | USO | DBC |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Pre-COVID | GMV | 2.7% | 0.0% | 0.0% | 0.0% | 94.4% | 0.0% | 2.9% | 0.0% |
| Pre-COVID | tangency | 51.8% | 0.0% | 0.0% | 43.1% | 0.0% | 5.1% | 0.0% | 0.0% |
| Post-COVID | GMV | 0.0% | 0.0% | 0.0% | 0.0% | 88.5% | 0.0% | 0.0% | 11.5% |
| Post-COVID | tangency | 33.1% | 0.0% | 0.0% | 0.0% | 0.0% | 47.2% | 0.4% | 19.2% |

GMV weights change by L1=0.231; tangency weights change by L1=1.235. The largest absolute correlation changes are SPY/TLT=+0.631, EEM/TLT=+0.588, EFA/TLT=+0.586, SPY/AGG=+0.511. The largest monthly covariance changes are USO/DBC=+0.002368, GLD/USO=-0.001813, EEM/USO=-0.001789, EEM/TLT=+0.001357. The shorter post-COVID sample makes these estimates less precise.

![Figure 6. Pre- and post-COVID Specification B frontiers and CALs on common axes.](../figures/pre_post_comparison.png)

*Figure 6. Pre- and post-COVID Specification B frontiers and CALs on common axes.*

## 8. Single-Index Model Estimation

For every non-market asset the regression is `(r_i - rf) = alpha_i + beta_i (r_SPY - rf) + epsilon_i`. SPY is assigned alpha=0, beta=1, and residual variance=0 and is not regressed on itself. The covariance model is `Sigma_SIM = beta beta' Var(SPY - RF) + diag(residual variances)`.

**Table 9. SIM estimates and model-implied expected returns**

| Asset | Expected return | Alpha | Beta | Residual SD | Residual variance | Systematic variance | Total variance | R² |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SPY | 10.50% | 0.00% | 1.000 | 0.00% | 0.000000 | 0.023163 | 0.023163 | 1.000 |
| EFA | 5.63% | -4.68% | 0.969 | 8.56% | 0.007328 | 0.021738 | 0.029065 | 0.749 |
| EEM | 5.98% | -4.71% | 1.031 | 13.81% | 0.019067 | 0.024640 | 0.043707 | 0.565 |
| TLT | 7.19% | 3.12% | -0.072 | 13.83% | 0.019138 | 0.000121 | 0.019259 | 0.006 |
| AGG | 5.77% | 0.83% | 0.074 | 4.42% | 0.001952 | 0.000125 | 0.002077 | 0.061 |
| GLD | 12.63% | 7.61% | 0.088 | 17.15% | 0.029424 | 0.000180 | 0.029604 | 0.006 |
| USO | 0.13% | -9.24% | 0.810 | 35.82% | 0.128313 | 0.015214 | 0.143527 | 0.106 |
| DBC | 4.35% | -3.41% | 0.542 | 16.92% | 0.028634 | 0.006816 | 0.035449 | 0.193 |

## 9. SIM Portfolio Optimization

**Table 10. SIM GMV and tangency results**

| Model/specification | Portfolio | Status | Expected return | Volatility | Sharpe | Gross exposure |
|---|---|---|---:|---:|---:|---:|
| SIM A | GMV | ATTAINED | 6.20% | 4.16% | 0.408 | 1.015 |
| SIM A | tangency | ATTAINED | 14.29% | 9.99% | 0.980 | 3.195 |
| SIM B | GMV | ATTAINED | 6.22% | 4.16% | 0.414 | 1.000 |
| SIM B | tangency | ATTAINED | 8.62% | 6.23% | 0.662 | 1.000 |
| SIM C | GMV | ATTAINED | 8.09% | 7.38% | 0.487 | 1.010 |
| SIM C | tangency | ATTAINED | 8.50% | 7.79% | 0.514 | 1.095 |

**Table 11. SIM portfolio weights**

| Model/specification | Portfolio | SPY | EFA | EEM | TLT | AGG | GLD | USO | DBC |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SIM A | GMV | -0.5% | 0.7% | -0.3% | 9.7% | 82.0% | 5.4% | 0.3% | 2.8% |
| SIM A | tangency | 123.7% | -65.1% | -25.2% | 16.6% | 43.1% | 26.3% | -7.3% | -12.1% |
| SIM B | GMV | 0.0% | 0.2% | 0.0% | 9.7% | 81.8% | 5.3% | 0.2% | 2.7% |
| SIM B | tangency | 20.4% | 0.0% | 0.0% | 15.4% | 39.9% | 24.3% | 0.0% | 0.0% |
| SIM C | GMV | 20.0% | 5.6% | -0.5% | 20.0% | 20.0% | 20.0% | 1.3% | 13.6% |
| SIM C | tangency | 20.0% | 11.3% | 4.2% | 20.0% | 20.0% | 20.0% | -4.8% | 9.3% |

![Figure 7. SIM complete-model frontier under Specification A.](../figures/sim_complete_A.png)

*Figure 7. SIM complete-model frontier under Specification A.*

![Figure 8. SIM complete-model frontier under Specification B.](../figures/sim_complete_B.png)

*Figure 8. SIM complete-model frontier under Specification B.*

![Figure 9. SIM complete-model frontier under Specification C.](../figures/sim_complete_C.png)

*Figure 9. SIM complete-model frontier under Specification C.*

## 10. Markowitz versus SIM: Covariance-Only Experiment

The expected-return vectors and observations are exactly identical. Markowitz uses full sample covariance; SIM uses single-index covariance. Every difference below is therefore a covariance-model effect. Categories are pointwise and no overall winner is declared.

**Table 12. Covariance-only common-target frontier diagnostics**

| Specification | Common targets | Min SIM−Markowitz SD | Max SIM−Markowitz SD | Mean absolute SD difference | MARKOWITZ | SIM | TIE |
|:---:|---:|---:|---:|---:|---:|---:|---:|
| A | 80 | -0.327% | 1.123% | 0.329% | 33 | 47 | 0 |
| B | 80 | -0.702% | 0.006% | 0.468% | 2 | 78 | 0 |
| C | 80 | -1.228% | 0.276% | 0.949% | 1 | 79 | 0 |

**Table 13. Covariance-only GMV and tangency comparison**

| Specification | Portfolio | Model | Expected return | Volatility | Sharpe | Gross exposure |
|:---:|---|---|---:|---:|---:|---:|
| A | GMV | Markowitz | 2.49% | 2.83% | -0.709 | 2.008 |
| A | GMV | Sim | 3.61% | 4.16% | -0.214 | 1.015 |
| B | GMV | Markowitz | 3.16% | 4.30% | -0.313 | 1.000 |
| B | GMV | Sim | 3.64% | 4.16% | -0.206 | 1.000 |
| B | tangency | Markowitz | 11.07% | 11.94% | 0.550 | 1.000 |
| B | tangency | Sim | 11.05% | 11.89% | 0.551 | 1.000 |
| C | GMV | Markowitz | 6.50% | 7.93% | 0.253 | 1.391 |
| C | GMV | Sim | 6.62% | 7.38% | 0.287 | 1.010 |
| C | tangency | Markowitz | 8.34% | 11.81% | 0.325 | 1.388 |
| C | tangency | Sim | 7.91% | 9.33% | 0.366 | 1.282 |

**Table 14. Largest covariance-only allocation differences**

| Specification | Portfolio | Largest-changing asset | Markowitz | SIM | Absolute change |
|:---:|---|---|---:|---:|---:|
| A | GMV | AGG | 142.66% | 81.98% | 60.68% |
| A | tangency | unavailable: NONATTAINED | — | — | — |
| B | GMV | AGG | 93.93% | 81.85% | 12.09% |
| B | tangency | TLT | 0.00% | 0.31% | 0.31% |
| C | GMV | EEM | -17.69% | -0.51% | 17.18% |
| C | tangency | DBC | 20.00% | -4.60% | 24.60% |

![Figure 10. Covariance-only Markowitz versus SIM comparison, Specification A.](../figures/comparison_covariance_only_A.png)

*Figure 10. Covariance-only Markowitz versus SIM comparison, Specification A.*

![Figure 11. Covariance-only Markowitz versus SIM comparison, Specification B.](../figures/comparison_covariance_only_B.png)

*Figure 11. Covariance-only Markowitz versus SIM comparison, Specification B.*

![Figure 12. Covariance-only Markowitz versus SIM comparison, Specification C.](../figures/comparison_covariance_only_C.png)

*Figure 12. Covariance-only Markowitz versus SIM comparison, Specification C.*

## 11. Complete Markowitz versus SIM Comparison

Markowitz uses sample means and full covariance. SIM uses alpha/beta/premium expected returns and SIM covariance. This experiment combines covariance and expected-return effects. Comparing it with Section 10 isolates the additional effect of changing the expected-return model.

**Table 15. Complete-model common-target frontier diagnostics**

| Specification | Common targets | Min SIM−Markowitz SD | Max SIM−Markowitz SD | Mean absolute SD difference | MARKOWITZ | SIM | TIE |
|:---:|---:|---:|---:|---:|---:|---:|---:|
| A | 80 | -1.895% | -0.409% | 1.606% | 0 | 80 | 0 |
| B | 80 | -3.264% | -1.389% | 2.314% | 0 | 80 | 0 |
| C | 80 | -4.592% | -3.692% | 4.213% | 0 | 80 | 0 |

**Table 16. Complete-model GMV and tangency comparison**

| Specification | Portfolio | Model | Expected return | Volatility | Sharpe | Gross exposure |
|:---:|---|---|---:|---:|---:|---:|
| A | GMV | Markowitz | 2.49% | 2.83% | -0.709 | 2.008 |
| A | GMV | Sim | 6.20% | 4.16% | 0.408 | 1.015 |
| B | GMV | Markowitz | 3.16% | 4.30% | -0.313 | 1.000 |
| B | GMV | Sim | 6.22% | 4.16% | 0.414 | 1.000 |
| B | tangency | Markowitz | 11.07% | 11.94% | 0.550 | 1.000 |
| B | tangency | Sim | 8.62% | 6.23% | 0.662 | 1.000 |
| C | GMV | Markowitz | 6.50% | 7.93% | 0.253 | 1.391 |
| C | GMV | Sim | 8.09% | 7.38% | 0.487 | 1.010 |
| C | tangency | Markowitz | 8.34% | 11.81% | 0.325 | 1.388 |
| C | tangency | Sim | 8.50% | 7.79% | 0.514 | 1.095 |

**Table 17. Largest complete-model allocation differences**

| Specification | Portfolio | Largest-changing asset | Markowitz | SIM | Absolute change |
|:---:|---|---|---:|---:|---:|
| A | GMV | AGG | 142.66% | 81.98% | 60.68% |
| A | tangency | unavailable: NONATTAINED | — | — | — |
| B | GMV | AGG | 93.93% | 81.85% | 12.09% |
| B | tangency | SPY | 63.50% | 20.43% | 43.07% |
| C | GMV | EEM | -17.69% | -0.51% | 17.18% |
| C | tangency | AGG | 4.25% | 20.00% | 15.75% |

![Figure 13. Complete-model Markowitz versus SIM comparison, Specification A.](../figures/comparison_complete_model_A.png)

*Figure 13. Complete-model Markowitz versus SIM comparison, Specification A.*

![Figure 14. Complete-model Markowitz versus SIM comparison, Specification B.](../figures/comparison_complete_model_B.png)

*Figure 14. Complete-model Markowitz versus SIM comparison, Specification B.*

![Figure 15. Complete-model Markowitz versus SIM comparison, Specification C.](../figures/comparison_complete_model_C.png)

*Figure 15. Complete-model Markowitz versus SIM comparison, Specification C.*

## 12. Covariance-Model Diagnostics

The monthly Frobenius norm of SIM minus full covariance is 0.00687156. Condition numbers are 607.64 for full covariance and 82.93 for SIM.

**Table 18. Largest off-diagonal covariance discrepancies**

| Pair | SIM − Markowitz monthly covariance |
|---|---:|
| USO/DBC | -0.00420245 |
| TLT/USO | +0.00144176 |
| EEM/GLD | -0.00073252 |
| GLD/DBC | -0.00071167 |
| EEM/USO | -0.00071004 |
| TLT/DBC | +0.00062706 |
| EEM/DBC | -0.00062553 |
| EFA/EEM | -0.00062098 |

**Table 19. Largest correlation discrepancies**

| Pair | SIM − Markowitz correlation |
|---|---:|
| TLT/AGG | -0.8503 |
| USO/DBC | -0.7093 |
| AGG/GLD | -0.3517 |
| TLT/USO | +0.3306 |
| TLT/DBC | +0.2894 |
| AGG/USO | +0.2776 |
| TLT/GLD | -0.2659 |
| GLD/DBC | -0.2638 |

Bonds, gold, oil, broad commodities, and international equities can have common influences that are not captured by SPY alone. Here that limitation is measured by the saved R² values and matrix discrepancies rather than asserted from asset labels alone.

## 13. Answers to Assignment Analysis Questions

### Question 1. What diversification benefit comes from bonds, gold, oil, and broad commodities?

Bonds produce the largest GMV reduction: 15.17% falls to 4.53%. Gold raises maximum Sharpe to 0.568. Oil and DBC lower all-asset GMV volatility to 4.29%, with no displayed Sharpe improvement.

### Question 2. What is the effect of allowing short sales?

Unrestricted A attains the lowest GMV risk but uses larger gross exposure and has no finite full-sample Markowitz tangency portfolio. Short sales enlarge the opportunity set while making allocations more sensitive to estimated inputs.

### Question 3. What is the effect of ±20% bounds?

C caps concentration and leverage, raises GMV volatility relative to A/B, and places several assets at +20%. Its geometry requires broad long exposure because eight capped positions must sum to one.

### Question 4. How do pre- and post-COVID covariance structures differ?

The largest saved changes involve USO/DBC covariance and equity/bond correlations. Post-COVID GMV volatility is 5.36% versus 3.50% pre-COVID, but the shorter post sample increases uncertainty.

### Question 5. How sensitive are tangency and GMV weights to expected returns?

Across pre/post samples, tangency L1 weight change is 1.235 versus 0.231 for GMV. This computed contrast is consistent with tangency weights depending directly on expected returns while GMV depends on covariance.

### Question 6. How good is the SIM approximation?

It is strongest for assets with high saved R² and weakest for GLD (R²=0.006), TLT (R²=0.006), AGG (R²=0.061). The matrix discrepancies in Tables 18 and 19 quantify approximation error.

### Question 7. Where are the SIM and Markowitz frontiers relative to each other?

They cross in covariance-only A: Markowitz has lower risk at 33 targets and SIM at 47. B and C favor SIM at most saved common targets in this in-sample comparison. No overall winner is assigned.

### Question 8. What are the practical limitations of SPY as the sole common factor?

A single US equity factor cannot reproduce residual cross-covariances. Low R² for several defensive and real-asset ETFs and the observed covariance/correlation discrepancies show where that assumption is restrictive in this sample.

## 14. Practical Interpretation and Limitations

Sample means are noisy, so tangency weights can be unstable. GMV is less directly exposed to mean error but remains sensitive to covariance estimation. Unrestricted leverage can be impractical, and constraints change both attainable returns and which estimates drive allocations. The post-COVID sample is short. SIM is parsimonious but omits common factors beyond SPY. All conclusions are in-sample and do not establish future performance.

## 15. Conclusion

The results show substantial diversification from bonds and a Sharpe improvement from gold. Constraints trade theoretical opportunity-set breadth for implementability. Pre/post estimates differ materially, especially for commodity and equity/bond relationships. SIM offers a structured covariance estimate but changes frontiers and weights because its one-factor restriction omits residual co-movement. The most aggressive theoretical solution is therefore not automatically the most economically usable one.

## Appendix A. Provenance and Reproducibility

- Production run ID: `20260921T172426819558Z_2ebe0baf`.
- Git commit: `10ceebd95f6b52919e281743835f53527b0b3f5f`.
- Configuration snapshot: `config_snapshot.yaml`.
- Data sources: Yahoo Finance adjusted prices and Fama–French monthly RF.
- CAL/tangency RF: 4.50% annual.
- SIM market-premium assumption: 6.00% annual.
- Solvers: CLARABEL for quadratic programs and SLSQP for constrained tangency.
- Constraint tolerance: 1e-07; PSD tolerance: 1e-10; frontier tie tolerance: 1e-08 annual SD.
- Pytest result: the analytical workflow does not self-invoke pytest; the complete release-suite result is reported alongside this frozen production artifact.
- Internal production output validation: PASSED.
This report was generated from the frozen run artifacts after numerical output validation. It does not perform portfolio estimation or optimization.
