#!/bin/bash

for CAT in ggHcat1 ggHcat2 ggHcat3 ggHcat4 ggHcat5
do

    echo "================================================="
    echo "Running bias study for ${CAT}"
    echo "================================================="

    CARD=../../Datacard_tutorial_${CAT}_mu_inclusive.root
    OUTDIR=bias_${CAT}

    # clean old outputs
    rm -rf BiasToys BiasFits BiasPlots

    mkdir -p ${OUTDIR}

    # generate toys
    python3 RunBiasStudy.py \
        -d ${CARD} \
        -t

    # run fits
    python3 RunBiasStudy.py \
        -d ${CARD} \
        -f \
        -c "--cminDefaultMinimizerStrategy 0 \
             --X-rtd MINIMIZER_freezeDisassociatedParams \
             --X-rtd MINIMIZER_multiMin_hideConstants \
             --X-rtd MINIMIZER_multiMin_maskConstraints \
             --X-rtd MINIMIZER_multiMin_maskChannels=2 \
             --freezeParameters MH"

    # make plots
    python3 RunBiasStudy.py \
        -d ${CARD} \
        -p \
        --gaussianFit

    # move outputs
    mv BiasToys  ${OUTDIR}/
    mv BiasFits  ${OUTDIR}/
    mv BiasPlots ${OUTDIR}/

done