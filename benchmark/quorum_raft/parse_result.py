import os
import glob
from config import *

OUTPUT_HEADER = "# n threads txrate nclients"
# return nsuccesses, nfails, latency
def read_all(n, ts, tr, nc, run):
  pattern = "{}/{}/client*".format(QUORUM_HOME,LOG_SUFFIX.format(n, ts, tr, nc, run))
  files = glob.glob(pattern)
  return files

# return tuple (nsuccesses, nfails)
def compute_throughput(files): 
  nsuccesses = 0
  for f in files:
    fn = open(f, 'r')
    line = ""
    tp = 0
    for l in fn.readlines():
      if l.startswith("polled block"):
        line =l
        tp += int(line.strip().split(' ')[4])
    if tp > nsuccesses:
      nsuccesses = tp
  return nsuccesses/float(SLEEP_TIME),0

def compute_latency(files):
  total_latency= 0
  count = 0
  for f in files:
    fn = open(f, 'r')
    for l in fn.readlines():
      if l.startswith("In the last 2s"):
        total_latency += float(l.strip().split(' ')[10])
        count += int(l.strip().split(' ')[7])
   
  if count==0:
    return 0
  return total_latency/count

if __name__ == "__main__":
  print OUTPUT_HEADER
  for run in RUNS:
    print "Run {}".format(run)
    for f in FS:
      for ts in THREADS:
        for tr in TXRATES:
          for nc in NR_CLIENTS:
            files = read_all(2*f+1,ts,tr,nc,run)
            tp,_ = compute_throughput(files)
            lt = compute_latency(files)
            print "{} {} {} {} {} {}".format(f,ts,tr,nc,tp,lt)
