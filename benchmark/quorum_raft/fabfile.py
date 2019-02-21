import fabric
import os
import subprocess
import json

DATADIR="/data/dinhtta/eth"
HOSTS="hosts"
HOMEDIR="/users/dinhtta/blockbench/benchmark/quorum_raft"
ENODE_CMD="./setup.sh"
GATHER_CMD="ssh {} \"cd {} && nohup fab get_enode:ip={},idx={} &\""
KEYS_FILE="{}/keys/{}"
def execute(cmd):
  os.system(cmd)

def get_ip(host):
  out = subprocess.check_output(["ping", "-c", "1", host])
  return out.split()[2].strip('()')

def get_enode(ip,idx):
  cmd = [ENODE_CMD]
  cmd.append(ip)
  p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  outs = p.communicate()[0].splitlines()[1:]

  f = open(KEYS_FILE.format(HOMEDIR,"enode{}".format(idx)), "w")
  o = outs[0]
  f.write("{}?{}".format(o.strip('""'), "raftport=50400"))
  f.close()

  f = open(KEYS_FILE.format(HOMEDIR,"nodekey{}".format(idx)), "w")
  f.write(outs[1])
  f.close()


'''
fab setup:<# nodes>

read n nodes from file "hosts"
init enodes and nodekeys for all nodes and writes to "keys" directory
create keys/static-nodesX.json containing X enodes (the node order is as listed in file "hosts")
'''
def setup(nodes):
  n = int(nodes)
  hf = open(HOSTS, 'r')
  hosts = [f.strip() for f in hf.readlines()]
  hosts=hosts[:n]
  for idx,h in enumerate(hosts):
    execute(GATHER_CMD.format(h, HOMEDIR, get_ip(h),idx))

  # create static files
  enodes=[]
  for i in range(n):
    f = open(KEYS_FILE.format(HOMEDIR, "enode{}".format(i)), "r")
    enodes.append(f.readlines()[0].strip('"'))
    f.close()
 
  f=0
  while ((2*f+1)<=n):
    fn = "static-nodes{}.json".format(2*f+1)
    fh = open(KEYS_FILE.format(HOMEDIR, fn), "w")
    fh.write(json.dumps(enodes[:(2*f+1)], indent=2))
    fh.close()
    f = f+1
