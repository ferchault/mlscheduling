## Overview

This folder contains an example how to use the machine-learnt timings for efficient load balancing on a high-performance computing cluster. The solution presented here is designed to have as few dependencies as possible to support as many clusters as possible.

On the compute cluster, this code needs either Python2 or Python3 but no further dependencies.

Moreover, the python package [QML](https://github.com/qmlcode/qml) is required on a workstation, but not on the compute cluster. Installation instructions can be found [here](http://www.qmlcode.org/installation.html), but the copy-and-paste two-liner is
```
sudo apt-get install python-pip gfortran libblas-dev liblapack-dev git
pip install --user qml
```

## General workflow

At first, a random subset of the planned calculations should be submitted to the HPC cluster as usual. The resulting timings and molecular geometries have to be collected as follows:
```
[XYZ file name without suffix (.xyz)] [WALLTIME in seconds] 
[XYZ file name without suffix (.xyz)] [WALLTIME in seconds]
...
```

Next, another text file is neeed that contains a list of XYZ files and the command you would run on the compute cluster to run the corresponding calculation. The file should look like this:

```
[XYZ file name without suffix (.xyz)] [command to run]
[XYZ file name without suffix (.xyz)] [command to run]

...
```
The python script `train-predict.py` then can be used to build a list of estimated timings as follows. This file is called `taskfile`
```
[WALLTIME in seconds] [command to run]
[WALLTIME in seconds] [command to run]
...
```
On the compute cluster, this file then can be passed on to `parallel.py` within a job script. The usage is
```
python parallel.py TASKFILE NUMBER_OF_CONCURRENT_INVOCATIONS TIMELIMIT_SECONDS
```
where `NUMBER_OF_CONCURRENT_INVOCATIONS` is an integer specifying how many independent calculation can be run in parallel and `TIMELIMIT_SECONDS` is the total duration of the whole job as specified to the queueing system / scheduler.


## Practical example

In our test case, we would like to run our favorite quantum chemistry code. We have 1000 calculations to do and they are structured as follows
```
main_folder/
  submit.job
  runs/
    run-0\
      input.xyz
      run.inp
    run-1\
      input.xyz
      run.inp
    ...
    run-999\
      input.xyz
      run.inp
```
In this case, `submit.job` is the job script that is used to submit the calculation to the scheduler/queueing system. For simplicity, we assume that executing `submit.job` in one of the `run-XXX` folders completes the calcuation.

### Training data
First, we need some calculations to be completed such that we can estimate the timings of the subsequent ones. For this, we submit the first 100 calculations. On SLURM, the command is `sbatch`, on PBS/Torque, it's `qsub` - use whatever belongs to the cluster you're using.

```bash
cd main_folder/runs
for i in $(seq 0 99)
do
  cd run-$i
  sbatch ../../submit.job
  cd ..
done
```
Once the jobs have completed, collect their total execution time. Usually, the software package you use prints this information at the end of the log file. Alternatively, the log files of the queueing system have this information as well. Convert it to seconds and prepare a file like this
```
4217 main_folder/runs/run-0/input.xyz
4711 main_folder/runs/run-1/input.xyz
1337 main_folder/runs/run-2/input.xyz
...
```
and name it `completed-timings.txt`. Now compile a list of calculations yet to complete
```
main_folder/runs/run-100/input.xyz
cd main_folder/runs/run-100; ../../submit.job
main_folder/runs/run-101/input.xyz
cd main_folder/runs/run-101; ../../submit.job
...
main_folder/runs/run-999/input.xyz
cd main_folder/runs/run-999; ../../submit.job
```
and name it `remaining-jobs.txt`. 

### Training
Copy all XYZ files to the machine where you have `qml` installed. Make sure to keep the directory structure intact. One way of doing this is
```bash
tar cf transfer.tar -T $(find . -type f -name '*.xyz')
# copy transfer.tar to new machine
tar xf transfer.tar
```

If you run `train-predict.py` as follows
```
python train-predict.py completed-timings.txt remaining-jobs.txt [path to xyz files]
```
the timings will be written to the terminal and you can forward them to a new file `tasklist.txt` that contains all commands from `remaining-jobs.txt` with a timing estimate. Copy it back to the compute cluster.

### Submission
Now you need to have a new submission script. Before, you had one execution per job script. This single call is called a "job step". Now you need multiple job steps to be run in parallel. Most compute clusters document how to do that. In almost all cases, it is sufficient to ask for an integer multiple of the compute resources and then execute the `submit.job` file multiple times. In this case, create a new job script that (after specifiying the resources) executes the following
```
python parallel.py taskfile.txt 12 43200
```
Here, we assume that we want to run 12 calculations in parallel and that our walltime limit is 12 hours, i.e. 43200 seconds.
