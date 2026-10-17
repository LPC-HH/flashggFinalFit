#!/bin/bash

set -e

VERSION="v2p4p2_newfits"

echo "Organizing outputs into ${VERSION}..."

# Signal
mkdir -p "Signal/${VERSION}"
mv -v Signal/outdir_packaged "Signal/${VERSION}/"
mv -v Signal/outdir_tutorial_combined "Signal/${VERSION}/"

# Background
mkdir -p "Background/${VERSION}"
mv -v Background/outdir_tutorial "Background/${VERSION}/"

# Plots
mkdir -p "Plots/${VERSION}"
mv -v Plots/plots_tutorial "Plots/${VERSION}/"

# Datacards

mkdir -p "Datacard/${VERSION}"
mv -v Datacard/Datacard_tutorial* "Datacard/${VERSION}/"

echo "Done."
echo "Outputs moved to ${VERSION}"
