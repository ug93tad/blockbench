from config import *

# post processing
# output:
#       #reads, time, average (and read_cdf file)
#       #writes, time, average (and write_cdf file)
#       #commits, time, average (and commit_cdf file)
#       #blocks
#       #client throughput (for writes only) and client_latency_cdf file
def post_process_server(server_log):
  server = open(server_log, 'r')

  read_times=[]
  write_times=[]
  commit_times=[]

  nreads = nwrites = read_total = write_total = ncommits = commit_total = 0
  lines = server.readlines()
  for l in lines:
    if l.find("GetState latency") != -1:
      read_times.append(int(l.split(' ')[8])/1000000.0)
    if l.find("PutState latency") != -1:
      write_times.append(int(l.split(' ')[8])/1000000.0)
    if l.find("Batch commit time") != -1:
      val = int(l.split(' ')[11])
      commit_times.append(val/1000000.0)
      ncommits = ncommits + 1
      commit_total = commit_total + val

    # stats
    if l.find("poll stats") != -1:
      nreads = int(l.split(' ')[9])
      nwrites = int(l.split(' ')[10])
      read_total = int(l.split(' ')[11])
      write_total = int(l.split(' ')[12])
      dbsize = int(l.split(' ')[13])

  if nreads==0:
   print("#reads: {} \t #total time (ms): {} \t average (ms): {}".format(0,0,0))
  else:
    print("#reads: {} \t #total time (ms): {} \t average (ms): {}".format(nreads, read_total/1000000.0,
  read_total/(nreads*1000000.0)))

  print("#writes: {} \t #total time (ms): {} \t average (ms): {}".format(nwrites, write_total/1000000.0,
  write_total/(nwrites*1000000.0)))
  print("#commits: {} \t #total time (ms): {} \t average (ms): {}".format(ncommits, commit_total/1000000.0,
  commit_total/(ncommits*1000000.0)))
  print("#blocks: {}".format(ncommits))

  #sort
  read_times.sort()
  write_times.sort()
  commit_times.sort()

  write_cdf(read_times, POST_PROCESS_DIR+"/read_cdf")
  write_cdf(write_times, POST_PROCESS_DIR+"/write_cdf")
  write_cdf(commit_times, POST_PROCESS_DIR+"/commit_cdf")

  server.close()
  return dbsize

def post_process_client(client_log):
  client = open(client_log, 'r')
  lines = client.readlines()
  nblocks = ntxs = times = 0 
  latencies = []
  
  for l in lines:
    if l.find('polled block') != -1:
      ntxs = ntxs + int(l.split(' ')[4])
      nblocks = nblocks + 1
    if l.find('last 2s') != -1:
      tokens = l.split(' ')
      times = times + 1
      if int(tokens[7]) != 0:
        latencies.append(float(l.split(' ')[10])/int(tokens[7]))

  print("avg block size: {}".format(float(ntxs)/nblocks))
  print("avg client throughput (tx/s): {}".format(float(ntxs)/times))
  print("avg client latency (s): {}".format(float(sum(latencies))/len(latencies)))
  latencies.sort()
  write_cdf(latencies, POST_PROCESS_DIR+"/client_latency_cdf")

  client.close()


def write_cdf(values, filename):
  f = open(filename, 'w')
  n = len(values)
  for i in range(n):
    f.write("{} {}\n".format(float(i)/n, values[i]))
  f.close()
