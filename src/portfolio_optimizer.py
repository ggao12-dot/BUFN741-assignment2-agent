"""Convex variance optimization and independently checked direct Sharpe maximization."""
from __future__ import annotations
from dataclasses import dataclass
import logging
import numpy as np
import pandas as pd
import cvxpy as cp
from scipy.optimize import linprog, minimize
from src.estimate_moments import portfolio_metrics
from src.validation import require, validate_covariance, validate_weights, ValidationError

LOG = logging.getLogger(__name__)


class OptimizationError(RuntimeError):
    """Solver failure, inadmissible portfolio or failed independent cross-check."""


@dataclass(frozen=True)
class ConstraintSpec:
    kind: str
    lower: float = -np.inf
    upper: float = np.inf

    @classmethod
    def from_config(cls, config: dict) -> 'ConstraintSpec':
        return cls(config['type'], config.get('lower', -np.inf), config.get('upper', np.inf))

    def bounds(self, n: int) -> tuple[np.ndarray, np.ndarray]:
        require(self.kind in {'unrestricted', 'long_only', 'bounded'}, 'Unknown constraint type')
        lo, hi = (-np.inf, np.inf) if self.kind == 'unrestricted' else (
            (0.0, np.inf) if self.kind == 'long_only' else (self.lower, self.upper))
        require(lo <= hi and n * lo <= 1 <= n * hi, f'Infeasible {self.kind} bounds for {n} assets')
        return np.full(n, lo), np.full(n, hi)


def analytical_gmv(cov: np.ndarray) -> np.ndarray:
    inverse_one = np.linalg.solve(cov, np.ones(len(cov)))
    return inverse_one / inverse_one.sum()


@dataclass
class TangencyResult:
    status: str
    weights: np.ndarray | None
    reason: str | None = None
    sharpe_supremum_monthly: float | None = None
    gross_exposure: float | None = None
    coefficients: dict[str, float] | None = None

    def to_dict(self) -> dict:
        return dict(status=self.status, weights=None if self.weights is None else self.weights.tolist(),
                    reason=self.reason, sharpe_supremum_monthly=self.sharpe_supremum_monthly,
                    sharpe_supremum_annual=None if self.sharpe_supremum_monthly is None else
                    float(np.sqrt(12) * self.sharpe_supremum_monthly),
                    gross_exposure=self.gross_exposure, coefficients=self.coefficients)


def analytical_tangency(mean: np.ndarray, cov: np.ndarray, rf: float,
                        tolerance: float = 1e-12) -> TangencyResult:
    one = np.ones(len(mean))
    inv_one, inv_mean = np.linalg.solve(cov, one), np.linalg.solve(cov, mean)
    a, b, c = float(one @ inv_one), float(one @ inv_mean), float(mean @ inv_mean)
    d, h = a * c - b ** 2, b - rf * a
    if np.ptp(mean) == 0:
        d = 0.0  # exact identity; avoid cancellation noise in the degenerate case
    require(d >= -np.finfo(float).eps * 32 * max(abs(a * c), b ** 2, 1),
            'Invalid analytical frontier discriminant')
    coefficients = dict(A=a, B=b, C=c, D=max(0.0, d), h=h, mu_GMV=b / a)
    if h <= tolerance:
        return TangencyResult('NONATTAINED', None,
                              'mu_GMV <= rf (within the tangency-existence tolerance): '
                              'the Sharpe supremum is approached at unbounded exposure; '
                              'there is no finite tangency portfolio or attained CAL.',
                              float(np.sqrt(max(0.0, d) / a)), None, coefficients)
    weights = (inv_mean - rf * inv_one) / h
    return TangencyResult('ATTAINED', weights, gross_exposure=float(np.abs(weights).sum()),
                          coefficients=coefficients)


def analytical_frontier(mean: np.ndarray, cov: np.ndarray, target: float) -> np.ndarray:
    if np.ptp(mean) == 0:
        require(abs(target - mean[0]) <= 1e-12, 'Constant means: target return infeasible')
        return analytical_gmv(cov)
    matrix = np.column_stack([np.ones(len(mean)), mean])
    directions = np.linalg.solve(cov, matrix)
    require(np.linalg.matrix_rank(matrix) == 2, 'Constant means: target frontier is degenerate')
    return directions @ np.linalg.solve(matrix.T @ directions, [1.0, target])


class PortfolioOptimizer:
    def __init__(self, mean: np.ndarray, cov: np.ndarray, rf: float,
                 spec: ConstraintSpec, options: dict | None = None):
        self.mean, self.cov = np.asarray(mean, dtype=float), np.asarray(cov, dtype=float)
        self.rf, self.spec, self.options = rf, spec, options or {}
        self.tol = self.options.get('constraint_tolerance', 1e-7)
        eig = validate_covariance(self.cov, self.options.get('psd_tolerance', 1e-10))
        require(self.mean.shape == (len(self.cov),) and np.isfinite(self.mean).all(), 'Invalid means')
        require(np.isfinite(rf), 'Invalid risk-free rate')
        require(eig.min() > 1e-14, 'Singular covariance: optimization requires positive definiteness; no implicit regularization')
        self.lower, self.upper = spec.bounds(len(self.mean))
        self.scale = float(np.diag(self.cov).mean())
        self.w = cp.Variable(len(self.mean))
        self.target = cp.Parameter()
        constraints = [cp.sum(self.w) == 1]
        if np.isfinite(self.lower).any():
            constraints.append(self.w >= self.lower)
        if np.isfinite(self.upper).any():
            constraints.append(self.w <= self.upper)
        objective = cp.Minimize(cp.quad_form(self.w, cp.psd_wrap(self.cov / self.scale)))
        self.gmv_problem = cp.Problem(objective, constraints)
        self.frontier_problem = cp.Problem(objective, constraints + [self.mean @ self.w == self.target])

    def check(self, weights: np.ndarray, target: float | None = None) -> None:
        try:
            validate_weights(weights, self.lower, self.upper, self.tol, self.mean, target)
        except ValidationError as exc:
            raise OptimizationError(str(exc)) from exc

    def minimum_variance(self, target: float | None = None) -> np.ndarray:
        problem = self.gmv_problem if target is None else self.frontier_problem
        if target is not None:
            self.target.value = target
        solver = self.options.get('solver', 'CLARABEL')
        kwargs = dict(tol_gap_abs=1e-10, tol_feas=1e-10, tol_gap_rel=1e-10, max_iter=300) if solver == 'CLARABEL' else {}
        try:
            problem.solve(solver=solver, warm_start=True, **kwargs)
        except cp.error.SolverError as exc:
            raise OptimizationError(f'{solver}: {exc}') from exc
        if problem.status != cp.OPTIMAL or self.w.value is None:
            raise OptimizationError(f'{solver}: status={problem.status}, target={target}')
        weights = np.asarray(self.w.value).ravel().copy()
        self.check(weights, target)
        return weights

    def return_extrema(self) -> tuple[float, float]:
        bounds = list(zip(self.lower, self.upper))
        values = []
        for sign in (1, -1):
            result = linprog(sign * self.mean, A_eq=np.ones((1, len(self.mean))), b_eq=[1],
                             bounds=bounds, method='highs')
            if not result.success:
                raise OptimizationError(f'Return-range LP failed: {result.message}')
            self.check(result.x)
            values.append(float(result.x @ self.mean))
        return values[0], values[1]

    def tangency(self, starts: list[np.ndarray]) -> tuple[np.ndarray, list[dict]]:
        require(self.options.get('tangency_solver', 'SLSQP') == 'SLSQP', 'Only SLSQP tangency supported')
        if self.spec.kind == 'unrestricted':
            require(analytical_tangency(self.mean, self.cov, self.rf,
                    self.options.get('tangency_existence_tolerance', 1e-12)).status == 'ATTAINED',
                    'NONATTAINED: do not approximate unrestricted tangency with finite SLSQP weights')
        excess = self.mean - self.rf

        def objective(w: np.ndarray) -> float:
            return -float(w @ excess) / np.sqrt(w @ self.cov @ w)

        def gradient(w: np.ndarray) -> np.ndarray:
            sd = np.sqrt(w @ self.cov @ w)
            return -excess / sd + (w @ excess) * (self.cov @ w) / sd ** 3

        candidates, attempts = [], []
        for start in starts:
            result = minimize(objective, start, jac=gradient, method='SLSQP',
                              bounds=list(zip(self.lower, self.upper)),
                              constraints=[{'type': 'eq', 'fun': lambda w: w.sum() - 1,
                                            'jac': lambda w: np.ones(len(w))}],
                              options={'ftol': 1e-12, 'maxiter': 2000})
            record = dict(success=bool(result.success), message=str(result.message), iterations=int(result.nit))
            if result.success:
                try:
                    self.check(result.x)
                    require(np.isfinite(result.fun), 'Non-finite Sharpe objective')
                    candidates.append(result.x.copy())
                except (OptimizationError, ValidationError) as exc:
                    record.update(success=False, message=str(exc))
            attempts.append(record)
            if not record['success']:
                LOG.warning('Rejected tangency attempt: %s', record)
        if not candidates:
            raise OptimizationError(f'All tangency solves failed: {attempts}')
        best = min(candidates, key=objective)
        require(-objective(best) > 0, 'No positive-excess tangency found; CAL construction undefined for this analysis')
        return best, attempts


@dataclass
class AnalysisResult:
    assets: list[str]
    mean: np.ndarray
    covariance: np.ndarray
    portfolios: pd.DataFrame
    frontier: pd.DataFrame
    cal: pd.DataFrame
    checks: dict
    tangency: TangencyResult | None = None


def analyze(mean: np.ndarray, cov: np.ndarray, assets: list[str], rf: float,
            spec: ConstraintSpec, frontier_options: dict, options: dict) -> AnalysisResult:
    optimizer = PortfolioOptimizer(mean, cov, rf, spec, options)
    count = int(frontier_options.get('points', 200))
    require(count >= 20, 'Frontier needs at least 20 points')
    gmv = optimizer.minimum_variance()
    gmv_return = float(gmv @ mean)
    checks: dict = {'gmv_solver': options.get('solver', 'CLARABEL'), 'gmv_status': 'optimal'}
    weight_tol = options.get('crosscheck_weight_tolerance', 2e-4)
    analytical_tan = None
    tangency_result = None
    if spec.kind == 'unrestricted':
        tangency_result = analytical_tangency(mean, cov, rf, options.get('tangency_existence_tolerance', 1e-12))
        analytical_tan = tangency_result.weights
        gmv_error = float(np.max(np.abs(gmv - analytical_gmv(cov))))
        require(gmv_error < weight_tol, 'Analytical/numerical GMV disagree')
        checks['gmv_analytical_max_weight_error'] = gmv_error
        padding = frontier_options.get('target_range_padding', 0.25)
        span = max(float(np.ptp(mean)), 0.001)
        lo = min(float(np.min(mean)), gmv_return) - padding * span
        hi = max(float(np.max(mean)), gmv_return if analytical_tan is None else
                 float(analytical_tan @ mean)) + padding * span
        if np.ptp(mean) == 0:
            lo = hi = float(mean[0])  # the entire minimum-variance frontier is one GMV point
    else:
        lo, hi = optimizer.return_extrema()
    # Include both branches and GMV; allocate half the resolution to each branch.
    targets = np.unique(np.concatenate([np.linspace(lo, gmv_return, count // 2),
                                        np.linspace(gmv_return, hi, count - count // 2 + 1)]))
    if np.ptp(mean) == 0:
        targets = np.array([float(mean[0])])
    rows, analytical_errors = [], []
    for target in targets:
        # A single failed point aborts this analysis; no partial frontier is returned/saved.
        weights = optimizer.minimum_variance(float(target))
        if spec.kind == 'unrestricted':
            analytical_errors.append(float(np.max(np.abs(weights - analytical_frontier(mean, cov, target)))))
        row = portfolio_metrics(weights, mean, cov, rf)
        row.update(target_monthly=float(target), efficient=bool(target >= gmv_return - 1e-12),
                   solver_status='optimal', **{f'w_{a}': float(w) for a, w in zip(assets, weights)})
        rows.append(row)
    frontier = pd.DataFrame(rows)
    efficient = frontier.loc[frontier.efficient]
    best_row = efficient.loc[efficient.sharpe_monthly.idxmax()]
    frontier_weights = best_row[[f'w_{a}' for a in assets]].to_numpy(dtype=float)
    tangency = None
    checks.update(frontier_max_sharpe_monthly=float(best_row.sharpe_monthly),
                  accepted_frontier_points=len(frontier))
    if tangency_result is None or tangency_result.status == 'ATTAINED':
        starts = [np.full(len(assets), 1 / len(assets)), gmv, frontier_weights]
        tangency, attempts = optimizer.tangency(starts)
        tangent_metrics = portfolio_metrics(tangency, mean, cov, rf)
        gap = tangent_metrics['sharpe_monthly'] - float(best_row.sharpe_monthly)
        require(-1e-7 <= gap <= options.get('frontier_sharpe_tolerance', 0.005),
                f'Tangency/frontier Sharpe cross-check failed (monthly gap {gap:.6g}); increase frontier.points')
        checks.update(tangency_attempts=attempts, tangency_frontier_sharpe_gap_monthly=gap)
        tangency_result = TangencyResult('ATTAINED', tangency,
                                        gross_exposure=tangent_metrics['gross_exposure'],
                                        coefficients=None if tangency_result is None else tangency_result.coefficients)
    else:
        checks.update(tangency_attempts=[], tangency_frontier_sharpe_gap_monthly=None)
    checks['tangency_status'] = tangency_result.status
    if analytical_errors:
        require(max(analytical_errors) < weight_tol, 'Analytical/numerical frontiers disagree')
        checks['frontier_analytical_max_weight_error'] = max(analytical_errors)
    if analytical_tan is not None:
        error = float(np.max(np.abs(tangency - analytical_tan)))
        require(error < weight_tol, f'Analytical/numerical tangency disagree: {error}')
        checks.update(tangency_analytical_max_weight_error=error,
                      frontier_analytical_max_weight_error=max(analytical_errors))
    portfolios = []
    for name, weights in [('GMV', gmv), ('tangency', tangency)]:
        if weights is None:
            continue
        row = dict(portfolio=name, **portfolio_metrics(weights, mean, cov, rf))
        row.update({f'w_{a}': float(w) for a, w in zip(assets, weights)})
        portfolios.append(row)
    # CAL allows lending/borrowing at the configured rate; risky holdings constraints apply
    # to the tangent fund, not to its scaled holdings in the combined cash/risky portfolio.
    cal = pd.DataFrame(columns=['risky_allocation', 'cash_allocation', 'sd_monthly',
                                'mean_monthly', 'sd_annual', 'mean_annual'])
    if tangency is not None:
        allocation = np.linspace(0, 1.5, 151)
        cal_sd = allocation * tangent_metrics['sd_monthly']
        cal_mean = rf + allocation * (tangent_metrics['mean_monthly'] - rf)
        cal = pd.DataFrame(dict(risky_allocation=allocation, cash_allocation=1 - allocation,
                               sd_monthly=cal_sd, mean_monthly=cal_mean,
                               sd_annual=np.sqrt(12) * cal_sd, mean_annual=12 * cal_mean))
    return AnalysisResult(assets, mean.copy(), cov.copy(), pd.DataFrame(portfolios), frontier, cal, checks, tangency_result)
