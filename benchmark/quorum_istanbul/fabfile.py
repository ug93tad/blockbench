import fabric
import os
import subprocess
import json

HOMEDIR="/users/dinhtta/blockbench/benchmark/quorum_istanbul"
ISTANBUL_CMD = "mkdir -p {} && cd {} && istanbul setup --num {} --verbose --quorum --nodes --save"
HOSTS="hosts"
def execute(cmd):
  os.system(cmd)

def get_ip(host):
  out = subprocess.check_output(["ping", "-c", "1", host])
  return out.split()[2].strip('()')

'''
fab setup:<# nodes>

read n nodes from file "hosts"
write to keys/nX directory: nodekey(s), static-nodes.json, genesis.json
'''
def setup(nodes):
  n = int(nodes)
  hf = open(HOSTS, 'r')
  hosts = [f.strip() for f in hf.readlines()]
  hosts=hosts[:n]

  # use istanbul-tools to generate keys and genesis file
  KEYS_DIR = "{}/keys".format(HOMEDIR)
  execute(ISTANBUL_CMD.format(KEYS_DIR, KEYS_DIR, n))
  
  # copy to ..keys/nX directory
  DEST = "{}/n{}".format(KEYS_DIR,n)
  execute("rm -rf {} && mkdir -p {}".format(DEST, DEST))
  for i in range(n):
    FROM = "{}/{}/nodekey".format(KEYS_DIR, i)
    execute("cp {} {}/nodekey{}".format(FROM, DEST, i))
    execute("rm -rf {}/{}".format(KEYS_DIR, i))
    
  # change static-nodes file
  fi = open("{}/static-nodes.json".format(KEYS_DIR), 'r')
  fo = open("{}/tmp".format(KEYS_DIR), 'w')
  lines = fi.readlines()
  c=0
  for l in lines:
    if l.find("0.0.0.0") != -1:
      fo.write(l.replace("0.0.0.0", get_ip(hosts[c])))
      c=c+1
    else:
      fo.write(l)
  fo.close()
  fi.close()
  execute("sed -i \'s/\"gasLimit\": \"0x47b760\"/\"gasLimit\": \"0xFFFFFFFFFF0\"/g\' {}/genesis.json".format(KEYS_DIR))
  execute("cp {}/tmp {}/n{}/static-nodes.json".format(KEYS_DIR, KEYS_DIR, n))
  execute("cp {}/genesis.json {}/n{}/".format(KEYS_DIR, KEYS_DIR, n))
  execute("rm -rf {}/tmp {}/static-nodes.json {}/genesis.json".format(KEYS_DIR, KEYS_DIR, KEYS_DIR))

def setup_all(nodes):
  f=0
  n = int(nodes)
  while (3*f+1 < n):
    setup(3*f+1)
    f=f+1
