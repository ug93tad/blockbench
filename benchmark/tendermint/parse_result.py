import os
import glob
from config import *

OUTPUT_HEADER = "# n txrate nclients throughput nblocks"
# return nsuccesses, nfails, latency
def read_all(n, tr, nc, run):
  pattern = "{}/{}/client*".format(TM_HOME,LOG_SUFFIX.format(n, tr, nc, run))
  files = glob.glob(pattern)
  return files

# return (tp, nblocks) 
def compute_throughput(files): 
  tp = 0
  nblocks = 0
  count=0
  for f in files:
    fn = open(f, 'r')
    lines = fn.readlines()
    if len(lines) != 3:
      continue
    else:
      tp += int(lines[1].split()[1])
      nblocks += int(lines[2].split()[4])
      count +=1
  return tp/float(count), nblocks/float(count)

if __name__ == "__main__":
  print OUTPUT_HEADER
  for run in RUNS:
    print "Run {}".format(run)
    for f in FS:
      for tr in TXRATES:
        for nc in NR_CLIENTS:
          files = read_all(3*f+1,tr,nc,run)
          tp, nblocks = compute_throughput(files)
          print "{} {} {} {} {}".format(f,tr,nc,tp,nblocks)
