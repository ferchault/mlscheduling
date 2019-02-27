## Overview

This folder contains an example how to use the machine-learnt timings for efficient load balancing on a high-performance computing cluster. The solution presented here is designed to have as few dependencies as possible to support as many clusters as possible.

Dependencies (on the HPC cluster) are:
- [GNU parallel](https://www.gnu.org/software/parallel/) which in turn only requires a C compiler
- bash

Moreover, the python package [QML](https://github.com/qmlcode/qml) is required on a workstation, but not necessarily on the compute cluster. Installation instructions can be found [here](http://www.qmlcode.org/installation.html), but the copy-and-paste one-liner is
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
A python script then can be used to build a list of estimated timings as follows.
```
[WALLTIME in seconds] [command to run]
[WALLTIME in seconds] [command to run]
...
```
On the compute cluster, this file then can be passed on to `parallel.sh` within a job script.
