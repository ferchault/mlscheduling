#!/usr/bin/bash
import queue
import shlex
import subprocess
import sys
import threading
import time

# read arguments
try:
	_, taskfile, concurrent, duration = sys.argv
	duration = float(duration)
	concurrent = int(concurrent)
except:
	print ("Usage: %s TASKFILE NUMBER_OF_CONCURRENT_INVOCATIONS TIMELIMIT_SECONDS")
	exit(1)

def submit_jobstep():
	while True:
		task = q.get()
		if task is None:
			break
		walltime, cmd = task
		if walltime + time.time() > deadline:
			print ('Skipped: %s %s' % (walltime, cmd))
		else:
			print ('Started: %s %s' % (walltime, cmd))
			process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
			process.wait()
			print ('Completed: %s %s %s' % (process.returncode, walltime, cmd))
		q.task_done()

# set deadline
deadline = time.time() + duration

# start workers
q = queue.Queue()
workers = []
for i in range(concurrent):
    w = threading.Thread(target=submit_jobstep)
    w.start()
    workers.append(w)

walltimes, cmds = [], []
with open(taskfile) as fh:
	for line in fh:
		walltime, cmd = line.strip().split(' ', maxsplit=1)
		walltimes.append(int(walltime))
		cmds.append(cmd)
tasks = sorted(zip(walltimes, cmds), key=lambda _: _[0])
for task in tasks:
	q.put(task)

q.join()
for i in range(concurrent):
	q.put(None)
for worker in workers:
	worker.join()
