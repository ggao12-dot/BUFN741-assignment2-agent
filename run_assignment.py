#!/usr/bin/env python3
"""CLI entry point; all analytics live in reusable modules."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import yaml
from workflow.orchestrator import run_assignment


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=Path('config/assignment2.yaml'))
    parser.add_argument('--offline', action='store_true', help='Require validated local raw caches; no network')
    parser.add_argument('--resume', metavar='RUN_ID', help='Archive prior attempt and replay this explicit run ID')
    args = parser.parse_args()
    try:
        config = yaml.safe_load(args.config.read_text())
        if args.offline:
            config['data']['offline'] = True
        path = run_assignment(config, Path(__file__).resolve().parent, args.resume)
    except Exception as exc:
        print(f'Assignment failed: {exc}', file=sys.stderr)
        return 1
    status = json.loads((path / 'state.json').read_text())['status']
    if status == 'PARTIAL':
        print(f'Assignment PARTIAL: Markowitz outputs available; external/dependent stages blocked. See {path}')
        return 2
    print(f'Assignment complete: {path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
