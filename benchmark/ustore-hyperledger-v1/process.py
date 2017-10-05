from config import *
import os

# post processing
# output:
#       #reads, time, average (and read_cdf file)
#       #writes, time, average (and write_cdf file)
#       #commits, time, average (and commit_cdf file)
#       #blocks
#       #client throughput (for writes only) and client_latency_cdf file
def post_process_server(server_log, db):
  server = open(server_log, 'r')

  read_times=[]
  write_times=[]

  nreads = nwrites = read_total = write_total = 0
  lines = server.readlines()
  for l in lines:
    if l.find("GetState latency") != -1:
      read_times.append(int(l.split(' ')[10])/1000000.0)
    if l.find("Commit time") != -1:
      wt = int(l.split(' ')[11])/1000000.0
      write_times.append(wt)
      write_total += wt
      nreads = int(l.split(' ')[13])
      read_total = int(l.split(' ')[15])/1000000.0

  nwrites = len(write_times)
  if nreads==0:
   print("#reads: {} \t #total time (ms): {} \t average (ms): {}".format(0,0,0))
  else:
    print("#reads: {} \t #total time (ms): {} \t average (ms): {}".format(nreads, read_total,
  read_total/(nreads)))

  print("#writes: {} \t #total time (ms): {} \t average (ms): {}".format(nwrites, write_total,
  write_total/(nwrites)))

  #sort
  read_times.sort()
  write_times.sort()

  os.system("mkdir -p {}".format(POST_PROCESS_DIR))
  write_cdf(read_times, POST_PROCESS_DIR+"/read_cdf_{}".format(db))
  write_cdf(write_times, POST_PROCESS_DIR+"/write_cdf_{}".format(db))

  server.close()

def write_cdf(values, filename):
  f = open(filename, 'w')
  n = len(values)
  for i in range(n):
    f.write("{} {}\n".format(float(i)/n, values[i]))
  f.close()
