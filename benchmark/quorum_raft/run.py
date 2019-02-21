import os
import subprocess
import sys
import time
from config import *

def get_ip(host):
  out = subprocess.check_output(["ping", "-c", "1", host])
  return out.split()[2].strip('()')

# return lists of servers and clients, and a map of client host to its ip
def get_hosts(N, C): 
  f = open("{}/{}".format(QUORUM_HOME,HOSTSFILE), 'r')
  hs = f.readlines()
  f.close()
  servers = [x.strip() for x in hs[:N]]
  clients = [x.strip() for x in hs[N:(N+C)]]
  ips = {}
  for idx, c in enumerate(clients):
    ips[c] = get_ip(servers[idx%N])

  return servers, clients, ips

def run_exp(f,threads, txrate, nclients, run):
  N = 2*f+1
  LOGPATH = LOG_SUFFIX.format(N, threads, txrate, nclients, run)
  
  SERVERS, CLIENTS, IPS = get_hosts(N, nclients)

  # start server
  execute(INIT_CMD.format(QUORUM_HOME, N, N, SERVER_LOG_PREFIX, LOGPATH))
  time.sleep(50)

  # start client
  for idx,c in enumerate(CLIENTS):
    CLIENT_LOG_DIR = "{}/{}".format(QUORUM_HOME, LOGPATH) 
    cmd = "ssh {} {}".format(c, CLIENT_CMD.format(CLIENT_LOG_DIR, YCSB_DIR, threads, IPS[c], txrate, CLIENT_LOG_DIR, idx))
    execute(cmd)

  time.sleep(SLEEP_TIME)
  
  #stop
  for c in CLIENTS:
    cmd = "ssh {} {}".format(c, KILL_CLIENT_CMD)
    execute(cmd)
  for s in SERVERS:
    cmd = "ssh {} {}".format(s, KILL_SERVER_CMD.format(QUORUM_HOME))
    execute(cmd)

if __name__=="__main__":
  for run in range(3):
    for f in FS:
      for ts in THREADS:
        for tr in TXRATES:
          for nc in NR_CLIENTS:
            print "Running f={}, ts={}, tr={}, nc={}".format(f,ts,tr,nc)
            run_exp(f,ts,tr,nc,run)
            time.sleep(10)
