rm -r summary/*
rm -r BiasJobs/*
bash preparefiles.sh
python3 create_condor_jobs.py
condor_submit condor/submit.sub