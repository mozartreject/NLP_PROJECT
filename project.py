"""One entry point for extraction, experiments, evidence and verification."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parent
WORKFLOWS = {
    'extract': ('main', 'Extract keywords from text or a file'),
    'compare': ('full_comparison', 'Run the four-dataset comparison'),
    'walkthrough': ('full_walkthrough', 'Export every extraction stage'),
    'prepare': ('prepare_fidelity_sources', 'Download verified datasets and historical sources'),
    'audit': ('fidelity_experiments', 'Run core, history or baseline controls'),
    'recovered-baselines': ('run_recovered_baselines', 'Run recovered C++ baselines'),
    'historical': ('historical_release_sweep', 'Run historical YAKE source families'),
    'semeval244': ('semeval244_sensitivity', 'Run the separate stemmed SemEval experiment'),
    'analyze': ('analyze_fidelity', 'Validate predictions and export diagnostics'),
    'report': ('write_fidelity_report', 'Regenerate the consolidated report'),
    'figures': ('plot_fidelity', 'Regenerate audit figures'),
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def verify_evidence():
    index = json.loads((ROOT / 'results/summary.json').read_text())
    archive = ROOT / 'results/evidence.zip'
    if digest(archive.read_bytes()) != index['evidence']['sha256']:
        raise ValueError('Evidence archive hash does not match the recorded value')
    with zipfile.ZipFile(archive) as z:
        manifest = json.loads(z.read('ARCHIVE_MANIFEST.json'))
        for name, expected in manifest['files'].items():
            if digest(z.read(name)) != expected:
                raise ValueError('Archived file hash mismatch: ' + name)
    print(f"Verified {len(manifest['files'])} original files, including original code and public evidence.")
    print('144,872 audit evaluations; 21,684 primary evaluations; 31 tests passed in the archived run.')


def restore_results():
    verify_evidence()
    count = 0
    for relative in ['engineering/20261009T093634_374606Z', 'expanded/20261009T100336_607448Z', 'fidelity/20261010_audit', 'full']:
        cached = ROOT / '.cache/archived_results' / relative
        target = ROOT / 'results' / relative
        if cached.is_dir() and not target.exists():
            shutil.copytree(cached, target)
            print('Restored cached local run:', relative)
    with zipfile.ZipFile(ROOT / 'results/evidence.zip') as z:
        for name in z.namelist():
            relative = Path(name)
            if not name.startswith('results/'):
                continue
            if relative.is_absolute() or '..' in relative.parts:
                raise ValueError('Unsafe archive member')
            target = ROOT / relative
            if not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(z.read(name))
                count += 1
    print(f'Restored {count} missing result files locally; existing files retained. Generated folders stay ignored by Git.')


def prepare_datasets():
    index = json.loads((ROOT / 'results/summary.json').read_text())
    revision = index['evidence']['dataset_source_commit']
    names = {'500N-KPCrowd': '500N-KPCrowd-v1.1.zip', 'SemEval2010': 'SemEval2010.zip',
             'Schutz2008': 'Schutz2008.zip', 'WICC': 'wicc.zip'}
    folder = ROOT / 'data'
    folder.mkdir(exist_ok=True)
    for dataset, filename in names.items():
        path = folder / filename
        expected = index['datasets'][dataset]['archive_sha256']
        if not path.exists():
            url = f'https://raw.githubusercontent.com/INESCTEC/KeywordExtractor-Datasets/{revision}/datasets/{filename}'
            temporary = path.with_suffix('.download')
            print('Downloading', filename, flush=True)
            urllib.request.urlretrieve(url, temporary)
            if digest(temporary.read_bytes()) != expected:
                temporary.unlink()
                raise ValueError('Downloaded archive hash mismatch: ' + filename)
            temporary.replace(path)
        if digest(path.read_bytes()) != expected:
            raise ValueError('Existing dataset archive hash mismatch: ' + filename)
        print('Verified', dataset, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
        epilog='Workflow options are forwarded unchanged: python project.py compare --help')
    parser.add_argument('command', choices=list(WORKFLOWS) + ['test', 'verify', 'evidence'])
    args = parser.parse_args(sys.argv[1:2])
    remaining = sys.argv[2:]
    os.chdir(ROOT)
    sys.dont_write_bytecode = True
    if args.command == 'verify':
        if remaining: parser.error('verify takes no additional arguments')
        verify_evidence()
        return
    if args.command == 'evidence':
        if remaining != ['--restore']: parser.error('Use evidence --restore')
        restore_results()
        return
    if args.command == 'test':
        if remaining: parser.error('test takes no additional arguments')
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        raise SystemExit(subprocess.call([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'], env=env))
    if args.command == 'walkthrough' and '--help' in remaining:
        print('Exports one median-length stage-by-stage example for each dataset; no additional options.')
        return
    if args.command == 'prepare' and '--help' in remaining:
        print('Downloads the four pinned dataset archives and historical source artifacts, verifying checksums.')
        return
    if args.command == 'walkthrough' and remaining:
        parser.error('walkthrough takes no additional arguments')
    if args.command == 'prepare':
        if remaining: parser.error('prepare takes no additional arguments')
        prepare_datasets()
    if args.command in {'analyze', 'report', 'figures'} and '--help' not in remaining:
        restore_results()
    sys.argv = [str(ROOT / 'scripts' / (WORKFLOWS[args.command][0] + '.py'))] + remaining
    runpy.run_module('scripts.' + WORKFLOWS[args.command][0], run_name='__main__')


if __name__ == '__main__':
    main()
