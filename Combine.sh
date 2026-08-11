cd Combine

echo "[INFO] Copying Signal, Data, and Datacards into combine folder"
bash copy.sh

echo "[INFO] Creating workspaces for Combine"
bash run_workspace.sh

echo "[INFO] Running asymptotic limits"
bash run_asym.sh  

echo "[INFO] Running significance"
bash run_sig.sh  
