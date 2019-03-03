## File description

### cluster-waittimes.txt
Queueing times for a large number of jobs on a real queueing system with high share of quantum chemistry calculations.

| Column | Comment | Type | Example |
|--|--|--|--|
| Eligible |  Time when the job entered the queueing system | Datetime | 2018-11-27T16:46:00|
| Start | Time when the job began to execute | Datetime | 2018-11-27T16:46:00|
| Timelimit | Walltime limit of the individual job | SLURM time | 06:00:00|
| NCPUS | Number of cores requested | Integer | 1 |

### *-_fchl_pred.txt

Real vs. predicted walltimes for the FCHL representation for all data sets. First letter of the filename indicates the dataset.

| Column | Comment | Type | Example |
|--|--|--|--|
| 1 | Real walltime duration in seconds | Decimal | 607
| 2 | Predicted walltime duration in seconds | Decimal | 1560.9
