#!/bin/bash

LOGFILE="run_Signifiance_results_$(date +%Y%m%d_%H%M%S).log"
CSVFILE="run_Signifiance_results_$(date +%Y%m%d_%H%M%S).csv"

categories=(
    ggH
    ggHcat1
    ggHcat2
    ggHcat3
    VBF
    VBFcat1
    VBFcat2
    VBFcat3
    VBFcat4
    All
)

echo "Category,Significance" > "$CSVFILE"

run_combine() {
    local category=$1
    local datacard="Datacard_tutorial_${category}_mu_inclusive.root"

    echo ">>> Running on $category ($datacard)" | tee -a "$LOGFILE"

    output=$(combine -M Significance "$datacard" -m 125 -t -1 --expectSignal 1 2>&1)

    echo "$output" >> "$LOGFILE"
    echo "" >> "$LOGFILE"

    val_sig=$(echo "$output" | grep "Significance:" | awk '{print $2}')

    echo "$category,$val_sig" >> "$CSVFILE"
}

for cat in "${categories[@]}"; do
    run_combine "$cat"
done

echo "All combine jobs finished."
echo "Full log: $LOGFILE"
echo "Summary CSV: $CSVFILE"
