#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys
from optparse import OptionParser
from collections import OrderedDict as od
from commonTools import *
from commonObjects import *
from tools.submissionTools import *

def get_options():
    parser = OptionParser()
    parser.add_option('--inputDir', dest='inputDir', default='', help="Top directory containing sample folders")
    parser.add_option('--inputConfig', dest='inputConfig', default='', help="Config file for trees2ws or trees2ws_data")
    parser.add_option('--ext', dest='ext', default='test', help="Extension for output job dir")
    parser.add_option('--mode', dest='mode', default='trees2ws', help="Mode: trees2ws or trees2ws_data or mass_shift")
    parser.add_option('--modeOpts', dest='modeOpts', default='', help="Extra options for the script (in quotes)")
    parser.add_option('--inputMass', dest='inputMass', default='125', help="Mass of signal")
    parser.add_option('--targetMasses', dest='targetMasses', default='120,130', help="For mass_shift only")
    parser.add_option('--batch', dest='batch', default='condor', help='condor or local')
    parser.add_option('--queue', dest='queue', default='espresso', help='Queue name for batch')
    parser.add_option('--jobOpts', dest='jobOpts', default='', help='Extra condor job options')
    parser.add_option('--printOnly', dest='printOnly', default=False, action="store_true", help='Only print, do not submit')
    return parser.parse_args()

(opt, args) = get_options()

print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ RUNNING WS SCRIPTS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

def leave():
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ RUNNING WS SCRIPTS (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    exit(0)

# Check input directory
if not os.path.isdir(opt.inputDir):
    print(f"[ERROR] inputDir {opt.inputDir} does not exist")
    leave()

# Walk over subfolders
for subfolder in sorted(os.listdir(opt.inputDir)):
    full_path = os.path.join(opt.inputDir, subfolder)
    if not os.path.isdir(full_path):
        continue

    # Extract year
    if "_" not in subfolder:
        print(f"[WARN] Subfolder '{subfolder}' skipped: no '_' in name")
        continue
    year = subfolder.split("_")[-1]

    # Find root file
    root_files = [f for f in os.listdir(full_path) if f.endswith(".root") and f.startswith("output_")]
    if not root_files:
        print(f"[WARN] No output_*.root in {full_path}, skipping")
        continue
    root_file = os.path.join(full_path, root_files[0])

    print(f" --> Found sample: {subfolder}, year: {year}, file: {root_file}")

    # Build options
    options = od()
    options['inputDir']     = full_path
    options['inputConfig']  = opt.inputConfig
    options['ext']          = opt.ext
    options['year']         = year
    options['mode']         = opt.mode
    options['modeOpts']     = f'--inputTreeFile {root_file} ' + opt.modeOpts
    options['inputMass']    = opt.inputMass
    options['targetMasses'] = opt.targetMasses
    options['batch']        = opt.batch
    options['queue']        = opt.queue
    options['jobOpts']      = opt.jobOpts
    options['printOnly']    = opt.printOnly

    # Check mode
    if options['mode'] not in ['trees2ws','trees2ws_data','mass_shift']:
        print(f"[ERROR] mode {options['mode']} not allowed")
        leave()

    # Prepare job directory
    job_dir = f"{twd__}/outdir_{options['ext']}"
    if not os.path.exists(job_dir):
        os.makedirs(job_dir)

    # Write submission script
    writeSubFiles(options)
    print(f"  --> Submission script written for {subfolder}")

    # Run or print only
    if not options['printOnly']:
        submitFiles(options)
    else:
        print("  --> printOnly mode: script not submitted")

leave()
