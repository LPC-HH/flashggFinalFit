#!/bin/bash
# ============================================================
# fitDYshapes.sh
#
# Wrapper around Background/bin/fitDYshapes.
#
# It takes care of the CMSSW environment (scram runtime plus
# flashggFinalFit/setup.sh, which exports ROOT_IO) and runs the
# tool from the Background directory, so that the four parameter
# files end up in Background/DYshapes/.
#
# Usage (from anywhere):
#
#   ./fitDYshapes.sh [fitDYshapes options]
#
# Examples:
#
#   ./fitDYshapes.sh                       # ggH + VBF, all categories found
#   ./fitDYshapes.sh --cats ggHcat1,ggHcat2
#   ./fitDYshapes.sh --cats VBFcat1 --no-plots
#   ./fitDYshapes.sh --cats ggHcat1 --tries 3
#
# The executable is built with:   cd Background && make
# ============================================================

set -e

HERE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"   # .../flashggFinalFit/Background
FFDIR="$( cd "$HERE/.." && pwd )"                          # .../flashggFinalFit
SRCDIR="$( cd "$FFDIR/.." && pwd )"                        # .../CMSSW_.../src

# --- CMSSW environment -------------------------------------------------
cd "$SRCDIR"

# the CMS setup script prints unrelated flatpak warnings, hide them
source /cvmfs/cms.cern.ch/cmsset_default.sh >/dev/null 2>&1 || true

eval `scramv1 runtime -sh`

# ROOT_IO + PYTHONPATH (also re-does the scram runtime)
source "$FFDIR/setup.sh"

# --- run ---------------------------------------------------------------
if [ ! -x "$HERE/bin/fitDYshapes" ]; then
    echo "[ERROR] $HERE/bin/fitDYshapes not found"
    echo "        build it first:   cd $HERE && make"
    exit 1
fi

cd "$HERE"

echo "[INFO] ROOT_IO = $ROOT_IO"
echo "[INFO] running ./bin/fitDYshapes $*"
echo

exec ./bin/fitDYshapes "$@"
