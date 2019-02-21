import fabric
import os
import subprocess
import json

HOSTS="hosts"
HOMEDIR="/users/dinhtta/blockbench/benchmark/tendermint"
TESTNET_CMD="mkdir -p {} && tendermint testnet --v {} --o {}"
TESTNET_DIR="testnet/n{}"
def execute(cmd):
  os.system(cmd)

def get_ip(host):
  out = subprocess.check_output(["ping", "-c", "1", host])
  return out.split()[2].strip('()')

'''
fab setup:<# nodes>

read n nodes from file "hosts"
setup testnet/n{XX} directory for the specified # nodes
'''
def setup(nodes):
  n = int(nodes)
  hf = open(HOSTS, 'r')
  hosts = [f.strip() for f in hf.readlines()]
  hosts=hosts[:n]

  # create node0,node1,.. in testnet directory
  DIR="{}/{}".format(HOMEDIR, TESTNET_DIR.format(n))
  execute(TESTNET_CMD.format(DIR, n, DIR))

  # go through all nodeX/config.toml file and change
  for i in range(n):
    src = "{}/node{}/config/config.toml".format(DIR,i)
    dst = "{}/node{}/config/tmp".format(DIR,i)
    fh = open(src, 'r')
    fo = open(dst,'w')
    lines = fh.readlines()
    for l in lines:
      if l.find("node0") != -1:
        for k in range(n):
          l = l.replace("node{}".format(k), get_ip(hosts[k]), 1)
      if l.find("size = 5000") != -1:
        l = l.replace("5000", "50000")
#      if l.find("_rate = 5120000") != -1:
#        l = l.replace("5120000", "51200000")

      fo.write(l)
    fh.close()
    fo.close()
    execute("cp {} {}".format(dst, src))

def setup_all(nodes):
  f=0
  n = int(nodes)
  while (3*f+1 < n):
    setup(3*f+1)
    f=f+1
