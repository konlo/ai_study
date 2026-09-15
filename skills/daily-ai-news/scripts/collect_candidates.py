#!/usr/bin/env python3
"""Run project collectors in a temporary copy, preserving existing edited digests."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--edition', choices=('both', 'korea', 'global'), default='both')
    args = parser.parse_args()
    source = args.repo.resolve() / 'daily_ai_summary'
    scripts = {'global': 'fetch_summarize.py', 'korea': 'fetch_korean.py'}
    editions = ('global', 'korea') if args.edition == 'both' else (args.edition,)
    required = ['scripts/fetch_summarize.py']
    for edition in editions:
        required += [f'scripts/{scripts[edition]}', 'feeds_ko.md' if edition == 'korea' else 'feeds.md']
    for relative in set(required):
        if not (source / relative).is_file():
            parser.error(f'Missing project file: {source / relative}')
    work = Path(tempfile.mkdtemp(prefix='daily-ai-news-')) / 'daily_ai_summary'
    work.mkdir()
    # Copy only collector inputs, never credentials or previous output files.
    for relative in set(required):
        target = work / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / relative, target)
    results = {}
    for edition in editions:
        try:
            result = subprocess.run([sys.executable, str(work / 'scripts' / scripts[edition])],
                                    cwd=work, timeout=180, check=False)
            results[edition] = {'success': result.returncode == 0, 'returncode': result.returncode}
        except subprocess.TimeoutExpired:
            results[edition] = {'success': False, 'error': 'collector timed out after 180 seconds'}
    outputs = sorted(str(path) for path in (work / 'site' / 'content').glob('*.md'))
    print(json.dumps({'candidate_directory': str(work), 'outputs': outputs, 'editions': results},
                     ensure_ascii=False, indent=2))
    return 0 if all(result['success'] for result in results.values()) else 1


if __name__ == '__main__':
    sys.exit(main())
