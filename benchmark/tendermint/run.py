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
  f = open("{}/{}".format(TM_HOME,HOSTSFILE), 'r')
  hs = f.readlines()
  f.close()
  servers = [x.strip() for x in hs[:N]]
  clients = [x.strip() for x in hs[N:(N+C)]]
  ips = {}
  for idx, c in enumerate(clients):
    ips[c] = get_ip(servers[idx%N])

  return servers, clients, ips

def run_exp(f, txrate, nclients, run):
  N = 3*f+1
  LOGPATH = LOG_SUFFIX.format(N, txrate, nclients, run)
  
  SERVERS, CLIENTS, IPS = get_hosts(N, nclients)

  # start server
  SRC_CONFIG = "{}/testnet/n{}".format(TM_HOME, N)
  DST_CONFIG = "{}/tendermint/testnet".format(TM_DATA)
  SERVER_LOG_PREFIX = "{}/{}".format(TM_DATA, LOGPATH)
  for i in range(N):
    execute("ssh {} {}".format(SERVERS[i], SERVER_CMD.format(DST_CONFIG, DST_CONFIG, SERVER_LOG_PREFIX,  SRC_CONFIG, DST_CONFIG, "{}/n{}/node{}".format(DST_CONFIG,N,i), SERVER_LOG_PREFIX)))
  time.sleep(60)

  # start client
  for idx,c in enumerate(CLIENTS):
    CLIENT_LOG_DIR = "{}/{}".format(TM_HOME, LOGPATH) 
    cmd = "ssh {} {}".format(c, CLIENT_CMD.format(CLIENT_LOG_DIR, SLEEP_TIME, txrate, IPS[c], CLIENT_LOG_DIR, idx))
    execute(cmd)

  time.sleep(SLEEP_TIME+5)
  
  #stop
  for s in SERVERS:
    cmd = "ssh {} {}".format(s, KILL_SERVER_CMD.format(DST_CONFIG))
    execute(cmd)
  for c in CLIENTS:
    cmd = "ssh {} {}".format(c, KILL_CLIENT_CMD)
    execute(cmd)

if __name__=="__main__":
  for run in RUNS:
    for f in FS:
      for tr in TXRATES:
        for nc in NR_CLIENTS:
          print "Running f={}, tr={}, nc={}".format(f,tr,nc)
          run_exp(f,tr,nc,run)
          time.sleep(5)
