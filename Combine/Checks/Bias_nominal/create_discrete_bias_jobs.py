#!/usr/bin/env python3
"""Standalone HTCondor job preparation for alternative-toy/discrete-nominal bias.

No jobs are submitted by this script. Outputs are separate from `condor/`.
Run under the initialized local CMSSW environment from Bias_nominal.
"""
import argparse
import os
from pathlib import Path
import shutil
import stat
import tarfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--categories', nargs='+', default=[f'ggHcat{i}' for i in range(1, 7)])
parser.add_argument('--n-toys', type=int, default=200)
parser.add_argument('--seed', type=int, default=12000)
parser.add_argument('--output-dir', default='condor_discrete')
parser.add_argument('--memory-mb', type=int, default=4500)
parser.add_argument('--clean', action='store_true', help='Delete only the directory named by --output-dir')
args = parser.parse_args()
if args.n_toys < 1 or args.memory_mb < 1 or args.seed < 1:
    parser.error('--n-toys, --seed, and --memory-mb must be positive')

base = Path.cwd().resolve()
output = (base / args.output_dir).resolve()
if output == base or base not in output.parents or output.name == 'condor':
    parser.error('--output-dir must be a separate directory below the current Bias_nominal directory (not condor/)')
if args.clean and output.exists():
    shutil.rmtree(output)
if output.exists() and any(output.glob('BiasCondor_*/split/toyPDF*/task.jdl')):
    parser.error('Prepared jobs already exist in --output-dir. Use --clean ONLY if you intend to replace them.')
output.mkdir(parents=True, exist_ok=True)

cmssw_base = os.environ.get('CMSSW_BASE')
arch = os.environ.get('SCRAM_ARCH')
if not cmssw_base or not arch:
    parser.error('Initialize CMSSW with cmsenv first')
cmssw_path = Path(cmssw_base).resolve()
release = cmssw_path.name
lib_dir = cmssw_path / 'lib' / arch
library_names = ('libHiggsAnalysisCombinedLimit.so', 'libflashggFinalFitDYCore.so')
libraries = [lib_dir / name for name in library_names]
for lib in libraries:
    if not lib.is_file():
        parser.error(f'Missing compiled library: {lib}')
dictionaries = sorted({*lib_dir.glob('*.pcm'), *lib_dir.glob('*.rootmap')})
combine = shutil.which('combine')
if not combine:
    parser.error('Cannot find combine; initialize CMSSW with cmsenv')

# The CMSSW ROOT dictionaries must see the full original C++ headers on worker nodes.
source_root = cmssw_path / 'src'
combine_headers = source_root / 'HiggsAnalysis/CombinedLimit/interface'
if not (combine_headers / 'RooMultiPdf.h').is_file():
    parser.error(f'Missing RooMultiPdf.h in {combine_headers}')
header_roots = [combine_headers]
for rel in ('CombineHarvester/CombineTools/interface', 'flashggFinalFit'):
    loc = source_root / rel
    if loc.is_dir():
        header_roots.append(loc)
suffixes = {'.h', '.hh', '.hpp', '.hxx', '.inc', '.icc', '.inl'}
headers = {}
for folder in header_roots:
    for header in folder.rglob('*'):
        if header.is_file() and header.suffix.lower() in suffixes:
            relative = header.relative_to(source_root)
            if not any(p in ('__pycache__', '.git') for p in relative.parts):
                headers[str(relative)] = header
archive = output / 'bias_headers.tar.gz'
with tarfile.open(archive, 'w:gz') as out:
    for rel, absolute in sorted(headers.items()):
        out.add(absolute, arcname=rel, recursive=False)
print(f'Header archive: {len(headers)} files; {archive.stat().st_size:,} bytes')

script = base / 'RunBiasStudy_discrete.py'
worker = base / 'run_discrete_by_cat.sh'
for required in (script, worker):
    if not required.is_file():
        parser.error(f'Missing script: {required}')

import ROOT
for lib in libraries:
    if ROOT.gSystem.Load(str(lib)) < 0:
        parser.error(f'Could not load ROOT library: {lib}')


def roo_collection(coll):
    itr = coll.createIterator()
    while True:
        obj = itr.Next()
        if not obj:
            break
        yield obj


def count_toy_pdfs(path):
    root = ROOT.TFile.Open(str(path))
    if not root or root.IsZombie():
        raise RuntimeError(f'Cannot read {path}')
    ws = root.Get('w')
    if not ws:
        raise RuntimeError(f'No workspace w in {path}')
    mp = [pdf for pdf in roo_collection(ws.allPdfs()) if pdf.InheritsFrom('RooMultiPdf')]
    if len(mp) != 1:
        raise RuntimeError(f'{path}: expected one RooMultiPdf; found {len(mp)}')
    n = mp[0].getNumPdfs()
    root.Close()
    return n


sender = ['#!/usr/bin/env bash', 'set -euo pipefail']
total = 0
for cat in args.categories:
    if not cat.replace('_', '').isalnum():
        parser.error(f'Invalid category: {cat}')
    toy_workspace = base / f'Datacard_tutorial_{cat}_mu_inclusive_toy.root'
    fit_workspace = base / f'Datacard_tutorial_{cat}_mu_inclusive.root'
    for p in (toy_workspace, fit_workspace):
        if not p.is_file() or p.stat().st_size == 0:
            parser.error(f'Missing/empty workspace: {p}')
    n_toy_pdfs = count_toy_pdfs(toy_workspace)
    print(f'{cat}: {n_toy_pdfs} alternative generating PDFs')
    for ipdf in range(n_toy_pdfs):
        job = output / f'BiasCondor_{cat}' / 'split' / f'toyPDF{ipdf}'
        job.mkdir(parents=True, exist_ok=True)
        for folder in ('log', 'out', 'err'):
            (job / folder).mkdir(exist_ok=True)
        copies = [
            (toy_workspace, f'Datacard_toy_{cat}.root'),
            (fit_workspace, f'Datacard_fit_{cat}.root'),
            (script, script.name),
            (Path(combine), 'combine'),
            *[(lib, lib.name) for lib in libraries],
            *[(d, d.name) for d in dictionaries],
            (archive, archive.name),
        ]
        transferred = []
        for source, target in copies:
            # Archive is shared by all jobs; transfer it without duplicating on disk.
            if source == archive:
                transferred.append(archive)
            else:
                dest = job / target
                shutil.copy2(source, dest)
                transferred.append(dest)
        worker_file = job / worker.name
        shutil.copy2(worker, worker_file)
        worker_file.chmod(worker_file.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        # Stable, separate seeds for each category and generating-PDF index.
        category_seed = sum((i + 1) * ord(c) for i, c in enumerate(cat)) * 1000
        seed = args.seed + category_seed + ipdf * 100000
        lines = [
            'universe = vanilla',
            f'initialdir = {job}',
            f'executable = {worker_file.name}',
            f'arguments = {cat} {ipdf} {release} {arch} {args.n_toys} {seed}',
            'log = log/$(ClusterId).$(ProcId).log',
            'output = out/$(ClusterId).$(ProcId).out',
            'error = err/$(ClusterId).$(ProcId).err',
            'should_transfer_files = YES',
            'when_to_transfer_output = ON_EXIT',
            'transfer_input_files = ' + ','.join(str(f) for f in transferred),
            'transfer_output_files = BiasResults',
            f'request_memory = {args.memory_mb}',
            'queue 1',
        ]
        proxy = os.environ.get('X509_USER_PROXY')
        if proxy and Path(proxy).is_file():
            lines.insert(7, f'x509userproxy = {proxy}')
        (job / 'task.jdl').write_text('\n'.join(lines) + '\n')
        sender.append(f'(cd "{job}" && condor_submit task.jdl)')
        total += 1

sender_file = base / 'condor_discrete_job_sender.sh'
sender_file.write_text('\n'.join(sender) + '\n')
sender_file.chmod(sender_file.stat().st_mode | stat.S_IXUSR)
print(f'Prepared {total} jobs under {output}; no jobs submitted.')
print(f'To submit: bash {sender_file.name}')
