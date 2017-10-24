# args: <workload file> <batchsize> <sample rate (ledger)> <sample rate (commit)>
# sample rate: 0 -> get data every sample
#             ~(1<<x) -> get data every 2^x samples                   
# outputs: 
  # 
import sys
import os
import time
from process import *
from config import *

usage = '''Usage:
    ustore-hyperledger.py <db> <nrecords> <nops> <w ratio> <r ratio> <batch size> <ledger sample interval>  <commit sample interval> <sleep>
    
      db:                       either ustore or rocksdb
      nrecords:                 total number of records
      nops:                     total number of read/write ops (after preloading nrecords)
      w ratio:                  write ratio [0,1]
      r ratio:                  read ratio [0,1]
      batch size:               block size
      ledger sample interval:   Put/Get sample period [2^x -1]
      commit sample interval:   Commit sample period
      sleep:                    how long to run the exps
    '''

def run_servers(nodes, cmds):
  for i in range(len(nodes)):
    cmd="ssh {} {}".format(nodes[i], cmds[i])
    print cmd
    os.system(cmd)

def run_clients(client, server, workload, thread, txrate):
  client_cmd = CLIENT_CMD.format(CLIENT_LOG_DIR, CLIENT_PATH, thread, CLIENT_PREFIX, workload, server, txrate, CLIENT_LOG_DIR, server, thread, txrate)
  cmd = "ssh {} {}".format(client, client_cmd)
  print cmd
  os.system(cmd)

def stop(client, servers):
  kill_client = "ssh {} {}".format(client, KILL_CLIENT_CMD)
  print kill_client
  os.system(kill_client)
  for s in servers:
    kill_server = "ssh {} {}".format(s, KILL_SERVER_CMD)
    print kill_server
    os.system(kill_server)

def run_exp(thread, txrate):
  N = 1  
  f = 0
  batch_size = int(sys.argv[6])
  ledger_sample_interval = int(sys.argv[7])
  execution_sample_interval = int(sys.argv[8])

  NODES=[]
  NODES.append(HOST.format(BOOTSTRAP_HOSTNO))
  for i in range(1,N):
    NODES.append(HOST.format(BOOTSTRAP_HOSTNO+i))
  
  CMDS=[] # list of commands
  for i in range(N): 
    env = ENV_TEMPLATE.format(i, "false", N, f, ledger_sample_interval, execution_sample_interval, batch_size, sys.argv[1])

    if i > 0:
      # add discoverynode
      env = "{} {}".format(env, ENV_EXTRA.format(NODES[0]))

    peer_log = PEER_LOG.format(LOG_PATH, "hl_log", thread, txrate)

    CMDS.append(CMD.format(peer_log, DEPLOY_PATH, LOG_PATH, DEPLOY_PATH, BUILD_PATH, USTOREDB_GOPATH, env, LOGGING_LEVEL, peer_log))

  run_servers(NODES, CMDS)
  time.sleep(10)

  CLIENT_NODE = HOST.format(CLIENT_HOSTNO)
  run_clients(CLIENT_NODE, NODES[0], WORKLOAD_FILE, thread, txrate)

  time.sleep(SLEEP_TIME)

  stop(CLIENT_NODE, NODES)
  time.sleep(5)
  return "{}/client_{}_{}_{}".format(CLIENT_LOG_DIR, NODES[0], thread, txrate)

def get_db_size():
  path = DEPLOY_PATH+"/production"
  size = 0
  for dirpath, dirname, filenames in os.walk(path):
    for f in filenames:
      fp = os.path.join(dirpath, f)
      size += os.path.getsize(fp)
  return size

# change the workload files with the given nrecords, nops,... parameters
def prepare_workload():
  cmd = "sed -i -e \'s|recordcount.*|recordcount={}|g\' -e \'s|operationcount.*|operationcount={}|g\' -e \'s|readproportion.*|readproportion={}|g\' -e \'s|updateproportion.*|updateproportion={}|g\' {}"
  cmd = cmd.format(sys.argv[2], sys.argv[3], sys.argv[5], sys.argv[4], WORKLOAD_FILE)
  print cmd
  os.system(cmd)

if __name__ == "__main__":
  if len(sys.argv) != 10 :
    print usage
    sys.exit(1)

  SLEEP_TIME = int(sys.argv[9])
  prepare_workload()
  for thread in THREADS:
    for txrate in TXRATES:
      client_log = run_exp(thread, txrate)
      peer_log = PEER_LOG.format(LOG_PATH, "hl_log", thread, txrate)
      dbsize = post_process_server(peer_log)
      post_process_client(client_log)
      if sys.argv[1]!="ustore":
        dbsize = get_db_size()
      print("db size: {}".format(dbsize))
