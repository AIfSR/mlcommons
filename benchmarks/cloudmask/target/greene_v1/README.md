# Benchmarking on NYU HPC Greene Cluster

## Pre-requisite
Before installing on Greene HPC:

1. Renew or request for a [NYU HPC 
Account](https://www.nyu.edu/life/information-technology/research-computing-services/high-performance-computing/high-performance-computing-nyu-it/hpc-accounts-and-eligibility.html).
2. Set up SSH keys for your github account. 



## Set-up Git

```bash
greene> git config pull.rebase false
greene> git config --global user.name "FIRST_NAME LAST_NAME"
greene> git config --global user.email "MY_NAME@example.com"
greene> git config --global core.editor "nano"
```

## Get Interactive node and login

Interactive jobs allow users to interact with HPC, allocate resources and run commands or scripts from the command line itself. You can run an interactive job like this:

```bash
greene> srun --gres=gpu:v100:1 --pty --mem=64G --time 02:00:00 /bin/bash
```

Here we are asking for one v100 GPU with 64G memory and for 2 hours. If you exceed the time or memory limits allocated for it, the job will also abort. Different gpu can be allocated by changing the '--gres' flag like --gres=gpu:rtx8000:1 would give access to rtx8000. Similarly, time can be changed using the '--time' flag.

## Generating Experiment Configurations

All bash terminal lines that are to be executed on the interactive node start with "node>". Below all the variables that start with '$' like $USER do not need to be changed as they are system variables. $USER will be automatically replaced with the person's username. 

```bash
node> export USER_SCRATCH=/scratch/$USER/github-fork
node> export PROJECT_DIR=$USER_SCRATCH/mlcommons/benchmarks/cloudmask
node> export PROJECT_DATA=$USER_SCRATCH/data

node> mkdir -p $USER_SCRATCH
node> mkdir -p $PROJECT_DATA
node> cd $USER_SCRATCH

node> git clone https://github.com/VarshithaChennamsetti/mlcommons.git

node> cd $PROJECT_DIR
```

## Set-up Python

Here, we are showing how to create a conda environment and python virtual environment. We are then using the python environment to install all package dependencies.

```bash
node> module purge
node> module load anaconda3/2020.07
node> module load cudnn/8.6.0.163-cuda11

greene> 
  mkdir -p $USER_SCRATCH
  mkdir -p $PROJECT_DATA
  cd $USER_SCRATCH
  git clone https://github.com/laszewsk/mlcommons.git
  node(alternative 1)> git clone https://github.com/rg3515/mlcommons.git
  node(alternative 2)> git clone https://github.com/VarshithaChennamsetti/mlcommons.git
  node(alternative 3)> git clone git@github.com:rg3515/mlcommons.git

# module load python/intel/3.8.6
node> python3 -m venv $USER_SCRATCH/ENV3

node> conda deactivate

node> source $USER_SCRATCH/ENV3/bin/activate

node> pip install pip -U
node> which python

```
The command 'which python' should return $USER_SCRATCH/ENV3/bin/python.

All the above commands are used whenever we are trying to set-up the environment for the very first time. For all other times, these commands are sufficient to run all the following commands. 

```bash
greene> srun --gres=gpu:v100:1 --pty --mem=64G --time 02:00:00 /bin/bash

node> export USER_SCRATCH=/scratch/$USER/github-fork
node> export PROJECT_DIR=$USER_SCRATCH/mlcommons/benchmarks/cloudmask
node> export PROJECT_DATA=$USER_SCRATCH/data

node> source $USER_SCRATCH/ENV3/bin/activate

```

Make sure to change the paths in the 'config.yaml' file to appropriate locations. The paths for 'train_dir', 'inference_dir', 'model_file', 'output_dir' and 'venvpath' must be fixed based on the user's directory.

```bash
node> cd $PROJECT_DIR/target/greene/
node> time make requirements
```
This command takes about 1 minute to execute.

## Obtain the data

There are two ways to obtain the data. The difference is in the way they are stored and obtained.

### 1. Obtain data stored on AWS S3 bucket

The following command is used to run a script which gets the data from an AWS S3 Bucket using the 'awscli' python package.

```bash
node> time make data
```

This command takes about 1hr to execute.

### 2. Obtain data stored on Globus

Besides using AWS to obtain the training/testing data, Globus is a viable, easy alternative.

### To-Do's on Greene ###
* Log into your Greene account on terminal; create a data/ directory under your scratch directory (e.g. /scratch/[your netid]/data/)

### To-Do's on Globus ###
* Go to [Globus.org](https://www.globus.org/)
* Log in with your NYU account
* Once you are log in, you should see a main page with different functionalities on the left/right side column
* Click on File Manager on the left/right column
* In the top right corner, you should see "Panels"; make sure to set it to two panes;
* On your left panel, go to Collection Search, and search for "mlcommons-cloudmask-data", and click it to select
* On your right panel, go to Collection Search and search for "Greene scratch directory"; once your selected it, your should see the path automatically populate to your scratch directory on Greene; Double-click to go into your newly created data/ directory
* Lastly, **Make Sure** to go back onto your left panel (the panel with collection "mlcommons-cloudmask-data"); click **Select All** on the horizontal bar (you need both one-day/ and ssts/ directory); and click **Start** _on the left panel_ to start data transferring

Now, you will need to wait for approximately 30 minutes for transfer completion.

## Run the code

Here, we are creating 'outputs' directory to store the inference model prediction masks. We are using the 'sbatch' command to run the slurm job, where details about resources like memory, time and gpu are given in the 'simple.slurm' file and also the command to run the program. 'squeue' command shows the status of the job i.e, if its pending or running etc.

```bash
greene> cd $PROJECT_DIR/target/greene/
greene> mkdir -p outputs
greene> sbatch simple.slurm
greene> squeue -u $USER
```

## Monitor/Check output

You can check the output by looking into the output log files. The location and names of those files can be found in 'config_simple.yaml' next to 'log_file:' and 'mlperf_logfile:'.

```bash
cat ./mlperf_cloudmask_v100_gpu_1.log
```

This will have output log lines in a form like this:

:::MLLOG {"namespace": "", "time_ms": 1687900000019, "event_type": "POINT_IN_TIME", "key": "submission_status", "value": "success", "metadata": {"file": "slstr_cloud.py", "lineno": 389}}

Each log line starts with ':::MLLOG' and generally has all the keys seen above. The type of event and values for each of them would be different. There are two log lines in particular that are to be checked for a successful run. One of them is as seen above, which has '"key": "submission_status", "value": "success"' in the line. This displays that the program ran successfully with no errors. The other line would have '"key": "result"' and has information about accuracy and loss. If both the lines are seen, then the program must've run successfully.

You can also keep looking at the output files while the program runs using the following command.

```bash
tail -f ./mlperf_cloudmask_v100_gpu_1.log
```

## Reproduce Experiments

This will create multiple copies of config_simple.yaml, simple.slurm and the output log files.

```bash
bash reproduce_experiments.sh
```

## Visualize results

To visualize the graphs, pass the paths to the log files as the arguments while running the file visualizer.py. You can pass along a single experiment log files or combine all of them and then pass them as inputs.

```bash
cat cloudmask_200* >> cloudmask_200.log
cat mlperf_cloudmask_200* >> mlperf_cloudmask_200.log
python3 visualizer.py mlperf_cloudmask_200.log cloudmask_200.log
```

---
**NOT TESTED FROM HERE ON**
---


# Parameterized jobs for rivanna with cloudmesh-sbatch

This version of cloudmask uses [cloudmesh-sbatch](https://github.com/cloudmesh/cloudmesh-sbatch) 
to coordinate a parameter sweep over hyperparameters. It significantly simplifies managing
different experiments as it stores the output in a directory format that 
simplifies analysis.




## 1. Programming Environment Prerequisites

### 1.1 LaTeX (optional)

We assume if you like to use the automated report generated (under
development) you have full version of latex installed

```bash
module load texlive
```

If you do not want to create the reports, please skip this step.

### 1.2 Python 3

We assume you have a fairly new version of Python installed susch as 
Python 3.10.8. However, a version greater than 3.10.4 will also do.
We install the version of python to be used in a python venv and 
install in it the required packages. Please note that as of
Dec 2022, python 3.11 is not supported by anaconda which we 
use for this project as it is the recommended version by the 
rivanna support staff.

If you have executed this step previously, you only have to say 

```bash
source ~/ENV3/bin/activate
```

Otherwise, do the following:

```bash
module purge
module load anaconda

conda create -y -n python310 python=3.10
source activate python310

python -m venv ~/ENV3
source ~/ENV3/bin/activate
mkdir ~/cm
cd ~/cm
pip install cloudmesh-installer
cloudmesh-installer get sbatch
cms help
```

In either case your command promt will have the prefix `(ENV3)`.

Note that we use two different python environment. 
One for running sbatch, the other in whcih we run tensorflow, which will be 
setup automatically in a later step.


## 2. Generating experiment configurations

Choose a PROJECT_DIR where you like to install the code. Rivanna offers some temporary
space in the /scratch directory. 

```bash
export PROJECT_DIR=/scratch/$USER
mkdir -p ${PROJECT_DIR}
cd ${PROJECT_DIR}
git clone ssh://git@github.com/laszewsk/mlcommons.git
cd mlcommons/benchmarks/cloudmask/target/rivanna
```
## 3. Obtaining the data

Next we obtain the data. The command uses an aws call to download both
daytime and nighttime images of the sky. The total space the data dir
will take up is 180GB. It will take around 20 minutes to finish downloading
the data. In case the data was previously downloaded, this stepp will take 15 
seconds.


```bash
time make data
```

The data is downloaded to 

```
$(PROJECT_DIR)/mlcommons/benchmarks/cloudmask/data
```

## 4. Generate parameterized jobs

Next we generate some parameterized jobs. These runs are controlled with two files.

* `config.yaml` -- Specifies the parameters for cloudmask and the 
  SLURM scripts.

* `ubuntu.in.slurm` -- Specifies the slurm script in which the parameters 
  defined by `config.yaml` will be substituted.

  This is simply done via the following make commands after you have selected 
  appropriate values in the yaml file. 

  ```bash
  # setup venv
  make setup  # this takes minutes 
  make project # this takes less then 15 seconds
  ```

  The makefile targets will generate two files and a subdirectory with individual 
  experiments:

* `project.sh` -- Is a file that contains each individual job submission 
  based on the parameter sweep that is defined by the YAML file.
* `project.json` -- Is a file that contains the metadata associated with the 
  individual job submissions generated from the experiment permutations
* `project` -- Is a directory that includes for each individual experiment a 
  slurm script and a yaml file.

## 5. Running the parameterized jobs

Before executing the `jobs-project.sh` script, it is advised that you inspect the 
output of the files and directories. 

Be aware that many jobs may take hours to complete.  We provide here a simple 
estimate while using some predefined model as specified in our yaml file.

| Epochs | Time in s |    Time |
|-------:|----------:|--------:|
|      1 |       900 | 15m 00s |
|     10 |      2667 | 44m 27s |
|     30 |       ??? |     ??? |
|     50 |       ??? |     ??? |
|    100 |       ??? |     ??? |

An example on how to look at a slurm script (assuming we use an a100 in the YAML file) is 

```bash
less project/card_name_a100_gpu_count_1_cpu_num_1_mem_64GB_repeat_1_epoch_10/rivanna.slurm
```

To look at the yaml file for this experiment, use 

```bash
less project/card_name_a100_gpu_count_1_cpu_num_1_mem_64GB_repeat_1_epoch_10/config.yaml
```

or simply call  which uses emacs to open both files from the firts parameterized job.

```bash
make inspect
```

Note: to exit emacs, press `Ctrl+x` and then `Ctrl+c` to return to your normal prompt.

## 6. Running the experiments

If all the output from above looks correct, you can execute the jobs
by running the last two scripts that are generated by cms sbatch
generate submit.

```bash
make run
# Submitted batch job 12345678
```

The number will be different for you.

To find out the status you can do the following commands. The first
looks up the job by the id, the second will list all jobs you
submitted. if you just have one job it will return just that one
job. `make status` is a shortcut to see all jobs of a user.

```bash
make status
```


The `make run` will submit the job to slurm, and the
notebook file will be outputted in the
`$(pwd)/cloudmask/<experiment_id>` directory.

You can see the progress of each job by inspecting the `*.out` and
`*.error` files located in the `$(pwd)/cloudmask/<experiment_id>`). 
The following log files will be created:

* `cloudmask-%j.log` -- Output created by SLURM from whole job.in.slurm script.
* `cloudmask-%j.error` -- Error messages caught by SLURM when either the job 
   writes to stderr, or an error is caught by SLURM.
* `gpu0.log` -- Logfile with Temperatures and energy values for the GPU0. This 
   assumes you run the code on the GPU with number 0.
* `mlperf_cloudmask.log` -- Logfile that records all MLCommons logging events.
* `cloudmask_run.log` --  Logfile for recording runtimes.
* `output.log` -- Logfile that covers all the output of the `slstr_cloud.py` file.

To watch the output dynamically for an example run you can use the command 

```bash
tail -f  project/card_name_a100_gpu_count_1_cpu_num_6_mem_64GB_TFTTransformerepochs_2/*.out
```

you will have to change the second parameter in the path according to your 
hyperparameters and what you like to watch 

The file `output.log` contains a convenient human readable summary of the various portions of the program execution generated with cloudmesh StopWatch. It includes details of the compute node, as well as runtimes.


```
+---------------------------------+---------------------------------------------------+
| Attribute                       | Value                                             |
|---------------------------------+---------------------------------------------------|
| ANSI_COLOR                      | "0;31"                                            |
| BUG_REPORT_URL                  | "https://bugs.centos.org/"                        |
| CENTOS_MANTISBT_PROJECT         | "CentOS-7"                                        |
| CENTOS_MANTISBT_PROJECT_VERSION | "7"                                               |
| CPE_NAME                        | "cpe:/o:centos:centos:7"                          |
| HOME_URL                        | "https://www.centos.org/"                         |
| ID                              | "centos"                                          |
| ID_LIKE                         | "rhel fedora"                                     |
| NAME                            | "CentOS Linux"                                    |
| PRETTY_NAME                     | "CentOS Linux 7 (Core)"                           |
| REDHAT_SUPPORT_PRODUCT          | "centos"                                          |
| REDHAT_SUPPORT_PRODUCT_VERSION  | "7"                                               |
| VERSION                         | "7 (Core)"                                        |
| VERSION_ID                      | "7"                                               |
| cpu                             | Intel(R) Xeon(R) Gold 6230 CPU @ 2.10GHz          |
| cpu_cores                       | 40                                                |
| cpu_count                       | 40                                                |
| cpu_threads                     | 40                                                |
| date                            | 2022-12-07 15:42:28.276533                        |
| frequency                       | scpufreq(current=2100.0, min=0.0, max=0.0)        |
| mem.active                      | 59.0 GiB                                          |
| mem.available                   | 308.5 GiB                                         |
| mem.free                        | 297.8 GiB                                         |
| mem.inactive                    | 9.2 GiB                                           |
| mem.percent                     | 18.1 %                                            |
| mem.total                       | 376.5 GiB                                         |
| mem.used                        | 61.4 GiB                                          |
| platform.version                | #1 SMP Wed Feb 23 16:47:03 UTC 2022               |
| python                          | 3.10.8 (main, Nov 24 2022, 14:13:03) [GCC 11.2.0] |
| python.pip                      | 22.2.2                                            |
| python.version                  | 3.10.8                                            |
| sys.platform                    | linux                                             |
| uname.machine                   | x86_64                                            |
| uname.node                      | udc-aj36-36                                       |
| uname.processor                 | x86_64                                            |
| uname.release                   | 3.10.0-1160.59.1.el7.x86_64                       |
| uname.system                    | Linux                                             |
| uname.version                   | #1 SMP Wed Feb 23 16:47:03 UTC 2022               |
| user                            | Gregor von Laszewski                              |
+---------------------------------+---------------------------------------------------+
```

```
+-------------------------+----------+---------+ ...
| Name                    | Status   |    Time | ...
|-------------------------+----------+---------+ ...
| total                   | ok       | 900.437 | ...
| training                | ok       | 751.567 | ...
| loaddata                | ok       |   2.313 | ...
| training_on_mutiple_GPU | ok       | 744.44  | ...
| inference               | ok       | 148.178 | ...
+-------------------------+----------+---------+ ...
```

This data is also available as CSV entries and can conveniently be grepped with 

```bash
$ grep "# csv" output.log
```

for further automated processing.


## 7. Generate Report

**TODO:** not implemented

```bash
pdflatex report.tex
pdflatex report.tex
# bibtex report.bib
pdflatex report.tex
```

This will create a pdf named `report.pdf`.  You can download this to
your local to view the output to view the report generated as a result
of the execution.
