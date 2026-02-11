# Stage3: Parallelized Image Retrieval and Classification

**Required Inputs:**
1) config_files/ neuron_<neuron_id>_results_ecii_V2.txt     (_Path: /homes/samatha94/ExAI_inputs_and_outputs/Stage1_Results/config_files_)
2) model_resnet50V2_10classes_retest2023June.h5             (_Path: /homes/samatha94/ExAI_inputs_and_outputs/Stage1_Results/model_resnet50V2_10classes_retest2023June.h5_)


**Expected Outputs:**                  (_Path: /homes/samatha94/ExAI_inputs_and_outputs/Stage3_Results_)
1) Google_images

   Google_images/neuron_<neuron_id>/solution1/<concept_name>/<image>.jpg
   
   Google_images/neuron_<neuron_id>/solution2/<concept_name>/<image>.jpg
   
   Google_images/neuron_<neuron_id>/solution3/<concept_name>/<image>.jpg
   
3) evaluation/neuron<neuron_id>_solution<solution_id>_evaluation_set.csv
4) verification/neuron<neuron_id>_solution<solution_id>_verification_set.csv

**Instructions to Set Up the Environment and Run the Python Script:**

1) Install Python 3.11.5

   Ensure Python 3.11.5 is installed on your system by executing below command
   
         python --version

2) Set Up a Virtual Environment

   Install virtualenv if it is not already installed
   
         pip install virtualenv

3) Create a virtual environment named 'venv'

         python -m venv venv

4) Activate the Virtual Environment

   On macOS/Linux:
   
         source venv/bin/activate
   
   On Windows:
   
         venv\Scripts\activate

5) Install Required Python Packages:

         pip install tensorflow Pillow pandas scikit-learn keras opencv-python requests python-magic python-magic-bin pygoogle_image

6) Run the Python Script

         python main.py

**Steps to Run the Script on BeoCat:**

**Bash file name:** job_stage3.sh

**Bash Scripts:**

https://github.com/Samatha1994/Bash_scripts/blob/main/job_stage3_generate_indices.sh
https://github.com/Samatha1994/Bash_scripts/blob/main/job_stage3.sh

**Bash Command to kick off the job:** sbatch job_stage3.sh

**Bash command to check the status of the job:** 

sacct --format=JobID,JobName,State,ReqMem,MaxRSS,Start,End,TotalCPU,Elapsed,NCPUS,NNodes,NodeList --jobs= <job_id>

**Log file:** my_job_output_<job_id>.txt (_Path: /homes/samatha94/_)

**Bash Command to cancel the job:** scancel job_id

**Guide to install python-magic-bin manually on Beocat:** https://github.com/Samatha1994/ExAI_related_documents/blob/main/installing%20python%20magic%20bin%20manually.docx


