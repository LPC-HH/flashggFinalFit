#!/usr/bin/env python3

import os
import ROOT as r
import math


# =========================
# configuration
# =========================


categories = [
    "ggHcat1",
    "ggHcat2",
    "ggHcat3",
    "ggHcat4",
    "ggHcat5",
    "ggHcat6",
    "VBFcat2",
    "VBFcat3",
    "VBFcat4",
    "VBFcat5",
    "VBFcat6",
]


datacard_pattern = (
    "Datacard_tutorial_{cat}_mu_inclusive_toy.root"
)


workspace_name = "w"


nToys = 2000
splitSize = 200


runScript = "run_bias_condor.sh"


# =========================
# helper
# =========================


def get_n_pdf(datacard):

    f = r.TFile.Open(datacard)

    if not f or f.IsZombie():
        raise RuntimeError(
            "Cannot open %s"%datacard
        )


    ws = f.Get(workspace_name)


    if not ws:
        raise RuntimeError(
            "Cannot find workspace %s"%workspace_name
        )


    pdfs = ws.allPdfs()


    n_pdf = None


    it = pdfs.createIterator()

    while True:

        pdf = it.Next()

        if not pdf:
            break


        if pdf.InheritsFrom(
            "RooMultiPdf"
        ):

            n_pdf = pdf.getNumPdfs()
            break



    if n_pdf is None:

        raise RuntimeError(
            "No RooMultiPdf found in %s"%datacard
        )


    f.Close()

    return n_pdf



# =========================
# make jobs
# =========================


jobs=[]


for cat in categories:


    toyDatacard = datacard_pattern.format(
        cat=cat
    )


    n_pdf = get_n_pdf(
        toyDatacard
    )


    n_split = math.ceil(
        nToys/splitSize
    )


    print(
        cat,
        ":",
        n_pdf,
        "pdfs",
        n_split,
        "splits"
    )


    for ipdf in range(n_pdf):

        for isplit in range(n_split):

            jobs.append(
                {
                    "cat":cat,
                    "pdf":ipdf,
                    "split":isplit,
                    "nToys":nToys,
                    "splitSize":splitSize
                }
            )



print(
    "Total jobs:",
    len(jobs)
)



# =========================
# write condor submit
# =========================


os.makedirs(
    "condor/logs",
    exist_ok=True
)


with open(
    "condor/submit.sub",
    "w"
) as f:


    f.write(
f"""
executable = {runScript}

arguments = $(cat) $(pdf) $(split) $(nToys) $(splitSize)


initialdir = {os.getcwd()}


output = condor/logs/$(ClusterId).$(ProcId).out
error  = condor/logs/$(ClusterId).$(ProcId).err
log    = condor/logs/$(ClusterId).$(ProcId).log


getenv = True


+Group = "long"
+HepJob_Experiment = "CMS"
+HepJob_RealGroup = "CMS"
+HepJob_VirtualGroup = "CMS"

+HepJob_Walltime = "default"

accounting_group = CMS.CMS.default

queue cat,pdf,split,nToys,splitSize from (
"""
    )


    for j in jobs:

        f.write(
            "{} {} {} {} {}\n".format(
                j["cat"],
                j["pdf"],
                j["split"],
                j["nToys"],
                j["splitSize"]
            )
        )


    f.write(
        ")\n"
    )


print(
    "Created condor/submit.sub"
)