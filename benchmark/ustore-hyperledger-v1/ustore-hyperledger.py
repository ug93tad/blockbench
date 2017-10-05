import sys
import os
import subprocess
import time
import random
from process import *
from config import *

usage = """ ustore-hyperledger <db> <nrecords> <nwrites> <nreads> <ops_per_commit>
              
              db: either "goleveldb" or "UStore"
              nrecords: number of record to pre-load
              nreads/nwrites: number of read/writes ops
              ops_per_commit: how many ops before committing (creating new block)
        """
def setup(db):
  PEER_ENV = PEER_ENV_TEMPLATE.format(MSPCONFIG_PATH, DEPLOY_PATH, db, DEFAULT_SAMPLE_READ, DEFAULT_SAMPLE_WRITE)
  CHANNEL_ENV = PEER_ENV_TEMPLATE.format(CHANNEL_MSPCONFIG_PATH, DEPLOY_PATH, db, DEFAULT_SAMPLE_READ, DEFAULT_SAMPLE_WRITE)

  cmd = START_ORDERER_CMD.format(SERVER_LOG_PATH, DEPLOY_PATH, BUILD_PATH, ORDERER_ENV_TEMPLATE.format(GENESIS_PATH,
  ORDERER_MSP_PATH, ORDERER_PATH), SERVER_LOG_PATH, db)
  print cmd
  os.system(cmd)
  cmd = START_PEER_CMD.format(BUILD_PATH, PEER_ENV, LOGGING_LEVEL, SERVER_LOG_PATH, db)
  print cmd
  os.system(cmd)
  
  time.sleep(2)

  cmd = START_CHANNEL_CMD.format(BUILD_PATH, CHANNEL_ENV, PEER_CHANNEL_HOST, PEER_CHANNEL_NAME,
  PEER_CHANNEL_PATH, SERVER_LOG_PATH, db)
  print cmd
  os.system(cmd)
  cmd = JOIN_CHANNEL_CMD.format(BUILD_PATH, CHANNEL_ENV, PEER_CHANNEL_NAME, SERVER_LOG_PATH, db)
  print cmd
  os.system(cmd)
  time.sleep(2)

  
  cmd = INSTALL_CHAINCODE_CMD.format(BUILD_PATH, CHANNEL_ENV, CHAINCODE_NAME, CHAINCODE_PATH, SERVER_LOG_PATH,
  db)
  print cmd
  os.system(cmd)
  cmd = INSTANTIATE_CHAINCODE_CMD.format(BUILD_PATH, CHANNEL_ENV, PEER_CHANNEL_HOST, PEER_CHANNEL_NAME,
  CHAINCODE_NAME, CHAINCODE_CONSTRUCTOR_OPTS, CHAINCODE_POLICY_OPTS, SERVER_LOG_PATH, db)
  print cmd
  os.system(cmd)
  
  time.sleep(2)

def run():
  interval = int(sys.argv[5])
  # loading
  nloads = int(sys.argv[2])/interval
  for i in range(nloads):
    start = i*interval
    cmd = CLIENT_CMD.format(CLIENT_LOG_PATH, BUILD_PATH, "write", start, interval, CLIENT_LOG_PATH, sys.argv[1])
    os.system(cmd)

  # writing
  nwrites = int(sys.argv[3])/interval
  for i in range(nwrites):
    start = (i+nloads)*interval
    cmd = CLIENT_CMD.format(CLIENT_LOG_PATH, BUILD_PATH, "write", start, interval, CLIENT_LOG_PATH, sys.argv[1])
    os.system(cmd)

  # reading (random ranges)
  total_keys = (nloads+nwrites)*interval
  nreads = int(sys.argv[4])/interval
  max_key = total_keys - interval
  for i in range(nreads):
    start = random.randint(0,max_key-1)
    cmd = CLIENT_CMD.format(CLIENT_LOG_PATH, BUILD_PATH, "scan", start, interval, CLIENT_LOG_PATH, sys.argv[1])
    os.system(cmd)

def get_db_size():
  path = DEPLOY_PATH+"/ledgersData"
  return subprocess.check_output(['du','-sh', path]).split()[0]

if __name__ == "__main__":
  
  if len(sys.argv) != 6 :
    print usage
    sys.exit(1)

  setup(sys.argv[1])
  start = time.time()
  run()
  et = time.time() - start

  os.system(KILL_CMD)
  post_process_server(SERVER_LOG_PATH+"/peer_{}".format(sys.argv[1]), sys.argv[1])
  print("client time (s): {}".format(et))
  print("db size: {}".format(get_db_size()))
