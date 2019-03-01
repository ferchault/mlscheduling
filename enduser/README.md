## Overview

This folder contains an example how to use the machine-learnt timings for efficient load balancing on a high-performance computing cluster. The solution presented here is designed to have as few dependencies as possible to support as many clusters as possible.

On the compute cluster, this code needs either Python2 or Python3 but no further dependencies.

Moreover, the python package [QML](https://github.com/qmlcode/qml) is required on a workstation, but not on the compute cluster. Installation instructions can be found [here](http://www.qmlcode.org/installation.html), but the copy-and-paste one-liner is
```
pip install --user qml
```

## General workflow

At first, a random subset of the planned calculations should be submitted to the HPC cluster as usual. The resulting timings and molecular geometries have to be collected as follows:
```
[WALLTIME in seconds] [path to XYZ file]
[WALLTIME in seconds] [path to XYZ file]
...
```

Next, another text file is neeed that contains a list of XYZ files and the command you would run on the compute cluster to run the corresponding calculation. The file should look like this:

```
[path to XYZ file]
[command to run]
[path to XYZ file]
[command to run]
...
```
A python script then can be used to build a list of estimated timings as follows. This file is called `taskfile`
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
