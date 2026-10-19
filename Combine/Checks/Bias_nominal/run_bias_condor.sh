#!/bin/bash

CAT=$1
PDF=$2
SPLIT=$3
NTOYS=$4
SPLITSIZE=$5


echo "Category : ${CAT}"
echo "PDF index: ${PDF}"
echo "Split    : ${SPLIT}"
echo "N toys   : ${NTOYS}"
echo "Split size: ${SPLITSIZE}"


# save original directory
WORKDIR=$(pwd)


JOBDIR=${WORKDIR}/BiasJobs/${CAT}/pdf${PDF}/split${SPLIT}


mkdir -p ${JOBDIR}


cd ${JOBDIR}



python3 ${WORKDIR}/RunBiasStudy_condor.py \
-d ${WORKDIR}/Datacard_tutorial_${CAT}_mu_inclusive_toy.root \
-w ${WORKDIR}/Datacard_tutorial_${CAT}_mu_inclusive.root \
-t \
-f \
-p \
--statOnly \
--gaussianFit \
--generateCSV \
-b ${CAT} \
-n ${NTOYS} \
--split ${SPLITSIZE} \
--toyIndex ${PDF} \
--toySplit ${SPLIT} \
--outCSV bias_${CAT}_${PDF}_${SPLIT}.csv \
-c "--setParameterRanges r=-20,20 \
--cminDefaultMinimizerStrategy 1 \
--X-rtd MINIMIZER_freezeDisassociatedParams \
--X-rtd MINIMIZER_multiMin_hideConstants \
--X-rtd MINIMIZER_multiMin_maskConstraints"