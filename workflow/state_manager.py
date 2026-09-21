"""Atomic, run-specific state; explicit resume archives and replays prior attempts."""
from __future__ import annotations
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import json
from pathlib import Path
import re
import shutil
import uuid
import yaml
from src.generate_tables import write_json
from src.validation import require, ExternalDataUnavailable

STAGES = ['configuration', 'yahoo_data', 'input_validation', 'markowitz_full',
          'markowitz_subsamples', 'diversification', 'ff_data', 'sim', 'comparisons',
          'numerical_outputs', 'output_validation', 'figures', 'markowitz_report', 'report']
DIRECTORIES = ['logs', 'data', 'models', 'tables', 'figures', 'diagnostics']


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


class RunState:
    def __init__(self, root: Path, config: dict, resume: str | None = None):
        root.mkdir(parents=True, exist_ok=True)
        run_id = resume or datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '_' + uuid.uuid4().hex[:8]
        require(bool(re.fullmatch(r'[A-Za-z0-9_-]+', run_id)), 'Invalid run ID')
        self.path = root / run_id
        if resume:
            require((self.path / 'state.json').is_file(), f'Unknown run ID: {resume}')
        else:
            self.path.mkdir(exist_ok=False)
        self.lock = (self.path / '.lock').open('a')
        try:
            fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self.lock.close()
            raise RuntimeError(f'Run {run_id} is active in another process')
        try:
            history = []
            if resume:
                previous = json.loads((self.path / 'state.json').read_text())
                snapshot = yaml.safe_load((self.path / 'config_snapshot.yaml').read_text())
                # Offline is an execution mode and may change when resuming the same analysis.
                a, b = yaml.safe_load(yaml.safe_dump(snapshot)), yaml.safe_load(yaml.safe_dump(config))
                a['data'].pop('offline', None)
                b['data'].pop('offline', None)
                require(a == b, 'Resume config differs from snapshot; use a new run for changed analysis')
                history = previous.get('attempt_history', []) + [dict(
                    attempt=previous['attempt'], status=previous['status'], updated_at=previous['updated_at'])]
                archive = self.path / 'attempts' / f"{previous['attempt']:03d}"
                archive.mkdir(parents=True, exist_ok=False)
                for name in DIRECTORIES + ['state.json', 'results_summary.json', 'interpretation.md',
                                            'markowitz_report.md', 'config_snapshot.yaml']:
                    source = self.path / name
                    if source.exists():
                        shutil.move(str(source), str(archive / name))
            for name in DIRECTORIES:
                (self.path / name).mkdir()
            (self.path / 'config_snapshot.yaml').write_text(yaml.safe_dump(config, sort_keys=False))
            self.state = dict(run_id=run_id, attempt=len(history) + 1, attempt_history=history,
                              created_at=now(), updated_at=now(), status='RUNNING',
                              stages={name: {'status': 'PENDING'} for name in STAGES})
            self.save()
        except BaseException:
            self.close()
            raise

    def save(self) -> None:
        self.state['updated_at'] = now()
        write_json(self.path / 'state.json', self.state)

    @contextmanager
    def stage(self, name: str, allow_external_block: bool = False):
        stage = self.state['stages'][name]
        stage.update(status='RUNNING', started_at=now())
        self.save()
        try:
            yield
        except BaseException as exc:
            if allow_external_block and isinstance(exc, ExternalDataUnavailable):
                stage.update(status='BLOCKED_EXTERNAL', finished_at=now(), reason=str(exc))
                self.save()
                return
            stage.update(status='FAILED', finished_at=now(), error=f'{type(exc).__name__}: {exc}')
            self.state['status'] = 'FAILED'
            for other in self.state['stages'].values():
                if other['status'] == 'PENDING':
                    other.update(status='SKIPPED', reason=f'Required stage {name} failed')
            self.save()
            raise
        else:
            stage.update(status='PASSED', finished_at=now())
            self.save()

    def block_dependency(self, name: str, dependency: str) -> None:
        stage = self.state['stages'][name]
        require(stage['status'] == 'PENDING', f'Cannot block already executed stage {name}')
        stage.update(status='BLOCKED_DEPENDENCY', reason=f'Requires {dependency}', dependency=dependency)
        self.save()

    def complete(self) -> None:
        require(all(s['status'] in {'PASSED', 'SKIPPED', 'BLOCKED_EXTERNAL', 'BLOCKED_DEPENDENCY'}
                    for s in self.state['stages'].values()),
                'Cannot complete a run with unfinished stages')
        self.state['status'] = 'PARTIAL' if any(s['status'].startswith('BLOCKED_')
                                              for s in self.state['stages'].values()) else 'PASSED'
        self.save()

    def close(self) -> None:
        fcntl.flock(self.lock, fcntl.LOCK_UN)
        self.lock.close()
